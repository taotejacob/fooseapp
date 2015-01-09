		############
		###Function to give everyone game_dict1v1
		############		

		for user in Account.query():
		    user.game_dict1v1 = "{ 'Ghost':[0,0,0] }"
		    user.put()

		###########    
		##Function to add data into new account dictionaries
        ###########

		gamesDB = db.GqlQuery("SELECT * FROM game_event WHERE game_type = '1v1' AND player_win = 1")

		data1 = []

		for row in gamesDB:
			ppplayers = [str(row.player_id), str(row.opp_id)]
			ssscores = [row.player_score_z, row.opp_score_z]
			prepped_data = prepData(ppplayers, ssscores)

			for gme in prepped_data:
				player_game_update(gme)

###################


		# ##create game_id_list1v1
		# for user in Account.query():
		#     user.game_id_list1v1 = '["."]'

		#     user.game_dict2v2 = '{"Ghost" : [0,0,0]}'
		#     user.game_id_list2v2 = '["."]'

		#     user.put()

		# ##add 2v2 games to account db
		# gamesDB = db.GqlQuery("SELECT * FROM game_event WHERE game_type = '2v2' AND player_win = 1")

		# data1 = []
		# id_val = []

		# for row in gamesDB:
		# 	ppplayers = [str(row.player_teammate_id), str(row.opp_id)]
		# 	ssscores = [row.player_score_z, row.opp_score_z]

		# 	#check if game has been entered
		# 	if row.game_id in id_val:
		# 		1+1
		# 	else:
		# 		prepped_data = prepData(ppplayers, ssscores)

		# 		for gme in prepped_data:
		# 			player_game_update2v2(gme)

		# 	id_val.append(row.game_id)





#function to get user names
def GetPlayers2(qry):
	user_list = []
	for players in qry:
		user_list.append((str(players.username), str(players.first_last)))

	return user_list

#create 'first_last' for all users
for user in Account.query():
    user.first_last = user.first_name + " " + user.last_name[0]
    user.put()


#create dictionary between nickname and first_last
qry = Account.query().fetch()
player_set = GetPlayers2(qry)
player_dict = dict(player_set)

#pull game database
gamesDB = db.GqlQuery("SELECT * FROM game_event ORDER BY date DESC")

#for each row in database replace player id, opp id, player teammate id, with first_last
for row in gamesDB:
	if row.player_id in player_dict.keys():	
		row.player_id = player_dict[str(row.player_id)]

	if str(row.player_teammate_id) in player_dict.keys():
		row.player_teammate_id = player_dict[str(row.player_teammate_id)]

	if str(row.opp_id) in player_dict.keys():
		row.opp_id = str(player_dict[row.opp_id])

	if str(row.game_type) == '2v2':
		team = teamNamer([row.player_teammate_id])
		h = []

		for i in team:
			if i in player_dict.keys():
				h.append(player_dict[i])
			else:
				h.append(i)

		row.player_teammate_id = ''.join(teamNamer(h))

		team = teamNamer([row.opp_id])
		h = []

		for i in team:
			if i in player_dict.keys():
				h.append(player_dict[i])
			else:
				h.append(i)
		row.opp_id = ''.join(teamNamer(h))

	if str(row.game_type) == '1v2':
		team = teamNamer([row.opp_id])
		h = []

		for i in team:
			if i in player_dict.keys():
				h.append(player_dict[i])
			else:
				h.append(i)
		row.opp_id = ''.join(teamNamer(h))

	row.put()