import random
from helper_functions import *


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



a3 = ["jacob", "mike and bill"]
b3 = [5, 4, 2]

a2 = ["jacob and jeff", "mike and tyler"]
b2 = [9, 4]

a1 = ["jacob", "jeff"]
b1 = [5, 3]

c1 = prepData(a1, b1)

players = ["jacob", "mike", "jeff", "bill", "tyler"]
holders = [[0,0,0.0]]*len(players)

Jacob_dict = dict(zip(players, holders))
Jeff_dict = dict(zip(players, holders))
Bob_dict = {}

print c1

def player_dict_update(player_dict, prepped_data):
	opp = prepped_data[4]

	data = [0,0,0.0]

	if opp in player_dict.keys():
		data[0] = player_dict[opp][0]
		data[1] = player_dict[opp][1]
		data[2] = player_dict[opp][2]

		data[0] = data[0] + 1 #increment games played
		data[1] = prepped_data[7] #add 0 if lost, 1 if won
		data[2] = data[2] + prepped_data[8] - prepped_data[9]

		player_dict[opp] = data

	else:
		player_dict[opp] = [1, prepped_data[7], prepped_data[8] - prepped_data[9]]

	return(player_dict)

def player_game_update(prepped_data):
	qry = Account.query(Account.first_last == prepped_data[2])
	player_dict = eval(qry.game_dict)
	player_dict = player_dict_update(player_dict, prepped_data)
	qry.game_dict = player_dict
	qry.put()

a = [3,4,6]

print sum(a)


