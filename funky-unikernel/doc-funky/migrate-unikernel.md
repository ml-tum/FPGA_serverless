## Migrate a QEMU VM using QEMU montor over unix sockets

One of the features of QEMU is [migration](https://github.com/qemu/qemu/blob/master/docs/devel/migration.rst). Migration consists of 2 parts, saving the vm state and loading the vm state. QEMU can also do a live migration where the vm migrates without stopping. Any of the 4 supported transports can be used for it. On the other hand we can also make an offline migration where the state of the vm can be saved as a file (it is just a bytestream) and using that file we can load later the vm state. The most important thing about migration in QEMU is that when we spawn the new vm that will load the saved state we have to use the exact same options as in the initial QEMU instance.

## QEMU monitor over unix sockets

One of the ways to start the migration is using [QEMU monitor](https://https://qemu-project.gitlab.io/qemu/system/monitor.html). The monitor lets a user control the instance of a virtual machine, adding new devices, requesting stats and more. Usually we can invoke the monitor by holding down the Ctrl and Alt keys (or whatever the "mouse grab" keystrokes are), and pressing `Shift-2`but we can use it over network or unix sockets too. We will use a unix socket in our case and we will start the vm adding the option `-monitor unix:/tmp/qemu-sock,server,nowait`.
```
qemu-system-x86_64 [...] -monitor unix:/tmp/qemu-sock,server,nowait
```
Afterwards we can send commands to this vm using the `/tmp/qemu-sock` socket. We can use the `nc` command or `socat`. If we just want to send one command we can use them like this:
```
##For nc
echo -e "[command]" | nc -w 0 -U /tmp/qemu-sock
##For socat
echo -e "[command]" | socat -u - unix-connect:/tmp/qemu-sock
```

Breaking down the command for `nc`:
- -w 0 is used to close the connection with the socket after we send our command 
- -U indicates that we will use a unix socket.

Breaking down the command for `socat`:
- -u is used for unidirectional mode.As a result we will only write to second address and read from first one.
- \- we only have one address, so we disable the first one.
- unix-connect: the unix socket which we want to connect to.

Bringing everything together we can migrate a IncludeOS unikernel with the following commands. At first we will start the vm with the -qmp option 
```
qemu-system-x86_64 -cpu host -enable-kvm -m 32 -nodefaults -display none -serial stdio -kernel ${INCLUDEOS_PREFIX}/includeos/chainloader -append "-initrd hello.bin" -initrd hello.bin -monitor unix:/tmp/qemu-sock,server,nowait
```
Afterwards we will invoke the migration command, saving the vm state in a file called `/tmp/statefile`.
```
##For nc
echo -e "migrate \"exec:cat > /tmp/statefile\"\n" | nc -w 0 -U /tmp/qemu-sock
##For socat
echo -e "migrate \"exec:cat > /tmp/statefile\"\n" | socat -u - unix-connect:/tmp/qemu-sock
```
After saving the vm state we can load it to a new QEMU instance adding the option `-incoming "exec: cat /tmp/statefile". It is important to use the same options as the initial vm.

```
qemu-system-x86_64 -cpu host -enable-kvm -m 32 -nodefaults -display none -serial stdio -kernel ${INCLUDEOS_PREFIX}/includeos/chainloader -append "-initrd hello.bin" -initrd hello.bin -monitor unix:/tmp/qemu-sock,server,nowait -incoming "exec: cat /tmp/statefile"
``` 
