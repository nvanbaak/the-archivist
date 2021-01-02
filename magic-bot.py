import discord
import config
import random

client = discord.Client()
current_game = None

class Game:
    def __init__(self):
        self.players = []
        self.first = []
        self.eliminated = []
        self.winner = []
        self.notes = []
        self.begin = False
        self.game_over = False

    # Given the name of a player, tracks them down in the player list. Returns -1 if not found.  Used to get deck information with spellchecking as a useful consequence.
    def get_player_index(self, player_name):
        
        # search for player in the player list
        index = 0
        for p in self.players:
            # break out of the for loop if we found the name
            if self.players[index][0] == player_name:
                return index
            # otherwise increment
            else:
                index += 1
        # We only get here if the name wasn't in the list, so return -1
        return -1

    # Checks to see if a player has been eliminated
    def get_elim_index(self, player_name):
        # search for player in the elimination list
        index = 0
        for p in self.eliminated:
            # break out of the for loop if we found the name
            if self.eliminated[index][0] == player_name:
                return index
            # otherwise increment
            else:
                index += 1
        # We only get here if the name wasn't in the list, so return -1
        return -1

    def pod_size(self):
        return len(self.players)

    # the main workhorse function of the class; performs a number of basic data commands based on user input
    def handle_command(self, message_obj):
        command = message_obj.content[6:]
        args = command.split(" ")

        if args[0] == "player":
            if not self.begin:
                self.players.append( [args[1], args[2]] )
                return "{player} is playing {deck}".format(player=args[1], deck=args[2])
            else:
                return "Can't add player—game has already started"

        if args[0] == "rename":
            player_index = self.get_player_index(args[1])
            self.players[player_index][0] = args[2]

        if args[0] == "first":
            if not self.begin:

                player_index = self.get_player_index(args[1])

                # -1 is our failure mode
                if player_index == -1:
                    return 'I was unable to find "{player}" in the list of players for this game.'.format(player=args[1])

                # If the player was found, we get their information from the player list and mark them as eliminated
                else:
                    self.first = self.players[player_index]
                    self.begin = True
                    return "{player} goes first!  Good luck!".format(player=args[1])

            else:
                return "{player} can't go first because the game has already started!".format(player=args[1])

        if args[0] == "elim" or args[0] == "eliminated" or args[0] == "defeat":
            if self.begin:

                player_index = self.get_player_index(args[1])

                # -1 is our failure mode
                if player_index == -1:
                    return 'I was unable to find "{player}" in the list of players for this game.'.format(player=args[1])

                # If the player was found, we get their information from the player list and mark them as eliminated
                else:
                    self.eliminated.append(self.players[player_index])
                    return "Ouch! Better luck next time, {player}!".format(player=args[1])
            else:
                return "{player} could not have been eliminated because the game has not started yet!".format(player=args[1])

        if args[0] == "win" or args[0] == "victory" or args[0] == "winner":
            if self.begin:

                if args[1] == "draw":
                    self.winner = "draw"
                    return "Welp, that must have been interesting."

                else:
                    player_index = self.get_player_index(args[1])

                    if player_index > -1:
                        self.winner = self.players[player_index]
                        self.game_over = True

                        win_str = "Congratulations {player}!".format(player=args[1])

                        win_str += "\n Anyone who wants to comment on the game can now do so by typing:\n```$game note [your note here]```\n"

                        return win_str
                    else:
                        return 'I was unable to find "{player}" in the list of players for this game.'.format(player=args[1])
            else:
                return "{player} could not have been won because the game has not started yet!".format(player=args[1])

        if args[0] == "state" or args[0] == "status":
            self.game_state()
            
        if args[0] == "threat":
            target = random.choice(self.players)
            return "Considered analysis of the situation suggests that {target} is the biggest threat".format(target=target)

        if args[0] == "note":
            if self.game_over:
                # Get author of message
                author = message_obj.author.name
                # Delete the first word of the note (which is "note")
                del args[0]
                # Rejoin to store as a single string
                note_str = " ".join(args)

                note_str = note_str.replace(":", " ")
                note_str = note_str.replace("&", " ")
                note_str = note_str.replace("|", " ")

                self.notes.append( (author, note_str) )
                return "Thanks, {player}".format(player=author)
            else:
                return "The game is not over.  History cannot be written until after it happens."

        if args[0] == "end":
            return "end"

        if args[0] == "cancel":
            return "cancel"

        else:
            return ""

    def game_state(self):
        state_str = ""

        player_str = ""

        if self.players:
            
            pl_list = []

            # for each player
            for pl in self.players:
                elim_index = self.get_elim_index(pl[0])

                pl_str = pl[0] + " (" + pl[1] + ")"

                # if they're eliminated, add strikethrough
                if elim_index > -1:
                    pl_list.append("~~" + pl_str + "~~")
                # otherwise just add the name
                else:
                    pl_list.append(pl_str)

            player_str += "Players: "
            player_str += ", ".join(pl_list)

        else:
            player_str += "No players have been added yet."
        
        state_str += player_str

        first_str = "\n"

        if self.first:
            first_str += self.first[0] + " went first."
        else:
            first_str += "The game has not started yet."

        state_str += first_str

        death_str = ""

        if self.eliminated:
            death_str += "\n" + self.eliminated[0][0] + " died first."
        elif len(self.players) < 3:
            pass
        elif self.game_over:
            death_str += "\nNo one died early."
        else:
            death_str += "\nEveryone's still alive... for now."

        state_str += death_str

        win_str = "\n"

        if self.winner:
            if self.winner == "draw":
                win_str += "The game was a draw.  Somehow."
            else:
                win_str += self.winner[0] + " won the game!"
        else:
            win_str += "The game is not finished yet."

        state_str += win_str

        if self.notes:
            notes_str = "\n\n Contemporary witnesses said:"
            for note in self.notes:
                notes_str += '\n"' + note[1] + '"'
                notes_str += '\n — ' + note[0] + '\n'
            
            state_str += notes_str

        return state_str

    # Parses information from stored games
    def parse_data(self, game_data):
        # Break up the string into data chunks
        data_arr = game_data.split("|")

        # Start by separating the players
        player_arr = data_arr[0].split("&")
        # split up players and their decks, then append to player list
        for player in player_arr:
            self.players.append(player.split(":"))

        # We need to split player from deck but otherwise first player can slot right in
        self.first = data_arr[1].split(":")

        # There might not have been eliminations so we check first
        if data_arr[2]:
            elim_arr = data_arr[2].split("&")
            for victim in elim_arr:
                self.eliminated.append(victim.split(":"))
        
        # Winner is simple like first player
        self.winner = data_arr[3].split(":")

        # Finally we get the notes
        if data_arr[4]:
            notes_arr = data_arr[4].split("&")
            for note in notes_arr:
                self.notes.append(note.split(":"))

        # This probably won't come up, but if we're reading data the game is long over
        self.begin = True
        self.game_over = True

    # Writes the game state to a text file
    def store_data(self, destination):
        if not self.players:
            return
        else:
            player_arr = map(lambda p: p[0] + ":" + p[1], self.players)
            player_str = "&".join(player_arr)

            first_str = self.first[0] + ":" + self.first[1]

            elim_arr = map(lambda p: p[0] + ":" + p[1], self.eliminated)
            elim_str = "&".join(elim_arr)

            win_str = ""
            if self.winner == "draw":
                win_str += "draw"
            else:
                win_str = self.winner[0] + ":" + self.winner[1]

            note_arr = map(lambda n: n[0] + ":" + n[1], self.notes)
            note_str = "&".join(note_arr)
            
            game_str = "|".join([player_str, first_str, elim_str, win_str, note_str])

            with open(destination, "a") as gamehist:
                gamehist.write(game_str + "\n")

class Statistics:
    def __init__(self):
        # We start with an empty games array and read all past games from memory
        self.games = []
        self.pods = [True, True, True, True, True, True]
        self.require_players = []
        self.block_players = []
        self.require_cmdrs = []
        self.block_cmdrs = []
        self.require_elim = []
        self.block_elim = []

        self.refresh()

    ##################################
    #         FILTER METHODS         #
    ##################################

    # sets the filters that define the game set
    def set_filters(self, args):

        allow_pod_modifier: True
        log_str = "Filtering game data..."

        for arg in args:

            # determine whether we're requiring or blocking
            permission = True
            if "-" in arg:
                permission = False
                arg = arg.replace("-", "")
            elif "+" in arg:
                arg = arg.replace("+", "")

            # pod size filters
            if "pod" in arg:
                arg = arg.replace("pod", "")

                # do we allow or disallow these pod sizes?
                perm_str = "Disallowed"
                if permission:
                    perm_str = "Allowed"


                # "hard equals" that restricts all results to a specific size; only works on true
                if "==" in arg:
                    arg = arg.replace("==", "")
                    index = 0
                    while index < 6:
                        self.pods[index] = (index == int(arg) - 2)
                        index += 1
                    log_str += "\n • Restricted pod size to {num}".format(num=int(arg))

                # pods with smaller sizes than the given number
                if "<" in arg:
                    arg = arg.replace("<", "")
                    index = int(arg) - 3
                    while index > -1:
                        self.pods[index] = permission
                        index -= 1

                    log_str += "\n • {permission} pod sizes below {index}".format(permission=perm_str, index=index+2)

                # pods larger than the given number
                if ">" in arg:
                    arg = arg.replace(">", "")
                    index = int(arg) - 1
                    while index < 6:
                        self.pods[index] = permission
                        index += 1

                    log_str += "\n • {permission} pod sizes above {index}".format(permission=perm_str, index=int(arg))

                # pods equal to the given number
                if "=" in arg:
                    arg = arg.replace("=", "")
                    self.pods[int(arg) - 2] = permission
                    log_str += "\n • {permission} pod sizes of {index}".format(permission=perm_str, index=int(arg))

            # player filters
            elif "player" in arg:
                arg = arg.replace("player_","")
                # if *requiring*:
                if permission: 
                    # add to require array
                    self.require_players.append(arg)
                    log_str += "\n • Required {player} in all games".format(player=arg)
                    # remove from block array
                    if arg in self.block_players:
                        log_str += " and removed them from blacklist"
                        index = self.block_players.index(arg)
                        del self.block_players[index]
                else:
                    # otherwise, vice versa
                    self.block_players.append(arg)
                    log_str += "\n • Disallowed games where {player} participated".format(player=arg)
                    if arg in self.require_players:
                        log_str += " and removed them from require list"
                        index = self.require_players.index(arg)
                        del self.require_players[index]

            # commander filters
            elif "cmdr" in arg or "commander" in arg:
                arg = arg.replace("cmdr_","")
                arg = arg.replace("commander_","")

                # if requiring:
                if permission:
                    # add to require array
                    self.require_cmdrs.append(arg)
                    log_str += "\n • Required {cmdr} in all games".format(cmdr=arg)
                    # remove from block array
                    if arg in self.block_cmdrs:
                        log_str += " and removed them from blacklist"
                        index = self.block_cmdrs.index(arg)
                        del self.block_cmdrs[index]
                else:
                    self.block_cmdrs.append(arg)
                    log_str += "\n • Disallowed games with {cmdr}".format(cmdr=arg)
                    # remove from block array
                    if arg in self.require_cmdrs:
                        log_str += " and removed them from require list"
                        index = self.require_cmdrs.index(arg)
                        del self.require_cmdrs[index]

        self.filter_games()
        log_str += "\n...Done. New sample set is {num} games.".format(num=len(self.games))
        return log_str

    # returns a breakdown of the filter settings currently in effect
    def filter_settings(self):
        log_str = "These are the current filter settings:"

        # pod filters
        log_str += "\n Allowed pod sizes: "
        index = 0
        pod_arr = []
        # add the pod sizes current set to true
        while index < 6:
            if self.pods[index]:
                pod_arr.append("{num}".format(num=index+2))
            index += 1
        # join into a string and concat
        log_str += ", ".join(pod_arr)

        # player filters
        if self.require_players:
            log_str += "\nThese players are required in all games:"
            for pl in self.require_players:
                log_str += "\n • {player}".format(player=pl)
        
        if self.block_players:
            log_str += "\nExcluding games with these players:"
            for pl in self.block_players:
                log_str += "\n • {player}".format(player=pl)

        # commander filters
        if self.require_cmdrs:
            log_str += "\nThese commanders are required in all games:"
            for cmdr in self.require_cmdrs:
                log_str += "\n • {cmdr}".format(cmdr=cmdr)
        
        if self.block_cmdrs:
            log_str += "\nExcluding games with these commanders:"
            for cmdr in self.block_cmdrs:
                log_str += "\n • {cmdr}".format(cmdr=cmdr)

        return log_str

    # filters the game set based on the established filter rules
    def filter_games(self):
        # set up new array to filter into
        new_game_array = []

        # iterate through games
        for game in self.games:

            # check against pod size constraints
            index = game.pod_size() - 2
            # if it's false, we skip the rest of the loop
            if not self.pods[index]:
                continue

            # Iterate through players to hit player and commander requirements
            
            # These two are true by default but go to false if any requirements exist.
            # We'll toggle them back to true later if we find the required items
            fits_player_require = True
            fits_cmdr_require = True

            if self.require_players:
                fits_player_require = False     
            if self.require_cmdrs:
                fits_cmdr_require = False

            # these two are just true
            fits_player_blacklist = True    # These get turned off if we find them in the game
            fits_cmdr_blacklist = True
            for player in game.players:
                if player[0] in self.require_players:
                    fits_player_require = True
                if player[1] in self.require_cmdrs:
                    fits_cmdr_require = True
                
                # these two break because either condition disqualifies the whole game, so no need to keep evaluating
                if player[0] in self.block_players:
                    fits_player_blacklist = False
                    break
                if player[1] in self.block_cmdrs:
                    fits_cmdr_blacklist = False
                    break
            
            # if we made it here that means we haven't been disqualified, so we can append
            if fits_cmdr_blacklist and fits_cmdr_require and fits_player_blacklist and fits_player_require:
                new_game_array.append(game)


            
        # once we're done, change the games reference to the new array
        self.games = new_game_array

    # set all filters to maximally permissive settings
    def reset_filters(self):
        self.pods = [True, True, True, True, True, True]
        self.require_players = []
        self.block_players = []
        self.require_cmdrs = []
        self.block_cmdrs = []
        self.require_elim = []
        self.block_elim = []

        self.games = []
        self.refresh()

    # Pull a fresh set of data from memory
    def refresh(self):
        # Read game history from file
        with open("gamehistory.txt", "r") as gamehistory:
            history_arr = gamehistory.read().split("\n")
            # delete the last entry because we know it's a newline
            del history_arr[-1]
            # For each game, create a Game object and append it to the Stats object
            for game_data in history_arr:
                new_game = Game()
                new_game.parse_data(game_data)
                self.games.append(new_game)

        self.filter_games()
        return "Successfully loaded game history! Sample set now {num} games.".format(num=len(self.games))

    # called by the bot to invoke various methods
    def handle_command(self, message_obj):
        args = message_obj.content[7:].split(" ")

        if args[0] == "games" or args[0] == "game":
            del args[0]
            return self.game_stats(args)

        if args[0] == "reset":
            if args[1] == "filter" or args[1] == "filters":
                self.reset_filters()
                return "All filters reset."

        if args[0] == "filter":
            if args[1] == "reset":
                self.reset_filters()
                return "All filters reset. New sample set is {num} games.".format(num=len(self.games))
            elif args[1] == "setting" or args[1] == "settings":
                return self.filter_settings()
            else:
                del args[0]
                return self.set_filters(args)

        if args[0] == "player":
            del args[0]
            return self.player_stats(args)

        if args[0] == "refresh":
            return self.refresh()

        else:
            return ""

    ##################################
    #          STATS METHODS         #
    ##################################

    # stats reference function for looking at player performance
    def player_stats(self, args):
        log_str = "Here are the stats on {name}:".format(name=args[0])

        total_games = 0
        games_won = 0
        baseline_win_chance = 0

        winning_games = []

        for game in self.games:
            index = game.get_player_index(args[0])
            if index > -1:
                total_games += 1

                if game.winner[0] == args[0]:
                    games_won += 1
                    winning_games.append(game)
            
                average_win = round(1 / game.pod_size(), 2)
                baseline_win_chance += average_win

        win_rate = round((games_won / total_games) * 100, 2)
        baseline_win_chance = round(baseline_win_chance, 2)
        projected_win_rate = round((baseline_win_chance / total_games) * 100, 2)
        efficiency = round((win_rate / baseline_win_chance) * 100, 2)

        log_str += "\n • **{num} games** played with a win rate of {win_rate}%".format(num=total_games, win_rate=win_rate)
        log_str += "\n • **{actual_wins} wins** out of an expected {projected_wins} ({efficiency}% efficiency)".format(actual_wins=games_won, projected_wins=baseline_win_chance,efficiency=efficiency)

        if winning_games:
            example_win = random.choice(winning_games)
            example_note = random.choice(example_win.notes)

            log_str += '\n • A sample note from a victorious game: \n```{note_text}\n — {note_author}```'.format(note_text=example_note[1],note_author=example_note[0])

        return log_str

    # stats reference function for analyzing game breakdown
    def game_stats(self, args):

        # "$stats game totals"
        if args[0] == "total" or args[0] == "totals":
            return "I have records of {total} games.".format(total=len(self.games))

        # "$stats games by ..."
        if args[0] == "by":

            # "...pod"
            if args[1] == "pod":
                # define an array of possible pod sizes, with the first index representing 1v1
                pod_size = [0, 0, 0, 0, 0]
                # For each game, count the players and increment appropriately
                for game in self.games:
                    pod_size[game.pod_size()-2] += 1
                
                response_str = "Here's a breakdown of my records by pod size:"

                # define an index to iterate with the array
                index = 0
                for tally in pod_size:
                    # if there's no games with that pod size we don't print them
                    if tally > 0:
                        response_str += "\n• [{index_value}]: {tally} games".format(index_value=index+2, tally=tally)
                    # increment the index either way
                    index += 1

                return response_str

            # "...deck"
            if args[1] == "deck" or args[1] == "commander":

                # Empty array of commanders to start
                commanders = []
                arr_length = 0

                # Iterate through all games
                for game in self.games:

                    # Get commander names
                    for player in game.players:
                        deck_str = player[1] + " (" + player[0] + ")"

                        # search for it in the arr
                        index = 0
                        for deck in commanders:
                            # if the name matches, increment the count
                            if deck[0] == deck_str:
                                deck[1] += 1
                                break
                            index += 1

                        # if the index matches the array length, our target wasn't there, so we add it with a count of 1
                        if index == len(commanders):
                            commanders.append([deck_str, 1])
                            arr_length += 1
                
                # then we sort the array; NB sort() modifies the original array
                commanders.sort(reverse=True, key=lambda d: d[1])

                # Now that we have our data, we can present it
                response_str = "Here are the most common commanders in my records:"
                display_size = 20
                index = 0
                # we limit display using the above variable
                for deck in commanders:
                    if index < display_size:
                        response_str += "\n • {cmdr}: {total} games".format(cmdr=deck[0], total=deck[1])
                        index += 1
                    else:
                        break
                # then we close up
                if arr_length > display_size:
                    response_str += "\n ...along with {arr_length} more entries.".format(arr_length=arr_length-display_size)

                return response_str

            # "...player"
            if args[1] == "player" or args[1] == "players":
                # Empty array of players to start
                players = []
                arr_length = 0

                # Iterate through all games
                for game in self.games:

                    # Get player names
                    for player in game.players:
                        name_str = player[0]

                        # search for it in the arr
                        index = 0
                        for player_name in players:
                            # if the name matches, increment the count
                            if player_name[0] == name_str:
                                player_name[1] += 1
                                break
                            index += 1

                        # if the index matches the array length, our target wasn't there, so we add it with a count of 1
                        if index == len(players):
                            players.append([name_str, 1])
                            arr_length += 1
                
                # then we sort the array; NB sort() modifies the original array
                players.sort(reverse=True, key=lambda d: d[1])

                # Now that we have our data, we can present it
                response_str = "These are the players in my records:"
                index = 0
                # we only return the 10 most played
                for player in players:
                    if index < 10:
                        response_str += "\n • {player}: {total} games".format(player=player[0], total=player[1])
                        index += 1
                    else:
                        break
                # then we close up
                if arr_length > 10:
                    response_str += "\n ...along with {arr_length} more competitors.".format(arr_length=arr_length-10)

                return response_str

            # "...winner"
            if args[1] == "winner" or args[1] == "winners" or args[1] == "wins" or args[1] == "win":
                # Empty array of players to start
                winners = []
                arr_length = 0

                # Iterate through all games
                for game in self.games:
                    win_str = game.winner[0] #+ " (" + game.winner[1] + ")"

                    # check against list
                    index = 0
                    for winner in winners:
                        # if the name matches, increment the count
                        if winner[0] == win_str:
                            winner[1] += 1
                            break
                        index += 1

                    # if the index matches the array length, our target wasn't there, so we add it with a count of 1
                    if index == arr_length:
                        winners.append([win_str, 1])
                        arr_length += 1

                # then sort
                winners.sort(reverse=True, key=lambda d: d[1])

                # Now that we have our data, we can present it
                response_str = "My records show the following victories:"
                index = 0
                # we only return the 10 most played
                for player in winners:
                    if index < 10:
                        response_str += "\n • {player}: {total} victories".format(player=player[0], total=player[1])
                        index += 1
                    else:
                        break
                # then we close up
                if arr_length > 10:
                    response_str += "\n ...along with {arr_length} more competitors.".format(arr_length=arr_length-10)

                return response_str



            else:
                return ""


        else: return ""

    # returns a random game from the sample set
    def random_game(self):
        return random.choice(self.games)

stats = Statistics()

@client.event
async def on_ready():
    print('Bot successfully logged in as: {user}'.format(user=client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    print(message)

    if message.content.startswith('$hello'):
        await message.channel.send('Hello {message.author.name}!'.format(message=message))

    if message.content.startswith('$randomEDH'):
        await message.channel.send(stats.random_game().game_state())

    if message.content.startswith('$stats'):
        response = stats.handle_command(message)

        if response == "":
            pass
        else:
            await message.channel.send(response)

    if message.content.startswith('$game'):
        # Check if there is is a game
        global current_game

        # user might just be checking if there's a game; we don't need to start a new one in that case
        status_update = message.content.startswith('$game status') or message.content.startswith('$game state')


        if status_update and current_game is None:
            await message.channel.send("There is currently no active game.")
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

        elif current_game is None:
            # Make a new game
            current_game = Game()
            await message.channel.send("Started a new game!")

        # There's an active game either way at this point, so we have it handle the message
        response = current_game.handle_command(message)

        if response == "end":
            # store game data
            current_game.store_data("gamehistory.txt")

            #refresh stats engine
            stats.refresh()
            
            # close out the game
            current_game = None

            # confirmation message
            await message.channel.send("Thanks for playing!")

        # this is the "quit without saving" option
        if response == "cancel":
            current_game = None
            await message.channel.send("I have cancelled the game for you.")

        elif response == "":
            pass

        else:
            # send the reponse as a message
            await message.channel.send(response)

client.run(config.bot_token)