# Notes


## SSH
add support for old Key Exchange Algorithms and Ciphers  
`ssh -o KexAlgorithms=diffie-hellman-group1-sha1 -o Ciphers=3des-cbc r@s3`

or add
```
KexAlgorithms=+diffie-hellman-group1-sha1
Ciphers=+3des-cbc
```
to ~/.ssh/config
