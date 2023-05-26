import modal
import os
stub = modal.Stub("hello-discord")

@stub.function(secret=modal.Secret.from_name("discord-bot"))
def f():
    return os.environ["DISCORD_BOT"]

@stub.function(secret=modal.Secret.from_name("my-custom-secret"))
def ft():
    print(os.environ["testke"])


@stub.local_entrypoint()
def main():
    ft.call()