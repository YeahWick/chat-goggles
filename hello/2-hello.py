from modal import Stub, Mount, Image, Function
import sys
sys.path.append('../run_model')

from run_model.vol import InvokeArgs

stub = Stub('2-hello-sandbox')
image = Image.debian_slim()

@stub.function(image=image)
def hello():
    f = Function.lookup("model-volume","invoke")

    instruction="write some python code that prints hello"
    prompt=f"Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:\n{instruction}\n\n### Response:"
    
    # Passing hello_callback directly doesn't appear to work, need to use Function lookup.
    f.spawn(InvokeArgs(
        repo_name="TheBloke/WizardCoder-Python-13B-V1.0-GGUF",
        file_name="wizardcoder-python-13b-v1.0.Q5_K_M.gguf",
        prompt=f"{prompt}", model_type="llama"), callback=Function.lookup("code-sandbox","code_callback"))