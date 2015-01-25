import os
import jinja2
import webapp2
import random
import csv

from helper_functions import *
from bracket_functions import *

from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.api import mail


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))



########################################3
##
##
## Databases
##
##
########################################3

#create users database:
class Account(ndb.Model):
	username = ndb.StringProperty()
	email = ndb.StringProperty()
	work_email = ndb.StringProperty()
	first_name = ndb.StringProperty()
	last_name = ndb.StringProperty()
	first_last = ndb.StringProperty()
	game_dict1v1 = ndb.TextProperty()
	game_id_list1v1 = ndb.TextProperty()
	game_dict2v2 = ndb.TextProperty()
	game_id_list2v2 = ndb.TextProperty()

	win_streak1v1 = ndb.IntegerProperty()
	total_points1v1 = ndb.IntegerProperty()
	ranking1v1 = ndb.FloatProperty()
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


#######################
###
### Helper Functions
###
#######################

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class Handler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)


#used to delete erronious game records
def p_dict_update(p1v1dict, opponent, p_win, diff):

	p_dict = eval(p1v1dict)

	if opponent in p_dict:

		results = p_dict[opponent]

		results[0] = results[0] - 1
		results[1] = int(results[1] - p_win)
		results[2] = results[2] - diff

		p_dict[opponent] = results

	return p_dict

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



def uploadRoundResults(tourn_results):
	for game in tourn_results:
		scores = unpackPrep(game[1], game[0], "")

		for s in scores:
			data_prepped = prepData(game[0], s)

			#only upload to account if 1v1 (for now!)
			if data_prepped[0][1] == '1v1':
				for game_data in data_prepped:
					player_game_update(game_data)

			if data_prepped[0][1] == '2v2':
				for game_data in data_prepped:
					player_game_update2v2(game_data)

			uploadData(data_prepped)

#######################
###
### Web classes
###
#######################



class Mail(Handler):
	def get(self):

		message = mail.EmailMessage(sender="Foos Master <eabfoosball@gmail.com>",
		                            subject="Your Weekly Update")

		message.to = "<jacob.rosch@gmail.com>"
		message.body = """
		Dear Albert:

		Your example.com account has been approved.  You can now visit
		http://www.example.com/ and sign in using your Google Account to
		access new features.

		Please let us know if you have any questions.

		The example.com Team
		"""

		message.send()


		self.render('tester.html')



class Tester(Handler):
	def get(self):


		self.render('tester.html')



class GameDel(Handler):
	def get(self):

		self.render('gamedel.html')

	def post(self):
		DEL_ID = str(self.request.get('del_it'))

		gqry = db.GqlQuery("SELECT * FROM game_event WHERE game_id = :num", num=DEL_ID)

		for row in gqry:
			player = row.player_id
			opponent = row.opp_id
			p_win = row.player_win
			diff = row.player_score_z - row.opp_score_z

			qry = Account.query()

			if row.game_type == '1v1':
				for p in qry:
					if p.first_last == player:
						#remove from dictionaries
						p.dict1v1_sum = str(p_dict_update(p.dict1v1_sum, opponent, p_win, diff))
						p.dict1v1_t0 = str(p_dict_update(p.dict1v1_t0, opponent, p_win, diff))
						p.game_dict1v1 = str(p_dict_update(p.game_dict1v1, opponent, p_win, diff))

						#remove from game_id list
						game_id_list = eval(p.game_id_list1v1)
						game_id_list.remove(DEL_ID)
						p.game_id_list1v1 = str(game_id_list)

						p.put()

				db.delete(row)	

		self.render('gamedel.html', 
			data1 = "Deleted record with id: " + DEL_ID)



all_hold = []
players_tourn = []
ranks = [5, 4, 3, 2, 1, 6, 7, 8]


class TournPlayers(Handler):
	def get(self):

		#pull list of registered users
		qry = Account.query().fetch()
		player_set = GetPlayers(qry)
		num_players=range(len(player_set))

		self.render('bracket.html',
			num_players = num_players,
			player_set = player_set)

	def post(self):
		global players_tourn
		players_tourn = self.request.get_all('team_1')
		players_tourn = [str(i) for i in players_tourn]

		self.redirect('/_min/bracket')		



class Bracket(Handler):
	def get(self):
		global all_hold
		all_hold = []

		global players_tourn
		global ranks
		
		#sort players
		players_sorted = playerSort(players_tourn, ranks)

		#generate matchups
		matchups = findMatchups(players_sorted)
		#create score holder
		scores = ScoreHolder(matchups[1])
		#print HTML & render it
		inputHTML = genScoreForm(matchups, scores)			


		self.render('bracket2.html',
			inputHTML = inputHTML,
			matchups = matchups,
			round_name = "Round " + str(len(all_hold)+1))

	def post(self):

		buy_players = eval(self.request.get('buy_players'))
		round_matchups = eval(self.request.get('round_matchups'))
		
		#find and update scores
		round_scores = eval(self.request.get('round_scores'))
		round_scores = round_scores_update(round_matchups, round_scores, self)

		#find results so far
		tourn_results = genTourn_results(round_matchups, round_scores)
		
		inputHTML = genScoreForm(round_matchups, round_scores)

		#if they haven't entered all of the round scores
		if len(round_scores) != len(tourn_results):
			self.render('bracket2.html', 
				inputHTML = inputHTML,
				matchups = round_matchups,
				round_name = "Round " + str(len(all_hold)+1))

		#if all round scores are entered
		else:
			uploadRoundResults(tourn_results)								#upload results into database

			all_hold.append(tourn_results)
			
			playeres_next_round = getWinners(tourn_results) + buy_players	#find players for next round	
			matchups_next_round = findMatchups(playeres_next_round)			#create matchups
			scores_next_round = ScoreHolder(matchups_next_round[1])			#create score holder
			
			#if this is not the last round...
			if len(playeres_next_round) > 1:
				#print HTML & render it
				inputHTML = genScoreForm(matchups_next_round, scores_next_round)

				self.render('bracket2.html',
					inputHTML = inputHTML,
					matchups = matchups_next_round,
					round_name = "Round " + str(len(all_hold)+1))
			
			#if this is the last round print different HTML
			else:
				self.render('bracket2.html',
					inputHTML = ['Congratulations', playeres_next_round[0], "!"], 
					round_name = "The Winner")








application = webapp2.WSGIApplication([('/_min/mail', Mail),
									   ('/_min/tester', Tester),
									   ('/_min/tourn', TournPlayers),
									   ('/_min/bracket', Bracket),
									   ('/_min/gamedel', GameDel)],
									    debug=True)
