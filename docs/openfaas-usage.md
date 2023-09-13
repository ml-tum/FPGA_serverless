## OpenFaas usage


# Prerequisite
Make sure that OpenFaas is installed and the API is accessible


# Deploy figlet (demo function)
faas-cli store deploy figlet
echo "hello" | faas-cli invoke figlet


# Download templates
`
faas-cli template pull
`


# Create new "Dockerfile" template
`
faas-cli new hello-kata --lang dockerfile
`


# Apply the profile
Edit the yaml of the function, e.g. `nano hello-kata.yaml`
To use a certain profile add an annotation:
`
    image: docker.io/ccgroup47/myrepo:hello-kata-latest
    annotations:
      com.openfaas.profile: kata-urunc
`


# Verify the runtimeclass of a pod
Look for the field `runtimeClassName` in
` 
kubectl get pod -o yaml -n openfaas-fn XYZ
`


## Example: Print 'mount' output

# Edit Dockerfile
nano `hello-kata/Dockerfile`
Change `ENV fprocess=cat` to `ENV fprocess="mount"`

# Edit OpenFaas template
Edit `hello-kata.yml`
Change image name and set a profile
`
    image: docker.io/ccgroup47/myrepo:hello-kata-latest
    annotations:
      com.openfaas.profile: kata
`

# Deploy with Docker
Deploy hello-kata lambda function
`
faas-cli up --yaml hello-kata.yml
`

# Or Deploy with buildkitd
`
faas-cli build --shrinkwrap -f hello-kata.yml
sudo buildctl build --frontend dockerfile.v0 --local context=./build/hello-kata/ --local dockerfile=./build/hello-kata/ --output type=image,name=docker.io/ccgroup47/myrepo:hello-kata-latest,push=true
`

