import discord
import config

client = discord.Client()

current_game = None

class Game:
    __init__(self):
        self.players = []
        self.first = []
        self.eliminated = []
        self.winner = []
        self.begin = false

    def add_player(player_str):
        if not begin:
            self.players.append(player_str)

    def add_first(player_str):
        if not begin:
            self.first.append(player_str)
            self.begin = true

    def add_elim(player_str, cause):
        if begin:
            self.eliminated.append( {player_str, cause} )

    def add_winner(player_str):
        if begin:
            self.winner.append(player_str)



@client.event
async def on_ready():
    print('Bot successfully logged in as: {0.user}'.format(client))

@client.event
async def on_message(message):
    print(message)
    if message.author == client.user:
        return
    
    if message.content.startswith('$hello'):
        await message.channel.send('Hello {message.author.name}!'.format(message=message))

    # $newgame opens a new Game class or sends back an exception error if one already exists
    if message.content.startswith('$newgame'):
        if current_game is None:
            current_game = Game()
            await message.channel.send("Started a new game!")
        else:
            await message.channel.send("There is already a game in progress!")

    # if there is a Game open, $player adds a player to the game

    # if there is a Game open, $first adds a first player

    # if there is a Game open, $winner defines a winner

    # $elim adds a player death and cause of death


client.run(config.bot_token)