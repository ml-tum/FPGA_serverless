.PHONY: all
all: primary daemon rest

SCHED_CFLAGS  += -Wall -Werror -O2
SCHED_LDFLAGS := -lpthread

primary: primary.o common.o
	$(CC) $(SCHED_LDFLAGS) $^ -o $@

daemon: daemon.o common.o
	$(CC) $(SCHED_LDFLAGS) $^ -o $@

primary.o: primary.c
	$(CC) $(SCHED_CFLAGS) -D_POSIX_C_SOURCE=199309L -std=c99 -c $< -o $@

daemon.o: daemon.c
	$(CC) $(SCHED_CFLAGS) -c $< -o $@

common.o: common.c
	$(CC) $(SCHED_CFLAGS) -std=c99 -c $< -o $@

rest: rest.go
	go build rest.go

.PHONY: clean

clean:
	rm -f primary daemon rest *.o
