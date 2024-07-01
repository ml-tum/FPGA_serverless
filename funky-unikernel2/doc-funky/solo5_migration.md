## Implementation of migration mechanism in Solo5

[Solo5](https://github.com/Solo5/solo5) ukvm is a lightweight hypervisor which
uses KVM and it defines its own hypercall ABI. In funky project solo5 will be
used as the hypervisor for the FPGA apps-unikernels which will be deployed.

One of the goals of the funky project is to enable task migration and scheduling
of FPGA applications among distributed nodes. In that context the hypervisor
needs to provide a migration mechanism.

# Adding migration in Solo5

Since the scheduler was not yet implemented, it was not easy to invoke the start
of migration in a running Solo5 instance. In order to do that a QEMU monior like
interface was created. Using this interface a user could send commands to the
Solo5 hypervisor. 

A new command line option `--mon=<path_to_socket>` has been added. This command
specifies the UNIX socket which will be used to send commands to the running
instance. A new thread is created, which is responsible to listen for commands
in that socket and later execute them.  Consequently if someone uses the above
option Solo5 will run with 2 threads:
1. The vCPU thread which executes the vCPU loop, using KVM.
2. The monitor thread which listens for commands in the socket.

As long as live migration was not suitable for the project, when the migration
starts the guest should stop its execution. KVM does not provide any API to
force a guest to stop  On the other hand when the thread which  executes the
vCPU loop receives a signal, KVM will force guest to VMEXIT for external
interrupt and then it will return the control to the process which is
responsible to handle the signal. As a result signals were used to cause
firstly a VMEXIT and secondly a KVM exit and return the control to Solo5. In
order to test this 2 commands were introduced in the monitor interface:
1. stop: `echo stop | socat -u - unix-connect:<path_to_socket>`. It stops the
   execution of the guest
2. resume: `echo resume | socat -u - unix-connect:<path_to_socket>`. It resumes
   the execution of a stopped guest.

Against this background the vCPU loop thread registers a signal handler for
SIGUSR1, which it does not do anything more rather than just consuming the signal.
The role of signal is to return the control to Solo5. Moreover an atomic 
global variable `vm_state` will keep track of the current state of the guest.
This variable can get 4 values:
- 0: Guest is running
- 1: Guest should stop
- 2: Guest should resume execution
- 3: Guest should migrate

When the monitor thread receives the stop command it changes the value of the
global variable to 1 and then sends a signal to vCPU loop thread. As described
before the signal will force the KVM\_RUN to return with `errno == -EINTR`. VCPU
thread will notice the change in `vm_state` and it will wait for a new signal
and a change to `vm_state` variable. 

The resume command will result to a new signal from monitor thread to vCPU
thread. Then the later will notice the cahnge in `vm_sate` and continue the
execution of vCPU loop.

Special handling was required when the guest was polling in Solo5. In case
guest just waits for an event the vCPU loop is blocked in the poll hypercall.
Under this condition the SIG\_USR1 signal had to be unblocked when ppoll was
called and the variable `vm_state` had to be checked after every hypercall.

Following the same logic the `savevm <file>` command was added. This command will
result in the creation of migration file which can be later used to load a VM.
The contents of the file are listed below:
1. REGS of vCPU
2. SREGS of vCPU
3. TSC MSR
4. Page size used for guest pages.
5. Total dirty saved pages of guest RAM.
6. First dirty saved RAM page
7. Second dirty saved RAM page 
8. other dirty saved RAM pages

Saving all the guest RAM pages would be overkill. To avoid that only the pages
which the guest has touched will be saved. In order to find these pages the
migration mechanism makes use of
[mincore](https://man7.org/linux/man-pages/man2/mincore.2.html) function.

*if the filename after savevm command is not a full path then the file will be
created under the same directory where the Solo5 instance was invoked*

At last the `--load=<file>` option was introduced in the Solo5 command line
options. This option does the same things as savevm in a reverse way. After
setting up the guest Solo5 will read the contents of the migration file and
restore the state of the guest which was migrated. An important note is that
Solo5 applys some memory permissions in guest's RAM when loading the elf file.
These permissions might not let the migration to finish, since some pages might
need to be overwritten. For that purpose the memory permissions are enforced
after the completion of migration.
