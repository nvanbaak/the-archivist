import discord
import config

client = discord.Client()
current_game = None

# with open("gamehistory.txt") as games:
#     games.read()

class Game:
    def __init__(self):
        self.players = []
        self.first = []
        self.eliminated = []
        self.winner = []
        self.begin = False
        self.post = False

    def handle_command(message_obj):
        command = message_obj.content[6:]
        args = command.split(" ")

        if args[0] == "player":
            if not begin:
                self.players.append( {args[1], args[2]} )
                return "{player} is playing {deck}".format(player=args[1], deck=args[2])
            else:
                return "Can't add player—game has already started"

        if args[0] == "first":
            if not begin:
                self.first.append( {args[1], args[2]} )
                self.begin = True
                return "{player} goes first!  Good luck!".format(player=args[1])
            else:
                return "{player} can't go first because the game has already started!".format(player=args[1])

        if args[0] == "elim" or args[0] == "eliminated":
            if begin:
                self.eliminated.append(args[1])
                return "Ouch! Better luck next time, {player}!".format(player=args[1])
            else:
                return "{player} could not have been eliminated because the game has not started yet!".format(player=args[1])

        if args[0] == "win" or args[0] = "victory" or args[0] == "winner":
            if begin:
                self.winner.append(args[1])
                if args[1] == "draw":
                    return "Welp, that must have been interesting."
                else:
                    return "Congratulations {player}!".format(player=args[1])
            else:
                return "{player} could not have been won because the game has not started yet!".format(player=args[1])

        if args[0] == "state":

            state_str = "Game state:"

            player_str = "\n\n"

            if self.players:
                separator = ", "
                player_str += "Players: " 
                player_str += separator.join(self.players)
            else:
                player_str += "No players have been added yet."
            
            state_str += player_str

            first_str = "\n"

            if self.first:
                first_str += self.first[0] + " went first."
            else:
                first_str += "The game has not started yet."

            state_str += first_str

            death_str = "\n" + "\n".join(self.eliminated)

            state_str += death_str

            win_str = "\n"

            if self.winner:
                if self.winner == "draw":
                    win_str += "The game was a draw.  Somehow."
                else:
                    win_str += self.winner + " won the game!"
            else:
                win_str += "The game is in progress."

            state_str += win_str

            return state_str




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

    if message.content.startswith('$game'):
        # Check if there is is a game
        global current_game
        if current_game is None:
            # Make a new game
            current_game = Game()

        # have the game handle it
        response = current_game.handle_command(message)

        # send the reponse as a message
        await message.channel.send(response)

client.run(config.bot_token)