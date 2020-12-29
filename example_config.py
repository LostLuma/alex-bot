# config file. copy to `config.py` and fill in your details.

import os

import discord

token = os.environ.get('BOT_TOKEN')

cat_token = os.environ.get('THECATAPI_KEY')

avwx_token = os.environ.get('AVWX_KEY')

prefix = "a!"

location = "prod or dev"

government_is_working = True

logging = {
    'info': 'webhook url here',
    'warning': 'webhook here too',
    'error': 'webhook url here three',

}
#  bots who's owner gets a dm whenever they go offline
monitored_bots = {
    288369203046645761: {  # Mousey
        'owner_id': 69198249432449024,  # SnowyLuma
        'shard_count': 2,  # Optional shard count of the Bot
    },
}

ringRates = {
    discord.Status.online: {
        "times": 4,
        "rate": 0.5
    },
    discord.Status.idle: {
        "times": 10,
        "rate": 1
    },
    discord.Status.dnd: {
        "times": 1,
        "rate": 1
    },
    discord.Status.offline: {
        "times": 15,
        "rate": 2
    }
}

listenServers = [272885620769161216]
listens = ['alex', 'alaska']
