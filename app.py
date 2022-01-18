import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template
import os,requests, json
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime as dt, timedelta

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class CustomerBet(db.Model):
    __tablename__ = 'customerbet'
    id = db.Column(db.Integer, primary_key=True)
    matchid = db.Column(db.String(40), nullable=False)
    team = db.Column(db.String(30), nullable=False)
    stake = db.Column(db.Float, nullable=False)
    odds = db.Column(db.Float, nullable=False)
    blcheck = db.Column(db.Integer, nullable=False)
    betwith = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, index=False, unique=False, nullable=False)

    def __init__(self, matchid, team, stake, odds, blcheck, betwith):
        self.matchid = matchid
        self.team = team
        self.stake = stake
        self.odds = odds
        self.blcheck = blcheck
        self.betwith = betwith
        self.created= dt.now()
 
def checkingbets():
    """Checking Matched Bet"""
    matchid = request.form['matchid']
    team = request.form['team']
    stake = float(request.form['stake'])
    odds = float(request.form['odds'])
    blcheck = int(request.form['blcheck'])
    betwithh = 0
    if blcheck:
        blflag=0
    else:
        blflag=1
    betwithh = 0
    if matchid and team and stake and odds :
        chck_match = CustomerBet.query.filter_by(matchid = matchid , team = team , stake = stake , odds = odds , blcheck = blflag , betwith = betwithh).first()
        if chck_match:
            return chck_match.id
        else:
            return 0

# Fetching from APIs
def fetchapi(src, sport):
    url = 'https://apis.odibets.com/v4/matches'
    cmptid = ''
    tab =''
    src = src
    sport_id=sport
    timeout=15
    try:
        response = requests.get(url, headers = {'Content-Type': 'application/json'}, params ={'src' : src, 'sport_id' : sport_id, 'tab' : tab, 'country_id' : '', 'day' : '', 'sort_by' : '', 'competition_id' : cmptid, 'trials' : 0}, timeout=timeout)
        json_data = json.loads(response.text)
        allmatches = []
        for comp1 in json_data['data']['competitions']:
            finalmatch=[]
            try:
                for match1 in comp1['matches']:
                    match1_time = dt.strptime(match1['start_time'], '%Y-%m-%d %H:%M:%S')
                    match_time_Indian = match1_time + timedelta(hours=2, minutes=30)
                    match1_teamH = match1['home_team']
                    match1_teamA = match1['away_team']
                    match1_draw = 'Draw'
                    match1_id = match1_teamH.replace(" ", "")[:3].lower()+ 'vs' +match1_teamA.replace(" ", "")[:3].lower() +str(match1_time.day)+str(match1_time.month)+str(match1_time.year)
                    match1_title = match1_teamH + ' Vs ' + match1_teamA
                    match1_oddsH = match1['markets'][0]['outcomes'][0]['odd_value']
                    match1_oddsH_prev = match1['markets'][0]['outcomes'][0]['prev_odd_value']
                    try:
                        match1_oddsA = match1['markets'][0]['outcomes'][2]['odd_value']
                        match1_oddsA_prev = match1['markets'][0]['outcomes'][2]['prev_odd_value']
                        match1_oddsD = float(match1['markets'][0]['outcomes'][1]['odd_value'])
                        match1_oddsD_prev = float(match1['markets'][0]['outcomes'][1]['prev_odd_value'])
                    except IndexError:
                        match1_oddsD = 0
                        match1_oddsD_prev = 0
                        match1_oddsA = match1['markets'][0]['outcomes'][1]['odd_value']
                        match1_oddsA_prev = match1['markets'][0]['outcomes'][1]['prev_odd_value']

                    case = {'match_id': match1_id, 'match_title': match1_title, 'match_time':match_time_Indian, 'draw_team': match1_draw, 'home_team': match1_teamH, 'away_team': match1_teamA, 'home_team_odds':match1_oddsH , 'home_team_odds_prev': match1_oddsH_prev, 'away_team_odds': match1_oddsA, 'away_team_odds_prev': match1_oddsA_prev, 'draw_team_odds': match1_oddsD,'draw_team_odds_prev':match1_oddsD_prev}
                    finalmatch.append(case)
            except KeyError:
                continue
            competition = {'competition_name': comp1['competition_name'], 'country_name':comp1['country_name'], 'matches': finalmatch}
            allmatches.append(competition)
        #For Booster Matches
        if len(json_data['data']['boosted']) > 0:
            finalmatchb=[]
            for match1 in json_data['data']['boosted']:
                match1_time = dt.strptime(match1['start_time'], '%Y-%m-%d %H:%M:%S')
                match_time_Indian = match1_time + timedelta(hours=2, minutes=30)
                match1_teamH = match1['home_team']
                match1_teamA = match1['away_team']
                match1_draw = 'Draw'
                match1_id = match1_teamH.replace(" ", "")[:3].lower()+ 'vs' +match1_teamA.replace(" ", "")[:3].lower() +str(match1_time.day)+str(match1_time.month)+str(match1_time.year)
                match1_title = match1_teamH + ' Vs ' + match1_teamA
                match1_oddsH = match1['market']['outcomes'][0]['odd_value']
                match1_oddsH_prev = match1['market']['outcomes'][0]['prev_odd_value']
                try:
                    match1_oddsA = match1['market']['outcomes'][2]['odd_value']
                    match1_oddsA_prev = match1['market']['outcomes'][2]['prev_odd_value']
                    match1_oddsD = float(match1['market']['outcomes'][1]['odd_value'])
                    match1_oddsD_prev = float(match1['market']['outcomes'][1]['prev_odd_value'])
                except IndexError:
                    match1_oddsD = 0
                    match1_oddsD_prev = 0
                    match1_oddsA = match1['market']['outcomes'][1]['odd_value']
                    match1_oddsA_prev = match1['market']['outcomes'][1]['prev_odd_value']

                caseb = {'match_id': match1_id, 'match_title': match1_title, 'match_time':match_time_Indian, 'draw_team': match1_draw, 'home_team': match1_teamH, 'away_team': match1_teamA, 'home_team_odds':match1_oddsH , 'home_team_odds_prev': match1_oddsH_prev, 'away_team_odds': match1_oddsA, 'away_team_odds_prev': match1_oddsA_prev, 'draw_team_odds': match1_oddsD,'draw_team_odds_prev':match1_oddsD_prev}
                finalmatchb.append(caseb)
            competitionb = {'competition_name': 'All Competition', 'country_name':'Upcoming Matches', 'matches': finalmatchb}
            allmatches.append(competitionb)
        return allmatches
    except requests.exceptions.Timeout:
        return 0
    except :
        return 0

def fetch_sports():
    sports=[{'sport_name':'Cricket', 'src':2}, {'sport_name':'Basketball', 'src':2}, {'sport_name':'Soccer', 'src':''}, {'sport_name':'Tennis', 'src':'2'}, {'sport_name':'Ice Hockey', 'src':'2'}]
    allsports=[]
    for sport in sports:
        allcomp = fetchapi(sport['src'], sport['sport_name'])
        if allcomp == 0: #API Service not available
            return 0
        allsports.append({'sport_name': sport['sport_name'], 'all_leagues' : allcomp})
    return allsports

@app.route('/')
def home():
    return render_template('index.html' , users = CustomerBet.query.all(), allsports =fetch_sports(), today=dt.today().strftime("%B %d, %Y"))

@app.route('/bet', methods = ['GET', 'POST'])
def bet():
    if request.method == 'POST':
        if not request.form['matchid'] or not request.form['team'] or not request.form['stake'] or float(request.form['stake']) <=0 or not request.form['odds'] or float(request.form['odds'])<=1.0:
             flash('Please enter all the fields', 'error')
        else:
            idd = checkingbets()
            """Created Bet"""
            userbet = CustomerBet(request.form['matchid'], request.form['team'],request.form['stake'], request.form['odds'], request.form['blcheck'], idd)
            db.session.add(userbet)
            db.session.commit()
            db.session.refresh(userbet)
            if idd:
                info = CustomerBet.query.filter_by(id=idd).first()
                info.betwith =userbet.id
                db.session.add(info)
                db.session.commit()
                flash('Bet Matched and successfully placed')
            else:
                flash('Bet successfully placed')
    return render_template('bet.html', users = CustomerBet.query.all())


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
    #run only one time for creating database
    #db.create_all()    
