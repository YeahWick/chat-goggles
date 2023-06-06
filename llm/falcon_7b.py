from modal import Stub, Secret, Image, gpu

def download_model():
    from huggingface_hub import snapshot_download

    snapshot_download(repo_id="tiiuae/falcon-7b-instruct", revision="9cbb1610be271fd06576e7e00f60e75612d53a4d")

def get_pretrained():
    from transformers import AutoTokenizer
    model = "tiiuae/falcon-7b-instruct"
    AutoTokenizer.from_pretrained(model, trust_remote_code=True, revision="22225c3ac76bdddc1c6c44ebea0e3109468de29f")

stub = Stub('llm-1')
image = Image.debian_slim().pip_install("transformers", "torch", "einops",
                                        "huggingface_hub").run_function(download_model).pip_install("accelerate").run_function(get_pretrained)

@stub.function(image=image, gpu="A100")
def llm_command(prompt: str, callback):
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import transformers
    import torch
    
    model_name = "tiiuae/falcon-7b-instruct"
    config = transformers.AutoConfig.from_pretrained(model_name,
                                                     revision="22225c3ac76bdddc1c6c44ebea0e3109468de29f", trust_remote_code=True)
    config.init_device = 'cuda:0' 
    model = AutoModelForCausalLM.from_pretrained("tiiuae/falcon-7b-instruct", config=config, revision="22225c3ac76bdddc1c6c44ebea0e3109468de29f", trust_remote_code=True)
    
    tokenizer = AutoTokenizer.from_pretrained(
        model_name, trust_remote_code=True, revision="22225c3ac76bdddc1c6c44ebea0e3109468de29f")
    pipeline = transformers.pipeline(
        "text-generation",
        model=model,
        config=config,
        tokenizer=tokenizer,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
        device_map="auto",
    )
    sequences = pipeline(
        prompt,
        max_length=400,
        do_sample=True,
        top_k=10,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
        #eos_token_id=11, #bug see https://huggingface.co/TheBloke/falcon-40b-instruct-GPTQ/discussions/8
    )
    for seq in sequences:
        #print(f"Result: {seq['generated_text']}")
        callback.spawn(seq['generated_text'])