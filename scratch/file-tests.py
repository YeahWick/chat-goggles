from modal import Stub, Image, Function, gpu

stub_name="file-testing"
model_name="TheBloke/Falcon-180B-Chat-GGUF"
model_file="falcon-180b-chat.Q4_K_M.gguf"
model_type="falcon"

def download_model():
    print("build image here")

stub = Stub(stub_name)
image = Image.debian_slim().copy_local_file("lib.py","/root/lib.py")

@stub.function(image=image)
def entry_function():
    from os import listdir, getcwd
    print(listdir())
    print(listdir("/"))
    print(getcwd())
    from lib import get_a_file
    get_a_file()