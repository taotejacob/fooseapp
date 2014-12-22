p = [(2, 4, 66, "adsf"), ("asdfs", 4, 5, 6), ("jacob", 2342, 2341234)]

f = []

for users in p:
	f.append(users[1])

print f
print f[-1]


del f[-1]
print f

a = [u'timefirst', u''] 


print str(a)
print a[0]
print a[1] == ""

if a[-1] == "":
	print "YES"

