class playerEvaluation:

    def add_player_values(self, player_dict):
        """ Method for calculating a players value based on the indvidual data in order to rank them

        Args:
            player_dict (dict): A dict where the players are stored as values

        Returns:
            None: updates the input dict instead
        """

        # Key will either be a specific team or a position, depending on which dict is given as input
        for key in player_dict:
            for player in range(len(player_dict[key])):
                fdr1 = player_dict[key][player]["fdr1"]
                fdr5 = player_dict[key][player]["fdr5"]
                fdr_remaining = player_dict[key][player]["fdr_remaining"]
                games_next_gw = player_dict[key][player]["games_next_gw"]
                games_next_five = player_dict[key][player]["games_next_five"]
                total_games_remaning = player_dict[key][player]["total_games_remaning"]
                gameweeks_lapsed = 38 - total_games_remaning  # 38 gw:s in a season

                total_points = player_dict[key][player]["total_points"]
                form = player_dict[key][player]["form"]
                position = player_dict[key][player]["element_type"]
                goals_scored = player_dict[key][player]["goals_scored"]
                assists = player_dict[key][player]["assists"]
                clean_sheets = player_dict[key][player]["clean_sheets"]
                saves = player_dict[key][player]["saves"]
                penalties_saved = player_dict[key][player]["penalties_saved"]

                # Goalkeepers
                if position == 1:
                    player_value_1, player_value_5, player_value_all = self._goalkeeper_eval(
                        fdr1, fdr5, fdr_remaining, games_next_gw, games_next_five, total_games_remaning, gameweeks_lapsed, total_points, float(form), clean_sheets, saves, penalties_saved, assists, goals_scored)

                # Defenders
                if position == 2:
                    player_value_1, player_value_5, player_value_all = self._defender_eval(
                        fdr1, fdr5, fdr_remaining, games_next_gw, games_next_five, total_games_remaning, gameweeks_lapsed, total_points, float(form), clean_sheets, goals_scored, assists)

                # Midfielders
                if position == 3:
                    player_value_1, player_value_5, player_value_all = self._midfielder_eval(
                        fdr1, fdr5, fdr_remaining, games_next_gw, games_next_five, total_games_remaning, gameweeks_lapsed, total_points, float(form), clean_sheets, goals_scored, assists)

                # Forward
                if position == 4:
                    player_value_1, player_value_5, player_value_all = self._forward_eval(
                        fdr1, fdr5, fdr_remaining, games_next_gw, games_next_five, total_games_remaning, gameweeks_lapsed, total_points, float(form), goals_scored, assists)

                player_dict[key][player]["PLAYER_VALUE"] = player_value_1
                player_dict[key][player]["PLAYER_5_VALUE"] = player_value_5
                player_dict[key][player]["PLAYER_REMAINING_VALUE"] = player_value_all

    def _goalkeeper_eval(self, fdr1, fdr5, fdr_remaining, games_next_gw, games_next_five, total_games_remaning,
                         gameweeks_lapsed, total_points, form, clean_sheets, saves, penalites_saved, assists, goals_scored):
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
            form, games_next_gw, 1, fdr1, total_points, gameweeks_lapsed, goalkeeper_value)

        # Next five
        upcomming_value5 = self._calc_form_value(
            form, games_next_five, 5, fdr5, total_points, gameweeks_lapsed, goalkeeper_value)

        # Remaining games
        upcomming_rest = self._calc_form_value(
            form, total_games_remaning, total_games_remaning, fdr_remaining, total_points, gameweeks_lapsed, goalkeeper_value)

        return upcomming_value1, upcomming_value5, upcomming_rest

    def _defender_eval(self, fdr1, fdr5, fdr_remaining, games_next_gw, games_next_five, total_games_remaning,
                       gameweeks_lapsed, total_points, form, clean_sheets, goals_scored, assists):
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
            form, games_next_gw, 1, fdr1, total_points, gameweeks_lapsed, defender_value)

        # Next five
        upcomming_value5 = self._calc_form_value(
            form, games_next_five, 5, fdr5, total_points, gameweeks_lapsed, defender_value)

        # Remaining games
        upcomming_rest = self._calc_form_value(
            form, total_games_remaning, total_games_remaning, fdr_remaining, total_points, gameweeks_lapsed, defender_value)

        return upcomming_value1, upcomming_value5, upcomming_rest

    def _midfielder_eval(self, fdr1, fdr5, fdr_remaining, games_next_gw, games_next_five, total_games_remaning,
                         gameweeks_lapsed, total_points, form, clean_sheets, goals_scored, assists):
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
            form, games_next_gw, 1, fdr1, total_points, gameweeks_lapsed,  midfielder_value)

        # Next five
        upcomming_value5 = self._calc_form_value(
            form, games_next_five, 5, fdr5, total_points, gameweeks_lapsed,  midfielder_value)

        # Remaining games
        upcomming_rest = self._calc_form_value(
            form, total_games_remaning, total_games_remaning, fdr_remaining, total_points, gameweeks_lapsed,  midfielder_value)

        return upcomming_value1, upcomming_value5, upcomming_rest

    def _forward_eval(self, fdr1, fdr5, fdr_remaining, games_next_gw, games_next_five, total_games_remaning,
                      gameweeks_lapsed, total_points, form, goals_scored, assists):
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
            form, games_next_gw, 1, fdr1, total_points, gameweeks_lapsed,  forward_value)

        # Next five
        upcomming_value5 = self._calc_form_value(
            form, games_next_five, 5, fdr5, total_points, gameweeks_lapsed,  forward_value)

        # Remaining games
        upcomming_rest = self._calc_form_value(
            form, total_games_remaning, total_games_remaning, fdr_remaining, total_points, gameweeks_lapsed,  forward_value)

        return upcomming_value1, upcomming_value5, upcomming_rest

    def _calc_form_value(self, form, games, should_play, fdr, total_points, gameweeks_lapsed, position_value):
        """ Helper method for handling the form-value calculation. 

        Args:
            form (float): player form
            games (int): games to be played
            should_playfdr (int): normally number of games, 1/gw
            total_points (int): total points so far 
            gameweeks_lapsed (int): how many gw have passed so far
            position_value (float): position specific value

        Returns:
            float: the evaluated number based on in parameters
        """

        # Only add values if games remaining

        gw_factor_dict = {
            0: 1,
            1: 2,
            -1: 0.5,
            2: 3,
            -2: 0.25
        }

        if games == 0:
            return -1
        else:
            # Historic data perspective
            history_value = total_points / gameweeks_lapsed

            gw_factor = games - should_play

            return history_value + position_value + (form * games) * gw_factor_dict[gw_factor] / fdr
