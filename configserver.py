#!/usr/bin/python
import httplib
import socket
import fcntl
import struct
import urllib
import json
import clienthandler
import util
import iptablesapi
import time, threading


class Server:
    
    def __init__(self, client_list=None):
        
        self.clientlist = clienthandler.ClientList()
        iptablesapi.initialSetup()
        self.isInitialRequestSent = False
        self.bootFlag = 0;
        

    def getClientPermissions(self):
            #Start polling thread
            threading.Timer(5.0, self.getClientPermissions).start()
            
            print 'Boot Flag: %s' % self.bootFlag
            
            httpServ = httplib.HTTPConnection("129.241.200.170", 8080)
            httpServ.connect()
            payload = urllib.urlencode({'macaddress': util.getMacAddress('eth0'), 'boot_flag' : self.bootFlag})
            headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
            request = httpServ.request('POST', '/rpi/getclients.php', payload , headers)
            response = httpServ.getresponse()
            print 'Permissions Polling Request Sent'
            
            if response.status == httplib.OK:
                array = response.read()
                data = json.loads(array)
                self.bootFlag = 1;
                
                if len(data) == 0:    
                    print 'No client updates recieved from server'
                
                else:
                    
                    for str in data:
                    
                        client_string = json.dumps(str)
                        print 'Client from server : %s' % client_string
                        client_json = json.loads(client_string)
                        key = client_json ['client']['client_info']['mac']
                        status = client_json ['client']['permissions']['access']['allow']
	
                        if status == True:
                        	self.clientlist.removeClient(key)
                        	self.clientlist.addClient(client_json)
                    	else:
				self.clientlist.blockClient(key)				

                        reload_leases_cmd = 'bash /etc/reload_dhcp_leases.sh %s' % key 
                        iptablesapi.executeCommand(reload_leases_cmd)
                
            httpServ.close()
            
    def sendBindingUpdate(self):
            #Start posting thread
            threading.Timer(60.0, self.sendBindingUpdate).start()
            
            httpServ = httplib.HTTPConnection("129.241.200.170", 8080)
            httpServ.connect()
            payload = urllib.urlencode({'macaddress': util.getMacAddress('eth0'), 'ipaddress': util.getIpAddress('eth0')})
            headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
            request = httpServ.request('POST', '/rpi/bindingupdate.php', payload, headers)
            
            response = httpServ.getresponse()
            print 'Binding Update Sent'
            if response.status == httplib.OK:
                print "Binding Update Success"
            
            httpServ.close()


serv = Server()
serv.getClientPermissions()
serv.sendBindingUpdate()
