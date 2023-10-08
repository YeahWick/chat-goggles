from modal import Stub, Mount, Image, Function
import sys
sys.path.append('../run_model')

from run_model.invoke import InvokeArgs

stub = Stub('3-compare')
image = Image.debian_slim()

@stub.function(image=image)
def hello():
    f = Function.lookup("invoke","invoke")

    instruction="Write python code that will make a request to http://slashdot.org and return story headings. Return working code only."
    prompt=f"Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:import \n{instruction}\n\n### Response:"
    
    # Passing hello_callback directly doesn't appear to work, need to use Function lookup.
    f.spawn(InvokeArgs(
        repo_name="TheBloke/WizardCoder-Python-13B-V1.0-GGUF",
        file_name="wizardcoder-python-13b-v1.0.Q5_K_M.gguf",
        prompt=f"{prompt}", model_type="llama"), callback=Function.lookup("code-sandbox","code_callback"))