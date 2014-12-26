import random

###########################
####
#### Helper functions to check and format team names
####
##############################

def stringTolist (team):
	if type(team) == str:
		name = [team]
		return(name)
	else:
		return(team)

def teamSizer (team):
	team = stringTolist(team)
	size = len(team)

	if size > 0 and size < 3:
		return(team)
	else:
		return(False)

def teamNamer (team):
	size = len(team)
	if size == 2:
		return [(team[0] + " and " + team[1])]
	elif str(team).find(" and ") > 0:
		return str(team[0]).split(" and ")
	else:
		return team

def teamCheck(team_1, team_2):
	#global team_names
	if team_2[-1] == "":
		del team_2[-1]

	team_1 = teamSizer(team_1)
	team_2 = teamSizer(team_2)

	if team_1 and team_2 and set(team_1).intersection(team_2) == set([]):
		players = len(team_1 + team_2)

		if players == 4:
			team_names = teamNamer(team_1) + teamNamer(team_2)
		else:
			team_names = (team_1 + team_2)

		return(team_names)

	else:
		return("Error")

def getGameId ():
	number = round(random.random()*10000000,0)
	game_id = str(number)
	return game_id




###################################
####
#### Helper functions for scores
####
###################################





#Registration functions
def GetPlayers(qry):
	user_list = []
	for players in qry:
		user_list.append(str(players.username))
	return(user_list)






#functions to convert scores to standardized base
def score_standardize (score, max_score, base = 10):
	score_z = float(score) * float(base) / float(max_score)
	return round(score_z, 2)

def getScoreStd(team_scores):
	max_score = max(team_scores)
	team_scores_z = []
	
	for i in range(len(team_scores)):
		team_scores_z.append(score_standardize(team_scores[i], max_score))

	return(team_scores_z)

def findWinner (team_scores):
	w = team_scores.index(max(team_scores))
	winner = [0]*len(team_scores)
	winner[w] = 1
	return(winner)

def getGameType (team_names):
	players = []
	for team in team_names:
		t = [team]
		players.extend(teamNamer(t))

	n_players = len(players)

	if n_players == 2:
		return "1v1"
	elif n_players == 3:
		return "1v2"
	else:
		return "2v2"


##combine player info into lists 
def prepData(team_names, team_scores):
	game_id = getGameId()
	game_type = getGameType(team_names)
	winner = findWinner(team_scores)
	team_scores_z = getScoreStd(team_scores)

	df = []

	for team in team_names:
		for player in teamNamer(stringTolist(team)):
			i = team_names.index(team)

			if game_type == "1v2":
				opponent = teamNamer(team_names[:i]+team_names[i+1:])[0]
			else:
				opponent = (team_names[:i]+team_names[i+1:])[0]

			df.append([game_id,  									#game id
					   game_type, 									#game type
					   player,										#main player
					   team, 										#player's team name
					   opponent,									#opponent team
					   team_scores[i],								#player score
					   max(team_scores[:i]+team_scores[i+1:]),		#opponent score
					   winner[i],									#win?
					   team_scores_z[i],							#player z_score
					   max(team_scores_z[:i]+team_scores_z[i+1:])	#opponent z_score
					   ])

	return(df)

def getScores(team_names, self):
	team_scores = []
	
	for n in range(len(team_names)):
		score = "score_" + str((n+1))
		team_scores.append(self.request.get(score))

	team_scores = [int(x) for x in team_scores]

	return team_scores



###############################
####
####  functions for calaculating results
####
###############################

def findWins(dataset, player):
	wins = 0.0
	for row in dataset:
		if row.player_id == player:
			wins = wins + row.player_win
	return wins

def findGames(dataset, player):
	games = 0.0
	for row in dataset:
		if row.player_id == player:
			games = games + 1
	return games

def findWinPct(dataset, player):
	wins = findWins(dataset, player) 
	games = findGames(dataset,player)

	if games == 0:
		return 0
	else:
		return round(wins/games,2)

def winSort(results):
	return sorted(results, key = lambda results: results[1], reverse = True)

def winRank(dataset):
	players = []
	for row in dataset:
		players.append(row.player_id)
	players = set([str(x) for x in players])

	results = []
	for player in players:
		results.append([player,findWinPct(dataset, player)])		
	return winSort(results)


def gameSummer(players):

	games = []
	i = 0

	for row in players:
		if row.player_win == 1:		
			player_team = str(row.player_teammate_id)
			opp_team = str(row.opp_id)
			score = str(row.player_score) + " - " + str(row.opp_score)
			out = [player_team, opp_team, score, i]
			games.append(out)
			
			if i > 0 and games[i][:3] == games[i - 1][:3]:
				games[i][3] = i - 1

			i = i + 1		

	games = set(map(tuple, games)) #remove duplicates
	games = sorted(games, key = lambda x: x[3], reverse = False) #sort

	return map(list,games)

#############################
###
###  output generator
###
#############################

def output_make(players):
	games = []

	for row in players:
		game_id = row.game_id
		game_type = row.game_type
		player = row.player_id
		player_2 = row.player_teammate_id
		opp = row.opp_id
		player_score = row.player_score
		opp_score = row.opp_score
		date = row.date
		out = [game_id, game_type, player, player_2, opp, player_score, opp_score, date]
		games.append(out)

	return(games)

#########################
###
###  Stats Calculators
###
#########################

def playerLister(gamesDB):
	playerlist = []
	for row in gamesDB:
		playerlist.append(str(row.player_id))
	return list(set(playerlist))


def playerMatrix(gamesDB, player_list, name):
	ngames = []
	for player in player_list:
		i = 0
		for row in gamesDB:
			if row.player_id == name and row.opp_id == player:
				i = i + 1
		ngames.append(i)
	return(ngames)

def gameMatrix(gamesDB, player_list):
	ngames = []
	for player in player_list:
		ngames.append(playerMatrix(gamesDB, player_list, player))
	return(ngames)

def playerpointDiff(gamesDB, name):
	player_pts = 0
	opp_pts = 0

	for row in gamesDB:
		if row.player_id == name:
			player_pts = player_pts + row.player_score_z
			opp_pts = opp_pts + row.opp_score_z

	return(player_pts - opp_pts)

def pointDiff(gamesDB, player_list):
	point_diff = []
	for name in player_list:
		diff = playerpointDiff(gamesDB, name)
		point_diff.append(diff)
	return(point_diff)

def gameSummer(gMatrix):
	ngames = [] #total games each player played
	for g in gMatrix:
		ngames.append(sum(g))
	return(ngames)

def scoreDiffAdj(gMatrix, gdiff):

	ngames = gameSummer(gMatrix)

	gdg = [] #each players point differential per game played
	for g in range(len(gdiff)):
		if gdiff[g] == 0 or ngames[g] == 0:
			out = 0
		else:
			out = float(gdiff[g])/float(ngames[g])
		gdg.append(out)

	adjgdg = [] #adj point differential
	for p in range(len(gdg)):
		gameShare = []
		for g in range(len(gdiff)):
			if ngames[p] > 0:
				out = float(gMatrix[p][g]) / float(ngames[p])
				out = out * float(gdg[g])
			else:
				out = 0
			gameShare.append(out)
		adjgdg.append(gdg[p]+sum(gameShare))

	output = [gdg, adjgdg]
	return(output)

def winPct(gamesDB, player_list, gMatrix, ngames):

	win_pct = []

	for p in range(len(player_list)):
		win = 0
		for row in gamesDB:
			if row.player_id == player_list[p]:
				win = win + row.player_win
		win_pct.append(float(win) / float(ngames[p]))

	return win_pct

def roundCleaner(mylist, n):
	newlist = []
	for i in mylist:
		i = round(float(i),n)
		newlist.append(i)
	return(newlist)

def statSorter(playerlist, ngames, win_pct, gdiff, gdgadj):
	combine_list = sorted(zip(win_pct, playerlist, ngames, gdiff, gdgadj), reverse=True)
	return combine_list

