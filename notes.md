# Notes

## Lab setup

### Traffic

using netcat
pi@rp1:~$ `nc -lk 8080 `
pi@rp2:~$ `vmstat -tn 2 | nc rp1 8080`

#### TODO:
 * ping pong script

### Sniffer
enable eth0
```
sudo ip link set eth0 up
sudo ip link set eth0 promisc on
```
tcpdump(8) capture
`sudo tcpdump -i eth0 -w capture.pcap -c 20  "host rp1 or host rp2"`

## SSH
add support for old Key Exchange Algorithms and Ciphers  
`ssh -o KexAlgorithms=diffie-hellman-group1-sha1 -o Ciphers=3des-cbc r@s3`

or add
```
KexAlgorithms=+diffie-hellman-group1-sha1
Ciphers=+3des-cbc
```
to ~/.ssh/config
