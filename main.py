from flask import Flask, render_template, request
from fplData import playerData, playerEvaluation, playerRanking, gameData
from secrets import secret
import sys
# sys.setrecursionlimit(1000000)

app = Flask(__name__)
gd = gameData.gameData()
pd = playerData.playerData()
pe = playerEvaluation.playerEvaluation()
pe.add_player_values(pd.position_and_player_dict)
pe.add_player_values(pd.team_and_player_dict)
pr = playerRanking.playerRanking()


# starting_eleven, captain, bench = pr.get_optimal_team(
#     pd.position_and_player_dict, 90, 1)
# starting_eleven, captain, bench = pr.get_optimal_team(
#     pd.position_and_player_dict, 95, 1)
# starting_eleven, captain, bench = pr.get_optimal_team(
#     pd.position_and_player_dict, 105, 1)
# starting_eleven, captain, bench = pr.get_optimal_team(
#     pd.position_and_player_dict, 110, 1)


@app.route("/")
def home():
    id_player_dict = pd.player_and_data_dict
    gameweek_data = gd.gw_data
    gw_games = gd.convert_fixtures(pd.id_and_team_dict)

    return render_template("index.html", secret=secret["font_awesome"], gw_data=gameweek_data, id_player=id_player_dict, gw_games=gw_games)


@app.route("/your-team")
def your_team():
    pass
    # VAD BEHÖVS HÄR?
    # playerRanking --> get_most_valuable, under_performers, transfer_suggestion


@app.route("/best-team-configurations")
def best_team_config():
    return render_template("config.html")


@app.route("/best-team", methods=["POST"])
def best_team():
    # Kolla så att det finns formulärdata annars redirect till config-sidan
    budget = float(request.form["budget"])
    to_consider = int(request.form["to_consider"])
    starting_eleven, captain, bench = pr.get_optimal_team(
        pd.position_and_player_dict, budget, to_consider)
    return render_template("optimal.html", starting_eleven=starting_eleven, bench=bench, captain=captain)


@app.route("/teams/<team>")
def team(team):
    # VAD BEHÖVS HÄR?
    # playerData --> team and player dict
    pass


@app.route("/about")
def about():
    # Nada, bara information om upplägget och algorithmen som använts
    # Länkar som varit bra etc
    pass


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()
