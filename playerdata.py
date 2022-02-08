import requests


class fplData:

    def __init__(self):
        response = requests.get(
            'https://fantasy.premierleague.com/api/bootstrap-static/')
        raw_data = response.json()
        self.id_and_team_dict = self._get_teams(raw_data)
        self.team_and_player_dict = self._populate_team_dict(raw_data)

    def _populate_team_dict(self, raw_data):
        player_data = raw_data['elements']
        team_and_player_dict = {}
        for player in player_data:
            team_id = player["team"]
            team_name = self.id_and_team_dict[team_id]
            if team_name not in team_and_player_dict.keys():
                team_and_player_dict[team_name] = [player]
            else:
                team_and_player_dict[team_name].append(player)
        return team_and_player_dict

    def _get_teams(self, raw_data):
        team_dict = {}
        for team in raw_data["teams"]:
            id_number = team["id"]
            team_name = team["name"]
            team_dict[id_number] = team_name
        return team_dict


# for player in fplData().team_and_player_dict["Arsenal"]:
#     print(f"Player: {player}")
#     print(50 * '*')

print(fplData().team_and_player_dict.keys())
