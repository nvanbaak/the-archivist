import discord
import config
import random
import os
from threading import Timer
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from game import Game
from stats import Statistics
from data_manager import Data_Manager
from lobby import Lobby
from state-_manager import State_Manager

client = discord.Client()


# create instances of stats engine, data manager, and state manager
stats = Statistics()
dm = Data_Manager()
state_manager = State_Manager()

# We set this value here because the state manager and the stats engine don't talk to each other right now
state_manager.game_count = len(stats.games)

@client.event
async def on_ready():
    print('Bot successfully logged in as: {user}'.format(user=client.user))
    state_manager.set_channel(client.get_channel(config.game_channel_id))
    await state_manager.game_channel.send("Archivist online!")

@client.event
async def on_message(message):
    await state_manager.route_message(message, stats, dm)

client.run(config.bot_token)