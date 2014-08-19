import sys
import os
import re

fin = open(sys.argv[1], 'r')
colors = {}

for line in fin:
    color, md5 = line.rstrip().split(',')
    colors[md5] = str(int(color) + 1)

fin.close()

fin = open(sys.argv[2], 'r')
fout = open(sys.argv[3], 'w')

for line in fin:
    sys.stdout.write("%s\t" % line)
    md5, _, host = line.partition(" -- ")
    if host:
        cid = colors.get(md5.strip('"'))
        if cid:
            line = re.sub(r'\n$', "[color=%s]\n" % cid, line)
    sys.stdout.write("%s\n" % line)
    fout.write(line)

fin.close()
fout.close()
