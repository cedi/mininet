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
    topo = IPsecNetworkTopo(switches=1, gateways=1,
            hostsubnets=1, hostinsubnet=1)

    info( "*** Configure phase\n")
    net = Mininet( topo=topo )

    info( "*** Starting mininet\n")
    net.start()

    r1 = net.getNodeByName('r1')
    h1 = net.getNodeByName('sn1_h1')
    #h2 = net.getNodeByName('sn1-h2')

    #info( "*** r1 ip a ls\n" )
    #info( r1.cmd( 'ip a ls' ) + "\n" )
    #info( "*** r1 ip r ls\n" )
    #info( r1.cmd( 'ip r ls' ) + "\n" )

    #info( "*** h1 ip a ls\n" )
    #info( h1.cmd( 'ip a ls' ) + "\n" )
    #info( "*** h1 ip r ls\n" )
    #info( h1.cmd( 'ip r ls' ) + "\n" )

    #info( "*** h1 ping r1\n" )
    #info( h1.cmd( "ping -c 1 -I 10.1.1.2 10.1.1.1" ) )
    #info( r1.cmd( "ping -c 1 -I 10.1.1.1 10.1.1.2" ) )

    net.ping( ( h1, r1 ) )
    #net.ping( ( h1, h2 ) )
    #net.ping( ( h2, r1 ) )

    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()
