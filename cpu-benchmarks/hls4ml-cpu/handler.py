import numpy as np
import tensorflow as tf
import time
from tensorflow.keras import backend as K
from tensorflow.keras.models import load_model
from qkeras.utils import _add_supported_quantized_objects
from tensorflow_model_optimization.sparsity.keras import strip_pruning
from tensorflow_model_optimization.python.core.sparsity.keras import pruning_wrapper
from os.path import exists
from pathlib import Path

co = {}
_add_supported_quantized_objects(co)
co['PruneLowMagnitude'] = pruning_wrapper.PruneLowMagnitude

pwd_path = 'quantized_pruned_cnn_model.h5'
ctr_path = '/home/app/function/quantized_pruned_cnn_model.h5'

if exists(pwd_path):
    model = load_model(pwd_path, custom_objects=co)
elif exists(ctr_path):
    model = load_model(ctr_path, custom_objects=co)
else:
    raise RuntimeError("model not found");

start_time = 0
end_time = 0

def measure_start():
  global start_time
  start_time = time.perf_counter_ns()

def measure_end():
  global end_time
  end_time = time.perf_counter_ns()

def handle(event, context):
    data = event.body
    results = handle_request(data)

    csvPath = str(Path.home()) + "/computation_time/log.csv"
    if exists(csvPath):
        with open(csvPath, "a") as csv:
            csv.write("hls4ml, cpu, %d, %d\n" % (len(data), diff))

    return {
        "statusCode": 200,
        "body": "results",
        "headers": {
            "X-computation-time": str(end_time-start_time) + " ns"
        }
    }

def noop():
    pass

def handle_request(data):
    delimiter = data.find(b'\n')
    count = int(data[0:delimiter])
    binary = data[delimiter+1:]

    nparr = np.frombuffer(binary,dtype=np.ubyte)
    nparr = nparr.reshape((count,32,32,3))
    X_test = tf.cast(nparr, tf.float32) / 255.0

    measure_start()
    Y = model.predict(X_test)
    measure_end()
    Y_classes = Y.argmax(axis=1)

    results = [f"Result: {cls}, Score: {y[cls]:.4f}" for (cls, y) in zip(Y_classes, Y)]
    results = "\n".join(results)

    return results
