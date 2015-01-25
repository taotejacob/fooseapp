
p1v1dict = {'Alex B': [4, 1, -9.36], 'Ghost': [0, 0, 0], 'Pat R': [1, 0, -1.43], 'tom t': [2, 0, -10.0]}
opponent = 'Alex B'
p_win = 1
diff = 2.36


def p_dict_update(p1v1dict, opponent, p_win, diff):

	p_dict = eval(p1v1dict)

	results = p_dict[opponent]

	results[0] = results[0] - 1
	results[1] = results[1] - p_win
	results[2] = results[2] - diff

	p_dict[opponent] = results

	return p_dict


                                                                                                                                                                                                                                                                                                                                                                                                                     



print p_dict_update(p1v1dict, opponent, p_win, diff)

