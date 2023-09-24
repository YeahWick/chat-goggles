from modal import Stub, Image, Function, gpu

model_name="TheBloke/Marcoroni-70B-GGUF"
model_file="marcoroni-70b.Q3_K_M.gguf"
model_type="llama"

def download_model():
    from ctransformers import AutoModelForCausalLM

    # Set gpu_layers to the number of layers to offload to GPU. Set to 0 if no GPU acceleration is available on your system.
    AutoModelForCausalLM.from_pretrained(model_name, model_file=model_file, model_type=model_type)# , gpu_layers=50)

stub = Stub('Marcoroni_70b')
image = Image.debian_slim().pip_install("ctransformers[cuda]").run_function(download_model)

@stub.function(image=image)
def entry_function():
    from ctransformers import AutoModelForCausalLM
    llm = AutoModelForCausalLM.from_pretrained(model_name, model_file=model_file, model_type=model_type, local_files_only=True)
    print(llm("User:\nWhat is the carry capacity of a fully laden swallow?\n\nResponse:", max_new_tokens=400))