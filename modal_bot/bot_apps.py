from modal import Image, Stub, Secret, Function

stub = Stub('bot-apps')
image = Image.debian_slim().pip_install("requests")

@stub.function()
def hello_app():
    print("hello from hello_app")

@stub.function()
def call_llm(prompt):
    f = Function.lookup("llm-2", "llm_command")
    f.spawn(prompt, ["bot-apps","post_msg"])

@stub.function(image=image,secret=Secret.from_name("discord-bot"))
def post_msg(message):
    import requests
    from os import getenv
    print(f"sending message {message}")
    requests.post(getenv("MESSAGE_URL"), json = { 'content': message })