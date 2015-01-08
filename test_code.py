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

c1 = prepData(a2, b2)

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



a3 = ["jacob", "mike and bill"]
b3 = [5, 4, 2]

a2 = ["jacob and jeff", "mike and tyler"]
b2 = [9, 4]

a1 = ["jacob", "jeff"]
b1 = [5, 3]

c1 = prepData(a2, b2)

a3 = ["jacob and jeff", "Rob and tyler"]
b3 = [9, 3]

c3 = prepData(a3, b3)

Jacob_dict = {}
print c1




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

print c1

#takes data and runs update function
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


a = {'jacob c and Jacob T': {'Jacob F and asdf f': [1, 1, 2.0], 'Bob A and Alex B': [1, 0, -5.0]}, 'Ghost': [0, 0, 0], 'Alex B and jacob c': {'Jacob F and asdf f': [1, 1, 3.75]}}

print a

print a.keys()

print [0]*3