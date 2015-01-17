import os
import jinja2
import webapp2
import random
import csv

from helper_functions import *

from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.api import users


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

#global variables
team_names = []
game_type = ""
logout_url = users.create_logout_url('/log-out')
login_url = users.create_login_url('/welcome')




########################################3
##
##
## Databases
##
##
########################################3

#create database for weekly standings
class WeeklyStandings(ndb.Model):
	mvp1v1 = ndb.StringProperty(required = True)
	games1v1 = ndb.StringProperty(required = True)
	winner1v1 = ndb.StringProperty(required = True)
	points1v1 = ndb.StringProperty(required = True)
	mvp2v2 = ndb.StringProperty(required = True)
	games2v2 = ndb.StringProperty(required = True)
	winner2v2 = ndb.StringProperty(required = True)
	points2v2 = ndb.StringProperty(required = True)
	date = ndb.DateTimeProperty(auto_now_add = True)
	winstreak1v1 = ndb.StringProperty()


#create users database:
class Account(ndb.Model):
	username = ndb.StringProperty()
	#userid = ndb.FloatProperty()
	email = ndb.StringProperty()
	work_email = ndb.StringProperty()
	first_name = ndb.StringProperty()
	last_name = ndb.StringProperty()
	first_last = ndb.StringProperty()

	#dictionaries to hold records
	game_dict1v1 = ndb.TextProperty()
	game_id_list1v1 = ndb.TextProperty()
	game_dict2v2 = ndb.TextProperty()
	game_id_list2v2 = ndb.TextProperty()

	#1v1 ranking info
	win_streak1v1 = ndb.IntegerProperty()
	total_points1v1 = ndb.IntegerProperty()
	ranking1v1 = ndb.FloatProperty()

	#weekly dictionaries
	dict1v1_t0 = ndb.TextProperty()
	dict1v1_sum = ndb.TextProperty()



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






####################
##
##
## HELPER FUNCTIONS
##
##
###################

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class Handler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)


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
				first_last = first_name + " " + last_name[0],
				game_dict1v1 = '{ "Ghost":[0,0,0] }',
				game_id_list1v1 = '["."]',
				game_dict2v2 = '{ "Ghost":[0,0,0] }',
				game_id_list2v2 = '["."]',
				win_streak1v1 = 0,
				total_points1v1 = 0,
				ranking1v1 = 450,
				dict1v1_t0 = '{ "Ghost":[0,0,0] }',
				dict1v1_sum = '{ "Ghost":[0,0,0] }'
				)
	p.put()



#takes data and runs update function for 1v1 games
def player_game_update(prepped_data):
	for user in Account.query(Account.first_last == prepped_data[2]):       #pull user from db
		if user:														    #check if user exists

			##total dictionary update
			player_dict = eval(user.game_dict1v1)							#get dictionary
			player_dict = player_dict_update(player_dict, prepped_data)		#update entry w/ prepped data
			
			##this week's dict update
			player_dict_t0 = eval(user.dict1v1_t0)							
			player_dict_t0 = player_dict_update(player_dict_t0, prepped_data)

			##add this week's dict to total
			player_dict_sum = eval(user.dict1v1_sum)							
			player_dict_sum = player_dict_update(player_dict_sum, prepped_data)

			##save both dict's back into db
			user.game_dict1v1 = str(player_dict)							
			user.dict1v1_t0 = str(player_dict_t0)
			user.dict1v1_sum = str(player_dict_sum)

			#winstreak update
			user.win_streak1v1 = (user.win_streak1v1 + 1)* prepped_data[7]

			#update total points
			user.total_points1v1 = user.total_points1v1 + prepped_data[5] + prepped_data[6]

			##game id list update
			player_game_id_list = eval(user.game_id_list1v1)				#pull list of game ids
			player_game_id_list.append(prepped_data[0])						#append latest game id
			user.game_id_list1v1 = str(player_game_id_list)					#save back in db

			user.put()														#put in db


#takes data and runs update function for 2v2 games
def player_game_update2v2(prepped_data):
	for user in Account.query(Account.first_last == prepped_data[2]):       #pull user from db
		if user:														    #check if user exists

			##dictionary update
			player_dict = eval(user.game_dict2v2)							#get dictionary
			player_dict = player_dict_update2v2(player_dict, prepped_data)		#update entry w/ prepped data
			user.game_dict2v2 = str(player_dict)							#save back in db


			##game id list update
			player_game_id_list = eval(user.game_id_list2v2)				#pull list of game ids
			player_game_id_list.append(prepped_data[0])						#append latest game id
			user.game_id_list2v2 = str(player_game_id_list)					#save back in db

			user.put()	

#takes standings data and puts it into the standings database
def standingPut(statlist1v1, statlist2v2):
	singles = prepforWeekly(statlist1v1)
	doubles = prepforWeekly(statlist2v2)

	qry = ndb.gql("SELECT * FROM Account ORDER BY win_streak1v1 DESC LIMIT 1")

	for row in qry:
		longest_streak_name = str(row.first_last)
		longest_streak_record = row.win_streak1v1

	p = WeeklyStandings(mvp1v1 = str(singles[0]),
				games1v1 = str(singles[1]),
				winner1v1 = str(singles[2]),
				points1v1 = str(singles[3]),
				mvp2v2 = str(doubles[0]),
				games2v2 = str(doubles[1]),
				winner2v2 = str(doubles[2]),
				points2v2 = str(doubles[3]),
				winstreak1v1 = str([longest_streak_name, longest_streak_record])
				)
	p.put()



#####################################
##
##  Webpage handlers
##
#####################################


class PublicHome(Handler):
	def get(self):
		qry = ndb.gql("SELECT * FROM WeeklyStandings ORDER BY date DESC LIMIT 1")
		weeklystand = getWeeklyStandings(qry)

		self.render('publichome.html', 
			data = weeklystand)


class About(Handler):
	def get(self):
		self.render('about.html')


class Welcome(Handler):
	def get(self):
		user_name = users.get_current_user()

		#Test if user is registered
		q = Account.query(Account.username == user_name.nickname()).count()
		if q < 1:
			self.redirect('/auth/register')



		self.render("welcome.html", 
			logout_url=logout_url, 
			user_nickname=user_name.nickname())


class Players(Handler):	
	def get(self):
		user_name = users.get_current_user()

		#pull list of registered users
		qry = Account.query().fetch()
		player_set = GetPlayers(qry)
		num_players=range(len(player_set))

		
		self.render("players.html", 
			logout_url=logout_url, 
			user_nickname=user_name.nickname(), 
			num_players=num_players, 
			player_set=player_set)

	def post(self):
		user_name = users.get_current_user()
		global team_names

		team_names = teamCheck(self.request.get_all('team_1'), self.request.get_all('team_2'))

		if team_names != "Error":
			team_names = [str(x) for x in team_names]
			self.redirect("/auth/scores")

		else:
			self.render("players.html", 
				size_error = "There was something wrong with the teams you selected", 
				logout_url=logout_url, 
				user_nickname=user_name.nickname())


class Scores(Handler):
	def get(self):
		global team_names

		user_name = users.get_current_user()

		self.render("scores.html", 
			team_range = range(len(team_names)), 
			team_names = team_names, 
			logout_url=logout_url,
			user_nickname=user_name.nickname())

	def post(self):
		global team_names

		team_scores = getScores3(team_names, self) #return [(4-3), (5-6)] or "Error"

		#if error tell player to try again
		if type(team_scores) == type(''):
			self.render("scores.html", 
				team_range = range(len(eval(self.request.get('team_names')))), 
				team_names = eval(self.request.get('team_names')), 
				logout_url=logout_url,
				error = "<i>" + team_scores + "</i><br><br>")

		#else input the data
		else:
			for game in team_scores:
				data_prepped = prepData(team_names, game)

				#only upload to account if 1v1 (for now!)
				if data_prepped[0][1] == '1v1':
					for game_data in data_prepped:
						player_game_update(game_data)

				if data_prepped[0][1] == '2v2':
					for game_data in data_prepped:
						player_game_update2v2(game_data)

				uploadData(data_prepped)

			self.redirect("/auth/welcome")


class Standings(Handler):
	def get(self):
		user_name = users.get_current_user()

		
		## get names and dictionaries
		qry = Account.query()

		values = get1v1Standings_sum(qry) 					#uses records from last 2 weeks only
		statlist1v1 = newStatTable(values[0], values[1])
		nplayers1v1 = range(len(statlist1v1))

		values2v2 = get2v2Standings(qry)
		statlist2v2 = newStatTable2v2(values2v2[0], values2v2[1])
		nplayers2v2 = range(len(statlist2v2))


		self.render('standings.html',
			nplayers1v1 = nplayers1v1,
			statlist1v1 = statlist1v1,
			nplayers2v2 = nplayers2v2,
			statlist2v2 = statlist2v2,
			# nplayers1v2 = nplayers1v2,
			# statlist1v2 = statlist1v2,
			logout_url=logout_url, 
			user_nickname=user_name.nickname())


class Logout(Handler):
	def get(self):
		self.render('log-out.html', login_url=users.create_login_url('/welcome'))


class Holder_log(Handler):
	def get(self):
		self.render('holder_log.html')


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
		self.redirect("/auth/holder_log")


class Output(Handler):
	def get(self):
		players = db.GqlQuery("SELECT * FROM game_event WHERE player_win = 1 ORDER BY date DESC LIMIT 10")
		data = output_make(players)
		n_rows = range(len(data))

		self.render('output.html', data = data, n_rows=n_rows)


class Download1v1(Handler):
	def get(self):
		players = db.GqlQuery("SELECT * FROM game_event WHERE game_type = '1v1' ORDER BY date DESC")
		self.response.headers['Content-Type'] = 'text/csv'
		self.response.headers['Content-Disposition'] = 'attachment; filename=Singles.Games.csv'
		writer = csv.writer(self.response.out)
		writer.writerow(['Game ID', 'Type', 'Player', 'Teammate', 'Opponent', 'Player Win?', 'Player Score', 'Opp Score', 'Date'])
		
		for row in players:
			writer.writerow([row.game_id, row.game_type, row.player_id, row.player_teammate_id, row.opp_id, row.player_win, row.player_score, row.opp_score, row.date])


class Download2v2(Handler):
	def get(self):
		players = db.GqlQuery("SELECT * FROM game_event WHERE game_type = '2v2' ORDER BY date DESC")
		self.response.headers['Content-Type'] = 'text/csv'
		self.response.headers['Content-Disposition'] = 'attachment; filename=Doubles.Games.csv'
		writer = csv.writer(self.response.out)
		writer.writerow(['Game ID', 'Type', 'Player', 'Teammate', 'Opponent', 'Player Win?', 'Player Score', 'Opp Score', 'Date'])
		
		for row in players:
			writer.writerow([row.game_id, row.game_type, row.player_id, row.player_teammate_id, row.opp_id, row.player_win, row.player_score, row.opp_score, row.date])


class WeeklyUpdate(Handler): #update singles scores and front page standings
	def get(self):
		qry = Account.query()

		values = get1v1Standings_t0(qry) 					#get singles standings from prior week
		statlist1v1 = newStatTable(values[0], values[1])

		values2v2 = get2v2Standings(qry) 					#get doubles standings from (all time)
		statlist2v2 = newStatTable2v2(values2v2[0], values2v2[1])

		standingPut(statlist1v1, statlist2v2) 				#update database

		for user in qry: 
			user.dict1v1_sum = user.dict1v1_t0				#more last weeks scores into sum		
			user.dict1v1_t0 = '{ "Ghost":[0,0,0] }'			#set last week's scores to zero
			user.put()




application = webapp2.WSGIApplication([('/', PublicHome),
									   ('/about', About),
									   ('/auth/players', Players),
									   ('/auth/scores', Scores),
									   ('/auth/welcome', Welcome),
									   ('/auth/', Welcome),
									   ('/auth/log-out', Logout),
									   ('/auth/register', Register),
									   ('/auth/standings', Standings),
									   ('/auth/output', Output),
									   ('/auth/holder_log', Holder_log),
									   ('/auth/download1v1', Download1v1),
									   ('/auth/download2v2', Download2v2),
									   ('/tasks/task1', WeeklyUpdate)],
									    debug=True)