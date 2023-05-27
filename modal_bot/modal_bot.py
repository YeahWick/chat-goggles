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

    web_app = Flask(__name__)

    CLIENT_PUBLIC_KEY = getenv('CLIENT_PUBLIC_KEY')

    @web_app.get("/")
    def home():
        return "Hello Flask World!"

    @web_app.post('/interactions')
    @verify_key_decorator(CLIENT_PUBLIC_KEY)
    def interactions():
        if request.json["type"] == 1:
            return jsonify({
                "type": 1
            })
        if request.json['type'] == InteractionType.APPLICATION_COMMAND:
            return jsonify({
                'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                'data': {
                    'content': 'Hello world'
                }
            })

    @web_app.after_request
    def after_request(response):
        timestamp = strftime('[%Y-%b-%d %H:%M]')
        print('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)
        return response

    return web_app