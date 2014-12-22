import os
import jinja2
import webapp2
import random

from helper_functions import *

from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.api import users


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

#global variables
team_names = []
team_scores = []
game_type = ""
logout_url = users.create_logout_url('/log-out')
login_url = users.create_login_url('/welcome')

def getGameId ():
	number = round(random.random()*10000000,0)
	game_id = str(number)
	return game_id

#function to upload game data
def uploadData(df):
	for gvent in df:
		p = game_event(game_id = gvent[0],
					   game_type = gvent[1],
					   player_id = gvent[2],
					   player_teammate_id = gvent[3],
					   opp_id = gvent[4],
					   player_score = gvent[5],
					   opp_score = gvent[6],
					   player_win = gvent[7],
					   player_score_z = gvent[8],
					   opp_score_z = gvent[9],
					   )
		p.put()


#function to register a new user
def inputUserData(work_email, first_name, last_name, user_name):
	p = Account(username = user_name.nickname(),
				#userid = user_name.user_id(),
				email = user_name.email(),
				work_email = work_email,
				first_name = first_name,
				last_name = last_name,
				)
	p.put()


#create users database:
class Account(ndb.Model):
	username = ndb.StringProperty()
	#userid = ndb.FloatProperty()
	email = ndb.StringProperty()
	work_email = ndb.StringProperty()
	first_name = ndb.StringProperty()
	last_name = ndb.StringProperty()

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class Handler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)




class Welcome(Handler):
	def get(self):
		user_name = users.get_current_user()

		#Test if user is registered
		q = Account.query(Account.username == user_name.nickname()).count()
		if q < 1:
			self.redirect('register')

		players = db.GqlQuery("SELECT * FROM game_event ORDER BY date DESC")

		p_out = gameSummer(players) 		#get recent games
		win_data = winRank(players) 		#get win percentages
		num_players = range(len(win_data)) 	#get number of players

		self.render("welcome.html", win_data=win_data, num_players=num_players, p_out=p_out, logout_url=logout_url, user_nickname=user_name.nickname())



#create game_event database
class game_event(db.Model):
	game_id = db.StringProperty(required = True)
	game_type = db.StringProperty(required = True)

	#main player and possible teammate
	player_id = db.StringProperty(required = True) 
	player_teammate_id = db.StringProperty(required = True) 

	#opponent(s)
	opp_id = db.StringProperty(required = True) 
	
	#score information
	player_score =  db.IntegerProperty(required = True)
	opp_score =  db.IntegerProperty(required = True)
	
	#did the main player win?
	player_win = db.IntegerProperty(required = True)

	#scores normalized to 10 point scale
	player_score_z = db.FloatProperty(required = True)
	opp_score_z =  db.FloatProperty(required = True)
	
	#game date
	date = db.DateTimeProperty(auto_now_add = True)


class Scores(Handler):
	def get(self):
		user_name = users.get_current_user()
		self.render("scores.html", team_range = range(len(team_names)), team_names = team_names, logout_url=logout_url, user_nickname=user_name.nickname())

	def post(self):
		global team_scores

		team_scores = getScores(team_names, self)

		uploadData(prepData(team_names, team_scores))

		self.redirect("welcome")


class Logout(Handler):
	def get(self):
		self.render('log-out.html', login_url=users.create_login_url('/welcome'))



class Register(Handler):
	def get(self):
		user_name = users.get_current_user()
		self.render('register.html', logout_url=logout_url, user_nickname=user_name.nickname())

	def post(self):
		user_name = users.get_current_user()
		work_email = self.request.get('work_email')
		first_name = self.request.get('first_name')
		last_name = self.request.get('last_name')
		inputUserData(work_email, first_name, last_name, user_name)
		self.redirect("holder_log")

class Holder_log(Handler):
	def get(self):
		self.render('holder_log.html')

class Players(Handler):	
	def get(self):
		user_name = users.get_current_user()

		#pull list of registered users
		qry = Account.query().fetch()
		player_set = GetPlayers(qry)
		num_players=range(len(player_set))
		self.render("players.html", logout_url=logout_url, user_nickname=user_name.nickname(), num_players=num_players, player_set=player_set)

	def post(self):
		user_name = users.get_current_user()
		global team_names

		team_names = teamCheck(self.request.get_all('team_1'), self.request.get_all('team_2'))

		if team_names != "Error":
			team_names = [str(x) for x in team_names]
			self.redirect("scores")

		else:
			self.render("players.html", size_error = "There was something wrong with the teams you selected", logout_url=logout_url, user_nickname=user_name.nickname())



class Test(Handler):
	def get(self):
		user_name = users.get_current_user()
		# nickname = user_name.nickname()
		qry = Account.query().fetch()
		player_set = GetPlayers(qry)
		q = player_set

		num_players=range(len(player_set))

		self.render('tester.html', text=q, num_players=num_players, player_set=player_set)


application = webapp2.WSGIApplication([('/', Welcome),
									   ('/players', Players),
									   ('/scores', Scores),
									   ('/welcome', Welcome),
									   ('/log-out', Logout),
									   ('/register', Register),
									   ('/tester', Test),
									   ('/holder_log', Holder_log)],
									    debug=True)
