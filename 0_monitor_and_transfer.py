"""
Persistent monitoring of MiSeq runs folder mounted at /media/macdatafile
for 'needsprocessing' flag, which will trigger a pipeline on the cluster.

The role of this script is to detect this flag, transfer the *.fastq.gz
files in Data/Intensities/BaseCalls/, uncompress the files, and call
the pipeline.  When the pipeline is complete, it will upload the end
results back to macdatafile, create an empty file named 'processingcomplete'
and remove 'needsprocessing'.

Processing will be done on a "first come first serve" basis, i.e., no
asynchronous processing where another MiSeq run becomes available for 
processing while the pipeline is being executed.
"""

import os, sys
from glob import glob
from datetime import datetime
from time import sleep

home='/data/miseq/'
delay = 3600

def timestamp(msg):
	# Display the date/time along with a message
	print '[%s] %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), msg)

while 1:
	runs = glob('/media/macdatafile/MiSeq/runs/*/needsprocessing')
	if len(runs) == 0:
		timestamp('No runs need processing')
		sleep(delay)
		continue
	
	# If any exist, sort list by runID (run_name)
	runs.sort()
	root = runs[0].replace('needsprocessing', '')
	timestamp ('Processing {}'.format(root))
	run_name = root.split('/')[-2]
	if not os.path.exists(home+run_name):
		os.system('mkdir %s%s' % (home, run_name))
	
	# Extract assay/description/chemistry from SampleSheet.csv
	infile = open(runs[0].replace('needsprocessing', 'SampleSheet.csv'), 'rU')
	assay, mode, chemistry = '', '', ''
	for line in infile:
		if line.startswith('Assay,'):
			assay = line.strip('\n').split(',')[1]
		elif line.startswith('Description,'):
			mode = line.strip('\n').split(',')[1]
		elif line.startswith('Chemistry,'):
			chemistry = line.strip('\n').split(',')[1]
			break
	infile.close()
	
	# mode must be Nextera or Amplicon: if not, mark as processed and proceed
	if mode not in ['Nextera', 'Amplicon']:
		print 'ERROR: Unrecognized mode "', mode, '"... skipping'

		# Eliminate 'needsprocessing' flag, add 'processed' flag
		os.remove(runs[0])
		flag = open(runs[0].replace('needsprocessing', 'processed'), 'w')
		flag.close()

		# Start over: this run will no longer be grepped
		continue
	
	
	# If run is valid, transfer fasta.gz files to cluster and unzip
	files = glob(root+'Data/Intensities/BaseCalls/*.fastq.gz')
	nfiles = 0

	for file in files:
		filename = file.split('/')[-1]

		# Do not process undetermined read files
		if filename.startswith('Undetermined'):
			continue
		
		local_file = home + run_name + '/' + filename
		timestamp('cp and gunzip %s' % filename)
		os.system('cp %s %s' % (file, local_file))
		os.system('gunzip -f %s' % local_file)
		nfiles += 1

	# paired-end reads, each sample has two FASTQ files
	timestamp('spawning MPI processes...')
	load_mpi = "module load openmpi/gnu"
	script_path = "/usr/local/share/miseq/scripts/0_MPI_wrapper.py"
	qCutoff = 20
	os.system("{}; mpirun -machinefile mfile python {} {} {} {}".format(load_mpi, script_path, home+run_name, mode, qCutoff))

	# Replace the 'needsprocesing' flag with a 'processed' flag
	os.remove(runs[0])
	flag = open(runs[0].replace('needsprocessing', 'processed'), 'w')
	flag.close()
	result_path = runs[0].replace('needsprocessing', 'Results')

	# Make a results folder if necessary
	if not os.path.exists(result_path): os.mkdir(result_path)

	# Upload results
	files = glob(home + run_name + '/*.fasta')
	files += glob(home + run_name + '/_g2p.csv')
	files += glob(home + run_name + '/_g2p.csv.consensus')
	files += glob(home + run_name + '/*.csf')
	files += glob(home + run_name + '/*.nuc.csv')
	files += glob(home + run_name + '/*.amino.csv')
	files += glob(home + run_name + '/*.v3prot')
	files += glob(home + run_name + '/_nuc_consensus.fasta')
	
	# Copy the results ontp macdatatile
	for file in files:
		filename = file.split('/')[-1]
		os.system('cp %s %s/%s' % (file, result_path, filename))

