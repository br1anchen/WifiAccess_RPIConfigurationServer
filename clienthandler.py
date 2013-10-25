#!/usr/bin/python
from xml.dom import minidom
import os
import json
import iptablesapi
import util

class ClientList:
    
    def __init__(self):
        self.clientlist = dict()
        self.ipaddress_pool = list()
        self.fillIPaddressPool()
        
    def addClient(self, client_json):      
        ip = self.ipaddress_pool.pop();
        client = Client(client_json, ip)
        #  Add static lease to DHCP lease file (mac, ip, lease time)
        add_lease_cmd = 'bash /etc/add_static_lease.sh %s %s 2m' % (client.mac, client.ip)
        iptablesapi.executeCommand(add_lease_cmd)
        self.clientlist[client.mac] = client

    def blockClient(self, key):

	self.removeClient(key);
	
	block_mac_cmd = 'bash /etc/block_static_lease.sh %s' % key
	iptablesapi.executeCommand(block_mac_cmd)
		
    
    def removeClient(self, key):
        
        if self.clientlist.has_key(key):
            client = self.clientlist[key]
            ip = client.ip
            self.ipaddress_pool.append(ip)
            #Remove static lease from lease file (mac)
            #NOT WORKING! 
            clear_lease_cmd = 'bash /etc/clear_dhcp_lease.sh %s' % client.mac
            iptablesapi.executeCommand(clear_lease_cmd)
            #Remove chains and rules from iptables 
            client.deleteInitialChainAndRules()
            del self.clientlist[key]
    	else:
		clear_lease_cmd = 'bash /etc/clear_dhcp_lease.sh %s' % key
		iptablesapi.executeCommand(clear_lease_cmd)
    
    def fillIPaddressPool(self):
        #Range for authorized subnet
        for x in xrange(60, 5, -1):
            ip = '10.0.0.%s' % x
            self.ipaddress_pool.append(ip)
        
    
class Client:
    
    def __init__(self, client_json, ip) :
        self.client_json = client_json
        self.ip = ip
        self.name = self.client_json['client']['client_info']['name']
        self.mac = self.client_json['client']['client_info']['mac']
        self.chain_name = 'client%s' %self.mac
        self.createInitialChainAndRules()
        self.convertJSONtoIptables()
    
    def convertJSONtoIptables(self):
        
        client_permissions = self.client_json['client']['permissions']
        allowAccess = client_permissions['access']['allow']      
        
        if (allowAccess):
            iptablesapi.acceptAllTrafficFromClient(self.chain_name)
        else:
            iptablesapi.blockAllTrafficFromClient(self.chain_name)
        
    def createInitialChainAndRules(self):
        iptablesapi.createNewClientChain(self.chain_name)
        iptablesapi.jumpFromBuiltInChainRule('FORWARD', self.chain_name, self.ip)
        
    def deleteInitialChainAndRules(self):
        iptablesapi.deleteClientChain(self.chain_name)
        iptablesapi.deleteJumpFromBuiltInChainRule('FORWARD', self.chain_name, self.ip)
