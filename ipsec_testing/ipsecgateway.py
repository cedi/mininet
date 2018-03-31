#!/usr/bin/python

"""
ipsecgateway.py: This implements an LinuxRouter object and derviates an
IPsec gateway from it, which establishes an IPsec connection in tunnel mode

Todo: To be documented!
"""


from mininet.topo import Topo
from mininet.net import Mininet
from mininet.nodelib import NAT
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class IPsecRouter( NAT ):
    """
    A IPsecRouter is primarily a LinuxRouter Object
    """
    def config( self, **params ):
        super( IPsecRouter, self).config( **params )

    def terminate( self ):
        super( IPsecRouter, self ).terminate()

