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

class State_Manager:
    def __init__(self):
        self.game_channel = None
        self.current_game = None
    
    def set_channel(self, channel_obj):
        self.game_channel = channel_obj
        print( "Set output channel to {channel}.".format(channel=channel_obj))
        return

    def is_this_the_game_channel(self, message_obj):
        if self.game_channel == message_obj.channel:
            return True
        else:
            return False

    async def route_message(self, message, stats, dm):
        if message.author == client.user:
            return
    
        print(message)

        if message.content.startswith('$hello'):
            await message.channel.send('Hello {message.author.name}!'.format(message=message))

        if message.content.startswith('$randomEDH'):
            await message.channel.send(stats.random_game().game_state())

        if message.content.startswith('$notif') or message.content.startswith('$remind'):
            remind = Reminder(message)
            remind.remind()

        if message.content.startswith('$stats'):
            response = stats.handle_command(message)

            if response == "":
                pass
            else:
                await message.channel.send(response)

        if message.content.startswith('$game'):
            # Check if there is is a game

            # user might just be checking if there's a game; we don't need to start a new one in that case
            status_update = message.content.startswith('$game status') or message.content.startswith('$game state')

            if status_update and self.current_game is None:
                await self.game_channel.send("There is currently no active game.")
                return

            # likewise, if they're just using the help menu, we don't need a new game either
            elif message.content.startswith('$game help'):

                help_str = "The $game menu is used to track __ongoing games of EDH__."
                help_str += "\n Begin by adding your name and deck with the following command:"
                help_str += "\n```$game player [your name] [commander name]```"
                help_str += "(note that there can't be any spaces in your commander's name or the bot will just take the first word)"
                help_str += "\n Once all players are added, start the game with this command:"
                help_str += "\n```$game first [name of the player who's going first]```"
                help_str += "Once in game, keep track of eliminations using the ```$game elim [player]``` command.  Posterity will thank you when you can point out that you're much more likely to die first and therefore not a threat!"
                help_str += "\n Declare victory with ```$game winner [player]``` Afterward, you can add commentary to the game record so everyone knows how awesome you are, or alternately how little your opponent deserved the win."
                help_str += "\n Once you're done, type ```$game end``` to store the game in memory. That's it!  You're done!"

                await message.channel.send(help_str)
                return

            elif self.current_game is None:
                # Make a new game
                self.current_game = Game()
                await self.game_channel.send("Started a new game!")

            # There's an active game either way at this point, so we have it handle the message
            response = self.current_game.handle_command(message)

            if response == "end":
                # store game data
                self.current_game.store_data("gamehistory.txt")

                #refresh stats engine
                stats.refresh()
                
                # close out the game
                self.current_game = None

                # confirmation message
                await message.channel.send("Thanks for playing!")

            # this is the "quit without saving" option
            elif response == "cancel":
                self.current_game = None
                await self.game_channel.send("I have cancelled the game for you.")

            elif response == "":
                pass

            else:
                # send the reponse as a message
                await self.game_channel.send(response)

        if message.content.startswith('$data'):
            # global game_channel
            response = dm.handle_command(message)

            if response == "":
                pass
            else:
                await self.game_channel.send(response)


# create instances of stats engine, data manager, and state manager
stats = Statistics()
dm = Data_Manager()
state_manager = State_Manager()

@client.event
async def on_ready():
    print('Bot successfully logged in as: {user}'.format(user=client.user))
    state_manager.set_channel(client.get_channel(config.game_channel_id))

@client.event
async def on_message(message):
    await state_manager.route_message(message, stats, dm)

client.run(config.bot_token)