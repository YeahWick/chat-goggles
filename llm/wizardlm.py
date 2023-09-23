from modal import Stub, Image, Function

def download_model():
    from ctransformers import AutoModelForCausalLM

    # Set gpu_layers to the number of layers to offload to GPU. Set to 0 if no GPU acceleration is available on your system.
    llm = AutoModelForCausalLM.from_pretrained("TheBloke/WizardLM-7B-uncensored-GGUF", model_file="WizardLM-7B-uncensored.Q4_K_M.gguf", model_type="llama")# , gpu_layers=50)

stub = Stub('wizardlm')
image = Image.debian_slim().pip_install("ctransformers").run_function(download_model)

@stub.function(image=image)
def wizardlm():
    from ctransformers import AutoModelForCausalLM
    llm = AutoModelForCausalLM.from_pretrained("TheBloke/WizardLM-7B-uncensored-GGUF", model_file="WizardLM-7B-uncensored.Q4_K_M.gguf", model_type="llama", local_files_only=True)# , gpu_layers=50)
    print(llm("A bash function to change a aws ec2 tag:"))
    print(llm.__dict__)
    print(help(llm))