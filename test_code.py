
aa = {'Ghost': [0, 0, 0], 'Jacob R': [9, 6, 6.0], 'Griffin D': [5, 2, -4.0]}
bb = {'Ghost': [0, 0, 0], 'Tyler M': [6, 6, 24.0], 'Griffin D': [7, 4, -2.0], 'Jacob R': [10, 6, 5.5]}
cc = {'Ghost': [0, 0, 0], 'Tyler M': [6, 6, 24.0]}


###add entries from arbitrary # of dictionaries to each other
def dictAdd(a, *b):
	##values added to dictorary listed first
	new_dict = a.items()
	new_dict = dict(new_dict)

	#cycle through other listed dictionaries
	for dictionary in b:

		#cycle through players listed in dictionary
		for player in dictionary.keys():
			if player in new_dict.keys(): #if exists add together
				new_dict[player] = [x+y for x,y in zip(new_dict[player],dictionary[player])]
			else: #else add new entry
				new_dict[player] = dictionary[player]

	return new_dict


print dictAdd(aa, bb, cc)


# from helper_functions import *

values = get1v1Standings(qry)
statlist1v1 = newStatTable(values[0], values[1])

values2v2 = get2v2Standings(qry)
statlist2v2 = newStatTable2v2(values2v2[0], values2v2[1])








# text_file = open("WeeklyStandings.txt", "w")
# text_file.write("%s" % [prepforWeekly(statlist1v1), prepforWeekly(statlist2v2)])
# text_file.close()


# 'p-score' 'name' 'games' 'win%' 'goal diff' 'adj goals'

# text_file = open("WeeklyStandings.txt", "w")
# text_file.write("['Jacob', 'bob', 'mike']")
# text_file.close()

# new = open("WeeklyStandings.txt", "r")

# # print new.read()

# a = eval(new.read())
# print a[0]
