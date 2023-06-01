from modal import Stub, Secret, Image, gpu

def download_model():
    from huggingface_hub import snapshot_download

    snapshot_download(repo_id="tiiuae/falcon-7b-instruct", revision="9cbb1610be271fd06576e7e00f60e75612d53a4d")

def get_pretrained():
    from transformers import AutoTokenizer
    model = "tiiuae/falcon-7b-instruct"
    AutoTokenizer.from_pretrained(model, trust_remote_code=True, revision="9cbb1610be271fd06576e7e00f60e75612d53a4d")

stub = Stub()
image = Image.debian_slim().pip_install("transformers", "torch", "einops",
                                        "huggingface_hub").run_function(download_model).pip_install("accelerate").run_function(get_pretrained)


@stub.function(image=image, gpu="A100")
async def llm_command():
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import transformers
    import torch
    
    model = "tiiuae/falcon-7b-instruct"
    
    tokenizer = AutoTokenizer.from_pretrained(model, trust_remote_code=True, revision="9cbb1610be271fd06576e7e00f60e75612d53a4d")
    pipeline = transformers.pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
        device_map="auto",
    )
    sequences = pipeline(
       "Please write out some code to post images with an interactions discord bot in python",
        max_length=400,
        do_sample=True,
        top_k=10,
        num_return_sequences=1,
        #eos_token_id=tokenizer.eos_token_id,
        eos_token_id=11, #bug see https://huggingface.co/TheBloke/falcon-40b-instruct-GPTQ/discussions/8
    )
    for seq in sequences:
        print(f"Result: {seq['generated_text']}")