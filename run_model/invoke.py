from modal import Stub, Image, Volume, Function, Queue, method
from ftypes import DownloadArgs, InvokeArgs

stub = Stub('invoke')
stub.volume = Volume.persisted("models")
stub.queue = Queue.persisted("invoke-queue")

vol_mnt = "/models"

image = Image.debian_slim().pip_install(["huggingface_hub", "ctranslate2", "torch", "transformers", "accelerate"])



@stub.function(image=image, volumes={vol_mnt: stub.volume})
def download(args: DownloadArgs):
    from huggingface_hub import hf_hub_download
    from ctranslate2.converters import TransformersConverter
    from pathlib import Path
    import os, shutil

    target_dir = f"{vol_mnt}/{args.repo_name}"
    os.makedirs(target_dir, exist_ok=True)

    #TODO move this
    import torch
    import gc
    from ctranslate2.converters.transformers import register_loader, ModelLoader
    from ctranslate2.specs import (
        common_spec,
        transformer_spec,
    )
    @register_loader("MistralConfig")
    class MistralLoader(ModelLoader):
        @property
        def architecture_name(self):
            return "MistralForCausalLM"

        def get_model_spec(self, model):
            num_layers = model.config.num_hidden_layers

            num_heads = model.config.num_attention_heads
            num_heads_kv = getattr(model.config, "num_key_value_heads", num_heads)
            if num_heads_kv == num_heads:
                num_heads_kv = None

            spec = transformer_spec.TransformerDecoderModelSpec.from_config(
                num_layers,
                num_heads,
                activation=common_spec.Activation.SWISH,
                pre_norm=True,
                ffn_glu=True,
                rms_norm=True,
                rotary_dim=0,
                rotary_interleave=False,
                num_heads_kv=num_heads_kv,
            )

            self.set_decoder(spec.decoder, model.model)
            self.set_linear(spec.decoder.projection, model.lm_head)
            return spec

        def get_vocabulary(self, model, tokenizer):
            tokens = super().get_vocabulary(model, tokenizer)

            extra_ids = model.config.vocab_size - len(tokens)
            for i in range(extra_ids):
                tokens.append("<extra_id_%d>" % i)

            return tokens

        def set_vocabulary(self, spec, tokens):
            spec.register_vocabulary(tokens)

        def set_config(self, config, model, tokenizer):
            config.bos_token = tokenizer.bos_token
            config.eos_token = tokenizer.eos_token
            config.unk_token = tokenizer.unk_token
            config.layer_norm_epsilon = model.config.rms_norm_eps

        def set_layer_norm(self, spec, layer_norm):
            spec.gamma = layer_norm.weight

        def set_decoder(self, spec, module):
            spec.scale_embeddings = False
            self.set_embeddings(spec.embeddings, module.embed_tokens)
            self.set_layer_norm(spec.layer_norm, module.norm)

            for layer_spec, layer in zip(spec.layer, module.layers):
                self.set_layer_norm(
                    layer_spec.self_attention.layer_norm, layer.input_layernorm
                )
                self.set_layer_norm(
                    layer_spec.ffn.layer_norm, layer.post_attention_layernorm
                )

                wq = layer.self_attn.q_proj.weight
                wk = layer.self_attn.k_proj.weight
                wv = layer.self_attn.v_proj.weight
                wo = layer.self_attn.o_proj.weight

                layer_spec.self_attention.linear[0].weight = torch.cat([wq, wk, wv])
                layer_spec.self_attention.linear[1].weight = wo

                self.set_linear(layer_spec.ffn.linear_0, layer.mlp.gate_proj)
                self.set_linear(layer_spec.ffn.linear_0_noact, layer.mlp.up_proj)
                self.set_linear(layer_spec.ffn.linear_1, layer.mlp.down_proj)

                delattr(layer, "self_attn")
                delattr(layer, "mlp")
                gc.collect()

    converter = TransformersConverter(args.repo_name, low_cpu_mem_usage=True)
    converter.convert(Path(f"{target_dir}/converted").as_posix(), quantization="int8")
    stub.volume.commit()

@stub.function(image=image, volumes={vol_mnt: stub.volume}, timeout=1800)
def invoke(args: InvokeArgs, callback: Function):
    from ctranslate2 import Generator
    from transformers import AutoTokenizer
    import os

    stub.volume.reload()
    file_path = f"{vol_mnt}/{args.repo_name}"
    if not os.path.isdir(f"{file_path}/converted"):
        download.remote(DownloadArgs(repo_name=args.repo_name, file_name=args.file_name))
        stub.volume.reload()

    translator = Generator(f"{vol_mnt}/{args.repo_name}/converted", compute_type="int8")
    tokenizer = AutoTokenizer.from_pretrained(args.repo_name) #TODO cache this too
    prompt_tokenized = tokenizer.convert_ids_to_tokens(
            tokenizer.encode(args.prompt)
        )
    print("call 1")
    output = translator.generate_batch([prompt_tokenized], max_length=args.context_length)
    target = output[0]
    print(output[0])
    print("call 2")
    output = translator.generate_batch([prompt_tokenized], max_length=args.context_length)
    target = output[0]
    print(output[0])
    print_out = tokenizer.decode(tokenizer.convert_tokens_to_ids(target.sequences[0]), skip_special_tokens=True)
    if callback is None:
        print(print_out)
    else:
        callback.spawn(output["choices"][0]["text"])

@stub.cls(image=image, volumes={vol_mnt: stub.volume}, timeout=1800)
class RunQueue():
    # TODO fix how this gets which model, right now
    # it just assumes all models within the queue are the same.
    def __enter__(self):
        from llama_cpp import Llama
        import os

        if stub.queue.len() > 0:
            args = stub.queue.get()
            stub.volume.reload()
            file_path = f"{vol_mnt}/{args.repo_name}/{args.file_name}"
            if not os.path.isfile(file_path):
                download.remote(DownloadArgs(repo_name=args.repo_name, file_name=args.file_name))
                stub.volume.reload()
            self.llm = Llama(f"{vol_mnt}/{args.repo_name}/{args.file_name}")
            self.invoke_llm(args.prompt, args.target, args.context_length)

    def invoke_llm(self, prompt, target, max_tokens):
        output = self.llm(prompt, max_tokens=max_tokens)
        print(output, target)

    @method()
    def run_queue(self):
        while stub.queue.len() > 0:
            args = stub.queue.get() #TODO use get_many and process multiple
            self.invoke_llm(args.prompt, args.target, args.context_length)

@stub.function(image=image, volumes={vol_mnt: stub.volume})
def list_files():
    import os
    stub.volume.reload()
    return_strs = []
    return_strs.append(f"{vol_mnt}\n")

    def traverse_directory(directory, return_strs):
        for item in os.listdir(directory):
            path = os.path.join(directory, item)
            if os.path.isfile(path):
                size = os.path.getsize(path)
                return_strs.append(f"{directory}/{item} {size}\n")
            elif os.path.isdir(path):
                traverse_directory(path, return_strs)

    traverse_directory(vol_mnt, return_strs)
    return ''.join(return_strs)

