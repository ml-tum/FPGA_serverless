import math
import json, os, sys, random, fileinput
import subprocess, sys
from subprocess import Popen, PIPE, STDOUT, DEVNULL
import time
from pathlib import Path
import numpy as np
import csv
import datetime
import concurrent.futures


HOME = str(Path.home())
DATASET_PATH = HOME + '/datasets'
#FPGA_PATH = HOME + '/fpga/no_unikernel'
#FPGA_PATH = HOME + '/FPGA_serverless/watchdog/serverless/no_unikernel'
FPGA_PATH = HOME + '/computation_time/no_unikernel'


rand_bytes = 8*1024*1024
batches = 25
reps = 30


def extract_timestamps(log):
	ok = False
	for line in log.split('\n'):
		if line.startswith("TIMESTAMPS "):
			ts = line.split(" ")[1:]
			ts = [int(num, base=10) for num in ts]
			ok = True
	if not ok:
		print("TIMESTAMPS IS MISSING:")
		print(log)
	return ts


def prepare_sha256():
	path = FPGA_PATH + '/sha256-fpga'
	chunksize = min(rand_bytes, 64*1024)
	assert(rand_bytes % chunksize == 0)

	p = Popen([path], stdin=PIPE, stdout=DEVNULL, stderr=PIPE, close_fds=True)
	for i in range(rand_bytes//chunksize):
		p.stdin.write(np.random.bytes(chunksize)) # send random data
	p.stdin.flush()

	return p


def fire(p):
	p.stdin.close() # this will allow the function to execute and start the timer
	p.wait()
	ts = extract_timestamps(p.stderr.read().decode())

	computation_time = ts[2]-ts[1] # function_end - function_start
	return computation_time


csv_name = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
csv_name = "parallelism_" + csv_name + ".csv"
csv_file = open(csv_name, 'w', newline='')
csv_writer = csv.writer(csv_file, delimiter=',')
csv_writer.writerow(['application', 'regions', 'batch', 'runtime_ns'])

regions = 2

print("Filename: " + csv_name)
input("Make sure the bitstream is already configured in the used regions. Hit enter to continue.")
input(f"Confirm number of regions = {regions}. Hit enter to continue.")


random.seed(a = 31415)

for b in range(batches):
	print("batch " + str(b))
	with concurrent.futures.ThreadPoolExecutor(max_workers=reps) as executor:
		futures = []
		ps = []
		for rep in range(reps):
			p = prepare_sha256()
			ps.append(p)

		for rep in range(reps):
			fut = executor.submit(fire, ps[rep])
			futures.append(fut)

		for rep in range(reps):
			print(str(rep), end=', ' if rep < reps-1 else '\n')
			computation_time = futures[rep].result()
			csv_writer.writerow(["sha256-fpga", regions, b+1, computation_time])
