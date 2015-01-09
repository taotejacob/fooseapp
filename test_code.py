
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

def tester(team_names, input_scores):
	game_scores = []

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

	return output

team_names = ['jacob', 'bob']
input_scores = ['4-6-8-3', '2-3-5-30']
# game_scores = zip(input_scores[0].split('-'), input_scores[1].split('-'))
aaa = [[4,6,5,7], [2,3,4,5]]
game_scores = tester(team_names, input_scores)
error = None


if len(set([len(x) for x in input_scores])) != 1:
	error = "You input the wrong number of scores"	

if tieCheck(game_scores):
	error = "This isn't soccer, we don't have tie games"

if max(sum(game_scores, ())) > 9:
	error = "No scores above 9 allowed"

if error:
	print error

print game_scores

print [zip(x) for x in aaa]

a = "asdfasdf"

print type(a) == type('')

# prepData(team_names, team_scores)