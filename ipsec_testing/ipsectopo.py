#!/usr/bin/python

"""
ipsectopo.py: Network Topo for the IPsec network setup

This creates a network with multiple ipsec gateways connected to a single switch
and one host object behind each ipsec gateway which can be used to generate
esp traffic.

Here a example topology:

    +----------------------------------------------------+
    |                     openVSwitch                    |
    +----------------------------------------------------+
                               |
            +------------------------------------+
            |                  |                 |
    +---------------+  +---------------+ +---------------+
    | IPsecGateway1 |  | IPsecGateway2 | | IPsecGateway3 |
    +---------------+  +---------------+ +---------------+
            |                  |                 |
        +-------+          +-------+         +-------+
        | Host1 |          | Host2 |         | Host3 |
        +-------+          +-------+         +-------+
"""


from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI


class IPsecNetworkTopo( Topo ):
    """
    An network Topo which connects clients to an ipsec gateway
    """

    def build( self, **_opts ):

        defaultIP = '192.168.1.1/24'  # IP address for r0-eth1
        router = self.addNode( 'r0', cls=LinuxRouter, ip=defaultIP )

        s1, s2, s3 = [ self.addSwitch( s ) for s in ( 's1', 's2', 's3' ) ]

        self.addLink( s1, router, intfName2='r0-eth1',
                      params2={ 'ip' : defaultIP } )  # for clarity

        self.addLink( s2, router, intfName2='r0-eth2',
                      params2={ 'ip' : '172.16.0.1/12' } )

        self.addLink( s3, router, intfName2='r0-eth3',
                      params2={ 'ip' : '10.0.0.1/8' } )


        h1 = self.addHost( 'h1', ip='192.168.1.100/24',
                           defaultRoute='via 192.168.1.1' )

        h2 = self.addHost( 'h2', ip='172.16.0.100/12',
                           defaultRoute='via 172.16.0.1' )

        h3 = self.addHost( 'h3', ip='10.0.0.100/8',
                           defaultRoute='via 10.0.0.1' )

        for h, s in [ (h1, s1), (h2, s2), (h3, s3) ]:
            self.addLink( h, s )

def run():
    "Test linux router"

    info("******************************************************************\n")
    topo = NHostTopo(hosts=4, max_hosts_per_sw=2)
    net = Mininet(topo=topo)

    net.start()
    net.iperf()
    net.stop()

    #topo = NetworkTopo()
    #net = Mininet( topo=topo )  # controller is used by s1-s3

    #net.start()

    #h1 = net.getNodeByName('h1')
    #h2 = net.getNodeByName('h2')
    #h3 = net.getNodeByName('h3')

    #net.iperf((h1, h2))
    #net.iperf((h1, h3))
    #net.iperf((h2, h3))

    #info( '*** Routing Table on Router\n' )
    ##CLI( net )
    #net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()
