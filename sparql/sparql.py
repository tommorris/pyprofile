import sys, os, rdflib

query = ''.join(open(sys.argv[1]).readlines())
g = rdflib.ConjunctiveGraph()
g.parse(sys.argv[2])
result = g.query(query)
print result.__dict__