from playerData import playerData
TEST_PLAYERS = {"Arsenal": [{'element_type': 1, 'first_name': 'Bernd', 'form': '0.0', 'id': 1, 'now_cost': 4.5, 'points_per_game': '1.3', 'selected_by_percent': '0.8', 'team': 1, 'total_points': 4, 'transfers_in': 63634, 'transfers_out': 188069, 'web_name': 'Leno', 'minutes': 270, 'goals_scored': 0, 'assists': 0, 'clean_sheets': 0, 'penalties_saved': 0, 'penalties_missed': 0, 'saves': 9, 'bonus': 0, 'points_per_million': 0.8888888888888888, 'fdr1': 5, 'fdr5': 13, 'fdr_remaining': 32, 'games_next_gw': 2, 'games_next_five': 5, 'total_games_remaning': 13},
                {'element_type': 1, 'first_name': 'Rúnar Alex', 'form': '0.0', 'id': 2, 'now_cost': 4.0, 'points_per_game': '0.0', 'selected_by_percent': '0.6', 'team': 1, 'total_points': 0, 'transfers_in': 19017, 'transfers_out': 76678, 'web_name': 'Rúnarsson', 'minutes': 0,
                    'goals_scored': 0, 'assists': 0, 'clean_sheets': 0, 'penalties_saved': 0, 'penalties_missed': 0, 'saves': 0, 'bonus': 0, 'points_per_million': 0.0, 'fdr1': 5, 'fdr5': 13, 'fdr_remaining': 32, 'games_next_gw': 2, 'games_next_five': 5, 'total_games_remaning': 13},
                {'element_type': 3, 'first_name': 'Willian', 'form': '0.0', 'id': 3, 'now_cost': 6.3, 'points_per_game': '0.0', 'selected_by_percent': '0.1', 'team': 1, 'total_points': 0, 'transfers_in': 914, 'transfers_out': 20442, 'web_name': 'Willian', 'minutes': 0, 'goals_scored': 0, 'assists': 0, 'clean_sheets': 0, 'penalties_saved': 0, 'penalties_missed': 0, 'saves': 0, 'bonus': 0, 'points_per_million': 0.0, 'fdr1': 5, 'fdr5': 13, 'fdr_remaining': 32, 'games_next_gw': 2, 'games_next_five': 5, 'total_games_remaning': 13}]}


class playerEvaluation:

    def __init__(self, team_and_players, position_and_players):
        self.team_and_players = self.add_player_values(team_and_players)

        # self.position_and_players = self._add_player_value(
        #     position_and_players)

    def add_player_values(self, player_dict):
        """ Method for calculating a players value based on the indvidual data in order to rank them

        Args:
            player_dict (dict): A dict where the players are stored as values

        Returns:
            dict: The player_dict but with the player_game_value:s k,v pair added.
        """

        player_value_1 = 0
        player_value_5 = 0
        player_value_all = 0

        for team in player_dict:
            for player in range(len(player_dict[team])):
                fdr1 = player_dict[team][player]["fdr1"]
                fdr5 = player_dict[team][player]["fdr5"]
                fdr_remaining = player_dict[team][player]["fdr_remaining"]
                games_next_gw = player_dict[team][player]["games_next_gw"]
                games_next_five = player_dict[team][player]["games_next_five"]
                total_games_remaning = player_dict[team][player]["total_games_remaning"]
                minutes = player_dict[team][player]["minutes"]
                gameweeks_lapsed = 38 - total_games_remaning  # 38 gw:s in a season

                total_points = player_dict[team][player]["total_points"]
                form = player_dict[team][player]["form"]
                position = player_dict[team][player]["element_type"]
                goals_scored = player_dict[team][player]["goals_scored"]
                assists = player_dict[team][player]["assists"]
                clean_sheets = player_dict[team][player]["clean_sheets"]
                saves = player_dict[team][player]["saves"]
                penalties_saved = player_dict[team][player]["penalties_saved"]

                # Goalkeepers
                if position == 1:
                    player_value_1, player_value_5, player_value_all = self._goalkeeper_eval(
                        fdr1, fdr5, fdr_remaining, games_next_gw, games_next_five, total_games_remaning, gameweeks_lapsed, minutes, total_points, float(form), clean_sheets, saves, penalties_saved, assists, goals_scored)

                # Defenders
                if position == 2:
                    player_value_1, player_value_5, player_value_all = self._defender_eval(
                        fdr1, fdr5, fdr_remaining, games_next_gw, games_next_five, total_games_remaning, gameweeks_lapsed, minutes, total_points, float(form), clean_sheets, goals_scored, assists)

                # Midfielders
                if position == 3:
                    player_value_1, player_value_5, player_value_all = self._midfielder_eval(
                        fdr1, fdr5, fdr_remaining, games_next_gw, games_next_five, total_games_remaning, gameweeks_lapsed, minutes, total_points, float(form), clean_sheets, goals_scored, assists)

                # Forward
                if position == 4:
                    player_value_1, player_value_5, player_value_all = self._forward_eval(
                        fdr1, fdr5, fdr_remaining, games_next_gw, games_next_five, total_games_remaning, gameweeks_lapsed, minutes, total_points, float(form), goals_scored, assists)

                player_dict[team][player]["PLAYER_VALUE"] = player_value_1
                player_dict[team][player]["PLAYER_5_VALUE"] = player_value_5
                player_dict[team][player]["PLAYER_REMAINING_VALUE"] = player_value_all
        return player_dict

    def _goalkeeper_eval(self, fdr1, fdr5, fdr_remaining, games_next_gw, games_next_five, total_games_remaning,
                         gameweeks_lapsed, minutes, total_points, form, clean_sheets, saves, penalites_saved, assists, goals_scored):
        """ Helper method for calculating the value of a goalkeeper. Return -1 if the player does not have matches
        left to play given the constraints given. 

        Args:
            fdr1 (int): fdr rating for next gw
            fdr5 (int): fdr rating for next 5 gw:s
            fdr_remaining (int): fdr rating for remaining gw:s
            games_next_gw (int): games in next gw
            games_next_five (int): games in next five gws
            total_games_remaning (int): remaining games of the season
            gameweeks_lapsed (int): games played so far
            minutes (int): minutes played so far
            total_points (int): points so far
            form (float): player form
            clean_sheets (int): number of clean sheets
            saves (int): number of saves made
            penalties_saved (int): penalties saved made
            assists (int): assists made
            goals_scored (int): goals_scored (can actually happen ;) )

        Returns:
            (float, float, float): Tuple containing the value for the goalkeeper for the next, next 5 and all remaining games.
        """

        goalkeeper_value = (saves % 3 + clean_sheets * 4 + penalites_saved *
                            5 + assists * 3 + goals_scored * 6) / gameweeks_lapsed

        # Next gameweek
        upcomming_value1 = self._calc_form_value(
            form, games_next_gw, fdr1, minutes, total_points, gameweeks_lapsed, goalkeeper_value)

        # Next five
        upcomming_value5 = self._calc_form_value(
            form, games_next_five, fdr5, minutes, total_points, gameweeks_lapsed, goalkeeper_value)

        # Remaining games
        upcomming_rest = self._calc_form_value(
            form, total_games_remaning, fdr_remaining, minutes, total_points, gameweeks_lapsed, goalkeeper_value)

        return upcomming_value1, upcomming_value5, upcomming_rest

    def _defender_eval(self, fdr1, fdr5, fdr_remaining, games_next_gw, games_next_five, total_games_remaning,
                       gameweeks_lapsed, minutes, total_points, form, clean_sheets, goals_scored, assists):
        """ Helper method for calculating the value of a defender. Returns -1 if the player does not have matches
        left to play given the constraints given. 

        Args:
            fdr1 (int): fdr rating for next gw
            fdr5 (int): fdr rating for next 5 gw:s
            fdr_remaining (int): fdr rating for remaining gw:s
            games_next_gw (int): games in next gw
            games_next_five (int): games in next five gws
            total_games_remaning (int): remaining games of the season
            gameweeks_lapsed (int): games played so far
            minutes (int): minutes played so far
            total_points (int): points so far
            form (float): player form
            clean_sheets (int): number of clean sheets
            goals_scored (int): number of goals_scored
            assists (int): number of assists made

        Returns:
            (float, float, float): Tuple containing the value for the defender for the next, next 5 and all remaining games.
        """

        defender_value = (goals_scored * 6 + clean_sheets *
                          4 + assists * 3) / gameweeks_lapsed

        # Next gameweek
        upcomming_value1 = self._calc_form_value(
            form, games_next_gw, fdr1, minutes, total_points, gameweeks_lapsed, defender_value)

        # Next five
        upcomming_value5 = self._calc_form_value(
            form, games_next_five, fdr5, minutes, total_points, gameweeks_lapsed, defender_value)

        # Remaining games
        upcomming_rest = self._calc_form_value(
            form, total_games_remaning, fdr_remaining, minutes, total_points, gameweeks_lapsed, defender_value)

        return upcomming_value1, upcomming_value5, upcomming_rest

    def _midfielder_eval(self, fdr1, fdr5, fdr_remaining, games_next_gw, games_next_five, total_games_remaning,
                         gameweeks_lapsed, minutes, total_points, form, clean_sheets, goals_scored, assists):
        """ Helper method for calculating the value of a midfielder. Returns -1 if the player does not have matches
        left to play given the constraints given. 

        Args:
            fdr1 (int): fdr rating for next gw
            fdr5 (int): fdr rating for next 5 gw:s
            fdr_remaining (int): fdr rating for remaining gw:s
            games_next_gw (int): games in next gw
            games_next_five (int): games in next five gws
            total_games_remaning (int): remaining games of the season
            gameweeks_lapsed (int): games played so far
            minutes (int): minutes played so far
            total_points (int): points so far
            form (float): player form
            clean_sheets (int): number of clean sheets
            goals_scored (int): number of goals_scored
            assists (int): number of assists made

        Returns:
            (float, float, float): Tuple containing the value for the midfielder for the next, next 5 and all remaining games.
        """

        midfielder_value = (goals_scored * 5 + clean_sheets *
                            1 + assists * 3) / gameweeks_lapsed

        # Next gameweek
        upcomming_value1 = self._calc_form_value(
            form, games_next_gw, fdr1, minutes, total_points, gameweeks_lapsed,  midfielder_value)

        # Next five
        upcomming_value5 = self._calc_form_value(
            form, games_next_five, fdr5, minutes, total_points, gameweeks_lapsed,  midfielder_value)

        # Remaining games
        upcomming_rest = self._calc_form_value(
            form, total_games_remaning, fdr_remaining, minutes, total_points, gameweeks_lapsed,  midfielder_value)

        return upcomming_value1, upcomming_value5, upcomming_rest

    def _forward_eval(self, fdr1, fdr5, fdr_remaining, games_next_gw, games_next_five, total_games_remaning,
                      gameweeks_lapsed, minutes, total_points, form, goals_scored, assists):
        """ Helper method for calculating the value of a forward. Returns -1 if the player does not have matches
        left to play given the constraints given. 

        Args:
            fdr1 (int): fdr rating for next gw
            fdr5 (int): fdr rating for next 5 gw:s
            fdr_remaining (int): fdr rating for remaining gw:s
            games_next_gw (int): games in next gw
            games_next_five (int): games in next five gws
            total_games_remaning (int): remaining games of the season
            gameweeks_lapsed (int): games played so far
            minutes (int): minutes played so far
            total_points (int): points so far
            form (float): player forms
            goals_scored (int): number of goals_scored
            assists (int): number of assists made

        Returns:
            (float, float, float): Tuple containing the value for the midfielder for the next, next 5 and all remaining games.
        """

        forward_value = (goals_scored * 4 + assists * 3) / gameweeks_lapsed

        # Next gameweek
        upcomming_value1 = self._calc_form_value(
            form, games_next_gw, fdr1, minutes, total_points, gameweeks_lapsed,  forward_value)

        # Next five
        upcomming_value5 = self._calc_form_value(
            form, games_next_five, fdr5, minutes, total_points, gameweeks_lapsed,  forward_value)

        # Remaining games
        upcomming_rest = self._calc_form_value(
            form, total_games_remaning, fdr_remaining, minutes, total_points, gameweeks_lapsed,  forward_value)

        return upcomming_value1, upcomming_value5, upcomming_rest

    def _calc_form_value(self, form, games, fdr, minutes, total_points, gameweeks_lapsed, position_value):
        """ Helper method for handling the form-value calculation. 

        Args:
            form (float): the player form
            games (int): games to be played
            fdr (int): fdr for games to be played

        Returns:
            float: the value
        """

        # Only add values if games remaining
        if games == 0:
            return -1
        else:
            # Historic data perspective
            history_value = (minutes * total_points) / (90 * gameweeks_lapsed)

            return history_value + position_value + (form * games) / fdr

    def _print_debugger(self, printed):
        print("*" * 50)
        print(printed)
        print("*" * 50)


pd = playerData()
pe = playerEvaluation(pd.team_and_player_dict, {})

# print(pe.team_and_players.keys())
for player in pe.team_and_players["Man City"]:
    print(f"Player: {player['web_name']}, gw1: {player['PLAYER_VALUE']}, gw5: {player['PLAYER_5_VALUE']}, gwRem: {player['PLAYER_REMAINING_VALUE']}")
    print(20 * '--')
