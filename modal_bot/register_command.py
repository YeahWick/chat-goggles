from modal import Stub, Secret, Image

stub = Stub()
image = Image.debian_slim().pip_install( "requests")

@stub.function(image=image, secrets=[Secret.from_name("discord-bot")])
async def reg_command():
    import requests
    import os
    
    guild_id = os.getenv("GUILD_ID")
    app_id = os.getenv("APP_ID")
    bot_token = os.getenv("BOT_TOKEN")
    
    url = f"https://discord.com/api/v10/applications/{app_id}/guilds/{guild_id}/commands"
    
    # This is an example USER command, with a type of 2
    json = {
        "name": "High Five",
        "type": 2
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