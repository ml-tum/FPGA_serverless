# OpenFaas unikernel functions


## What
Unikernel apps are bundeled in a container image.
The purpose of the unikernel app is to pass the input to the FPGA and return the result back.
1. The input is read from the incoming HTTP request.
2. The input is then passed to the FPGA and the FPGA is instructed to execute the requested user logic.
3. After the FPGA has completed processing, the results are read back and returned inside the response body of the HTTP request.

Each FPGA user logic has its own unikernel app and container image.
Relaying the HTTP request to the correct unikernel app is the responsibility of OpenFaas.


## Building container images
Checkout the funky-unikernel repository.
Change into the `serverless` directory.
Call the `build_ctr_image.sh` script and pass the name of the function you want to build, e.g. `build_ctr_image.sh sha3-fpga`.
You can see the names of all existing functions in the `src` directory.
The script will build the unikernel container image and upload it to docker hub.


## OpenFaas descriptor
To install the function via OpenFaas, we first need a descriptor:
```
version: 1.0
provider:
  name: openfaas
  gateway: http://127.0.0.1:8080
functions:
  bm-sha3-fpga:
    lang: Dockerfile
    image: docker.io/ccgroup47/myrepo:bm-sha3-fpga
    annotations:
      com.openfaas.profile: kata-urunc
```

Note the name of the image. It's the image we uploaded in the previous step.
Now use the OpenFaas CLI and pass the file name of the descriptor:
`faas-cli deploy -f sha3-fpga.yml`

(Note: In our VM image the descriptor files already exist in `~/fpga/benchmark`).


## Invoke function
After the container has started, we can use the function like this:
`echo -n "I want the hash of this text" | faas-cli invoke bm-sha3-fpga`

As a result you should see the SHA3-512 hash of the example text on your terminal window.