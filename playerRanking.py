from playerData import playerData
from playerEvaluation import playerEvaluation


class playerRanking:

    def _sort_players_on_attribute(self, attribute, player_list):
        """ Method for merge sorting the players based on a specific attribute

        Args:
            attribute (String): the attribute that should be sort on
            player_list (list): the list to be sorted

        """

        if len(player_list) > 1:
            mid = len(player_list) // 2
            left = player_list[:mid]
            right = player_list[mid:]

            self._sort_players_on_attribute(attribute, left)
            self._sort_players_on_attribute(attribute, right)

            # Half iterators
            i = 0
            j = 0

            # Main list iterator
            m = 0

            while i < len(left) and j < len(right):
                if left[i][attribute] <= right[j][attribute]:
                    player_list[m] = left[i]
                    i += 1
                else:
                    player_list[m] = right[j]
                    j += 1
                m += 1

            while i < len(left):
                player_list[m] = left[i]
                i += 1
                m += 1

            while j < len(right):
                player_list[m] = right[j]
                j += 1
                m += 1

    def get_most_valuable_list(self, attribute, players, nbr):
        """ Returns the most valueable players depending on attribute.

        Args:
            attribute (string): the attribute in which to rank the players
            players (dict): the players from which the most valueable should be found
            nbr (_type_): how many players to return
        Returns:
            _type_: A list of with the most valueable players
        """

        self._sort_players_on_attribute(attribute, players)
        # Desc ordering
        players = players[::-1]

        assert nbr <= len(players)

        return players[:nbr]


pd = playerData()
team_dict = pd.team_and_player_dict
position_dict = pd.position_and_player_dict
pe = playerEvaluation()
pe.add_player_values(position_dict)
pe.add_player_values(team_dict)
pr = playerRanking()

print(position_dict.keys())

all_players = position_dict["Goalkeepers"] + position_dict["Defenders"] + \
    position_dict["Midfielders"] + position_dict["Forwards"]

ten_goalies = pr.get_most_valuable_list(
    'PLAYER_REMAINING_VALUE', all_players, 10)

for player in ten_goalies:
    print(20 * '-')
    print(
        f"Player: {player['web_name']} - next_gw_value: {player['PLAYER_REMAINING_VALUE']}")

# pr._sort_players_on_attribute(
#     'PLAYER_5_VALUE', position_dict['Goalkeepers'])


# pr._sort_players_on_attribute('PLAYER_5_VALUE', team_dict['Aston Villa'])

# print(team_dict.keys())


# for player in position_dict['Goalkeepers'][::-1]:
#     print(20 * '-')
#     print(
#         f"Player: {player['web_name']} - next_gw_value: {player['PLAYER_5_VALUE']}")
