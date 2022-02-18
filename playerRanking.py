from playerData import playerData
from playerEvaluation import playerEvaluation


class playerRanking:

    def sort_players_on_attribute(self, attribute, player_list):
        """ Method for merge sorting the players based on a specific attribute

        Args:
            attribute (String): the attribute that should be sort on
            player_list (list): the list to be sorted

        """

        if len(player_list) > 1:
            mid = len(player_list) // 2
            left = player_list[:mid]
            right = player_list[mid:]

            self.sort_players_on_attribute(attribute, left)
            self.sort_players_on_attribute(attribute, right)

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


pd = playerData()
team_dict = pd.team_and_player_dict
position_dict = pd.position_and_player_dict
pe = playerEvaluation()
pe.add_player_values(position_dict)
pe.add_player_values(team_dict)
pr = playerRanking()
pr.sort_players_on_attribute('PLAYER_VALUE', position_dict['Midfielders'])


for goalie in position_dict['Midfielders'][::-1]:
    print(20 * '-')
    print(
        f"Player: {goalie['web_name']} - next_gw_value: {goalie['PLAYER_VALUE']}")
