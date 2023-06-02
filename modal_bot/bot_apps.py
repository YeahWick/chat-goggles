from modal import Image, Stub, Secret, Function

stub = Stub('bot-apps')
image = Image.debian_slim().pip_install("requests")

@stub.function()
def hello_app():
    print("hello from hello_app")

@stub.function()
def call_llm(prompt):
    f = Function.lookup("llm-1", "llm_command")
    f.spawn(prompt, post_msg)

@stub.function(image=image,secret=Secret.from_name("discord-bot"))
def post_msg(message: str):
    import requests
    from os import getenv
    requests.post(getenv("MESSAGE_URL"), json = { 'content': message })