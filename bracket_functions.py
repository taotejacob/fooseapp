from helper_functions import *

def getWinners(tourn_results):
	winners = []

	for game in tourn_results:
		players = game[0]
		scores = game[1]

		scores = unpackPrep(scores, players, "aa")

		wins = 0

		for s in scores:
			if s[0] > s[1]:
				wins = wins + 1
			else:
				wins = wins - 1

		if wins > 0:
			winners.append(players[0])
		else:
			winners.append(players[1])

	return winners



def playerSort(players, ranks, decreasing = False):
	p = sorted(zip(ranks, players), reverse = decreasing)
	p = zip(*p)[1]
	return list(p)



def createPairs(players_sorted, random_order = False):
	p = len(players_sorted)/2
	if random_order:
		random.shuffle(players_sorted)
		return zip(players_sorted[:p], players_sorted[p:])

	else:
		rev = players_sorted[::-1]

		return zip(players_sorted[:p], rev[:p])



def findMatchups (players_sorted, randomize = False):
	n = len(players_sorted)
	
	if n == 2:
		return [[], createPairs(players_sorted, random_order = randomize)]

	else:
		remain = n % 4

		if remain == 0:
			buys = []
			play = createPairs(players_sorted, random_order = randomize)
		if remain == 1:
			buys = players_sorted[:n-2]
			play = createPairs(players_sorted[n-2::], random_order = randomize)
		if remain == 2:
			buys = players_sorted[:2]
			play = createPairs(players_sorted[2::], random_order = randomize)
		if remain == 3:
			buys = players_sorted[:1]
			play = createPairs(players_sorted[1::], random_order = randomize)

		return [buys, play]


def round_scores_update(round_matchups, round_scores, self):
	games = round_matchups[1]
	for n in range(len(round_scores)):
		score1 = str(games[n][0])
		score2 = str(games[n][1])

		if self.request.get(score1) and self.request.get(score2):
			round_scores[n] = [str(self.request.get(score1)), str(self.request.get(score2))]

	return round_scores



def genTourn_results(matchups, scores):
	matches = matchups[1]
	finished = []
	i = 0
	for s in scores:
		if s != [0,0]:
			finished.append([matches[i], s])
		i = i+1
	return finished


def ScoreHolder(matchups):
	scores = []
	for n in matchups:
		scores.append([0,0])
	return scores


def genScoreForm(matchups, scores):
	buys = matchups[0]
	matches = matchups[1]
	inputHTML = []
	finished = []
	i = 0
	for s in scores:
		if s == [0,0]:
			inputHTML.append('%s vs %s<br>' % (matches[i][0], matches[i][1]))
			inputHTML.append("<div class='ui-grid-b' style='text-align: center'><div class='ui-block-a' style='padding-right: 10px'><input type='text' name='%s' id='score_%sa' placeholder='%s&#39;s Score'></div><div class='ui-block-b' style='padding-right: 10px'><input type='text' name='%s' id='score_%sb' placeholder='%s&#39;s Score'></div><div class='ui-block-c'><input type='submit' value='Submit Score' class='ui-mini'></div></div>" % (matches[i][0], i, matches[i][0], matches[i][1], i, matches[i][1]))
		else:
			finished.append([matches[i], s])
		i = i+1	
	inputHTML.append('<input type="hidden" value="%s" name="round_scores">' % scores)
	inputHTML.append('<input type="hidden" value="%s" name="tourn_results">' % finished)
	inputHTML.append('<input type="hidden" value="%s" name="buy_players">' % buys)

	return inputHTML