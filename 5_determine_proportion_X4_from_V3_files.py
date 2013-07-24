"""
determine_proportion_X4.py

For each .v3 file, enumerate through fasta contents, and determine
proportion X4 for that patient/QC rule, as determined by sequence count
and G2PFPR cutoff.

Input: HIV1B-env.remap.sam.<qCutoff>.fasta.<minCount>.seq.V3
Output: summary.X4 (Contains name of file and percent X4)
"""

import os
import sys
import re
from glob import glob
from seqUtils import convert_fasta

helpOutput = """Usage: python determine_proportion_X4.py <G2PFPR cutoff> <folderContainingV3Files>
Example (X4 if G2P <= 3.5): python determine_proportion_X4.py 3.5 ../path/to/files/"""

if len(sys.argv) != 3:
	print helpOutput
	sys.exit()

G2P_FPR_cutoff = float(sys.argv[1])
G2P = str(G2P_FPR_cutoff) # Shorthand

# "q" needed to prevent excel from interpreting my labels as dates
print "sample,G2P_FPR_Cutoff,q0-1" + G2P + ",q10-1-" + G2P + ",q15-1-" + G2P + ",q20-1-" + G2P + ",q0-3-" + G2P + ",q10-3-" + G2P + ",q15-3-" + G2P + ",q20-3-" + G2P + ",q0-50-" + G2P + ",q10-50" + G2P + ",q15-50" + G2P + ",q20-50" + G2P

globPath = sys.argv[2] + '*.HIV1B-env.remap.sam.*.fasta.*.seq.v3'
files = glob(globPath)
d = {}

# For each v3 file containing G2P scores, determine proportion X4
for f in files:

	# Get sample/qCutoff/minCount information out of filename
	filename = os.path.basename(f)

	# Ignore positive controls and negative controls
	if "pn" in filename or "neg" in filename or "NEG" in filename: continue	

	filenameFields = re.split('[.]', filename)
	sample =filenameFields[0]
	qCutoff = filenameFields[4]
	minCount = filenameFields[6]

	infile = open(f, 'rU')
	try:
		fasta = convert_fasta(infile.readlines())
	except:
		sys.stderr.write('Failed to convert ' + f + '\n')
		continue
	infile.close()

	total_seqs = 0
	total_X4_seqs = 0

	# For each V3 sequence, decide if X4 or R5
	for header, v3Seq in fasta:

		# Drop fields when GP2_FPR is nil (Couldn't be generated by Conan's G2P)
		try:
			G2P_FPR = float(re.split('G2PFPR_([0-9]+[.][0-9])+', header)[1])
			count = int(re.split('count_([0-9]+)',header)[1])

			if G2P_FPR < G2P_FPR_cutoff:
				total_X4_seqs += count

			total_seqs += count

		except:
			continue


	proportion_X4 = float(total_X4_seqs) / float(total_seqs) * 100

    # Each sample contains a list of (filterType, data) tuples - themselves also tuples
	filterType = (qCutoff, minCount, str(G2P_FPR_cutoff))
	data = "%.3f" % proportion_X4

	myTuple = (filterType, data)

	if sample not in d.keys():
		d[sample] = []

	d[sample].append(myTuple)

# For each sample
for sample in d:

	q_0_min_1 = "NA"; q_10_min_1 = "NA"; q_15_min_1 = "NA"; q_20_min_1 = "NA"
	q_0_min_3 = "NA"; q_10_min_3 = "NA"; q_15_min_3 = "NA"; q_20_min_3 = "NA"
	q_0_min_50 = "NA"; q_10_min_50 = "NA"; q_15_min_50 = "NA"; q_20_min_50 = "NA"

	# Traverse the list
	for myTuple in d[sample]:
		filterType = myTuple[0]; data = myTuple[1]
		qCutoff = int(filterType[0]); minCount = int(filterType[1]); G2P_cutoff = float(filterType[2])

		if qCutoff == 0 and minCount == 1:
			q_0_min_1 = data

		elif qCutoff == 0 and minCount == 3:
			q_0_min_3 = data

		elif qCutoff == 0 and minCount == 50:
			q_0_min_50 = data

		elif qCutoff == 10 and minCount == 1:
			q_10_min_1 = data

		elif qCutoff == 10 and minCount == 3:
			q_10_min_3 = data

		elif qCutoff == 10 and minCount == 50:
			q_10_min_50 = data

		elif qCutoff == 15 and minCount == 1:
			q_15_min_1 = data

		elif qCutoff == 15 and minCount == 3:
			q_15_min_3 = data

		elif qCutoff == 15 and minCount == 50:
			q_15_min_50 = data

		elif qCutoff == 20 and minCount == 1:
			q_20_min_1 = data

		elif qCutoff == 20 and minCount == 3:
			q_20_min_3 = data

		elif qCutoff == 20 and minCount == 50:
			q_20_min_50 = data

	print sample + "," + str(G2P_FPR_cutoff) + "," + q_0_min_1 + "," + q_10_min_1 + "," + q_15_min_1 + "," + q_20_min_1 + "," + q_0_min_3 + "," + q_10_min_3 + "," + q_15_min_3 + "," + q_20_min_3 + "," + q_0_min_50 + "," + q_10_min_50 + "," + q_15_min_50 + "," + q_20_min_50