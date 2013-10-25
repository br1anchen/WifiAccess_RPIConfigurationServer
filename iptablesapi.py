#!/usr/bin/python
import subprocess

def createNewClientChain(chain_name):
        new_chain_cmd = 'iptables -N %s' % chain_name
        executeCommand(new_chain_cmd)
        
def deleteClientChain(chain_name):
        delete_chain_cmd = 'iptables -X %s' % chain_name
        executeCommand(delete_chain_cmd)
        
def jumpFromBuiltInChainRule(builtin_chain_name, custom_chain_name, client_ip):
        jump_rule_cmd1 = 'iptables -I %s -s %s -j %s'  % (builtin_chain_name, client_ip, custom_chain_name)
        jump_rule_cmd2 = 'iptables -I %s -d %s -j %s'  % (builtin_chain_name, client_ip, custom_chain_name)
        executeCommand(jump_rule_cmd1)
        executeCommand(jump_rule_cmd2)

def deleteJumpFromBuiltInChainRule(builtin_chain_name, custom_chain_name, client_ip):
        #delete_jump_rule_cmd = 'iptables -D %s -m mac --mac-source %s -j %s'  % (builtin_chain_name, client_mac, custom_chain_name)  
        delete_jump_rule_cmd1 = 'iptables -D %s -s %s -j %s'  % (builtin_chain_name, client_ip, custom_chain_name)
        delete_jump_rule_cmd2 = 'iptables -D %s -d %s -j %s'  % (builtin_chain_name, client_ip, custom_chain_name)
        executeCommand(delete_jump_rule_cmd1)
        executeCommand(delete_jump_rule_cmd2)

def acceptAllTrafficFromClient(chain_name):
    accept_traffic_cmd = 'iptables -I %s -j ACCEPT' % chain_name
    delete_drop_rule_cmd = 'iptables -D %s -j DROP' % chain_name
    executeCommand(accept_traffic_cmd)
    executeCommand(delete_drop_rule_cmd)

def blockAllTrafficFromClient(chain_name):
    block_traffic_cmd = 'iptables -I %s -j DROP' % chain_name
    delete_accept_rule_cmd = 'iptables -D %s -j ACCEPT' % chain_name
    executeCommand(block_traffic_cmd)
    executeCommand(delete_accept_rule_cmd)

def initialSetup():
    setup_cmd = 'sh /etc/network/if-up.d/iptables_setup.sh'
    executeCommand(setup_cmd)

def executeCommand(cmd):
     print 'executing command: %s' %cmd
     return_value =  subprocess.call(cmd, shell=True) 
    
     if return_value == 0:
        print 'success'
     elif return_value == 1:
        print 'something went wrong'
