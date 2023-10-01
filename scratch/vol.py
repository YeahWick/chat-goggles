from modal import Stub, Image, Volume

stub = Stub('volume-test')
stub.volume = Volume.persisted("models-test1")

image = Image.debian_slim().pip_install(["huggingface_hub", "ctransformers"])

@stub.function(image=image, volumes={"/models": stub.volume})
def download(repo_name: str, file_name: str):
    from huggingface_hub import hf_hub_download, hf_hub_url
    import os, shutil
    os.mkdir("/model_downloads")
    model_file = hf_hub_download(repo_id=repo_name, filename=file_name, cache_dir=f"/model_downloads/")
    shutil.copy(model_file, "/models/")
    stub.volume.commit()  # Persist changes

@stub.function(image=image, volumes={"/models": stub.volume}, timeout=1800)
def invoke(repo_name: str, file_name: str, prompt: str, model_type: str):
    from ctransformers import AutoModelForCausalLM
    stub.volume.reload()
    llm = AutoModelForCausalLM.from_pretrained(f"/models/{file_name}", model_type=model_type)
    print(llm(f"{prompt}", max_new_tokens=400))

@stub.function(image=image, volumes={"/models": stub.volume})
def list_files():
    import os
    for f in os.listdir("/models"):
        s=os.path.getsize(f"/models/{f}")
        print(f"{f} {s}")