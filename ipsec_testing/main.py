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

from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI

from ipsectopo import IPsecNetworkTopo


def run():
    """
    Run the IPsec test network
    """

    info( "*** Setup phase\n")
    topo = IPsecNetworkTopo(switches=2, gateways=2, hosts=2)

    info( "*** Configure phase\n")
    net = Mininet( topo=topo )

    info( "*** Starting mininet\n")
    net.start()

    r1 = net.getNodeByName('s1_r1')
    h1 = net.getNodeByName('s1_r1_h1')
    h2 = net.getNodeByName('s1_r1_h2')
    r2 = net.getNodeByName('s1_r2')
    h3 = net.getNodeByName('s1_r2_h1')
    h4 = net.getNodeByName('s1_r2_h2')

    r3 = net.getNodeByName('s2_r1')
    h5 = net.getNodeByName('s2_r1_h1')
    h6 = net.getNodeByName('s2_r1_h2')
    r4 = net.getNodeByName('s2_r2')
    h7 = net.getNodeByName('s2_r2_h1')
    h8 = net.getNodeByName('s2_r2_h2')

    net.ping( ( r1, h1, h2 ) )
    net.ping( ( r2, h3, h4 ) )
    net.ping( ( r3, h5, h6 ) )
    net.ping( ( r4, h7, h8 ) )

    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()
