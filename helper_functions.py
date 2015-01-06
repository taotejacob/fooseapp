import random

###########################
####
#### Helper functions to check and format team names
####
##############################

def stringTolist(team):
	if type(team) == str:
		name = [team]
		return(name)
	else:
		return(team)

def teamSizer(team):
	team = stringTolist(team)
	size = len(team)

	if size > 0 and size < 3:
		return(team)
	else:
		return(False)

def teamNamer(team):
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
		user_list.append([str(players.first_last), str(players.username)])
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
		player_win = row.player_win
		player_score = row.player_score
		opp_score = row.opp_score
		date = row.date
		out = [game_id, game_type, player, player_2, opp, player_win, player_score, opp_score, date]
		games.append(out)

	return(games)

#########################
###
###  Stats Calculators
###
#########################

def type_def(n):
	out = ['1v1', '2v2', '1v2']
	return out[n-1]


#generate list of all players
def playerLister(gamesDB, n):
	playerlist = []
	game_type = type_def(n) #find game type

	#pull only opp id for 2v2 games
	if game_type == '2v2':
		for row in gamesDB:
			if row.game_type == '2v2':
				playerlist.append(str(row.opp_id))

	#for 1v1 & 1v2 pull only player_id for same game type
	else:
		for row in gamesDB:
			if row.game_type == game_type:
				playerlist.append(str(row.player_id))

	return list(set(playerlist))

#generate one player's opponent matrix
def playerMatrix(gamesDB, player_list, name, game_type):
	ngames = []

	for opponent in player_list:
		i = 0
		for row in gamesDB:

			#these conditionals deal with special case for 2v2
			if game_type == '2v2': 
				player_team = row.player_teammate_id ##player_teammate_id already combines players into team
				opp_team = row.opp_id
			else:
				player_team = row.player_id #player_id and player_teammate_id will be the same
				opp_team = teamNamer([row.opp_id]) ##for 1v2 need to split opp_id into each

			#add games within specific game type
			if (name == player_team) and (opponent in opp_team) and row.game_type == game_type:
				i = i + 1

		ngames.append(i)

	return ngames


#generate an opponent matrix for all players
def gameMatrix(gamesDB, player_list, n):
	ngames = []
	game_type = type_def(n)

	for player in player_list:
		ngames.append(playerMatrix(gamesDB, player_list, player, game_type))
	return(ngames)

#generate a players total point differential
def playerpointDiff(gamesDB, name, game_type):
	player_pts = 0
	opp_pts = 0

	for row in gamesDB:

		#for 2v2 need to check against teammate_id
		if game_type == '2v2':
			team_name = row.player_teammate_id
		else: 
			team_name = row.player_id

		#add up points
		if team_name == name:
			player_pts = player_pts + row.player_score_z
			opp_pts = opp_pts + row.opp_score_z

	return(player_pts - opp_pts)

#generate all player's total point differential
def pointDiff(gamesDB, player_list, game_type):
	point_diff = []

	for name in player_list:
		diff = playerpointDiff(gamesDB, name, game_type)
		point_diff.append(diff)
	return(point_diff)

#find number of games each player played
def gameSummer(gMatrix):
	ngames = [] #total games each player played
	for g in gMatrix:
		ngames.append(sum(g))
	return(ngames)

#calculate adjusted point differential
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

#calculate each player's win percentage
def winPct(gamesDB, player_list, gMatrix, ngames, game_type):

	win_pct = []

	for p in range(len(player_list)):
		win = 0
		for row in gamesDB:

			#for 2v2 check against teammate_id
			if game_type == '2v2':
				team_name = row.player_teammate_id
			else:
				team_name = row.player_id

			#add up wins
			if team_name == player_list[p] and row.game_type == game_type:
				win = win + row.player_win
		win_pct.append(float(win) / float(ngames[p]))

	return win_pct

#round numbers in a list to the n'th digit
def roundCleaner(mylist, n):
	newlist = []
	for i in mylist:
		i = round(float(i),n)
		newlist.append(i)
	return(newlist)

# #combine and sort multiple lists based on key list (which goes first)
# def statSorter(sort_key, playerlist, ngames, win_pct, gdiff, gdgadj, min_games):
# 	combine_list = sorted(zip(sort_key, playerlist, ngames, win_pct, gdiff, gdgadj), reverse=True)
	
# 	#remove records where # of games played was below 5
# 	combine_list_min = [i for i in combine_list if i[2] >= min_games]

# 	return combine_list_min

def p_scoreCalc(statdata_min):
	win_pct = zip(*statdata_min)[2]
	gdgadj = zip(*statdata_min)[4]

	win_dist = []
	gdg_dist = []

	for p in win_pct:
		a = float(max(win_pct) - p) / float(max(win_pct))
		win_dist.append(a)

	for g in gdgadj:
		minval = float(max(gdgadj) - min(gdgadj)) #control for 0 gdgadj

		if minval == 0:
			a = 0
		else:
			a = float(max(gdgadj) - g) / minval

		gdg_dist.append(a)

	pvalues = [x+y for x,y in zip(win_dist, gdg_dist)]

	# add p_score to begining of each list
	for i in range(len(statdata_min)):
		statdata_min[i] = [pvalues[i]] + list(statdata_min[i])

	output = sorted(statdata_min, reverse = False)

	return output

def mingameRemove(playerlist, ngames, win_pct, gdiff, gdgadj, min_games):
	statdata = zip(playerlist, ngames, win_pct, gdiff, gdgadj) #zip data together
	statdata_min = [i for i in statdata if i[1] >= min_games]  #remove records where <min games
	
	return statdata_min

def statsTable(gamesDB, gMatrix, playerlist, n):
	game_type = type_def(n)
	min_games = 5

	ngames = gameSummer(gMatrix)
	win_pct = winPct(gamesDB, playerlist, gMatrix, ngames, game_type)
	gdiff = pointDiff(gamesDB, playerlist, game_type)
	out = scoreDiffAdj(gMatrix, gdiff)
	gdg = out[0]
	gdgadj = out[1]

	statdata_min = mingameRemove(playerlist, ngames, roundCleaner(win_pct,2), roundCleaner(gdiff,2), roundCleaner(gdgadj,2), min_games) #remove players with < min_games

	#for case where not enough games
	if len(statdata_min) == 0:
		blank = [("-", "Not enough games", 0, 0, 0, 0)]
		return blank

	#for other cases, find p-values and sort
	else:
		statlist = p_scoreCalc(statdata_min) #calculate p_score & sort
		return statlist
		## 'p-score', 'playerName', 'Ngames', 'WinPct','PointDiff', 'AdjPoints'