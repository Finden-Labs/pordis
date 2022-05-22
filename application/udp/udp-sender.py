# ----- sender.py ------
#!/usr/bin/env python
from socket import *
import sys

s = socket(AF_INET,SOCK_DGRAM)
host = "0.0.0.0"
port = 9999
buf =1024
addr = (host,port)

file_name=b'main.py'

s.sendto(file_name,addr)

f=open(file_name,"rb")
data = f.read(buf)
while (data):
    if(s.sendto(data,addr)):
        print("sending ...")
        data = f.read(buf)
s.close()
f.close()