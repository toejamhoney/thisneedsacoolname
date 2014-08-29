import sys
import os
import re

fin_fams = open(sys.argv[1], 'r')
fin_bwdot = open(sys.argv[2], 'r')
fout = open("pretty-colors-%s" % (sys.argv[2]), 'w')

def write_nodes(fin, fout):
    for line in fin:
        color_id, md5 = line.rstrip().split(',')
        line = '"%s" [color=%s]\n' % (md5, color_id)
        fout.write(line)
        sys.stdout.write(line)

def get_colors(fin):
    for line in fin:
        color_id, md5 = line.rstrip().split(',')
        colors[md5] = str(int(color_id) + 1)

def color_edge(line):
    line = re.sub(r'\n$', "[color=%s]\n" % cid, line)

before_edges = True
for line in fin_bwdot:
    sys.stdout.write("%s\n\t" % line)
    md5, _, host = line.partition(" -- ")
    if host and before_edges:
        write_nodes(fin_fams, fout)
        before_edges = False
    fout.write(line)

fin_fams.close()
fin_bwdot.close()
fout.close()
