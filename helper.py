# Helper functions and classes for PyScan...
from __future__ import annotations
import ssl
import urllib
import os
import sys
import io
import http

import socket as s


class HTTPDirBuster:
    """This class contains UI stuff but also state information,doesnt use sockets!!
        Basically does the same work as PyScan class instance but for the enumeration.
        Pyscan->HTTPDirBuster--> State
                            |----> UI elements
    """
    
    sslcont=ssl.create_default_context()
    def __init__(self,url: str,ext="html": str)-> dict:
        self.url=url
        self.ext = ext
        
    
    def bust_directories(self,wordlist):
        for w in wordlist:
            self.httpsconn=http.client.HTTPSConnection(url, 443, timeout=30,context=self.sslcont)
            url =self.url + ("/"+w+"."+self.ext)
            self.httpsconn.request("GET", url, body=None,encode_chunked=False)
        

class HostsDatabase:
    filename="./hosts.db"
    
    def __init__(self):
        self.entries=[]
        if os.path.isfile(self.filename):
            self.load_db()
        else:
            with open(self.filename,mode="x",encoding="utf8") as fh:
                fh.close()
            self.load_db()
            

    def save_db(self):
        with open(self.filename,mode="w",encoding="utf8") as fh:
            fh.write(json.dumps(self.entries))

    def load_db(self):
        with open(self.filename,mode="r",encoding="utf8") as fh:
            fdat=fh.read()
            if not fdat == "":
                self.entries = json.loads(fdat)
    
    def new_entry(self,ipaddr: str): 
        self.entries.append({"ipaddr":ipaddr,"hostname": host, "openports": [], "services": {} })
        self.save_db()


class ProbeSocket:
    """Placeholder class only
      - coded for clarity, not efficiency
    """

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        # Attempt connection
        self.sock.connect((host, port))

    def send_stress(self, payload):
        #If we can connect try to send arbitrary data
        totalsent = 0
        while totalsent < MSGLEN:
            sent = self.sock.send(payload[totalsent:])
            if sent == 0:
                return False
                #raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent
        return True

    def myreceive(self):
        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == b'':
                return False
                #raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)
    
# HELPER FUNCS ==== 
def ip2domain(ip):
    """
    Returns a domain name matching the provided entry.

    >>> ip2domain('127.0.0.1')
    'localhost'

    """
    return s.getfqdn(ip) or False

def domain2ip(domname):
    """
    Returns the IP address of a specified domain name

    >>> domain2ip('localhost')
    127.0.0.1
    """
    return s.gethostbyname(domname)[0]

def port_service(port):
    return s.getservbyport(port)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
