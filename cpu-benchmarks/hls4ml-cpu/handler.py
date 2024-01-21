import numpy as np
import tensorflow as tf
from tensorflow.keras import backend as K
from tensorflow.keras.models import load_model
from qkeras.utils import _add_supported_quantized_objects
from tensorflow_model_optimization.sparsity.keras import strip_pruning
from tensorflow_model_optimization.python.core.sparsity.keras import pruning_wrapper

co = {}
_add_supported_quantized_objects(co)
co['PruneLowMagnitude'] = pruning_wrapper.PruneLowMagnitude
model = load_model('/home/app/function/quantized_pruned_cnn_model.h5', custom_objects=co)

def handle(event, context):
    data = event.body
    delimiter = data.find(b'\n')
    count = int(data[0:delimiter])
    binary = data[delimiter+1:]
    
    nparr = np.frombuffer(binary,dtype=np.ubyte)
    nparr = nparr.reshape((count,32,32,3))
    X_test = tf.cast(nparr, tf.float32) / 255.0
    
    Y = model.predict(X_test)
    Y_classes = Y.argmax(axis=1)
    
    results = [f"Result: {cls}, Score: {y[cls]:.4f}" for (cls, y) in zip(Y_classes, Y)]
    results = "\n".join(results)
  
    return {
        "statusCode": 200,
        "body": results
    }
  
