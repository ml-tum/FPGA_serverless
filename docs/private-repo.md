# Private repo


## Save credentials for private repo in containerd config
Edit `/etc/containerd/config.toml` on all nodes.
Find the section `[plugins."io.containerd.grpc.v1.cri".registry.configs]` and add these lines:
```
        [plugins."io.containerd.grpc.v1.cri".registry.configs."registry-1.docker.io".auth]
          username = "tdzhb@mytrashmailer.com"
          password = "tdzhb@mytrashmailer.com"
```


## And as docker config (e.g. for buildkitd)
```
mkdir /root/.docker
nano /root/.docker/config.json
```
Insert:
```
{
  "auths": {
    "https://index.docker.io/v1/": {
      "auth": "dGR6aGJAbXl0cmFzaG1haWxlci5jb206dGR6aGJAbXl0cmFzaG1haWxlci5jb20="
    }
  }
}
```
