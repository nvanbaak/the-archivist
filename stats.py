import os
import random

from game import Game

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

        self.refresh(False)

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
                arg = arg.replace("player=","")
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
                # remove the commander term
                arg = arg.replace("cmdr=","")
                arg = arg.replace("commander=","")

                # replace underscores with spaces
                arg = arg.replace("_"," ")

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

        filter_after_refresh = True
        self.refresh(filter_after_refresh)
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

        # we don't need to filter again because there are no filters active now
        filter_after_refresh = False
        self.refresh(filter_after_refresh)

    # Pull a fresh set of data from memory
    def refresh(self, filter_when_done):

        # clear current game history
        self.games = []

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

        if filter_when_done:
            self.filter_games()
        return "Successfully loaded game history! Sample set now {num} games.".format(num=len(self.games))

    # called by the bot to invoke various methods
    def handle_command(self, message_obj):
        args = message_obj.content[7:].split(" ")

        if args[0] == "reset":
            if args[1] == "filter" or args[1] == "filters":
                self.reset_filters()
                return "All filters reset. New sample set is {num} games.".format(num=len(self.games))

        if args[0] == "filter":
            if args[1] == "reset":
                self.reset_filters()
                return "All filters reset. New sample set is {num} games.".format(num=len(self.games))
            elif args[1] == "setting" or args[1] == "settings":
                return self.filter_settings()
            else:
                del args[0]
                return self.set_filters(args)

        if args[0] == "games" or args[0] == "game":
            del args[0]
            return self.game_stats(args)

        if args[0] == "player":
            del args[0]
            return self.player_stats(args)

        if args[0] == "deck" or "commander" or "cmdr":
            
            # get the commander name
            cmdr_name = " ".join(args[1:])

            # declare list for oppoenents
            opponents_arr = []
            total_games = 0
            total_wins = 0

            # Run through games to find games with this commander
            for game in self.games:
                # if the searched commander is present
                cmdr_index = game.get_player_index(cmdr_name)
                if cmdr_index > -1:
                    # increment game total
                    total_games += 1

                    # get the name of the commander that won the game
                    winner = game.winner[1]
                    if winner == cmdr_name:
                        total_wins += 1

                    # iterate through commanders, skipping this one
                    num_players = game.pod_size()
                    index = 0
                    while index < num_players:
                        if index != cmdr_index: # skip everything if this is the searched commander
                            opponent_name = game.players[index][1]
                            impact_quotient = 0
                            if num_players > 2:
                                impact_quotient = round(2 / num_players, 2)

                            # Check the opponents array for this commander
                            op_index = 0
                            op_arr_len = len(opponents_arr)
                            while op_index < op_arr_len:
                                # If the opponent is already in the array:
                                if opponents_arr[op_index][0] == opponent_name:

                                    # increment games played
                                    opponents_arr[op_index][3] += 1

                                    # check who won
                                    if opponent_name == winner:
                                        # increment their wins and impact quotient (explained below)
                                        opponents_arr[op_index][1] += 1
                                        opponents_arr[op_index][4] += 1 - impact_quotient
                                    elif cmdr_name == winner:
                                        # increment losses-to-me and impact quotient
                                        opponents_arr[op_index][2] += 1
                                        opponents_arr[op_index][4] += 1- impact_quotient
                                    else: #otherwise a third party won, so subtract impact
                                        opponents_arr[op_index][4] -= impact_quotient

                                    # we got what we need, so break the loop
                                    break
                                op_index += 1
                            
                            # if we looped through everything and didn't find what we need, add the enemy commander to the array
                            if op_index == op_arr_len:
                                # check if they won
                                if opponent_name == winner:
                                    # append with one victory
                                    opponents_arr.append([opponent_name, 1, 0, 1, 1 - impact_quotient])
                                elif cmdr_name == winner:
                                    # append with one loss
                                    opponents_arr.append([opponent_name, 0, 1, 1, 1 - impact_quotient])
                                else:
                                    # append with one game played
                                    opponents_arr.append([opponent_name, 0, 0, 1, -1 * impact_quotient])
                        
                        index += 1
            
            # We should now have a list of decks we've played against and their relative success against the searched deck

            # Now we filter out the decks with short game histories (currently <5 games)
            result_arr = []
            for op in opponents_arr:
                if op[3] < 5:
                    result_arr.append(op)
                else:
                    break

            win_rate = round(total_wins / total_games, 2) * 100

            response_str = "**Matchup statistics for {cmdr_name}:**".format(cmdr_name=cmdr_name)
            response_str += "\n\n • Overall: {wins} wins and {losses} losses for a win rate of {win_rate}%".format(wins=total_wins,losses=total_games-total_wins,win_rate=win_rate)

            # Get top five matchups (if there are that many)
            result_arr.sort(reverse = True, key=lambda op: op[2] / op[1])
            
            response_str += "\n\n • Best Matchups:"

            result_index = 0
            while result_arr < 5:
                
                op_name = result_arr[result_index][0]
                op_win = result_arr[result_index][1]
                op_lose = result_arr[result_index][2]
                op_games = result_arr[result_index][3]
                impact = result_arr[result_index][4]

                #####################################
                #    SIDEBAR ON IMPACT FACTOR MATH
                if False:
                    #  In a perfectly average world, each deck has an equal chance of
                    #  winning the game.  Impact factor is a way of measuring whether
                    #  the matchup is *more likely than chance* to decide the outcome
                    #  of the game.
                    #  
                    #  For a pod of three, the chance of either deck winning is 2/3.
                    #  The impact quotient for one game is thus R - 2/3, where R is 
                    #  either 1 or 0 based on whether one of the matchup candidates 
                    #  won.  Results involving a matchup deck add 1/3, while non-matchup
                    #  results subtract 2/3rds.  Because matchup results are twice
                    #  as common, this averages out to 0 if the decks are all equal.
                    #
                    #  Impact factors above 0 thus indicate a deck that has an outsized
                    #  effect on match outcomes (not necessarily victory, as this 
                    #  metric also counts wins by the opponent's deck).  Impact factors
                    #  below 0 indicate decks that have unusually little impact on the
                    #  table.
                    pass

                response_str += "\n{index}. {op} — Won against: {op_lose}; Lost to: {op_win}. ({op_games} games total; impact factor: {impact}).".format(index=result_index, op=op_name, op_lose=op_lose, op_win=op_win, op_games=op_games, impact=impact)

                result_index += 1

            # Get bottom five matchups (if there are that many)
            result_arr.sort(key=lambda op: op[2] / op[1])

            response_str += "\n\n • Worst Matchups:"

            result_index = 0
            while result_arr < 5:
                
                op_name = result_arr[result_index][0]
                op_win = result_arr[result_index][1]
                op_lose = result_arr[result_index][2]
                op_games = result_arr[result_index][3]
                impact = result_arr[result_index][4]

                response_str += "\n{index}. {op} — Won against: {op_lose}; Lost to: {op_win}. ({op_games} games total; impact factor: {impact}).".format(index=result_index, op=op_name, op_lose=op_lose, op_win=op_win, op_games=op_games, impact=impact)

                result_index += 1

            return response_str

        if args[0] == "refresh":
            return self.refresh(True)

        else:
            return ""

    ##################################
    #          STATS METHODS         #
    ##################################

    # stats reference function for looking at player performance
    def player_stats(self, args):

        total_games = 0
        total_duels = 0
        total_multis = 0
        games_won = 0
        duel_wins = 0
        multi_wins = 0
        average_duel_wins = 0
        average_multi_wins = 0
        baseline_win_chance = 0

        winning_duels = []
        winning_multis = []

        for game in self.games:
            index = game.get_player_index(args[0])
            if index > -1:
                total_games += 1

                pod_size = game.pod_size()

                average_win = round(1 / pod_size, 2)
                baseline_win_chance += average_win
                
                
                if pod_size > 2:
                    total_multis += 1
                    average_multi_wins += average_win

                    if game.winner[0] == args[0]:
                        games_won += 1
                        multi_wins += 1
                        winning_multis.append(game)
                else:
                    total_duels += 1
                    average_duel_wins += average_win

                    if game.winner[0] == args[0]:
                        games_won += 1
                        duel_wins += 1
                        winning_duels.append(game)
                        
        # Stats for all games
        total_win_rate = round((games_won / total_games) * 100, 2)
        expected_wins_general = baseline_win_chance = round(baseline_win_chance, 2)
        expected_win_rate_general = round((expected_wins_general / total_games) * 100, 2)
        general_efficiency = round((games_won / expected_wins_general) * 100, 0)

        # Stats for duels; if there's no duels in the pool we skip this section
        if total_duels > 0:        
            duel_win_rate = round((duel_wins / total_duels) * 100, 2)
            average_duel_win_rate = round((average_duel_wins / total_duels), 2)
            duel_win_efficiency = round((duel_wins / average_duel_wins)*100, 0)

        # Stats for multis; if there's no multiplayer games in the pool we skip this section
        if total_multis > 0:
            multi_win_rate = round((multi_wins / total_multis) * 100, 2)
            average_multi_win_rate = round((average_multi_wins / total_multis), 2)
            multi_win_efficiency = round((multi_wins / average_multi_wins) * 100, 0)

        # create a string to display the information
        log_str = "Here are the stats on {name}:".format(name=args[0])

        log_str += "\n • **{num} games** played, with {duels} duels and {multi} multiplayer games".format(num=total_games, duels=total_duels, multi=total_multis)

        if total_duels > 0:
            log_str += "\n • {player} won {duel_wins} duels (statistical average: {avg_duel_wins} wins) for a win rate of {duel_win_rate}% (efficiency: {efficiency}%)".format(player=args[0],duel_wins=duel_wins,avg_duel_wins=average_duel_wins,duel_win_rate=duel_win_rate,efficiency=duel_win_efficiency)

        if total_multis > 0:
            log_str += "\n • {player} won {multi_wins} multiplayer games (statistical average: {avg_multi_wins} wins) for a win rate of {multi_win_rate}% (efficiency: {efficiency}%)".format(player=args[0],multi_wins=multi_wins,avg_multi_wins=round(average_multi_wins,2),multi_win_rate=multi_win_rate,efficiency=multi_win_efficiency)

        log_str += "\n • **{actual_wins} wins** out of an expected {projected_wins} ({efficiency}% efficiency)".format(actual_wins=games_won, projected_wins=baseline_win_chance,efficiency=general_efficiency)

        if winning_duels:
            example_win = random.choice(winning_duels)
            example_note = random.choice(example_win.notes)

            log_str += '\n • A sample note from a victorious duel: \n```{note_text}\n — {note_author}```'.format(note_text=example_note[1],note_author=example_note[0])

        if winning_multis:
            example_win = random.choice(winning_multis)
            example_note = random.choice(example_win.notes)

            log_str += '\n • A sample note from a victorious multiplayer game: \n```{note_text}\n — {note_author}```'.format(note_text=example_note[1],note_author=example_note[0])
        
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
                return self.games_by_deck(args[2:])

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

                # we limit display using either the user value or 10 if they didn't give us one
                display_size = 10
                if len(args) > 2:
                    display_size = int(args[2])

                index = 0

                for player in players:
                    if index < display_size:
                        response_str += "\n • {player}: {total} games".format(player=player[0], total=player[1])
                        index += 1
                    else:
                        break

                # then we close up
                if arr_length > display_size:
                    response_str += "\n ...along with {arr_length} more competitors.".format(arr_length=arr_length-display_size)

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

                display_size = 10
                if len(args) > 2:
                    display_size = args[2]

                for player in winners:
                    if index < display_size:
                        response_str += "\n • {player}: {total} victories".format(player=player[0], total=player[1])
                        index += 1
                    else:
                        break

                # then we close up
                if arr_length > display_size:
                    response_str += "\n ...along with {arr_length} more competitors.".format(arr_length=arr_length-display_size)

                return response_str

            else:
                return ""

        else: return ""

    # stats reference function for analyzing games by commander; submethod of game_stats
    def games_by_deck(self, args):
        # Set up the filter arrays
        require_player = []
        require_cmdr = []
        block_player = []
        block_cmdr = []

        # start error log
        error_log = ""

        # sort & process filter terms into their respective arrays
        for arg in args:
            if arg.startswith("+player="):
                arg = arg.replace("+player=","")
                require_player.append(arg)

            elif arg.startswith("+cmdr=") or arg.startswith("+deck=") or arg.startswith("+commander="):
                arg = arg.replace("+cmdr=","")
                arg = arg.replace("+deck=","")
                arg = arg.replace("+commander=","")

                # commanders might have spaces in them, so we have to deal with that too
                arg = arg.replace("_", " ")

                require_cmdr.append(arg)

            elif arg.startswith("-player="):
                arg = arg.replace("-player=","")
                block_player.append(arg)

            elif arg.startswith("-cmdr=") or arg.startswith("-deck=") or arg.startswith("-commander="):
                arg = arg.replace("-cmdr=","")
                arg = arg.replace("-deck=","")
                arg = arg.replace("-commander=","")

                arg = arg.replace("_", " ")
                require_cmdr.append(arg)

                block_cmdr.append(arg)

            # todo: add play_count argument handling

            # todo: add display_count argument handling

            # todo: add hide_player argument handling

            else:
                error_log += "Games by deck: ignored invalid search term '{term}'".format(term=arg)

        # Empty array of commanders to start
        commanders = []
        arr_length = 0

        # Iterate through all games
        for game in self.games:

            # Get player data from games
            for player in game.players:

                # this code determines whether to add the player information
                fits_require = True
                fits_block = True

                # If any positive requirements exist, we assume guilty until proven innocent
                if require_player or require_cmdr:
                    fits_require = False
                    if player[0] in require_player or player[1] in require_cmdr:
                        fits_require = True
                
                # The block requirements
                if player[0] in block_player or player[1] in block_cmdr:
                    fits_block = False
                
                # Finally, add to array if all requirements are met
                if fits_require and fits_block:
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
        
        # then we sort the array
        commanders.sort(reverse=True, key=lambda d: d[1])

        # Now that we have our data, we can present it
        response_str = "Games by commanders played:"
        index = 0

        # we limit display using either the user value or 20 if they didn't give us one
        display_size = 20

        # This code no longer works due to the changes that allow filtering; will refactor later
        # if len(args) > 2:
        #     display_size = int(args[2])
        
        for deck in commanders:
            if index < display_size:
                response_str += "\n • {cmdr}: {total} games".format(cmdr=deck[0], total=deck[1])
                index += 1
            else:
                break

        # then we close up
        if arr_length > display_size:
            response_str += "\n ...along with {arr_length} more entries.".format(arr_length=arr_length-display_size)

        print(error_log)
        return response_str

    # returns a random game from the sample set
    def random_game(self):
        return random.choice(self.games)
