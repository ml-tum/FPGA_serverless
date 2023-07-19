# run benchmarks

## run on hinoki

### fix current deps

Make sure all dependencies are stored in `requirements.txt`:

```sh
pip freeze > requirements.txt
```

### download production traces

Follow the instructions in [the Microsoft Azure traces repository](https://github.com/Azure/AzurePublicDataset/blob/master/AzureFunctionsInvocationTrace2021.md).

### start on remote machine

```sh
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt

export PYTHONPATH="$PYTHONPATH:$(pwd)"

cd benchmarks

python3 benchmark.py
```