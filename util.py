#!/usr/bin/python
import re
import httplib
import socket
import fcntl
import struct
import urllib



def getIpAddress(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915, # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
        )[20:24])

def getMacAddress(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', ifname[:15]))
        return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]


def getMacAddressFromIP(ip):
    dhcpleases = open("/var/lib/misc/dnsmasq.leases", "r")

    for line in dhcpleases:
        if (ip in line):
                s = line.split()
                mac = s[1]
                return mac
            
def parseBoolString(theString):
    return theString[0].upper()=='T'

