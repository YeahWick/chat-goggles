from modal import Stub, Image, Function, gpu

stub_name="file-testing"
model_name="TheBloke/Falcon-180B-Chat-GGUF"
model_file="falcon-180b-chat.Q4_K_M.gguf"
model_type="falcon"

def download_model():
    from ctransformers import AutoModelForCausalLM

    # Set gpu_layers to the number of layers to offload to GPU. Set to 0 if no GPU acceleration is available on your system.
    #AutoModelForCausalLM.from_pretrained(model_name, model_file=model_file, model_type=model_type)# , gpu_layers=50)
    print("build image here")

stub = Stub(stub_name)
image = Image.debian_slim().pip_install("ctransformers[cuda]")\
        .run_commands(["echo 123 > file1", "echo 567 > file2", "cat file1 file2 > file3"])\
        .run_function(download_model).pip_install("shshsh")

@stub.function(image=image)
def entry_function():
    from ctransformers import AutoModelForCausalLM
    #llm = AutoModelForCausalLM.from_pretrained(model_name, model_file=model_file, model_type=model_type, local_files_only=True)
    #print(llm("What is the carry capacity of a fully laden swallow?", max_new_tokens=400))
    from shshsh import I
    from sys import stdout
    res = I >> "cat /file3" | stdout
    res.wait()