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

from ipsecgateway import IPsecRouter

"""
Global Variables for the correct naming formats
"""
switchFormat = "s{}"
gatewayFormat = "r{}"
hostFormat = "sn{}-h{}"
ifFormat = "{}-eth{}"

"""
The IP Address format.

The base Address is 10.0.0.0/8 and then substituted to
10.0.0.0/16 for the IPsec gateway subnet and
10.0.0.0/24 for the Subnets behind an IPsec gateway

Example:
    10.1.0.1/16 is the WAN IP Address of the first IPsec gateway

    10.1.1.1/24 is the LAN IP Address of the first IPsec gateway in the first
        host Subnet

    10.1.1.2/24 is the LAN IP Address of the first host in the first host
        subnet on the first IPsec gateway gateway

    10.1.1.254/24 is the LAN IP Address of the last host in the first host
        subnet on the first IPsec gateway gateway
"""
ipFormat = "10.{}.{}.{}/{}"

class IPsecNetworkTopo( Topo ):
    """
    An network Topo which connects clients to an ipsec gateway
    """

    def addIPsecGateway( self, name ):
        "Add a IPsecRouter component to the network"
        return self.addHost( name )

    def build( self, **_opts ):
        """
        Builds the (virtual) network

        *** named arguments ***
        :switch: the number of switches. Ideally is to use the same number as
            your machine physical ports have.
            Parameter is optional. Default = 1 switch

        :gateways: number of gateways. Must be between 1 and 254
            Parameter is optional. Default = 1 gateway

        :hostsubnets: number of host subnets. Must be between 1 and 254
            Parameter is optional. Default = 1 subnet

        :hostsinsubnet: (optional) must be between 1 and 253, parameter is
            Parameter is optional. Default = 1 host
        """

        switchCnt = _opts.get('switches', 1)
        gatewayCnt = _opts.get('gateways', 1)
        hostSubnetCnt = _opts.get('hostsubnets', 1)
        hostsInSubnetCnt = _opts.get('hostinsubnet', 1)

        info("*** Switches: {}, Gateways: {}, Subnets per GW: {}, Hosts in Subnet: {}\n".format(switchCnt, gatewayCnt, hostSubnetCnt, hostsInSubnetCnt))
        switches = self.addVSwitch(switchCnt, gatewayCnt, hostSubnetCnt,
                hostsInSubnetCnt)

    def addVSwitch( self, switches, gateways, hostsubnets, hostsinsubnet):
        for sw in range( 1, switches + 1 ):
            swName = switchFormat.format( sw )
            info( "*** Adding switch: " + swName + "\n" )

            switch = self.addSwitch( swName )
            self.addGateway( switch, gateways, hostsubnets, hostsinsubnet )

    def addGateway( self, switch, gateways, hostSubnets, hostsInSubnet):
        for gw in range( 1, gateways + 1):
            gwName = gatewayFormat.format( gw )

            info( "*** Adding gateway: " + gwName + "\n")

            # determine the first interface on the gateway
            gwDefIfaceName = ifFormat.format( gwName, 0 )

            # determine the WAN IP of the IPsec gateway
            gwIP = ipFormat.format( gw, 0, 1, 16 )

            # add the gateway and link it to the switch
            gateway = self.addIPsecGateway( gwName )

            info( "*** Add Link ({}, {})\n".format( switch, gateway ) )
            self.addLink( switch, gateway,
                    intfName2=gwDefIfaceName,
                    params2={ 'ip' : gwIP } )

            self.addHosts( gateway, gw, hostSubnets, hostsInSubnet )

    def addHosts( self, gateway, gwIpPortion, hostSubnets, hostsInSubnet):
        for sn in range( 1, hostSubnets + 1 ):
            lanIpOfGw = ipFormat.format( gwIpPortion, sn, 1, 24 )
            # lanIfaceNameOfGw = ifFormat( hName, 0 )

            for h in range( 1, hostsInSubnet + 1 ):
                hName = hostFormat.format( sn, h )

                # determine the LAN interface name for the host
                hIfaceName = ifFormat.format( hName, 0 ) # is always hostname-eth0
                gwIfaceName = ifFormat.format( str(gateway), h )

                # determine the WAN IP of the IPsec gateway
                hIP = ipFormat.format( gwIpPortion, sn, h + 1, 24 )
                gwIP = ipFormat.format( gwIpPortion, sn, h, 24 )

                # determine the default route for this subnet
                hDefRoute = "via {}".format( lanIpOfGw )

                # add the gateway and link it to the switch
                host = self.addHost( hName, ip=hIP, defaultRoute=hDefRoute )

                info( "*** Add Link ({}, {})\n".format( gateway, host ) )
                self.addLink( host, gateway,
                        intfName2=gwIfaceName,
                        params2={ 'ip': gwIP } )


