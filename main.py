import imp
from flask import Flask, render_template
from fplData import playerData, playerEvaluation, playerRanking, gameData
from secrets import secret

app = Flask(__name__)
gd = gameData.gameData()
pd = playerData.playerData()

# PlayerEvaluation behöver köra add_player_values på position-,team..-dict från PlayerData


@app.route("/")
def home():
    # VAD BEHÖVS HÄR?
    # gameData --> gw_data, convert_fixtures
    # playerData --> id_and_team_dict för att kunna convert
    id_player_dict = pd.player_and_data_dict
    gameweek_data = gd.gw_data
    # gw_games = gd.convert_fixtures(pd.id_and_team_dict) gw_games=gw_games
    return render_template("index.html", secret=secret["font_awesome"], gw_data=gameweek_data, id_player=id_player_dict)


@app.route("/your-team")
def your_team():
    pass
    # VAD BEHÖVS HÄR?
    # playerRanking --> get_most_valuable, under_performers, transfer_suggestion


@app.route("/best-team")
def best_team():
    pass
    # VAD BEHÖVS HÄR?
    # playerRanking en instans att skicka med
    # playerData, position_dict


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
