import argparse
import math
import json, os, sys, random, fileinput
import subprocess, sys
from subprocess import Popen, PIPE, STDOUT, DEVNULL
import time
import numpy as np

HOME = '/home/martin'
DATASET_PATH = '/home/martin/datasets'
CPU_PATH = '/home/martin/computation_time/cpu'
FPGA_PATH = '/home/martin/computation_time/no_unikernel'

def popen(path):
	return Popen([path], stdin=PIPE, stdout=DEVNULL)

def pwrite(process, s):
	if(type(s) is str):
		process.stdin.write(s.encode())
	else:
		process.stdin.write(s)

def pwait(process):
	process.stdin.flush()
	process.stdin.close()
	process.wait()

def executables(name):
	# e.g. '/home/ubuntu/fpga/cpu/addmul-cpu/addmul'
	return [CPU_PATH + '/' + name, FPGA_PATH + '/' + name + '-fpga']

def readfile(path):
    with open(path, 'rb') as f:
        return f.read()

def run_addmul(ints):
	paths = executables('addmul')

	for path in paths:
		p = popen(path)
		pwrite(p, "3 10139\n")
		for i in range(ints):
			pwrite(p, "%d " % random.uniform(0, 10**6))
		pwait(p)

def run_aes(bytes):
	paths = executables('aes128ecb')
	chunksize = min(bytes, 64*1024)
	assert(bytes % chunksize == 0)

	for path in paths:
		p = popen(path)
		for i in range(bytes//chunksize):
			pwrite(p, np.random.bytes(chunksize))
		pwait(p)

def run_sha256(bytes):
	paths = executables('sha256')
	chunksize = min(bytes, 64*1024)
	assert(bytes % chunksize == 0)

	for path in paths:
		p = popen(path)
		for i in range(bytes//chunksize):
			pwrite(p, np.random.bytes(chunksize))
		pwait(p)

def run_sha3(bytes):
	paths = executables('sha3')
	chunksize = min(bytes, 64*1024)
	assert(bytes % chunksize == 0)

	for path in paths:
		p = popen(path)
		for i in range(bytes//chunksize):
			pwrite(p, np.random.bytes(chunksize))
		pwait(p)

def run_corner(jpgfile):
	paths = executables('corner')

	for path in paths:
		p = popen(path)
		pwrite(p, readfile(DATASET_PATH + '/' + jpgfile))
		pwait(p)

def run_hyperloglog(ints):
	paths = executables('hyperloglog')

	for path in paths:
		p = popen(path)
		for i in range(ints):
			val = int(random.betavariate(alpha=2, beta=5) * 10**6)
			pwrite(p, "%d " % val)
		pwait(p)

def run_matmul(arg):
	paths = executables('matmul64')

	for path in paths:
		p = popen(path)
		for i in range(64*64):
			pwrite(p, "%d " % random.uniform(0, 10**6))
		pwait(p)

def run_gzip(file):
	paths = executables('gzip')

	for path in paths:
		p = popen(path)
		pwrite(p, readfile(DATASET_PATH + '/' + file))
		pwait(p)

def run_nw(words):
	assert(math.log(words,2).is_integer())
	paths = executables('nw')
	bytes_per_word = 64
	size = bytes_per_word * words * 2
	chunksize = min(size, 64*1024)
	assert(size % chunksize == 0)

	for path in paths:
		p = popen(path)
		pwrite(p, "%d %d\n" % (words, words))
		for i in range(size//chunksize):
			pwrite(p, np.random.bytes(chunksize))
		pwait(p)

def run_hls4ml(file):
	paths = [["/usr/bin/python3", "-u", CPU_PATH + '/hls4ml-cpu/measure_computation_time.py'], [FPGA_PATH + '/hls4ml-fpga']]

	for path in paths:
		p = Popen(path, cwd=CPU_PATH+'/hls4ml-cpu/', stdin=PIPE, stdout=DEVNULL, creationflags=subprocess.HIGH_PRIORITY_CLASS)
		pwrite(p, readfile(DATASET_PATH + '/' + file))
		pwait(p)

def run(func, args, repetitions=1):
	runs = []
	for arg in args:
		for rep in range(repetitions):
			runs.append((arg,rep))
	#random.seed(a = 31415)
	#random.shuffle(runs)
	for (arg,rep) in runs:
		random.seed(a = 31415+rep)
		func(arg)
		time.sleep(0.2)

reps = 30
'''
run(run_hls4ml, ['svhn_test_100.bin', 'svhn_test_1000.bin', 'svhn_test_5000.bin', 'svhn_test.bin'], reps)
run(run_gzip, ['gzip_input_alice.bin', 'gzip_input_dickens.bin', 'gzip_input_mozilla.bin', 'gzip_input_linux.bin'], reps)
run(run_addmul, [2**10, 2**18, 2**22], reps)
run(run_aes, [2**12, 2**20, 2**24], reps)
run(run_sha256, [2**12, 2**20, 2**24], reps)
run(run_sha3, [2**12, 2**20, 2**24], reps)
run(run_hyperloglog, [2**10, 2**18, 2**22], reps)
run(run_matmul, [None], reps)
run(run_corner, ['tum_logo_bw.jpg'], reps)
run(run_gzip, ['gzip_input_alice.bin', 'gzip_input_dickens.bin', 'gzip_input_mozilla.bin'], reps)
run(run_nw, [2**4, 2**6, 2**8], reps)
'''

run(run_sha3, [2**22], reps)
#run(run_matmul, [None], reps)
#run(run_gzip, ['gzip_input_alice.bin'], reps)
run(run_hyperloglog, [2**19], reps)
run(run_corner, ['tum_logo_bw.jpg'], reps)
run(run_nw, [2**4], reps)
