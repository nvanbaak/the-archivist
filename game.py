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

    def rename_cmdr(self, old_name, new_name):
        # check if the commander is in there
        for player in self.players:
            if player[1] == old_name:
                player[1] = new_name
                return "Renamed {player}'s commander to {new_name}!".format(player=player[0], new_name=new_name)
 
        # if we made it through the loop without hitting anything, send a failure message
        return "Could not find any commanders named {old_name}.".format(old_name=old_name)

    def add_player(self, player, cmdr):
        self.players.append([player, cmdr])
        return "{player} is playing {cmdr}.".format(player=player, cmdr=cmdr)

    # the main workhorse function of the class; performs a number of basic data commands based on user input
    def handle_command(self, alias, command, content, stats):

        # sets cmdr name using alias
        if command == "cmdr":
            # check if they have an alias registered:
            if alias:

                # get spelling variants
                fuzz_str = self.fuzz_cmdr(content, stats)

                # if the game hasn't already started...
                if not self.begin: 

                    # add player to game if not already present
                    if self.get_player_index(alias) == -1:
                        self.players.append( [alias, content] ) 
                        
                        return "{alias} is playing {cmdr} {fuzz}".format(alias=alias, cmdr=content, fuzz=fuzz_str)
                    else:
                        p_index = self.get_player_index(alias)
                        self.players[p_index][1] = content

                        return "Player {alias} has changed commanders to {cmdr}.{fuzz}".format(alias=alias, cmdr=content, fuzz=fuzz_str)

                else:
                    return "Can't add a new player -- the game has already started. If you forgot to add them before starting the game, you can use `$restart` to create a new game with the same commanders."

            else:
                return "You need to register your name with the Archivist to use this command. To register, type ``$register your name``.  The Archivist will remember you by this name."

        # sets player and cmdr name using provided arguments
        elif command == "player":
            if not self.begin:
                
                # split string into player (index 0) & cmdr (index 1) names
                names = content.split(" ", 1)

                if self.get_player_index(names[0]) == -1:
                    fuzz_str = self.fuzz_cmdr(names[1], stats)

                    self.players.append( [names[0], names[1]] )
                    return "{player} is playing {cmdr} {fuzz}".format(player=names[0], cmdr=names[1], fuzz=fuzz_str)
                else:
                    return "Can't add {player} — they're already participating in the game."
            else:
                return "Can't add player—game has already started"

        # renames a commander
        elif command == "rename":

            # return error if no > in content
            if not " > " in content:
                return "The proper syntax for this command is ``$game rename *old name* > *new name*``"

            # get old and new names
            args = content.split(" > ")

            # rename
            return self.rename_cmdr(args[0],content)

        # sets the first player
        elif command == "first":
            player_index = self.get_player_index(content)

            # -1 is our failure mode
            if player_index == -1:
                return 'I was unable to find "{player}" in the list of players for this game.'.format(player=content)

            # If the player was found, add them to self.first and start the game
            else:
                self.first = self.players[player_index]
                
                if not self.begin:
                    self.begin = True
                    return "{player} goes first!  Good luck!".format(player=content)
                else:
                    return "Changed first player to {player}. If this is a mistake, you may have forgotten to end the previous game.".format(player=content)

        # sets a player as eliminated
        elif command == "elim":
            if self.begin:

                player_index = self.get_player_index(content)

                # -1 is our failure mode
                if player_index == -1:
                    return 'I was unable to find "{player}" in the list of players for this game.'.format(player=content)

                # If the player was found, we get their information from the player list and mark them as eliminated
                else:
                    self.eliminated.append(self.players[player_index])
                    return "Ouch! Better luck next time, {player}!".format(player=content)
            else:
                return "{player} could not have been eliminated because the game has not started yet!".format(player=content)

        # declares a player as the winner
        elif command == "win":
            if self.begin:

                if content == "draw":
                    self.winner = "draw"
                    return "Welp, that must have been interesting."

                else:
                    player_index = self.get_player_index(content)

                    if player_index > -1:
                        if self.winner:
                            win_str = "Changed winner {old_winner} to {new_winner}.  If you didn't mean to do that, `$win {old_winner}` will change it back.".format(old_winner=self.winner[0], new_winner=content)
                        
                        else:
                            win_str = "Congratulations {player}!".format(player=content)

                            win_str += "\n Anyone who wants to comment on the game can now do so by typing:\n```$note your note here```\n"
                        
                        self.winner = self.players[player_index]
                        self.game_over = True

                        return win_str
                    else:
                        return 'I was unable to find "{player}" in the list of players for this game.'.format(player=content)
            else:
                return "I can't declare {player} the winner until I know who went first!".format(player=content)

        # returns a string summarizing the status of the game
        elif command == "status":
            return self.game_state()
        
        # returns a random player
        elif command == "random":
            
            # args_length = len(args)
            # output_str = "Random selection: "

            # # check if user supplied additional arguments, else return a random player
            # if args_length > 1:
            #     if content == "player":

            #         # We may have to randomly select a player multiple times
            #         if args_length > 2:
            #             num_selections == int(args[2])
            #             # target_list = []
            #             index = 0
            #             while index < num_selections:

            #                 target = random.choice(self.players)
            #                 output_str += target + " "
            #                 index += 1
            #         else:
            #             output_str = random.choice(self.players)

            # # else return a random player
            # else:
            output_str = random.choice(self.players)

            return output_str

        # deletes all information except the participating players and commanders.
        elif command == "restart":
            self.first = []
            self.eliminated = []
            self.winner = []
            self.notes = []
            self.begin = False
            self.game_over = False
            self.completed_notes = []

            response = "Started a new game with these people:\n" 
            
            for player in self.players:
                response += " • {player} ({cmdr})\n".format(player=player[0], cmdr=player[1])

            response += "\nYou can change your commander with the `$cmdr` command."

            return response


        # returns a "threat analysis" string.  While the plan is eventually to have a statistically-powered bayesian calculation, the current "analysis" is a random number generator.
        if command == "threat":    
            target = random.choice(self.players)
            return "Considered analysis of the situation suggests that {target} is the biggest threat".format(target=target)

        # appends commentary to the game object before storage.
        if command == "note":
            if self.game_over:
                # Get author of message
                author = alias

                content = content.replace(":", "*colon;")
                content = content.replace("&", "*ampersand;")
                content = content.replace("|", "*pipe;")

                self.notes.append( (author, content) )
 
                # Add author to list of people who completed notes
                if author not in self.completed_notes:
                    self.completed_notes.append(author)
                    
                    # automatically end the game if everyone has submitted a note
                    if len(self.completed_notes) == len(self.players):
                        return "end"

                return "Thanks, {player}.".format(player=author)
            else:
                return "The game is not over.  History cannot be written until after it happens."

        if command == "end":
            return "end"

        if command == "cancel":
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

    # Summarized version of game summary, intended for use after the game is over
    def game_summary(self):

        output_str = "**GAME #{}**\n\nPlayers:".format(self.index)

        for player in self.players:
            elim_index = self.get_elim_index(player[0])

            player_str = player[0] + " (" + player[1] + ")"

            # if they're eliminated, add strikethrough
            if elim_index > -1:
                output_str += "\n • ~~" + player_str + "~~"
            # otherwise just add the name
            else:
                output_str += "\n • " + player_str

            output_str += "\n\n**{}** won the game.  Here's what players said:".format(self.winner[0])

            for note in self.notes:

                output_str += '\n"{content}"\n—{author}\n~'.format(content=note[1], author=note[0])

            return output_str

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
                split_notes = note.split(":")
                
                # replace character placeholders with actual characters
                split_notes[1] = split_notes[1].replace("*colon;",":")
                split_notes[1] = split_notes[1].replace("ampersand;","&")
                split_notes[1] = split_notes[1].replace("*pipe;","|")

                # append
                self.notes.append(split_notes)

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

