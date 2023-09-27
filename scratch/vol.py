from modal import Stub, Image, Volume

stub = Stub('volume-test')
stub.volume = Volume.persisted("models-test1")

image = Image.debian_slim().pip_install(["huggingface_hub", "ctransformers"])

@stub.function(image=image, volumes={"/models": stub.volume})
def download(repo_name: str, file_name: str):
    from huggingface_hub import cached_download, hf_hub_url
    cached_download(hf_hub_url(repo_id=repo_name, filename=file_name), force_filename=f"/models/{file_name}")
    stub.volume.commit()  # Persist changes

@stub.function(image=image, volumes={"/models": stub.volume})
def invoke(repo_name: str, file_name: str, prompt: str):
    from ctransformers import AutoModelForCausalLM
    stub.volume.reload()
    llm = AutoModelForCausalLM.from_pretrained(f"/models/{file_name}", model_type="falcon")
    print(llm(f"{prompt}", max_new_tokens=400))