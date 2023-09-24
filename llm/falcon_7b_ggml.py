from modal import Stub, Image, Function

model_name="TheBloke/WizardLM-Uncensored-Falcon-7B-GGML"
model_file="wizardlm-7b-uncensored.ggccv1.q4_1.bin"

def download_model():
    from ctransformers import AutoModelForCausalLM

    # Set gpu_layers to the number of layers to offload to GPU. Set to 0 if no GPU acceleration is available on your system.
    llm = AutoModelForCausalLM.from_pretrained(model_name, model_file=model_file, model_type="falcon")# , gpu_layers=50)

stub = Stub('falcon_7b')
image = Image.debian_slim().pip_install("ctransformers").run_function(download_model)

@stub.function(image=image)
def entry_function():
    from ctransformers import AutoModelForCausalLM
    llm = AutoModelForCausalLM.from_pretrained(model_name, model_file=model_file, model_type="falcon", local_files_only=True)# , gpu_layers=50)
    print(llm("What is the carry capacity of a full laden swallow?", max_new_tokens=400))