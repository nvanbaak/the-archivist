class Lobby:
    def __init__(self, name):
        self.game = None
        self.name = name
        self.players = []
    
    def add_player(self, player):

        if not player == self.players:
            self.players.append(player)
            return "{player} has joined **{lobby}**.".format(player=player, lobby=self.name)
        else:
            return "{player} is already in **{lobby}**.".format(player=player, lobby=self.name)

    def remove_player(self, player):
        try:
            self.players.remove(player)
            return "{player} has left **{lobby}**.".format(player=player, lobby=self.name)
        except ValueError:
            return "Error — attempted to remove non-existant player {player} from lobby **{lobby}**!".format(player=player, lobby=self.name)

    def list_players(self):
        if self.players:
            response = "["
            list_str = ""
            for player in self.players:
                list_str += ", {player}".format(player=player)
            response += list_str[2:]
            response += "]"
            return response
        else:
            return ""
