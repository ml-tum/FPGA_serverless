# run evaluation

## run on hinoki

### fix current deps

Make sure all dependencies are stored in `requirements.txt`:

```sh
pip freeze > requirements.txt
```

### download production traces

Follow the instructions
in [the Microsoft Azure traces repository](https://github.com/Azure/AzurePublicDataset/blob/master/AzureFunctionsInvocationTrace2021.md).

### start on remote machine

```sh
python3.9 -m venv .venv
source .venv/bin/activate
python3.9 -m pip install -r requirements.txt

export PYTHONPATH="$PYTHONPATH:$(pwd)"

cd evaluation

COMMIT_HASH=$(git rev-parse HEAD) MAX_REQUESTS=10000000 NEW_RELIC_CONFIG_FILE=../newrelic.ini python3.9 scalability.py
```

## plotting specific results

Start by downloading the tar archive containing the results from S3, then unpack it:

```
tar -xzvf ~/path/to/results.tar.gz
```

Then, run the following command to plot the results in this (simulator) directory:

```
python3.9 -m venv .venv
source .venv/bin/activate
python3.9 -m pip install -r requirements.txt

export PYTHONPATH="$PYTHONPATH:$(pwd)"

cd evaluation

PLOT_ON_RESULTS=~/path/to/unpacked_results.json python3.9 scalability.py
```

e.g.

```
PLOT_ON_RESULTS=~/scalability_figure_evaluation_results_20240513182734.json python3.9 scalability.py
```
