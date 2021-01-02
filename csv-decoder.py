import csv

global data_arr
data_arr = []

class Game:
    def __init__(self):
        self.players = []
        self.first = []
        self.eliminated = []
        self.winner = []
        self.notes = []

    def parse_csv_entry(self, csv_obj):
        # First data item is the date, which Magic Butler doesn't track.
        # Second data item is the game's winner.

        winner_str = game_data[1]
        # We get the data in name!deck format, so splitting the string works fine
        self.winner = winner_str.split("!")
        
        # Third item is the list of players.  First player in the list went first.
        player_arr = game_data[2].split(", ")
        for pl in player_arr:
            player = pl.split("!")
            self.players.append(player)

        self.first = self.players[0]

        # Fourth item is Tim's note, so we'll just add that in
        self.notes.append(["Jaeil", game_data[3]])

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


with open("EDH_Record_-_Games.csv", newline='') as csvfile:
    gamereader = csv.reader(csvfile, delimiter=',',quotechar='"')
    for row in gamereader:
        data_arr.append(row)

for game_data in data_arr:

    # Start by making a new game
    current = Game()

    # run the game's parsing method
    current.parse_csv_entry(game_data)
    current.store_data("gamehistory.txt")