import os,re
base = "populations/game_0/4580/"
files = [o for o in os.listdir(base) if re.match('.*\.dat',o)]

a = []
b_f=-99999
b = -1
for f in sorted(files,key= lambda m:int(re.match('([0-9]+).dat',m).group(1))):
	r = re.match('([0-9]+).dat',f)
	i = int(r.group(1))
	print "i:{0}".format(i)
	dat_file = open(base+f).read().split('\n')
	# print dat_file[1]
	fitness = float(re.match('fitness: ([\-0-9.]+)',dat_file[1]).group(1))
	print "fitness:",fitness
	if fitness > b_f:
		b_f = fitness
		b = i

print "best:",b