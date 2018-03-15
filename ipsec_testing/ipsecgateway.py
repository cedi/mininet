#!/usr/bin/python

"""
ipsecgateway.py: This implements an LinuxRouter object and derviates an
IPsec gateway from it, which establishes an IPsec connection in tunnel mode

Todo: To be documented!
"""


from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI

import math

class LinuxRouter( Host ):
    "A simple Host with IP forwarding enabled, so it can route properly"

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()

class IPsecRouter( LinuxRouter ):
    """
    A IPsecRouter is primarily a LinuxRouter Object
    """
    pass;
