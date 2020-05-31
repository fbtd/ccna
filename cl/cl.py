#!/usr/bin/env python3

import sys, time, fcntl, os
from subprocess import *

DEBUG = False

# ^] = 0x1B

addr = sys.argv[1]
port = sys.argv[2]
int(port)

def set_nonblocking(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL,  os.O_NONBLOCK | flags)

op = print
def print(*args, **kwargs):
    if DEBUG: op(*args, **kwargs)

p = Popen(["telnet", addr, str(port)], stdin=PIPE, stdout=PIPE, stderr=PIPE)
set_nonblocking(p.stdout.fileno())

state = "not connected"
conf  = list()
lines = list()

def send(msg, check_echo=True, add_crnl=True):
    print(f"sending: {msg}")
    msg = msg.encode()
    if add_crnl: msg = msg + b"\r\n"
    p.stdin.write(msg)
    p.stdin.flush()
    # wait for echo
    time.sleep(0.5)
    if len(msg) - 2 and check_echo:
        echo = p.stdout.read(len(msg)-2)
        print(echo, msg[:-2])
        assert echo == msg[:-2], "wrong echo"

def get_line():
    if lines:
        p_out = lines.pop()
    else:
        time.sleep(0.1)
        p_out = p.stdout.readline().decode()
    print(f"getting: {p_out}")
    return p_out

def put_line(msg):
    lines.push(msg)

def get_all_lines():
    lines = list()
    l = True
    while l:
        l = get_line()
        if l:
            lines.append(l)
    print(lines)
    return lines
# connect
get_all_lines()

# get to console
send("")
send("")
time.sleep(1)

l = get_all_lines()[-1]
#l = l.rstrip("\r\n")

if l[-1] == '>':
    send("en")
elif l[-1] != '#':
    send("end")
    l = get_all_lines()[-1]
assert l[-1] == '#', "should be in prviledged mode!"
prompt = l

send("terminal length 0")
get_all_lines()
send("sh run")
time.sleep(5)
configuration = get_all_lines()[:-2]
print(".........")
op("".join(configuration))
exit(0)
