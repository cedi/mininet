#!/usr/bin/python

"""
main.py: Run the ipsec network

This file is the entry point for the IPsec testing network

The Network contains a IPsecNetworkTopo topology, which is described in
ipsectopo.py.

It then establishes all tunnels and perform an iperf test to generate some esp
traffic

Each network leaf consists of a single IPsec gateway with a single host behind
it to generate esp traffic.
"""

# Python includes
import re
from optparse import OptionParser

# Mininet includes
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.link import Intf
from mininet.cli import CLI
from mininet.util import quietRun
from mininet.log import error

# actual loadtest includes
from ipsectopo import IPsecNetworkTopo

def checkIntf(intf):
    '''
    Make sure intf exists and is not configured.
    '''
    config = quietRun('ifconfig %s 2>/dev/null' % intf, shell=True)
    if not config:
        error('Error:', intf, 'does not exist!\n')
        return False

    ips = re.findall(r'\d+\.\d+\.\d+\.\d+', config)
    if ips:
        error('Error:', intf, 'has an IP address, and is probably in use!\n')
        return False

    return True

def connectSwitchesToEths(net, interfaces):
    '''
    Connects a physical interface to a openVSwitch
    '''
    switchFormat = "sw{}"
    for sw in range(1, len(interfaces) + 1):
        swName = switchFormat.format(sw)
        switch = net.getNodeByName(swName)
        eth = interfaces[sw-1]

        info("*** Connect sw '{}' to iface '{}'\n".format(swName, eth))
        if checkIntf(eth):
            Intf(eth, node=switch)
        else:
            exit(1)


def run(interfaces, gateways, hosts):
    """
    Run the IPsec test network
    """

    info("*** Setup phase\n")
    topo = IPsecNetworkTopo(interfaces=interfaces, gateways=gateways,
                            hosts=hosts)

    info("*** Configure phase\n")
    net = Mininet(topo=topo)

    # bridge eths to switches
    connectSwitchesToEths(net, interfaces)

    info("*** Starting mininet\n")
    net.start()

    #r1 = net.getNodeByName('sw_1_r1')
    #h1 = net.getNodeByName('sw_1_r1_h1')
    #h2 = net.getNodeByName('sw_1_r1_h2')
    #r2 = net.getNodeByName('sw_1_r2')
    #h3 = net.getNodeByName('sw_1_r2_h1')
    #h4 = net.getNodeByName('sw_1_r2_h2')

    #r3 = net.getNodeByName('sw_2_r1')
    #h5 = net.getNodeByName('sw_2_r1_h1')
    #h6 = net.getNodeByName('sw_2_r1_h2')
    #r4 = net.getNodeByName('sw_2_r2')
    #h7 = net.getNodeByName('sw_2_r2_h1')
    #h8 = net.getNodeByName('sw_2_r2_h2')

    #net.ping((r1, h1, h2))
    #net.ping((r2, h3, h4))
    #net.ping((r3, h5, h6))
    #net.ping((r4, h7, h8))

    CLI(net)
    net.stop()

def optionParse():
    '''
    parse the command line options
    '''
    parser = OptionParser()

    parser.add_option('-i', '--interfaces', dest="interfaces", action="append",
                      default=[])

    parser.add_option('-n', '--nodes', dest="hosts", action="store",
                      default="1", type="int")

    parser.add_option('-g', '--gateways', dest="gateways", action="store",
                      default="1", type="int")

    options, args = parser.parse_args()

    return options

if __name__ == '__main__':
    setLogLevel('info')
    args = optionParse()
    run(args.interfaces, args.gateways, args.hosts)
