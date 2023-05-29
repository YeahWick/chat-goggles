from modal import Stub, Secret, Image

stub = Stub()
image = Image.debian_slim().pip_install( "requests")

@stub.function(image=image, secrets=[Secret.from_name("discord-bot")])
async def reg_command(environment: str):
    import requests
    import os
    
    guild_id = os.getenv("GUILD_ID")

    app_config = dict(
        dev=dict(
            app_id=os.getenv("APP_ID"),
            bot_token=os.getenv("BOT_TOKEN"),
            name_suffix="-dev"
        ),
        prod=dict(
            app_id=os.getenv("APP_ID_PROD"),
            bot_token=os.getenv("BOT_TOKEN_PROD"),
            name_suffix=""
        )
    )
    app_id = app_config.get(environment).get("app_id")
    name_suffix = app_config.get(environment).get("name_suffix")
    bot_token = app_config.get(environment).get("bot_token")

    
    url = f"https://discord.com/api/v10/applications/{app_id}/guilds/{guild_id}/commands"
    
    json = {
        "name": f"Message Send{name_suffix}",
        "type": 3
    }
    
    # For authorization, you can use either your bot token
    headers = {
        "Authorization": f"Bot {bot_token}"
    }
    
    # or a client credentials token for your app with the applications.commands.update scope
    #headers = {
    #    "Authorization": "Bearer <my_credentials_token>"
    #}
    
    requests.post(url, headers=headers, json=json, timeout=15)

@stub.function(image=image, secrets=[Secret.from_name("discord-bot")])
async def list_commands():
    import requests
    import os
    
    guild_id = os.getenv("GUILD_ID")
    app_id = os.getenv("APP_ID")
    bot_token = os.getenv("BOT_TOKEN")
    
    url = f"https://discord.com/api/v10/applications/{app_id}/guilds/{guild_id}/commands"
    
    headers = {
        "Authorization": f"Bot {bot_token}"
    }

    print(requests.get(url, headers=headers, timeout=15).content)

@stub.function(image=image, secrets=[Secret.from_name("discord-bot")])
async def del_command(command_id: int):
    import requests
    import os
    
    guild_id = os.getenv("GUILD_ID")
    app_id = os.getenv("APP_ID")
    bot_token = os.getenv("BOT_TOKEN")

    url = f"https://discord.com/api/v10/applications/{app_id}/guilds/{guild_id}/commands/{command_id}"

    headers = {
        "Authorization": f"Bot {bot_token}"
    }

    print(requests.delete(url, headers=headers, timeout=15).content)