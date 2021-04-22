import os
import random

from game import Game

class Statistics:
    def __init__(self):
        # We start with an empty games array and read all past games from memory
        self.games = []

        self.import_games("gamehistory.txt")

        # master list of filter options to make the Command Parsing section easier to type out
        self.master_filter_dict = {
            "!player" : self.games_with_exactly_these_players,
            "-player" : self.games_without_players,
            "+player" : self.games_with_players,
            "player" : self.games_with_players,
            "!cmdr" : self.games_with_exactly_these_players,
            "-cmdr" : self.games_without_players,
            "+cmdr" : self.games_with_players,
            "cmdr" : self.games_with_players,
            "-win" : self.games_these_guys_did_not_win,
            "+win" : self.games_these_guys_won,
            "win" : self.games_these_guys_won,
            "-pod" : self.pods_not_this_size,
            "+pod" : self.pods_this_size,
            "pod" : self.pods_this_size
        }


    ##################################
    #         GAME RETRIEVAL         #
    ##################################

    # Reads game data from a .txt document into an array of Game objects
    def import_games(self, file_location):
        # clear current game history
        self.games = []

        # Read game history from file, splitting at newlines
        if os.path.exists(file_location):
            with open(file_location, "r", -1, "utf8") as gamehistory:
                history_arr = gamehistory.read().split("\n")
                
                # last list entry is empty because of the newline at the end of the file, so we delete it here
                del history_arr[-1]

                # for each entry, make a Game object and put it in the stats bin
                index = 0 # some user-facing methods care about database index
                for game_data in history_arr:
                    new_game = Game(index)
                    new_game.parse_data(game_data)
                    self.games.append(new_game)
                    index +=1
            
            print("Loaded {num} games from {location}.".format(num=len(self.games), location=file_location))

            return "Successfully loaded game history! Sample set now {num} games.".format(num=len(self.games))

    ##################################
    #     PLAYER / CMDR FILTERING    #
    ##################################

    # mode can be 0 for player names or 1 for cmdr names.

    # Given a list of Game objects, returns the subset of Games in which all of the specified players participated
    def games_with_players(self, mode, game_list, player_names):

        result_list = []

        # check all games in the database
        for game in game_list:
            
            # Assume the game is valid until we prove a required player is not present
            everyone_here = True

            # now check that each player in the parameters is present
            for player_name in player_names:
                # to begin, we haven't found them yet
                are_they_here = False
                
                for player in game.players:
                    # did we find them?
                    if player[mode] == player_name:    
                        are_they_here = True
                        break

                # didn't find them?  This game's a bust, then
                if not are_they_here:
                    everyone_here = False
                    break
            
            # if everyone's here, add the game to the result list
            if everyone_here:
                result_list.append(game)

        # once we've gone through all the games, return the list
        return result_list

    # Given a list of Game objects, returns the subset of Games in which none of the specified players participated        
    def games_without_players(self, mode, game_list, player_names):
        result_list = []

        # run through all the games
        for game in game_list:

            # Initially we assume we're good to go
            undesirables_present = False

            for player_name in player_names:
                for player in game.players:
                    # check the lists against each other; one match and we break
                    if player[mode] == player_name:
                        undesirables_present = True
                        break
                
                # we don't need to keep looping if we found a blacklist target
                if undesirables_present:
                    break

            # if we got through everything without hitting a blacklisted name, append to results
            if not undesirables_present:
                result_list.append(game)

        return result_list

    # Given a list of games and a list of players, returns only games where that exact set of players participated. More computationally efficient than running the two previous methods sequentially.
    def games_with_exactly_these_players(self, mode, game_list, player_list):

        result_list = []

        # loop through candidate games
        for game in game_list:

            # start with a checksum for easy disqualification
            if len(game.players) == len(player_list):

                # assume we're good to go
                rosters_match = True

                # get the player names out of the game object
                for player in game.players:
                    
                    # If that name is not in the desired roster, throw out the game
                    if not player[mode] in player_list:
                        rosters_match = False
                        break
                
                # If the rosters are the same size, and all of the game's players are in the desired roster, then they match. Therefore we add it to the result list
                if rosters_match:
                    result_list.append(game)
        
        # return the results once we're done looping
        return result_list

    ##################################
    #     GAME DETAIL FILTERING      #
    ##################################

    # Only returns games where one of the named players/commanders won
    def games_these_guys_won(self, game_list, player_list):
        
        result_list = []

        # check all the games
        for game in game_list:

            our_buddies_won = False

            # Look up the winning player / commander
            if game.winner[0] in player_list or game.winner[1] in player_list:
                our_buddies_won = True
            
            if our_buddies_won:
                result_list.append(game)
        
        return result_list

    # only returns games where none of the named players/commanders won
    def games_these_guys_did_not_win(self, game_list, player_list):
        result_list = []

        # check all the games
        for game in game_list:

            our_buddies_won = False

            # Look up the winning player / commander
            if game.winner[0] in player_list or game.winner[1] in player_list:
                our_buddies_won = True
            
            if not our_buddies_won:
                result_list.append(game)
        
        return result_list

    # returns games based on the given operation and pod size
    def pods_this_size(self, mode, game_list, pod_size):

        result_list = []

        for game in game_list:

            if mode == "=":
                if len(game.players) == pod_size:
                    result_list.append(game)
            elif mode == ">":
                if len(game.players) > pod_size:
                    result_list.append(game)
            elif mode == "<":
                if len(game.players) < pod_size:
                    result_list.append(game)
        
        return result_list
    
    # returns games based on not meeting the given operation and pod size
    def pods_not_this_size(self, mode, game_list, pod_size):
        result_list = []

        for game in game_list:

            if mode == "=":
                if len(game.players) != pod_size:
                    result_list.append(game)
            elif mode == ">":
                if len(game.players) <= pod_size:
                    result_list.append(game)
            elif mode == "<":
                if len(game.players) >= pod_size:
                    result_list.append(game)
        
        return result_list


    ##################################
    #       STATISTICS METHODS       #
    ##################################

    # Returns the total number of games
    def tally_games(self, game_list):
        
        response = "There are {num} games matching those filters.".format(num=len(game_list))
        
        return response

    # Counts wins for all players in the given list of games
    def tally_player_wins(self, game_list, filter_dict):

        # counting these guys is easier with a dictionary
        win_totals = {}
        
        # for each game:
        for game in game_list:

            # grab the winner's name
            winner = game.winner[0]

            # if they're already in the total count, plus one win. Otherwise, start them at 1 win.
            try:
                win_totals[winner] += 1
            except KeyError:
                win_totals[winner] = 1

        # Now we transfer the dict to a list to sort
        sorted_winners = []

        for winner in win_totals:
            sorted_winners.append([winner, win_totals[winner]])

        # if there's a filter setting, use it to sort the list
        try:
            sort_type = filter_dict["sort"]
            
            if sort_type == "rand" or sort_type == "random":
                random.shuffle(sorted_winners)
            elif sort_type == "desc":
                sorted_winners.sort(reverse=False, key=lambda p: p[1])
            else:
                sorted_winners.sort(reverse=True, key=lambda p: p[1])
        # if not sort term was given, we sort most to least
        except KeyError:
            sorted_winners.sort(reverse=True, key=lambda p: p[1])

        # finally, turn the results into a string
        response = "Win totals:\n"

        # set return limit to user-entered limit or 10 if no limit given
        try:
            result_limit = int(filter_dict["limit"])
        except KeyError:
            result_limit = 10

        # iterate through winners while there's room
        result_index = 0
        for winner in sorted_winners:
            if result_index < result_limit:
                response += " • {player}: {total}\n".format(player=winner[0], total=winner[1])
                result_index += 1
            else:
                break

        return response

    # Returns elimination stats
    def get_eliminations(self, game_list):

        # build dictionary of eliminated players

        result_list = {}

        for game in game_list:

            elim_index = 1
            for player in game.eliminated:

                try:
                    result_list[player[0]] += 1
                except KeyError:
                    result_list[player[0]] = 1

                elim_index += 1
    
        # transfer dict to list for sorting
        sorted_elims = []

        for elim in result_list:
            sorted_elims.append([elim, result_list[elim]])

        # if there's a filter setting, use it to sort the list
        try:
            sort_type = filter_dict["sort"]
            
            if sort_type == "rand" or sort_type == "random":
                random.shuffle(sorted_elims)
            elif sort_type == "desc":
                sorted_elims.sort(reverse=False, key=lambda p: p[1])
            else:
                sorted_elims.sort(reverse=True, key=lambda p: p[1])
        # if not sort term was given, we sort most to least
        except KeyError:
            sorted_elims.sort(reverse=True, key=lambda p: p[1])

        # set return limit to user-entered limit or 10 if no limit given
        try:
            result_limit = int(filter_dict["limit"])
        except KeyError:
            result_limit = 10

        # build response string

        response = "Eliminations:\n"

        result_index = 0
        for winner in sorted_elims:
            if result_index < result_limit:
                response += " • {player}: eliminated {total} times\n".format(player=winner[0], total=winner[1])
                result_index += 1
            else:
                break
            
        return response


    ##################################
    #         COMMAND PARSING        #
    ##################################


    # Given a list of filter arguments, returns a dict with filter options
    def parse_filters(self, terms):
        # set up dict to be returned when we're done
        filter_args = {}

        error_log = ""

        # for each term:
        for term in terms:

            # Check filter words
            if "player=" in term or "cmdr=" in term or "win=" in term:
                term = term.split("=")

                # This is counter-intuitive; basically the code in the try block should only work if a previous filter has already added that setting to the dictionary.  That shouldn't happen, so we give them an error message.  If the setting does not exist, it throws a KeyError, which tells us it's safe to add the filter setting.
                try:
                    error_log += " • **Filter conflict:** {filter}={value} requirement conflicts with existing {existing} requirement and was ignored. To require multiple terms, join the terms with semicolons (without spaces), e.g. ``!cmdr=\"The Gitrog Monster\";Chandra;Atraxa``\n".format(filter=term[0], value=term[1], existing=filter_args[term[0]])
                except KeyError:
                    filter_args[term[0]] = term[1].split(";")

            elif "pod=" in term or "pod>" in term or "pod<" in term:
                # This one's handled a bit differently because we want to preserve the =/>/<, which means we can't use the split method above

                # Get the endpoint of the inequality statement
                index = 4

                filter_term = term[:index]
                filter_value = term[index:]
                            
                try:
                    error_log += " • **Filter conflict:** {term} requirement conflicts with existing {existing} requirement and was ignored. To require multiple terms, join the terms with semicolons (without spaces), e.g. ``!cmdr=\"The Gitrog Monster\";Chandra;Atraxa``\n".format(term=term, existing=filter_args[term[:index]])
                except KeyError:
                    filter_args[filter_term] = int(filter_value)

            elif "sort=" in term or "limit=" in term:
                term = term.split("=")
                try:
                    error_log += " • **Filter conflict:** {filter}={value} requirement conflicts with existing {existing} requirement and was ignored. You may only sort one way at a time.".format(filter=term[0], value=term[1], existing=filter_args[term[0]])
                except KeyError:
                    filter_args[term[0]] = term[1]


        # after checking all the filters, save the error log to the dict
        filter_args["error_log"] = error_log
            
        # return the dict
        return filter_args

    # returns a list of games from the stats engine master databse, reduced using the filters in the provided dict
    def filter_games(self, filter_dict):
        
        games_list = self.games

        # retrieve the error log so we can keep adding to it
        error_log = filter_dict["error_log"]

        # run through each option, filtering the games list as we go
        for option in filter_dict:
            try:
                if "player" in option:
                    games_list = self.master_filter_dict[option](0, games_list, filter_dict[option])
                elif "cmdr" in option:
                    games_list = self.master_filter_dict[option](1, games_list, filter_dict[option])
                elif "win" in option:
                    games_list = self.master_filter_dict[option](games_list, filter_dict[option])
                elif "pod" in option:
                    print(self.master_filter_dict[option[:4]])
                    games_list = self.master_filter_dict[option[:4]](option[4], games_list, filter_dict[option])
            except KeyError:
                pass

        # drop the error log in console, then return the games
        print(error_log)

        return games_list
        


    # called by the bot to invoke various methods
    async def handle_command(self, command, terms, channel):

        # parse filter terms
        filter_dict = self.parse_filters(terms)        

        # filter games
        games_list = self.filter_games(filter_dict)

        # perform requested analytics

        # refresh stats manager game set
        if command == "reset" or command == "refresh":
            return self.import_games("gamehistory.txt")

        # Tally wins
        elif command == "wins":
            return self.tally_player_wins(games_list, filter_dict)

        # Tally total games
        elif command == "games":
            return self.tally_games(games_list)

        elif command == "elims" or command == "eliminations":
            return self.get_eliminations(games_list)


        else:
            return ""

        



        # All of these commands will be refactored, so there's currently no way to reach them in the progam logic


        if args[0] == "games" or args[0] == "game":
            del args[0]
            return self.game_stats(args)

        elif args[0] == "player":
            del args[0]
            return self.player_stats(args)

        elif args[0] == "deck" or args[0] == "commander" or args[0] == "cmdr":
            
            # get the commander name
            cmdr_name = " ".join(args[1:])

            # declare list for oppoenents
            opponents_arr = []
            total_games = 0
            total_wins = 0

            # Run through games to find games with this commander
            for game in self.games:
                # if the searched commander is present
                cmdr_index = game.get_cmdr_index(cmdr_name)
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
                                        # calculate impact quotient
                                        impact_quotient = 0
                                        if num_players > 2:
                                            impact_quotient = 1 - round(2 / num_players, 2)

                                        # update their wins and impact quotient (explained below)
                                        opponents_arr[op_index][1] += 1
                                        opponents_arr[op_index][4] += impact_quotient

                                    elif cmdr_name == winner:
                                        # calculate impact quotient
                                        impact_quotient = 0
                                        if num_players > 2:
                                            impact_quotient = 1 - round(2 / num_players, 2)

                                        # update losses-to-me and impact quotient
                                        opponents_arr[op_index][2] += 1
                                        opponents_arr[op_index][4] += impact_quotient

                                    else: #otherwise a third party won, so subtract impact
                                        impact_quotient = 0
                                        if num_players > 2:
                                            impact_quotient = round(-2 / num_players, 2)

                                        opponents_arr[op_index][4] += impact_quotient

                                    # we got what we need, so break the loop
                                    break
                                op_index += 1
                            
                            # if we looped through everything and didn't find what we need, add the enemy commander to the array
                            if op_index == op_arr_len:
                                # check if they won
                                if opponent_name == winner:
                                    # calculate impact quotient
                                    impact_quotient = 0
                                    if num_players > 2:
                                        impact_quotient = 1 - round(2 / num_players, 2)

                                    # append with one victory
                                    opponents_arr.append([opponent_name, 1, 0, 1, impact_quotient])

                                elif cmdr_name == winner:
                                    # calculate impact quotient
                                    impact_quotient = 0
                                    if num_players > 2:
                                        impact_quotient = 1 - round(2 / num_players, 2)

                                    # append with one loss
                                    opponents_arr.append([opponent_name, 0, 1, 1, impact_quotient])
                                else:
                                    # calculate impact quotient
                                    impact_quotient = 0
                                    if num_players > 2:
                                        impact_quotient = round(-2 / num_players, 2)

                                    # append with one game played
                                    opponents_arr.append([opponent_name, 0, 0, 1, impact_quotient])
                        
                        index += 1
            
            # We should now have a list of decks we've played against and their relative success against the searched deck

            # Now we filter out the decks with short game histories (currently <5 games)
            result_arr = []
            for op in opponents_arr:
                # if op[3] < 5:
                result_arr.append(op)
                # else:
                    # break

            win_rate = round(total_wins / total_games, 2) * 100

            response_str = "**Matchup statistics for {cmdr_name}:**".format(cmdr_name=cmdr_name)
            response_str += "\n\n**Overall:** {wins} wins and {losses} losses for a win rate of {win_rate}%".format(wins=total_wins,losses=total_games-total_wins,win_rate=win_rate)

            # Get top five matchups (if there are that many)
            result_arr.sort(reverse = True, key=lambda op: op[2] - op[1])
            
            response_str += "\n\n**Best Matchups:**"

            result_index = 0
            while result_index < 5:
                
                op_name = result_arr[result_index][0]
                op_win = result_arr[result_index][1]
                op_lose = result_arr[result_index][2]
                op_games = result_arr[result_index][3]
                impact = round(result_arr[result_index][4],2)

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

                response_str += "\n{index}. {op} — Won against: {op_lose}; Lost to: {op_win}. ({op_games} games total; impact factor: {impact}).".format(index=result_index+1, op=op_name, op_lose=op_lose, op_win=op_win, op_games=op_games, impact=impact)

                result_index += 1

            # Get bottom five matchups (if there are that many)
            result_arr.sort(key=lambda op: op[2] - op[1])

            response_str += "\n\n**Worst Matchups:**"

            result_index = 0
            while result_index < 5:
                
                op_name = result_arr[result_index][0]
                op_win = result_arr[result_index][1]
                op_lose = result_arr[result_index][2]
                op_games = result_arr[result_index][3]
                impact = round(result_arr[result_index][4],2)

                response_str += "\n{index}. {op} — Won against: {op_lose}; Lost to: {op_win}. ({op_games} games total; impact factor: {impact}).".format(index=result_index+1, op=op_name, op_lose=op_lose, op_win=op_win, op_games=op_games, impact=impact)

                result_index += 1

            return response_str

        elif args[0] == "notes":

            result_count = min(10, len(self.games))
            sort_method = "most recent"

            # see if they gave us a length term
            if len(args) > 1:
                result_count = int(args[1])

            if len(args) > 2:
                if args[2] == "random":
                    sort_method = "random"
                elif args[2] == "old" or args[2] == "oldest":
                    sort_method = "oldest"

            game_sample = []
            if sort_method == "random":
                game_sample = random.shuffle(self.games)
            elif sort_method == "oldest":
                game_sample = self.games
            else:
                game_sample = reversed(self.games)

            await message_obj.channel.send("Returning {count} {sort} game notes:".format(count=result_count,sort=sort_method))

            for game in reversed(self.games):
                if result_count > 0:

                    result_str = "\n\n**GAME #{num}**\nPlayers: ".format(num=game.index)

                    for player in game.players:
                        result_str += "{player} ({cmdr}), ".format(player=player[0], cmdr=player[1])

                    result_str += "\n\n**{winner} won** the game.  Here's what players said:".format(winner=game.winner[0])

                    for note in game.notes:
                        result_str += '\n"{content}"\n—{author}\n~'.format(content=note[1], author=note[0])

                    await channel.send(result_str)
                    
                    result_count -= 1

                else:
                    return ""




    ##################################
    #       OLD STATS METHODS        #
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
