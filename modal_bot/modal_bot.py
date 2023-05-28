from modal import Image, Stub, wsgi_app, Secret

stub = Stub("bot-v2")
image = Image.debian_slim().pip_install( "flask", "discord_interactions")

@stub.function(image=image,
               secret=Secret.from_name("discord-bot"))
@wsgi_app()
def flask_app():
    from flask import Flask, request, jsonify
    from discord_interactions import verify_key_decorator, InteractionType, InteractionResponseType
    from os import getenv
    from time import strftime
    import json, sys

    web_app = Flask(__name__)

    CLIENT_PUBLIC_KEY = getenv('CLIENT_PUBLIC_KEY')

    @web_app.get("/")
    def home():
        return "Hello Flask World!"

    @web_app.post('/interactions')
    @verify_key_decorator(CLIENT_PUBLIC_KEY)
    def interactions():
        if request.json['type'] == InteractionType.APPLICATION_COMMAND:
            msgs = " ".join([v['content'] for k,v in request.json['data']['resolved']['messages'].items()])
            return jsonify({
                'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                'data': {
                    'content': f"responding to: {msgs}"
                }
            })

    @web_app.after_request
    def after_request(response):
        timestamp = strftime('[%Y-%b-%d %H:%M]')
        print(f"{timestamp}, remote add: {request.remote_addr}, method: {request.method}, scheme: {request.scheme}, path: {request.full_path}, status: {response.status}")
        return response

    return web_app