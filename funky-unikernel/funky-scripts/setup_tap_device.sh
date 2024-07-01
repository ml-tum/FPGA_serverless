#!/bin/bash

sudo ip tuntap add tap100 mode tap user $USER
sudo ip link set dev tap100 up
sudo ip addr add 10.0.0.1/24 dev tap100
