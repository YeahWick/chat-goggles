from modal import Stub, Image, Volume

stub = Stub('volume-combine-files')
stub.volume = Volume.persisted("models-test1")

image = Image.debian_slim().pip_install(["huggingface_hub", "ctransformers"])

@stub.function(image=image, volumes={"/models": stub.volume}, timeout=15000)
def download(repo_name: str, file_names: str, destination_name: str):
    from huggingface_hub import hf_hub_download
    import os, shutil
    file_names_list = file_names.split(",")
    model_files = []
    for f in file_names_list:
        model_files.append(hf_hub_download(repo_id=repo_name, filename=f, cache_dir=f"/models"))

    model_file = open(f"/models/{destination_name}","wb")
    for f in model_files:
        fo=open(f,"rb")
        shutil.copyfileobj(fo, model_file)
        fo.close()
    model_file.close()
    from pathlib import Path
    stub.volume.commit()  # Persist changes