from modal import Stub, Image, Volume
from typing import NamedTuple

# Define NamedTuple classes for download and invoke arguments
class DownloadArgs(NamedTuple):
    repo_name: str
    file_name: str

    def __post_init__(self):
        self.repo_name = self.repo_name.replace("/", "-")

class InvokeArgs(NamedTuple):
    repo_name: str
    file_name: str
    prompt: str
    model_type: str

    def __post_init__(self):
        self.repo_name = self.repo_name.replace("/", "-")

stub = Stub('model-volume')
stub.volume = Volume.persisted("models")

vol_mnt = "/models"
max_tokens = 500

image = Image.debian_slim().pip_install(["huggingface_hub", "ctransformers"])

@stub.function(image=image, volumes={vol_mnt: stub.volume})
def download(args: DownloadArgs):
    from huggingface_hub import hf_hub_download
    import os, shutil

    target_dir = f"{vol_mnt}/{args.repo_name}"
    os.makedirs(target_dir, exist_ok=True)

    downloads_dir = "/model_downloads"
    os.mkdir(downloads_dir)
    model_file = hf_hub_download(repo_id=args.repo_name, filename=args.file_name, cache_dir=downloads_dir)

    shutil.copy(model_file, target_dir)
    stub.volume.commit()

@stub.function(image=image, volumes={vol_mnt: stub.volume}, timeout=1800)
def invoke(args: InvokeArgs):
    from ctransformers import AutoModelForCausalLM

    stub.volume.reload()
    file_path = f"{vol_mnt}/{args.repo_name}/{args.file_name}"
    if not os.path.isfile(file_path):
        download(DownloadArgs(repo_name=args.repo_name, file_name=args.file_name))

    llm = AutoModelForCausalLM.from_pretrained(f"{vol_mnt}/{args.repo_name}/{args.file_name}", model_type=args.model_type)
    print(llm(args.prompt, max_new_tokens=max_tokens))

@stub.function(image=image, volumes={vol_mnt: stub.volume})
def list_files():
    import os
    print(f"{vol_mnt}")
    for f in os.listdir(f"{vol_mnt}"):
        s = os.path.getsize(f"{vol_mnt}/{f}")
        print(f"{f} {s}")