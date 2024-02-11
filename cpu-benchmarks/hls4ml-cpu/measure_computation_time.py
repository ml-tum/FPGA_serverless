import time
import handler
import sys
import handler
from pathlib import Path

# call this script with -u flag, e.g. python3 -u xyz.py

start_time = 0
end_time = 0

def measure_start():
  global start_time
  start_time = time.perf_counter_ns()

def measure_end():
  global end_time
  end_time = time.perf_counter_ns()

data = sys.stdin.buffer.read()

handler.handle_request(data, measure_start, measure_end)

diff = end_time-start_time

print(f"Elapsed time: {diff} ns", file=sys.stderr)

with open(str(Path.home()) + "/output/benchmark.csv", "a") as csv:
    csv.write("hls4ml, cpu, %d, %d\n" % (len(data), diff))
