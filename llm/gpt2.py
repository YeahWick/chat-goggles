from modal import Stub, Image, Function

def download_model():
    from huggingface_hub import snapshot_download

    snapshot_download(repo_id="gpt2")

def transformers_cache():
    import transformers
    transformers.utils.move_cache()

stub = Stub('llm-2')
image = Image.debian_slim().pip_install("transformers", "torch", "einops",
                                        "huggingface_hub").run_function(download_model).pip_install("accelerate").run_function(transformers_cache)

@stub.function(image=image, gpu="any")
def llm_command(prompt: str, callback = None):
    import torch
    from transformers import AutoTokenizer
    import transformers

    model_name = 'gpt2'

    pipeline = transformers.pipeline(
        "text-generation",
        model=model_name,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
        device_map="auto"
    )
    sequences = pipeline(
        prompt,
        max_length=400,
        do_sample=True,
        top_k=10,
        num_return_sequences=1,
    )
    if callback != None:
        print("calling callback")
        cb = Function.lookup(callback[0],callback[1])
        cb.spawn(sequences[0]['generated_text'])
    else:
        print(sequences[0]['generated_text'])