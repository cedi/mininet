#!/usr/bin/python

"""
ipsecgateway.py: This implements an LinuxRouter object and derviates an
IPsec gateway from it, which establishes an IPsec connection in tunnel mode

Todo: To be documented!
"""


from mininet.nodelib import NAT

class IPsecRouter(NAT):
    """
    A IPsecRouter is primarily a LinuxRouter Object
    """
    def config(self, **params):
        super(IPsecRouter, self).config(**params)

    def terminate(self):
        super(IPsecRouter, self).terminate()

