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

client = discord.Client()

class Reminder:
    def __init__(self, message_obj):
        args = message_obj.content.split(" ")
        self.args = args
        self.time_arg = False

    def remind(self):
        if self.args[0] == "min" or self.args[0] == "mins" or self.args[0] == "minute" or self.args[0] == "minutes" or self.args[0] == "m":
            self.time *= 60
            self.time_arg = True
        elif self.args[0] == "hour" or self.args[0] == "hours" or self.args[0] == "hr" or self.args[0] == "hrs" or self.args[0] == "h":
            self.time *= 3600
            self.time_arg = True
        elif self.args[0] == "day" or self.args[0] == "days" or self.args[0] == "d":
            self.time *= 86400
            self.time_arg = True

        t = Timer(self.time, self.handle_command)
        t.start()


    def handle_command(self):
        reponse_str = " ".join(self.args)
        print(response_str)


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