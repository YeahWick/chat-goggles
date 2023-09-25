from modal import Stub, Image, Function

model_name="TheBloke/WizardLM-Uncensored-Falcon-7B-GGML"
model_file="wizardlm-7b-uncensored.ggccv1.q4_1.bin"

def download_model():
    from ctransformers import AutoModelForCausalLM

    # Set gpu_layers to the number of layers to offload to GPU. Set to 0 if no GPU acceleration is available on your system.
    llm = AutoModelForCausalLM.from_pretrained(model_name, model_file=model_file, model_type="falcon")# , gpu_layers=50)

stub = Stub('falcon_7b_testload')
image = Image.debian_slim().pip_install("ctransformers").run_function(download_model).pip_install("shshsh")

@stub.function(image=image)
def entry_function():
    from ctransformers import AutoModelForCausalLM
    from shshsh import I
    from sys import stdout
    I >> "ls -lahR .cache" | stdout
    I >> "cat .cache/huggingface/hub/models--TheBloke--WizardLM-Uncensored-Falcon-7B-GGML/blobs/4fbd426045375e836e4684bd0654beb64d1777f8" | stdout
    llm = AutoModelForCausalLM.from_pretrained(".cache/huggingface/hub/models--TheBloke--WizardLM-Uncensored-Falcon-7B-GGML/blobs/3cbbee3b69abaa933e9c96ef6e4b558fd85ac012f02a7a6fbec034ad2d2172a6", model_type="falcon")
    print(llm("What is the carry capacity of a full laden swallow?", max_new_tokens=400))