# simulator

## preparing for evaluation

### install dependencies

```bash
pip install -r requirements.txt
``` 

### prepare traces

First, download and unpack the traces from [Microsoft Azure](https://github.com/Azure/AzurePublicDataset/raw/master/data/AzureFunctionsInvocationTraceForTwoWeeksJan2021.rar).

Then, run the trace resampler to upscale the traces.

```bash
python trace_resampler.py --input AzureFunctionsInvocationTraceForTwoWeeksJan2021.txt --output resampled.csv 
```

### run the simulator

```bash
cd evaluation
python scalability.py
```