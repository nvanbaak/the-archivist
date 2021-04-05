import os
import config
import random
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

class Game:
    def __init__(self, index):
        self.players = []
        self.first = []
        self.eliminated = []
        self.winner = []
        self.notes = []
        self.begin = False
        self.game_over = False
        self.index = index
        self.completed_notes = []

    # Given the name of a player, tracks them down in the player list. Returns -1 if not found.  Used to get deck information with spellchecking as a useful consequence.
    def get_player_index(self, player_name):
        
        # search for player in the player list
        index = 0
        for p in self.players:
            # break out of the for loop if we found the name
            if self.players[index][0].casefold() == player_name.casefold():
                return index
            # otherwise increment
            else:
                index += 1
        # We only get here if the name wasn't in the list, so return -1
        return -1

    def get_cmdr_index(self, cmdr_name):
        # search for player in the player list
        index = 0
        for p in self.players:
            # break out of the for loop if we found the name
            if self.players[index][1].casefold() == cmdr_name.casefold():
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
    def handle_command(self, message_obj, alias, stats):
        command = message_obj.content[6:]
        args = command.split(" ")

        if command.startswith("cmdr") or command.startswith("commander") or command.startswith("deck"):
            # check if they have an alias registered:
            if alias:
                # remove command term from message content
                cmdr = ""
                if command.startswith("cmdr ") or command.startswith("deck "):
                    cmdr = command[5:]
                if command.startswith("commander "):
                    cmdr = command[10:]

                # get spelling variants
                fuzz_str = self.fuzz_cmdr(cmdr, stats)

                # if the game hasn't already started...
                if not self.begin: 

                    # add player to game if not already present
                    if self.get_player_index(alias) == -1:
                        self.players.append( [alias, cmdr] )
                        return "{alias} is playing {cmdr} {fuzz}".format(alias=alias, cmdr=cmdr, fuzz=fuzz_str)
                    else:
                        return "Player {alias} is already participating in this game.".format(alias=alias)

                else:
                    return "Can't add a new player -- the game has already started."

            else:
                return "You need to register your name with the Archivist to use this command. To register, type ``$register your name``.  Your name is only stored temporarily for the purposes of making it simpler for you to enter certain types of game data."

        if command.startswith("player"):
            if not self.begin:
                player_name = args[1]
                last_index = len(args)
                cmdr_name = " ".join(args[2:last_index])

                if self.get_player_index(player_name) == -1:
                    fuzz_str = self.fuzz_cmdr(cmdr_name, stats)

                    self.players.append( [player_name, cmdr_name] )
                    return "{player} is playing {deck} {fuzz}".format(player=args[1], deck=cmdr_name, fuzz=fuzz_str)
                else:
                    return "Can't add {player} — they're already participating in the game."
            else:
                return "Can't add player—game has already started"

        if command.startswith("rename"):

            # First remove the rename command
            command = command[8:]

            # return error if no > in command
            if not " > " in command:
                return "The proper syntax for this command is ``$game rename *old name* > *new name*``"

            # get old and new names
            args = command.split(" > ")

            # check if it's a commander name; this is the most likely use case given that aliases are usually handled before we get here
            cmdr_index = self.get_cmdr_index(args[0])

            if cmdr_index > -1:
                self.players[cmdr_index][1] = args[1]
                return "Renamed cmdr {old} to {new}".format(old=args[0], new=args[1])

            # check if it's a player name
            player_index = self.get_player_index(args[0])

            if player_index > -1:
                self.players[player_index][0] = args[1]
                return "Renamed player {player} to {new_player}".format(player=args[0], new_player=args[1])

            else:
                return "'{old}' is not a player or commander in the active game.  Use ``$game status`` to double-check the list of players."

        if args[0] == "first":
            if not self.begin:

                player_index = self.get_player_index(args[1])

                # -1 is our failure mode
                if player_index == -1:
                    return 'I was unable to find "{player}" in the list of players for this game.'.format(player=args[1])

                # If the player was found, add them to self.first and start the game
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

                        win_str += "\n Anyone who wants to comment on the game can now do so by typing:\n```$game note your note here```\n"

                        return win_str
                    else:
                        return 'I was unable to find "{player}" in the list of players for this game.'.format(player=args[1])
            else:
                return "I can't declare {player} the winner until I know who went first!".format(player=args[1])

        if args[0] == "state" or args[0] == "status":
            return self.game_state()
            
        if args[0] == "random":
            args_length = len(args)
            output_str = "Random selection: "

            # check if user supplied additional arguments, else return a random player
            if args_length > 1:
                if args[1] == "player":

                    # We may have to randomly select a player multiple times
                    if args_length > 2:
                        num_selections == int(args[2])
                        # target_list = []
                        index = 0
                        while index < num_selections:

                            target = random.choice(self.players)
                            output_str += target + " "
                            index += 1
                    else:
                        output_str = random.choice(self.players)

            # else return a random player
            else:
                output_str = random.choice(self.players)

            return output_str

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
 
                # Add author to list of people who completed notes
                if author not in self.completed_notes:
                    self.completed_notes.append(author)
                    
                    # automatically end the game if everyone has submitted a note
                    if len(self.completed_notes) == len(self.players):
                        return "end"

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

    # Parses information from stored games; essentially used as a constructor for archived games
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

            with open(destination, "a", -1, "utf8") as gamehist:
                gamehist.write(game_str + "\n")

    def fuzz_cmdr(self, cmdr_name, stats):
        match_arr = []
        no_match_arr = []
        
        # run through the list of games
        for game in stats.games:

            # for each game, run through list of commanders
            for cmdr in game.players:

                # skip if it's the same name or we've already hit this one
                if cmdr[1] in match_arr or cmdr[1] in no_match_arr or cmdr[1] == cmdr_name:
                    continue
                else:
                    # otherwise get fuzziness score
                    full_fuzz = fuzz.ratio(cmdr_name, cmdr[1])
                    partial_fuzz = fuzz.partial_ratio(cmdr_name, cmdr[1])

                    # Discriminate based on fuzzy match
                    if full_fuzz > 70 or partial_fuzz > 70:
                        match_arr.append(cmdr[1])
                    else: 
                        no_match_arr.append(cmdr[1])

        # once we've gotten all the matches, return a list
        if match_arr:
            output_str = "\n\nHere's a list of similar names in the database:"
            
            for cmdr in match_arr:
                output_str += "\n • {cmdr}".format(cmdr=cmdr)

            return output_str
        else:
            return ""

