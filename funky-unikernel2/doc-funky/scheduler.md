## Funky scheduler

Following a centralized architecture the scheduler consists of 2+1 parts the
primary, the daemon and a simple http server. Primary is responsible to receive
new tasks, apply the scheduling policy and communicate with the available nodes
in order to execute the selected task. The daemon resides in each node and
communicates with the primary scheduler waiting for new commands or reporting
the state of running tasks. The http server, should be executed in the same node
as the primary scheduler andit provides an upload endpoint which can be used to
upload new binaries and add a new task.

Even if scheduler is inside Solo5 repo, it is seperated having its own directory
`scheduler` and is not built along with Solo5.

### How to build the scheduler
First of all we have to build the scheduler which is as simple as running make
inside the scheduler directory. THe result will be 3 binaries:
- primary: The main scheduler.
- daemon: The daemon which needs to be executed in every node
- rest: http server

*Notice: Depending on the operating system, building might require to replace
lpthread with pthread in scheduler's Makefile*

### How to use the scheduler
THe most important part of the scheduler is the primary binary. We can simple
execute primary scheduler by just running the binary, without any arguments.
Secondly we need to setup the execution environment in every available node of
our cluster. Firstly we need an up to date version of Solo5 which can easily get
built running make inside the top directory of the repository. After a
successful build of SOlo5 we will set the environment variable `UKVM_BIN` to
point to the ukvm binary which was produced. This variable will be used from the
daemon in order to execute the tasks. 
```
export UKVM_BIN=<path_to_ukvm_binary>
```
Secondly we will need 2 tap interfaces for the guests (tap0 and tap1). Dameon
will spawn ukvm using mostly tap0 but in case of a task eviction tap1 will be used.
```
sudo ip tuntap add dev tap0 mode tap
sudo ip tuntap add dev tap1 mode tap
sudo ip link set dev tap0 up
sudo ip link set dev tap1 up
```
At last we need to execute the daemon which will communicate with the primary
scheduler. Daemon requires 2 arguments:
- the ip address of the server where primary runs
- and the port which primary listens to (default is 4217)

```
daemon -i <ip_address_of_primary_server> -p 4217
```

*Optional: We can also run the http server simply executing the `rest` binary.*

#### Deploy a task

We can directly communicate with the primary scheduler in order to add a new task.
Primary scheduler listens at `/tmp/front.sock` socket and it accepts 2 types of
commands:
- Deploy a new task
- Request the migration of a task to a different node

The syntax to deploy a new command is:
```
echo -n "New: <path_to_binary> priority: <0_or_1> args: <cmd_arguments>" | socat -u - unix-connect:/tmp/front.sock
```

where `cmd_arguments` are the arguments of the task we want to deploy.

Task with priority 0 will be executed first and tasks with priority 1 will get
executed only if there are not any other available high priority tasks. In case
there are no available nodes and a new task has high priority then, if a node
executes a low priority task, the task will be evicted in favor of high priority
one. After high priority finishes its execution the low priority task wil
lresume its execution automatically.

Moreover a user can request the migration of a running task to an available node
with the folllowing command:

```
echo -n "Task: <task_id> Node: <node_id>" | socat -u - unix-connect:/tmp/front.sock
```
