from modal import Stub, Image, Function

model_splits = []

def download_model_splits():
    import huggingface_hub
    from shshsh import I
    for i in ["a", "b", "c"]:
        model_url = huggingface_hub.hf_hub_url(repo_id="TheBloke/Falcon-180B-Chat-GGUF", filename=f"falcon-180b-chat.Q4_K_M.gguf-split-{i}")
        model_splits.append(huggingface_hub.cached_download(model_url))
    mp_str = " ".join(model_splits)
    print(f"cat {mp_str} > /falcon-180b-chat.Q4_K_M.gguf")
    c4 = I >> f"cat {mp_str}" | "tee /falcon-180b-chat.Q4_K_M.gguf"
    c4.wait()
    for i in model_splits:
        c5 = I >> f"rm {i}"
        c5.wait()

stub = Stub('falcon_180b_v2')
image = Image.debian_slim().pip_install(["ctransformers", "shshsh","huggingface_hub"])\
    .run_function(download_model_splits)

# This has not successfully run. Ill leave it here but will try to move the model to a volume so the image is small.
@stub.function(image=image)
def entry_function():
    from ctransformers import AutoModelForCausalLM
    llm = AutoModelForCausalLM.from_pretrained("/falcon-180b-chat.Q4_K_M.gguf", model_type="falcon")
    print(llm("What is the carry capacity of a fully laden swallow?", max_new_tokens=400))