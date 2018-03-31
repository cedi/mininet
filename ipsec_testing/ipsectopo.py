#!/usr/bin/python

"""
ipsectopo.py: Network Topo for the IPsec network setup

This creates a network with multiple ipsec gateways connected to a single switch
and one host object behind each ipsec gateway which can be used to generate
esp traffic.

Here a example topology:

                                +--------------+
                                |  Hostsystem  |
                                |     eth1     |
                                +------+-------+
                                       |
                             +---------+---------+
                             |    openVSwitch    |
                             +---------+---------+
                                       |
                             +---------+---------+
                             |                   |
                      +------+--------+  +-------+-------+
                      | IPsecGateway1 |  | IPsecGateway2 |
                      +-------+-------+  +-------+-------+
                              |                  |
                       +------+                  +------+
                       |                                |
             +---------+-----------+         +----------+----------+
             |     openVSwitch     |         |     openVSwitch     |
             +------+-----+--------+         +-------+-----+-------+
                    |     |                          |     |
                 +--+     +--+                    +--+     +--+
                 |           |                    |           |
             +---+---+   +---+---+            +---+---+   +---+---+
             | Host1 |   | Host2 |            | Host1 |   | Host2 |
             +-------+   +-------+            +-------+   +-------+

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
hostSwitchFormat = "sn{}_s{}"
gatewayFormat = "r{}"
hostFormat = "sn{}_h{}"
ifFormat = "{}_eth{}"

"""
Global Variables
"""
globalSwitchCnt = 0

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
ipFormat = "10.{}.{}.{}"

class IPsecNetworkTopo( Topo ):
    """
    An network Topo which connects clients to an ipsec gateway
    """

    def addIPsecGateway( self, name, localSubnet, inetIface, localIface ):
        "Add a IPsecRouter component to the network"
        return self.addHost( name, cls=IPsecRouter,
                subnet="{}/24".format( localSubnet ), inetIntf=inetIface,
                localIntf=localIface )

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

        if hostSubnetCnt != 1:
            info( "*** Currently only one subnet behind each gateway is supported" )
            assert switchCnt == 1

        switches = self.addVSwitch(switchCnt, gatewayCnt, hostSubnetCnt,
                hostsInSubnetCnt)

    def addVSwitch( self, switches, gateways, hostsubnets, hostsinsubnet):
        global globalSwitchCnt
        global switchFormat

        for sw in range( 1, switches + 1 ):
            globalSwitchCnt += 1
            swName = switchFormat.format( globalSwitchCnt )
            info( "*** Adding switch: " + swName + "\n" )

            switch = self.addSwitch( swName )
            self.addGateway( switch, gateways, hostsubnets, hostsinsubnet )

    def addGateway( self, wanSwitch, gateways, hostSubnets, hostsInSubnet):
        global globalSwitchCnt
        global ifFormat
        global ipFormat
        global switchFormat

        for gw in range( 1, gateways + 1):
            gwName = gatewayFormat.format( gw )

            info( "*** Adding gateway: " + gwName + "\n")

            # determine the WAN interface on the gateway
            gwWANIface = ifFormat.format( gwName, 0 )

            # determine the LAN interface on the gateway
            gwLANIface = ifFormat.format( gwName, 1 )

            # determine the WAN IP of the IPsec gateway
            gwWANIP = ipFormat.format( gw, 0, 1 )

            # determine the WAN IP of the IPsec gateway
            # XXX: Ugly as motherfucking hell, but i want to get this stuff to
            # to work now, so i'll do this hack here... Should be refactored
            # soon!!!
            # TODO: Make Subnet part dynamic
            gwLANIP = ipFormat.format( gw, 1, 2 )

            # XXX: Ugly as motherfucking hell, but i want to get this stuff to
            # to work now, so i'll do this hack here... Should be refactored
            # soon!!!
            # TODO: Make Subnet part dynamic
            lanSubnet = ipFormat.format( gw, 1, 1 )

            # add the gateway and link it to the switch
            gateway = self.addIPsecGateway( gwName, lanSubnet, gwWANIface,
                    gwLANIface )

            info( "*** Add Link between Gateway-WAN (IP: {}/24) and WAN-Switch ({}, {})\n".format( gwWANIP, gateway, wanSwitch ) )
            self.addLink( wanSwitch, gateway,
                    intfName2=gwWANIface,
                    params2={ 'ip' : "{}/24".format( gwWANIP ) } )

            # create a new switch where all hosts are attachted to
            globalSwitchCnt += 1
            swName = switchFormat.format( globalSwitchCnt )

            info( "*** Adding switch: " + swName + "\n" )
            lanSwitch = self.addSwitch( swName )

            info( "*** Add Link between Gateway-LAN and LAN-Switch ({}, {})\n".format( lanSwitch, gateway ) )
            self.addLink( lanSwitch, gateway, intfName2=gwLANIface,
                    params2={ 'ip' : "{}/24".format( gwLANIP ) } )

            self.addHosts( lanSwitch, gw, gwLANIP, hostSubnets, hostsInSubnet )

    def addHosts( self, switch, gwIpPortion, gwWANIP, hostSubnets, hostsInSubnet):
        global ifFormat
        global ipFormat
        global hostFormat

        for sn in range( 1, hostSubnets + 1 ):
            for h in range( 1, hostsInSubnet + 1 ):
                hName = hostFormat.format( sn, h )

                # determine the LAN interface name for the host
                # should always be hostname-eth0
                hIfaceName = ifFormat.format( hName, 0 )

                # determine the WAN IP of the IPsec gateway
                hIP = ipFormat.format( gwIpPortion, sn, h + 2 )
                info( "Host: {}, Host Iface: {},LAN-IP: {}\n".format( hName, hIfaceName, hIP ) )

                # determine the default route for this subnet
                hDefRoute = "via {}".format( gwWANIP )
                info( "default: '{}'\n".format( hDefRoute ) )

                info( "Host: {}, defaultRoute = '{}'\n".format( hName, hDefRoute ) )
                # add the gateway and link it to the switch
                host = self.addHost( hName, ip="{}/24".format( hIP ), defaultRoute=hDefRoute )

                info( "*** Add Link ({}, {})\n".format( switch, host ) )
                self.addLink( host, switch )


