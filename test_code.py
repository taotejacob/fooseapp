
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



def GetProb(p1_rank, p2_rank):
	return 1 / (1 + pow(2, float((p2_rank - p1_rank))/100))


def ScoreUpdate(p1_win, p1_games, p1_rank, p2_games, p2_rank):
	a = p1_win - (GetProb(p1_rank, p2_rank) * (1))
	b = (p2_games + 1)  - (1)
	c = (p1_games + 1) * (p2_games + 1)
	out = 630 * a * b / float(c)

	return out

print ScoreUpdate(1, 6, 100, 6, 100)
print ScoreUpdate(0, 6, 100, 6, 100)
