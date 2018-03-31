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
gatewayFormat = "s{}_r{}"
hostSwitchFormat = "s{}_r{}_s1"
hostFormat = "s{}_r{}_h{}"
ifFormat = "{}_eth{}"

"""
The IP Address format.

The base Address is 10.0.0.0/8 and then substituted to
10.0.0.0/16 for the IPsec gateway subnet and
10.0.0.0/24 for the Subnets behind an IPsec gateway

Example:
    10.1.0.1/16 is the WAN IP Address of the first IPsec gateway

    10.1.0.1/24 is the LAN IP Address of the first IPsec gateway in the first
        host Subnet

    10.1.0.2/24 is the LAN IP Address of the first host in the first host
        subnet on the first IPsec gateway gateway

    10.1.0.254/24 is the LAN IP Address of the last host in the first host
        subnet on the first IPsec gateway gateway
"""
ipFormat = "10.{}.0.{}"

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

        :hosts: (optional) must be between 1 and 253, parameter is
            Parameter is optional. Default = 1 host
        """

        switchCnt = _opts.get('switches', 1)
        gatewayCnt = _opts.get('gateways', 1)
        hostsCnt = _opts.get('hosts', 1)

        info("*** Switches: {}, Gateways: {}, Hosts per Router: {}\n".format(switchCnt, gatewayCnt, hostsCnt))

        self.addVSwitch(switchCnt, gatewayCnt, hostsCnt)

    def addVSwitch( self, switches, gateways, hosts ):
        global switchFormat

        for sw in range( 1, switches + 1 ):
            swName = switchFormat.format( sw )
            info( "*** Adding switch: " + swName + "\n" )

            switch = self.addSwitch( swName )
            self.addGateway( sw, switch, gateways, hosts )

    def addGateway( self, sw, wanSwitch, gateways, hosts):
        global ifFormat
        global ipFormat
        global switchFormat

        for gw in range( 1, gateways + 1):
            gwName = gatewayFormat.format( sw, gw )

            info( "*** Adding gateway: " + gwName + "\n")

            # determine the WAN and LAN interface names on the gateway
            gwWANIface = ifFormat.format( gwName, 0 )
            gwLANIface = ifFormat.format( gwName, 1 )

            # determine the WAN IP of the IPsec gateway
            gwWANIP = ipFormat.format( gw, 1 ) # /16 Netmask

            # determine the LAN IP and subnet of the IPsec gateway
            gwLANIP = ipFormat.format( gw, 1 ) # /24 Netmask
            lanSubnet = ipFormat.format( gw, 1 )

            # add the gateway and link it to the switch
            gateway = self.addIPsecGateway( gwName, lanSubnet, gwWANIface,
                    gwLANIface )

            info( "*** Add Link between Gateway-WAN (IP: {}/24) and WAN-Switch ({}, {})\n".format( gwWANIP, gateway, wanSwitch ) )
            self.addLink( wanSwitch, gateway,
                    intfName2=gwWANIface,
                    params2={ 'ip' : "{}/16".format( gwWANIP ) } )

            # create a new switch where all hosts are attachted to
            hostSwitchName = hostSwitchFormat.format( sw, gw )

            info( "*** Adding switch: " + hostSwitchName + "\n" )
            hostSwitch = self.addSwitch( hostSwitchName )

            info( "*** Add Link between Gateway-LAN and LAN-Switch ({}, {})\n".format( hostSwitch, gateway ) )
            self.addLink( hostSwitch, gateway, intfName2=gwLANIface,
                        params2={ 'ip' : "{}/24".format( gwLANIP ) } )

            self.addHosts( hostSwitch, sw, gw, gwLANIP, hosts )

    def addHosts( self, switch, sw, gateway, gwLANIP, hosts ):
        global ifFormat
        global ipFormat
        global hostFormat

        for h in range( 1, hosts + 1 ):
            hName = hostFormat.format( sw, gateway, h )

            # determine the LAN interface name for the host
            # should always be hostname-eth0
            hIfaceName = ifFormat.format( hName, 0 )

            # determine the WAN IP of the IPsec gateway
            hIP = ipFormat.format( gateway, h + 1 )
            info( "Host: {}, Host Iface: {},LAN-IP: {}\n".format( hName, hIfaceName, hIP ) )

            # determine the default route for this subnet
            hDefRoute = "via {}".format( gwLANIP )
            info( "default: '{}'\n".format( hDefRoute ) )

            info( "Host: {}, defaultRoute = '{}'\n".format( hName, hDefRoute ) )
            # add the gateway and link it to the switch
            host = self.addHost( hName, ip="{}/24".format( hIP ), defaultRoute=hDefRoute )

            info( "*** Add Link ({}, {})\n".format( switch, host ) )
            self.addLink( host, switch )

