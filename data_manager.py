import os
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import config
from game import Game


class Data_Manager:
    def __init__(self):
        self.games = []
        self.output = "gamehistory_test.txt"
        self.current_action = None
        self.confirm_flag = False

    # this is our transit center function
    def handle_command(self, message_obj):
        # First, weed out unauthorized users
        if message_obj.author.id != config.admin_id:
            return "My apologies, sir. You are not authorized to access the data editor."

        # Next, split string into command words
        args = message_obj.content.split(" ")
        
        if len(args) == 1: # that is, if they just typed "$data"
            return ""

        # Then route
        if args[1] == "load" or args[1] == "reload":
            try:
                file_location = args[2]
            except:
                file_location = "gamehistory.txt"

            return self.load_games(file_location)

        # all our actual commands go here
        elif self.games:

            if not self.confirm_flag:

                if args[1] == "fuzz":
                    if args[2] == "player":
                        return self.fuzz_player(args[3])

                    if args[2] == "deck" or args[2] == "cmdr" or args[2] == "commander":
                        cmdr_name = " ".join(args[3:])
                        return self.fuzz_cmdr(cmdr_name)
                    
                    else:
                        return ""

                elif args[1] == "summary":
                    return self.game_summary()

                elif args[1] == "unload" or args[1] == "cancel" or args[1] == "clear":
                    self.games = []
                    return "Cleared the data manager."

                elif args[1] == "save":
                    try:
                        os.remove(args[2])
                    finally:
                        return self.output_history(args[2])

                elif args[1] == "rename":
                    # this puts the data back the way they were entered
                    args = " ".join(args[2:])
                    
                    # determine mode and get it off the arg string
                    mode = None
                    if args.startswith("cmdr") or args.startswith("deck"):
                        mode = 1
                        args = args[5:]
                    elif args.startswith("commander"):
                        mode = 1
                        args = args[10:]
                    elif args.startswith("player"):
                        mode = 0
                        args = args[7:]
                    else:
                        return "No changes made — can only rename players and commanders."

                    # next, split the new name off from the rest
                    args = args.split(" > ")
                    new_name = args[1]

                    # finally, split the targets into an array
                    targets_arr = args[0].split(" | ")

                    return self.rename(mode, targets_arr, new_name)

                else:
                    return ""

            elif args[1] == "confirm":
                self.onfirm_flag = False
                return "confirmed."

            elif args[1] == "cancel":
                self.confirm_flag = False
                return "I have cancelled the request."

            else:
                return "You still have a pending {action} action. Please type ```$data confirm``` or ```$data cancel```".format(action=self.current_action)

        # this triggers if nothing's loaded and they tried to do something other than loading
        else:
            return "The data manager currently has nothing loaded.  To get started, type: `$data load`"

    # uses fuzzy search to find possible variant spellings of players
    def fuzz_player(self, player_name):

        # make empty result array and nonresult array
        match_arr = []
        no_match_arr = []

        # for each game
        for game in self.games:

            # for each player
            for player in game.players:

                # skip if the player name is in the result array or nonresult array
                if player[0] in match_arr:
                    continue

                no_match = False
                for player_result in no_match_arr:
                    if player_result[0] == player[0]:
                        no_match = True
                        break
                if no_match:
                    continue

                # else, get fuzziness score
                else:
                    full_fuzz = fuzz.ratio(player_name, player[0])
                    partial_fuzz = fuzz.partial_ratio(player_name, player[0])

                    # if > 90, add to result array
                    if full_fuzz > 50 or partial_fuzz > 50:
                        match_arr.append(player[0])
                    
                    # else add to nonresult array
                    else:
                        no_match_arr.append([player[0], full_fuzz, partial_fuzz])

        # then output info
        response_str = "Here's a list of possible matches for {player_name}:".format(player_name=player_name)

        for name in match_arr:
            response_str += "\n • {match}".format(match=name)

        response_str += "\nRejected matches:"

        no_match_arr.sort()

        for name in no_match_arr:
            response_str += "\n • {match} (full score: {full}; partial score: {partial})".format(match=name[0],full=name[1],partial=name[2])


        return response_str

    # like fuzz_player but for commanders
    def fuzz_cmdr(self, cmdr_name):

        # make empty result array and nonresult array
        match_arr = []
        no_match_arr = []

        # for each game
        for game in self.games:

            # for each player
            for cmdr in game.players:

                # skip if the commander name is in the result array or nonresult array
                if cmdr[1] in match_arr:
                    continue

                no_match = False
                for cmdr_result in no_match_arr:
                    if cmdr_result[0] == cmdr[1]:
                        no_match = True
                        break
                if no_match:
                    continue

                # else, get fuzziness score
                else:
                    full_fuzz = fuzz.ratio(cmdr_name, cmdr[1])
                    partial_fuzz = fuzz.partial_ratio(cmdr_name, cmdr[1])

                    # if > 90, add to result array
                    if full_fuzz > 60 or partial_fuzz > 60:
                        match_arr.append(cmdr[1])
                    
                    # else add to nonresult array
                    else:
                        no_match_arr.append([cmdr[1], full_fuzz, partial_fuzz])

        # then output info
        response_str = "Here's a list of possible matches for {cmdr_name}:".format(cmdr_name=cmdr_name)

        for name in match_arr:
            response_str += "\n • {match}".format(match=name)

        response_str += "\nRejected matches:"

        no_match_arr.sort(reverse=True, key=lambda s: s[2])

        index = 0
        for name in no_match_arr:
            if index < 10:
                response_str += "\n • {match} (full score: {full}; partial score: {partial})".format(match=name[0],full=name[1],partial=name[2])
                index += 1
            else:
                break
        
        rejected_matches = len(no_match_arr)

        if rejected_matches > 10:
            response_str += "\n...plus {num} lower-scoring matches".format(num=rejected_matches-10)

        return response_str

    def rename(self, mode, targets_arr, new_name):
        overwrites = 0

        index = 0
        log_index = 0
        log_str = ""
        # for each game
        for game in self.games:
            index += 1

            # Check each item against the target list
            for item in game.players:
                for target in targets_arr:

                    # if they match, overwrite with new name
                    if item[mode] == target:
                        if log_index < 10:
                            log_str += "\n • Game #{index}: replaced '{old}' with '{new}'".format(index=index, old=item[mode],new=new_name)
                            log_index += 1
                        item[mode] = new_name
                        overwrites += 1
            
            # If we're checking player names, we also have to hit the first player, winner, and elimination data
            for target in targets_arr:
                if game.first[mode] == target:
                    game.first[mode] = new_name
                    if log_index < 10:
                        log_str += "\n • Game #{index}: replaced first player '{old}' with '{new}'".format(index=index, old=target,new=new_name)
                        log_index += 1
                    overwrites += 1

                if game.winner[mode] == target:
                    game.winner[mode] = new_name
                    if log_index < 10:
                        log_index += 1
                        log_str += "\n • Game #{index}: replaced winner '{old}' with '{new}'".format(index=index, old=target,new=new_name)
                    overwrites += 1

                for item in game.eliminated:
                    if item[mode] == target:
                        item[mode] == new_name
                        if log_index < 10:
                            log_index += 1
                            log_str += "\n • Game #{index}: replaced eliminated player '{old}' with '{new}'".format(index=index, old=target,new=new_name)
                        overwrites += 1

        if overwrites > log_index:
            log_str += "\n...plus {num} additional changes".format(num=overwrites-10)

        response_str = ""

        if overwrites > 0:
            response_str += "Database update complete. Updated {num} entries:".format(num=overwrites)
        else:
            response_str += "No changes made — could not find any targets with that name."

        return response_str + log_str
                    
    # returns a summary of the games in memory
    def game_summary(self):
        return "This function returns a summary of the database contents"

    # loads all games from memory
    def load_games(self, file_location):

        # clear current game history
        self.games = []

        # Read game history from file
        if os.path.exists(file_location):
            with open(file_location, "r") as gamehistory:
                history_arr = gamehistory.read().split("\n")
                # delete the last entry because we know it's a newline
                del history_arr[-1]
                # For each game, create a Game object and append it to the Stats object
                index = 0
                for game_data in history_arr:
                    new_game = Game(index)
                    new_game.parse_data(game_data)
                    self.games.append(new_game)
                    index += 1
        else:
            return "Could not open {file_location} — load failed.".format(file_location=file_location)

        # Now we back up the data

        # if old backup exists, delete it
        if os.path.exists("backup.txt"):
            os.remove("backup.txt")

        # then we back up
        self.output_history("backup.txt")

        return "Data manager loaded {num} games from memory and backed up to backup.txt".format(num=len(self.games))

    # outputs local game history to a text file
    def output_history(self, destination):
        for game in self.games:
            game.store_data(destination)
        
        return "Wrote game history to {dest}".format(dest=destination)
