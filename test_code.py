
aa = {'Ghost': [0, 0, 0], 'Jacob R': [9, 6, 6.0], 'Griffin D': [5, 2, -4.0]}
bb = {'Ghost': [0, 0, 0], 'Tyler M': [6, 6, 24.0], 'Griffin D': [7, 4, -2.0], 'Jacob R': [10, 6, 5.5]}
cc = {'Ghost': [0, 0, 0], 'Tyler M': [6, 6, 24.0]}




def GetProb(p1_rank, p2_rank):
	return 1 / (1 + pow(2, float((p2_rank - p1_rank))/100))


def ScoreUpdate(p1_points, p1_games, p1_rank, p2_points, p2_games, p2_rank):
	a = p1_points - (GetProb(p1_rank, p2_rank) * (p1_points + p2_points))
	b = p2_games  - (p1_points + p2_points)
	c = p1_games * p2_games
	out1 = 630 * a * b / float(c)

	a = p2_points - (GetProb(p2_rank, p1_rank) * (p2_points + p1_points))
	b = p1_games  - (p2_points + p1_points)
	c = p2_games * p1_games
	out2 = 630 * a * b / float(c)

	return [out1 + p1_rank, out2 + p2_rank]

print ScoreUpdate(1, 12, 100, 5, 12, 100)

