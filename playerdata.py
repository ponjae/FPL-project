import requests


class fplData:

    def __init__(self):
        response = requests.get(
            'https://fantasy.premierleague.com/api/bootstrap-static/')
        raw_data = response.json()
        self.id_and_team_dict = self._get_teams(raw_data)
        self.team_and_player_dict = self._populate_team_dict(raw_data)
        self.position_and_player_dict = self._populate_position_dict(raw_data)

    def _get_teams(self, raw_data):
        team_dict = {}
        for team in raw_data["teams"]:
            id_number = team["id"]
            team_name = team["name"]
            team_dict[id_number] = team_name
        return team_dict

    def _populate_team_dict(self, raw_data):
        player_data = raw_data['elements']
        team_and_player_dict = {}
        for player in player_data:
            team_id = player["team"]
            team_name = self.id_and_team_dict[team_id]
            filtered_player = self._filter_player_data(player)
            if team_name not in team_and_player_dict.keys():
                team_and_player_dict[team_name] = [filtered_player]
            else:
                team_and_player_dict[team_name].append(filtered_player)
        return team_and_player_dict

    def _populate_position_dict(self, raw_data):
        element_types = raw_data["element_types"]
        player_data = raw_data["elements"]
        position_dict, id_position_dict = self._set_up_prerequisites(
            element_types)
        for player in player_data:
            player_position = id_position_dict[player["element_type"]]
            filtered_player = self._filter_player_data(player)
            position_dict[player_position].append(filtered_player)
        return position_dict

    def _set_up_prerequisites(self, element_types):
        position_dict = {}
        id_position_dict = {}
        for position in element_types:
            id_position_dict[position["id"]] = position["plural_name"]
            position_dict[position["plural_name"]] = []
        return position_dict, id_position_dict

    def _filter_player_data(self, player):
        wanted_data = {'first_name', 'web_name', 'form', 'id', 'points_per_game', 'selected_by_percent', 'team', 'total_points', 'transfers_in',
                       'transfers_out', 'minutes', 'goals_scored', 'assists', 'clean_sheets', 'penalties_saved', 'penalties_missed', 'saves', 'bonus'}
        filtered_data = {}
        for data_key in player.keys():
            if data_key in wanted_data:
                filtered_data[data_key] = player[data_key]
        return filtered_data

    def _print_debugger(self, printed):
        print("*" * 50)
        print(printed)
        print("*" * 50)


fpl = fplData()
for player in fpl.team_and_player_dict["Arsenal"]:
    fpl._print_debugger(player)


# for team, players in fplData().team_and_player_dict.items():
#     for player in players:
#         print(f"Player: {player['web_name']} plays for {team}")
#         print(' ')

#     print(50 * '*')

# print(fplData().team_and_player_dict.keys())
