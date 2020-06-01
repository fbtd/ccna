#!/usr/bin/env python3

import sys, time, fcntl, os
import argparse
from subprocess import *

parser = argparse.ArgumentParser()
parser.add_argument("host", help="target hostname")
parser.add_argument("port", help="target port", type=int)
parser.add_argument("-d", "--debug", help="enable debugging output",
                                     action="store_true")
parser.add_argument("-s", "--show-run", "--sh-run", dest="sh_run",
                                    help="show running configuration",
                                    action="store_true")
parser.add_argument("-l", "--load", help="load configuration from stdin",
                                     action="store_true")
args = parser.parse_args()

def set_nonblocking(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL,  os.O_NONBLOCK | flags)

op = print
def print(*arg, **kwargs):
    if args.debug: op(*arg, **kwargs)

p = Popen(["telnet", args.host, str(args.port)], stdin=PIPE, stdout=PIPE, stderr=PIPE)
set_nonblocking(p.stdout.fileno())

state = "not connected"
lines = list()

def send(msg, sleep_time=0.5, check_echo=True, add_crnl=True):
    print("sending: ", msg.rstrip("\r\n"))
    msg = msg.encode()
    if add_crnl: msg = msg + b"\r\n"
    p.stdin.write(msg)
    p.stdin.flush()
    # wait for echo
    if len(msg) - 2 and check_echo:
        time.sleep(sleep_time)
        echo = p.stdout.read(len(msg)-2)
        print(echo, msg[:-2])
        assert echo == msg[:-2], "wrong echo"

def get_line():
    if lines:
        p_out = lines.pop()
    else:
        time.sleep(0.05)
        p_out = p.stdout.readline().decode()
    print("getting: ", p_out.rstrip("\r\n"))
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

def connect_priviledged():
    get_all_lines()
    send("")
    send("")
    time.sleep(1)
    l = get_all_lines()[-1]

    if l[-1] == '>':
        send("en")
        l = get_all_lines()[-1]
    elif ")#" in l:
        send("end")
        l = get_all_lines()[-1]

    assert l[-1] == '#', "should be in prviledged mode!"
    send("terminal length 0")
    get_all_lines()

def print_running_config():
    send("sh run")
    time.sleep(5)
    configuration = get_all_lines()[4:-2]
    print(".........")
    op("".join(configuration))

def load_config():
    send("write erase")
    get_all_lines()
    send("conf t")
    for line in sys.stdin:
        line = line.rstrip("\r\n")
        send(line, check_echo=False, sleep_time=0.1)
        for ret_line in get_all_lines():
            assert "Invalid input detected" not in ret_line
            assert "Incomplete command" not in ret_line
            assert "Ambiguous command" not in ret_line
    time.sleep(1)
    get_all_lines()

connect_priviledged()
if args.sh_run: print_running_config()
if args.load: load_config()
