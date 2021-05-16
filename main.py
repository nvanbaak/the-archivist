import discord
import config
import random
import os
from threading import Timer
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from state_manager import State_Manager

client = discord.Client()
state_manager = State_Manager(client)

@client.event
async def on_ready():
    print('Bot successfully logged in as: {user}'.format(user=client.user))
    state_manager.set_channel(client.get_channel(config.game_channel_id))
    await state_manager.game_channel.send("Archivist online!")

@client.event
async def on_message(message):
    await state_manager.route_message(message)

client.run(config.bot_token)