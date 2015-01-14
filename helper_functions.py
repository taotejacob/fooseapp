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

def getGameId():
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
		user_list.append(str(players.first_last))
	return(user_list)


def tieCheck(game_scores):
	check = []

	for game in game_scores:
		if len(set(game)) == 1:
			check.append(1)
		else:
			check.append(0)

	if sum(check) > 0:
		return True
	else:
		return False



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

#takes data from userinput and formats into usable score information
def getScores3(team_names, self):
	input_scores = []
	game_scores = []
	team_names = eval(self.request.get('team_names'))

	for n in range(len(team_names)):
		score = "score_" + str((n+1))
		input_scores.append(str(self.request.get(score)))

	# upack scores when multiple games entered	
	for n in input_scores:
		scores = n.split('-')
		scores = [int(x) for x in scores]
		game_scores.append(scores)

	# zip scores together
	if len(team_names) < 3:
		output = zip(game_scores[0], game_scores[1])

	else:
		output = zip(game_scores[0], game_scores[1], game_scores[2])

	if validateScores(input_scores, output):
		return validateScores(input_scores, output)
	else:
		return output


def validateScores(input_scores, output):
	error = None
	##validate scores
	if len(set([len(x) for x in input_scores])) != 1:	#Uneven # of scores
		error = "You input the wrong number of scores"	

	if tieCheck(output):							#game ended in tie
		error = "This isn't soccer, we don't accept tie games"

	if max(sum(output, ())) > 9:					#score over 9
		error = "No scores above 9 allowed"

	return error


#############################
###
###   generator
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

#round numbers in a list to the n'th digit
def roundCleaner(mylist, n):
	newlist = []
	for i in mylist:
		i = round(float(i),n)
		newlist.append(i)
	return(newlist)

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

	pvalues = [(x+y)/2 for x,y in zip(win_dist, gdg_dist)]
	pvalues = roundCleaner(pvalues, 3)

	# add p_score to begining of each list
	for i in range(len(statdata_min)):
		statdata_min[i] = [pvalues[i]] + list(statdata_min[i])

	output = sorted(statdata_min, reverse = False)

	return output

def mingameRemove(playerlist, ngames, win_pct, gdiff, gdgadj, min_games):
	statdata = zip(playerlist, ngames, win_pct, gdiff, gdgadj) #zip data together
	statdata_min = [i for i in statdata if i[1] >= min_games]  #remove records where <min games
	
	return statdata_min



##############################
###
###
### Standings Database stuff
###
##############################


#function to update record in dictionary
def player_dict_update(player_dict, prepped_data):
	opp = prepped_data[4]				#find opp name

	data = [0,0,0.0]					#holder for game data

	if opp in player_dict.keys():		#if opponent exists, pull out record
		#some holder BS
		data[0] = player_dict[opp][0]	
		data[1] = player_dict[opp][1]
		data[2] = player_dict[opp][2]

		data[0] = data[0] + 1 						#increment games played
		data[1] = data[1] + prepped_data[7] 		#add 0 if lost, 1 if won
		data[2] = round(data[2] + prepped_data[8] - prepped_data[9],4) #update score differential

		player_dict[opp] = data         #update record in dict

	else:
		player_dict[opp] = [1, prepped_data[7], round(prepped_data[8] - prepped_data[9],4)]  #create new record if no record exists

	return(player_dict)


def player_dict_update2v2(player_dict, prepped_data):

	team_name = prepped_data[3]
	opp_name = prepped_data[4]
	win = prepped_data[7]
	dif = prepped_data[8] - prepped_data[9]

	if team_name in player_dict.keys():
		if opp_name in player_dict[team_name]:
			##add stuff together
			dat = player_dict[team_name][opp_name]
			dat[0] = dat[0] + 1
			dat[1] = dat[1] + win
			dat[2] = dat[2] + dif
			player_dict[team_name][opp_name] = dat
		else:
			player_dict[team_name][opp_name] = [1,win,dif]

	else:
		player_dict[team_name] = {opp_name:[1,win,dif]}

	return player_dict


def get1v1Standings(qry):

	pname = []
	pdicts = []

	for row in qry:
		pname.append(str(row.first_last))
		pdicts.append(str(row.game_dict1v1))

	return [pname, pdicts]

def get2v2Standings(qry):

	pname = []
	pdicts = []

	for row in qry:
		pname.append(str(row.first_last))
		pdicts.append(str(row.game_dict2v2))

	return [pname, pdicts]

def get2v2TeamNames(pname, pdict):
	nplayers = range(len(pname))

	teams2v2 = []

	for n in nplayers:
		tms = eval(pdict[n]).keys()
		teams2v2.extend(tms)

	output = list(set(teams2v2))
	output.remove('Ghost')

	return output


def MatrixCalculator2v2(pname, pdicts, teamnames):
	nplayers = range(len(pname))
	nteams = range(len(teamnames))

	gMatrix = []	#holder for game matrix - games played against each player
	wMatrix = []	#holder for win matrix - wins against each player
	pMatrix = []	#holder for point matrix - point diff against each player

	hgames = {}
	hwins = {}
	hpoints = {}

	for n in nplayers:
		player_dict = eval(pdicts[n])  #select right player dictionary

		for team in teamnames:		   #did player play on team_1

			nPGames = []
			nWGames = []
			win_pct = []
			pPoints = []

			if team in player_dict.keys():  #if yes player was on team
				for opp in teamnames:   #check values of each opponent
					if opp in player_dict[team].keys(): #did this team play this opponent?
						nPGames.append(player_dict[team][opp][0])
						nWGames.append(player_dict[team][opp][1])
						pPoints.append(player_dict[team][opp][2])
					else:
						nPGames.append(0)
						nWGames.append(0)
						pPoints.append(0)

				hgames[team] = nPGames
				hwins[team] = nWGames
				hpoints[team] = pPoints

	for team in teamnames:
		gMatrix.append(hgames[team])
		wMatrix.append(hwins[team])
		pMatrix.append(hpoints[team])

	return [gMatrix, wMatrix, pMatrix]
			
def newStatTable2v2(pname, pdicts):

	teamnames = get2v2TeamNames(pname, pdicts)

	MMatrix2v2 = MatrixCalculator2v2(pname, pdicts, teamnames)
	OutComes2v2 = WinPtsCalculator(MMatrix2v2)

	min_games = 0

	playerlist = teamnames
	ngames = [sum(i) for i in MMatrix2v2[0]]
	win_pct = OutComes2v2[0]
	gdiff = OutComes2v2[1]
	out = scoreDiffAdj(MMatrix2v2[0], gdiff)
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


def MatrixCalculator(pname, pdicts):

	## number of players
	nplayers = range(len(pname))
			
	gMatrix = []	#holder for game matrix - games played against each player
	wMatrix = []	#holder for win matrix - wins against each player
	pMatrix = []	#holder for point matrix - point diff against each player


	##find gMatrix, wMatrix, pMatrix for each player
	for n in nplayers:
		player_dict = eval(pdicts[n])

		nPGames = []
		nWGames = []
		win_pct = []
		pPoints = []

		for player in pname:
			if player in player_dict.keys():
				nPGames.append(player_dict[player][0])
				nWGames.append(player_dict[player][1])
				pPoints.append(player_dict[player][2])
			else:
				nPGames.append(0)
				nWGames.append(0)
				pPoints.append(0)

		gMatrix.append(nPGames)
		wMatrix.append(nWGames)
		pMatrix.append(pPoints)

	return [gMatrix, wMatrix, pMatrix]

def WinPtsCalculator(MMatrix):

	## number of players
	nplayers = range(len(MMatrix[0][0]))
	gMatrix = MMatrix[0]
	wMatrix = MMatrix[1]
	pMatrix = MMatrix[2]
	##find Win Pct & Point Diff for each player
	pointDiff = []
	win_pct = []

	for n in nplayers:
		wins = sum(wMatrix[n])
		tgam = sum(gMatrix[n])

		if tgam > 0:
			pct = float(wins)/float(tgam)
			win_pct.append(pct)

		else:
			win_pct.append(0)

		pointDiff.append(sum(pMatrix[n]))

	return [win_pct, pointDiff]

def newStatTable(pname, pdicts):

	MMatrix = MatrixCalculator(pname, pdicts)
	OutComes = WinPtsCalculator(MMatrix)

	min_games = 5

	playerlist = pname
	ngames = [sum(i) for i in MMatrix[0]]
	win_pct = OutComes[0]
	gdiff = OutComes[1]
	out = scoreDiffAdj(MMatrix[0], gdiff)
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




#####################################3
###
###   CRON Job Functions
###
######################################

#prep statlist data for entry into weekly standings database
def prepforWeekly(statlist):
	output = zip(*statlist)
	pscore = list(sorted(zip(output[0], output[1]))[0])
	games = list(sorted(zip(output[2], output[1]), reverse=True)[0])
	winner = list(sorted(zip(output[3], output[1]), reverse=True)[0])
	points = list(sorted(zip(output[5], output[1]), reverse=True)[0])
	return [pscore, games, winner, points]


#format data query from weekly standings database
def getWeeklyStandings(qry):
	output = []
	for row in qry:
		output.append(eval(row.mvp1v1))
		output.append(eval(row.games1v1))
		output.append(eval(row.winner1v1))
		output.append(eval(row.points1v1))
		output.append(eval(row.mvp2v2))
		output.append(eval(row.games2v2))
		output.append(eval(row.winner2v2))
		output.append(eval(row.points2v2))
	return output