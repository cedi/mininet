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

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI

from ipsectopo import IPSecNetworkTopo


def run():
    """
    Run the IPsec test network
    """
    topo = IPsecNetworkTopo()
    net = Mininet( topo=topo )

    net.start()

    #h1 = net.getNodeByName('h1')
    #h2 = net.getNodeByName('h2')
    #h3 = net.getNodeByName('h3')

    #net.iperf((h1, h2))
    #net.iperf((h1, h3))
    #net.iperf((h2, h3))

    #CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()
