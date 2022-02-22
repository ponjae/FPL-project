import requests


class playerData:

    def __init__(self):
        self.load_fpl_data()

    def load_fpl_data(self):
        """
        Function for fetching and loading the data from the api and store it in the class
        """
        response = requests.get(
            'https://fantasy.premierleague.com/api/bootstrap-static/')
        raw_data = response.json()
        fdr_dict = self._get_fdr_dict()
        next_gw_number = min(fdr_dict.keys())
        self.team_and_player_dict = self._populate_team_dict(
            raw_data, fdr_dict, next_gw_number)
        self.position_and_player_dict = self._populate_position_dict(
            raw_data, fdr_dict, next_gw_number)
        self.player_and_data_dict = self._populate_player_dict(
            self.team_and_player_dict)

    def _get_fdr_dict(self):
        """ Function for fetching the Fixture Difficulty Data and converting it to a dict containing a dict with 
        every upcomming gameweek fdr for each team in that specific gameweek. Ex)

        {28:
            {
                1: [3, 4],
                2: [2, 5],
                ...
            }
        29: ..
        }

        Gameweek number is the first key, then the team id is the second key with the value of their opponents 
        fdr rating for that specific gameweek. 

        Returns:
            dict : The remaning gameweeks with each teams upcomming fdr rating collected. 
        """
        game_week_fdr_dict = {}
        response = requests.get(
            f"https://fantasy.premierleague.com/api/fixtures?future=1")
        game_data = response.json()
        for game in game_data:
            game_week = game["event"]

            # Add the gw number as the key for all fixtures within it
            if game_week not in game_week_fdr_dict:
                game_week_fdr_dict[game_week] = {}
            home_team = game["team_h"]
            away_team = game["team_a"]
            home_difficulty = game["team_h_difficulty"]
            away_difficulty = game["team_a_difficulty"]

            # In case of a dgw this needs to be checked
            if home_team in game_week_fdr_dict[game_week].keys():
                game_week_fdr_dict[game_week][home_team].append(
                    home_difficulty)
            else:
                game_week_fdr_dict[game_week][home_team] = [home_difficulty]
            if away_team in game_week_fdr_dict[game_week].keys():
                game_week_fdr_dict[game_week][away_team].append(
                    away_difficulty)
            else:
                game_week_fdr_dict[game_week][away_team] = [away_difficulty]

        return game_week_fdr_dict

    def _set_up_prerequisites(self, element_types):
        """ Helper method for setting up helper dicts for converting to a more 
        user friendly state.

        Args:
            element_types (list): containing a dict for each available position

        Returns:
            (dict, dict): a dict with positions as keys and empty list to be filled with players as values,
            a dict with id for each position as keys.
        """

        position_dict = {}
        id_position_dict = {}
        for position in element_types:
            id_position_dict[position["id"]] = position["plural_name"]
            position_dict[position["plural_name"]] = []
        return position_dict, id_position_dict

    def _get_teams(self, raw_data):
        """ Helper method for mapping a teams id with their normal name

        Args:
            raw_data (dict): the data fetched from the api-call

        Returns:
            [dict]: a dict containing the team id as key and their real names as values
        """

        team_dict = {}
        for team in raw_data["teams"]:
            id_number = team["id"]
            team_name = team["name"]
            team_dict[id_number] = team_name
        return team_dict

    def _populate_team_dict(self, raw_data, fdr_dict, next_gw_number):
        """ Function for adding players to their respective team in the team dict.

        Args:
            raw_data (dict): data fetched from the API
            fdr_dict (dict): fdr dict to be passed on
            next_gw_number (int): the upcomming gw number

        Returns:
            [dict]: A dict containing all the players with their team as the key
        """

        player_data = raw_data['elements']
        id_and_team_dict = self._get_teams(raw_data)
        team_and_player_dict = {}
        for player in player_data:
            team_id = player["team"]
            team_name = id_and_team_dict[team_id]
            filtered_player = self._filter_player_data(
                player, fdr_dict, next_gw_number)
            if team_name not in team_and_player_dict.keys():
                team_and_player_dict[team_name] = [filtered_player]
            else:
                team_and_player_dict[team_name].append(filtered_player)
        return team_and_player_dict

    def _populate_position_dict(self, raw_data, fdr_dict, next_gw_number):
        """ Function for adding players to their respective position in the position dict.

        Args:
            raw_data (dict): data fetched from the API
            fdr_dict (dict): fdr dict to be passed on
            next_gw_number (int): the upcomming gw number

        Returns:
            [dict]: A dict containing all the players with their position as the key
        """

        element_types = raw_data["element_types"]
        player_data = raw_data["elements"]
        position_dict, id_position_dict = self._set_up_prerequisites(
            element_types)
        for player in player_data:
            player_position = id_position_dict[player["element_type"]]
            filtered_player = self._filter_player_data(
                player, fdr_dict, next_gw_number)
            position_dict[player_position].append(filtered_player)
        return position_dict

    def _populate_player_dict(self, team_and_player_dict):
        """ Method for populating a dict where player_names are the keys 
        and their corresponding data is the value.

        Args:
            team_and_player_dict (dict): The input dict containing team and players for now

        Returns:
            dict: the player dict
        """
        player_dict = {}

        for team in team_and_player_dict:
            for player in team_and_player_dict[team]:
                # Player id is the unique key.
                player_dict[f"{player['id']}"] = player
        return player_dict

    def _filter_player_data(self, player, fdr_dict, next_gw_number):
        """ Filters out any unrelevant data that will not be used in a later stage. 

         Args:
            player: the player to be filtered
            remaining_gws ([dict]): the fdr dict
            next_gw_number ([int]): the upcomming gw_number (where to start looking)

        Returns:
            dict: the filtered player data
        """

        wanted_data = {"first_name", "web_name", "form", "id", "points_per_game", "element_type", "selected_by_percent", "team", "now_cost", "total_points", "transfers_in",
                       "transfers_out", "minutes", "goals_scored", "assists", "clean_sheets", "penalties_saved", "penalties_missed", "saves", "bonus"}
        filtered_data = {}
        for data_key in player.keys():
            if data_key in wanted_data:
                filtered_data[data_key] = player[data_key]
        filtered_data["now_cost"] = filtered_data["now_cost"] / \
            10  # make it right format
        points_per_million = filtered_data["total_points"] / \
            filtered_data["now_cost"]
        filtered_data["points_per_million"] = points_per_million

        player_team = filtered_data["team"]
        fdr1, fdr5, fdr_remaining = self._calculate_player_fdr(
            player_team, fdr_dict, next_gw_number)
        filtered_data["fdr1"] = fdr1
        filtered_data["fdr5"] = fdr5
        filtered_data["fdr_remaining"] = fdr_remaining
        filtered_data["points_per_million"]

        games_next_gw, games_next_five, total_games_remaning = self._get_remaining_games(
            player_team, fdr_dict, next_gw_number)
        filtered_data["games_next_gw"] = games_next_gw
        filtered_data["games_next_five"] = games_next_five
        filtered_data["total_games_remaning"] = total_games_remaning
        return filtered_data

    def _get_remaining_games(self, team, remaining_gws, next_gw_number):
        """ Calculate the games left to play for a certain player beloning to a certain team. 

        Args:
            team (int): the id of the team that the player belongs to
            remaining_gws ([dict]): the fdr dict
            next_gw_number ([int]): the upcomming gw_number (where to start looking)

        Returns:
            (int, int, int): A tuple containing the games for the next, next-five
            and total remaining gameweeks if present, else 0
        """

        next_gw_games = 0
        next_five_gws = 0
        remaining_games = 0
        gw_remaining = len(remaining_gws)

        if gw_remaining >= 1:
            next_gw = remaining_gws[next_gw_number]
            if team in next_gw.keys():
                next_gw_games = len(next_gw[team])

        if gw_remaining > 4:
            next_five_gws = sum([len(remaining_gws[gw][team]) for gw in range(
                next_gw_number, next_gw_number + 5) if team in remaining_gws[gw].keys()])

        remaining_games = sum([len(remaining_gws[gw][team]) for gw in range(
            next_gw_number, next_gw_number + len(remaining_gws)) if team in remaining_gws[gw].keys()])

        return next_gw_games, next_five_gws, remaining_games

    def _calculate_player_fdr(self, team, remaining_gws, next_gw_number):
        """ Function for calculating the fdr rating for a specific player beloning to a specific team

        Args:
            team (int): the id of the team that the player belongs to
            remaining_gws ([dict]): the fdr dict
            next_gw_number ([int]): the upcomming gw_number (where to start looking)

        Returns:
            (Union(int, None), Union(int, None), Union(int, None)): A tuple containing the fdr-sum for the next, next-five
            total remaining games if present, else None
        """

        next_gw_fdr = None
        next_five_fdr = None
        remaining_fdr = None
        games_remaining = len(remaining_gws)
        if games_remaining >= 1:
            next_gw = remaining_gws[next_gw_number]
            if team in next_gw.keys():
                next_gw_fdr = sum(next_gw[team])

        if games_remaining > 4:
            next_five_fdr = sum([sum(remaining_gws[gw][team]) for gw in range(
                next_gw_number, next_gw_number + 5) if team in remaining_gws[gw].keys()])

        remaining_fdr = sum([sum(remaining_gws[gw][team]) for gw in range(
            next_gw_number, next_gw_number + len(remaining_gws)) if team in remaining_gws[gw].keys()])

        return next_gw_fdr, next_five_fdr, remaining_fdr


pd = playerData()
