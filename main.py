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

class Lobby:
    def __init__(self, name):
        self.game = None
        self.name = name
        self.players = []
    
    def add_player(self, player):
        self.players.append(player)
        return "{player} has joined the **{lobby}** lobby.".format(player=player, lobby=self.name)

    def remove_player(self, player):
        try:
            self.players.remove(player)
            return "{player} has left the **{lobby}** lobby.".format(player=player, lobby=self.name)
        except ValueError:
            return "Error — attempted to remove non-existant player {player} from lobby **{lobby}**!".format(player=player, lobby=self.name)

class State_Manager:
    def __init__(self):
        # Channel setup
        self.game_channel = None
        
        # Lobby setup; "open" libraries are potential lobbies with no activity; "active" libraries can be joined and host games; "closed" libraries have active games and are not available for the state machine to start new games
        self.open_lobbies = ["Jace","Chandra","Nissa","Liliana","Gideon","Sorin","Venser","Saheeli","Ajani","Bolas","Ashiok","Tamiyo","Nahiri"]
        random.shuffle(self.open_lobbies)
        self.active_lobbies = {}
        self.closed_lobbies = []
        
        # Player -> Lobby assignment
        self.player_assign = {}

        # alias setup
        self.aliases = {}

        # load any existing aliases
        if os.path.exists("alias.txt"):
            with open("alias.txt", "r", -1, "utf8") as alias_list:
                alias_data = alias_list.read().split("\n")

                # delete the newline at the end
                del alias_data[-1]

                # add each alias to the state machine
                for alias in alias_data:
                    alias = alias.split("&separator;")
                    self.aliases[alias[0]] = alias[1]
                # note that this collapses duplicate entries to whatever the player entered last

                # save dict back to file (which removes duplicate entries)

                # Make a string out of alias dict
                alias_str = ""
                for key in self.aliases:
                    alias_str += "{account}&separator;{alias}\n".format(account=key, alias=self.aliases[key])

                # save to file
                with open("alias.txt","w",-1,"utf8") as alias_list:
                    alias_list.write(alias_str)

        # game count; currently this value is set by counting the number of games set in the stat manager, so we don't set it here
        self.game_count = 0

        # legacy game storage; removing this will break any $game commands that don't use the lobby architecture, which is all of them at this point
        self.current_game = None



    
    def set_channel(self, channel_obj):
        self.game_channel = channel_obj
        print( "Set output channel to {channel}.".format(channel=channel_obj))
        return "Set output channel to {channel}.".format(channel=channel_obj)

    def is_this_the_game_channel(self, message_obj):
        if self.game_channel == message_obj.channel:
            return True
        else:
            return False

    def get_player_alias(self, author_name):
        alias = None
        try:
            alias = self.aliases[author_name]
        except KeyError:
            response = "get_player_alias call failed: '{author}' is not a key".format(author=author_name)
            print(response)
            return response

        return alias

    # Used to create a new lobby
    def activate_lobby(self):

        new_lobby = self.open_lobbies.pop(0)
        self.active_lobbies[new_lobby] = Lobby(new_lobby)
        
        return "Opened **{lobby}** lobby.".format(lobby=new_lobby)

    # command to create new Game object inside an available lobby
    def new_game(self):
        # set up output str and lobby key
        response = ""
        lobby_name = ""

        # check if there's an open lobby
        if len(self.active_lobbies) == len(self.closed_lobbies):

            # if not, make one
            new_lobby = self.open_lobbies.pop(0)
            self.active_lobbies[new_lobby] = Lobby(new_lobby)                

            lobby_name = new_lobby

            response += "Opened **{lobby}** lobby.\n".format(lobby=new_lobby)

        else:
            # if there is, find it
            for lobby in self.active_lobbies:
                if not lobby in self.closed_lobbies:
                    lobby_name = lobby
        
        # make new game in the open lobby
        self.game_count += 1
        self.active_lobbies[lobby_name].game = Game(self.game_count)

        # this lobby is now closed, so add it to the list
        self.closed_lobbies.append(lobby_name)

        response += "Created a new game in **{lobby}**.".format(lobby=lobby_name)
        return response         

    async def route_message(self, message, stats, dm):

        # Nope out if the message is from this bot
        if message.author == client.user:
            return
        
        print(message)

        # set up response string
        response = ""

        # Command to start a new lobby
        if message.content.startswith("$new lobby"):

            # Open a new lobby and store the return string
            response = self.activate_lobby()

        # Command to print active lobbies
        else if message.content.startswith("$lobbies"):

            # start response string
            response = "Open lobbies: \n"

            # iterate through active lobbies and add to string
            lobby_list_str = ""
            for lobby in self.active_lobbies:
                lobby_list_str += ", {lobby}".format(lobby=lobby)
            response += lobby_list_str[2:]

        # Command to start new game
        else if message.content.startswith("$new game"):
            response = self.new_game()
        
        # Command to join a lobby
        else if message.content.startswith("$join"):

            # get player name
            player = message.author

            # get lobby name
            join_target = message.content[6:]
            print(join_target)

            # if lobby is not active, pull it off the open_lobbies list and make it active
            if not join_target in self.active_lobbies:
                try:
                    self.open_lobbies.remove(join_target)
                    self.active_lobbies[join_target] = Lobby(join_target)

                except ValueError:
                    return "Couldn't find lobby {lobby}".format(lobby=join_target)

            # Add player to lobby and update player_assign
            self.active_lobbies[join_target].add_player(player)
            self.player_assign[player] = join_target

            response = "{player} has joined **{lobby}**.".format(player=player, lobby=join_target)

        # Send confirmation message to Discord
        await self.game_channel.send(response)

        ######
        # These functions use the pre-lobby architecture
        ######

        if message.content.startswith('$hello'):

            alias = self.get_player_alias(message.author.name)

            if alias:
                await message.channel.send('Hello {alias}!'.format(alias=alias))

            else:
                await message.channel.send('Hello {message.author.name}!'.format(message=message))

        if message.content.startswith("$set output"):
            return self.set_channel(message.channel)

        if message.content.startswith("$lorem"):
            lorem = "Token engine firebreathing blinking mono blue Rakdos Steve stabilize Grixis interrupt restricted mono white Rakdos 4 turn clock decking fixing sideboard Selesnya dome Chimney Pimp big butt decking gas bolt 3 drop chump tank token enchantment topdeck mana pool tank dork utility land standard race card swing race nut draw artifact Golgari dig beatstick race hate mono green Sultai pro mana rock Naya pro-blue Vorthos pop off dig for an answer Orzhov CMC wheel Canadian Threshold land for turn Abzan tank maindeck grindy trade blow up Temur nut draw Sultai chump meta top 8 meta combat trick fatty sorcery Blinky power 9 hate mono black pro-black 2 drop drain fixing in the air modern beatstick prison Vorthos stabilize artifact mirror match Chimney Pimp moxen hard cast hydra land drop grinder aggro aggro Simic Esper weenie 4 turn clock 4 turn clock hate exile enchantment Naya Naya big butt cantrip fetch dig reanimate restricted proxy go off legacy grinder protection interrupt maindeck decking Naya Grixis prison creatureball 2 drop hate bear beats wedge 2 drop wheel enchantment vintage playset Temur 4 turn clock mana birds decking vanilla pro-blue EDH shock land wedge crack fetch wheel durdler mill Blinky chump block mana pool curve card pool mana hose dragon reanimate moxes glass cannon Gruul mana dork sorcery clock hate bear fetch token engine mana hose tempo pro-black card Timmy Grixis\n\nCheck land playset threat Izzet shock on a stick allied colors blow up bomb grind in response Grixis value legacy fixing race legacy glass cannon land for turn combo shock land durdler Grixis mulligan reanimate deck hoser Steve proxy wedge Gruul reanimate jankey mana hose aggro response pro-white pro-red combat trick CMC board state token ping Academy bolt mill he's got a bit of an ass on him hate mana pool Jund board presence blow up Canadian Threshold dig color Timmy pro-red prime time mana pool ping reanimator bomb reanimator mulligan dragon gas dork shock keeper man land wheel shock on a stick aggro big butt playset on a stick beefcake synergy reanimate allied colors control Jeskai fixing jankey 1 drop bear Esper 1 drop board presence bomb shell mana birds go wide Boros grindy hard cast pain land vintage cut interrupt sorcery blink Selesnya finisher metagame control reanimate mana screwed beatstick blow up ping board presence Mardu ritual out of gas Gruul card pool bolt archetype stabilize mono black beefcake pro-white chump block dead card bomb pain land blow up pump jankey combo pain land tutor 2 drop beatdown Mardu planeswalker dragon swing hydra fixing Izzet allied colors mana pool nut draw prison control hate bear modern run Jund land for turn legendary cut fixing ETB lethal shock chump voltron Gruul mana dork chump block pro-black moxen restricted playset Bob card pool"
            await self.send_multiple_responses(lorem)

        if message.content.startswith('$randomEDH'):
            await message.channel.send(stats.random_game().game_state())

        if message.content.startswith('$register'):
            # retrieve Discord name and given name from message
            author_name = message.author.name
            alias = message.content
            alias = alias.replace("$register ","")
            alias = alias.replace("$register","")

            if alias:
                # set that value in the alias list
                self.aliases[author_name] = alias
                
                alias_str = "{author_name}&separator;{alias}\n".format(author_name=author_name, alias=alias)

                # save alias to alias list
                with open("alias.txt", "a", -1, "utf8") as alias_list:
                    alias_list.write(alias_str)

                # confirmation message
                await self.game_channel.send("Registered {author} as {alias}!".format(author=author_name, alias=alias))

            else:
                await self.game_channel.send("You need to provide a name to use that command.")

        if message.content.startswith('$notif') or message.content.startswith('$remind'):
            remind = Reminder(message)
            remind.remind()

        if message.content.startswith('$stats'):
            response = await stats.handle_command(message)

            if response == "":
                pass
            else:
                await self.send_multiple_responses(response)

        if message.content.startswith('$game '):
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
                help_str += "\n``$game player [your name] [commander name]``"
                help_str += "(note that there can't be any spaces in your commander's name or the bot will just take the first word)"
                help_str += "\n Once all players are added, start the game with this command:"
                help_str += "\n``$game first [name of the player who's going first]``"
                help_str += "Once in game, keep track of eliminations using the ``$game elim [player]`` command.  Posterity will thank you when you can point out that you're much more likely to die first and therefore not a threat!"
                help_str += "\n Declare victory with ``$game winner [player]`` Afterward, you can add commentary to the game record so everyone knows how awesome you are, or alternately how little your opponent deserved the win."
                help_str += "\n Once you're done, type ``$game end`` to store the game in memory. That's it!  You're done!"

                await message.channel.send(help_str)
                return

            elif self.current_game is None:

                # get the current number of games
                index = len(stats.games)

                # Make a new game
                self.current_game = Game(index)
                await self.game_channel.send("Created a new game!")

            # There's an active game either way at this point, so we have it handle the message
            alias = self.get_player_alias(message.author.name)
            response = ""

            response = self.current_game.handle_command(message, alias, stats)

            if response == "end":
                # store game data
                self.current_game.store_data("gamehistory.txt")

                #refresh stats engine
                filter_when_done = True
                stats.refresh(filter_when_done)
                
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
                if len(response) > 1900:
                    self.send_multiple_responses(response)

                await self.game_channel.send(response)

        if message.content.startswith('$data'):
            # global game_channel
            response = dm.handle_command(message)

            if response == "":
                pass
            else:
                await self.game_channel.send(response)

    async def send_multiple_responses(self, response):
        while len(response) > 1949:
            await self.game_channel.send(response[:1950])
            response = response[1950:]
        await self.game_channel.send(response)



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

@client.event
async def on_message(message):
    await state_manager.route_message(message, stats, dm)

client.run(config.bot_token)