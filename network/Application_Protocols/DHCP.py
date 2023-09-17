import random
from abc import ABC, abstractmethod
from operations import globalVars

option_50 = ["PREFERRED_IP", ""]
option_51 = "LEASE_TIME"
option_54 = "DHCP_IP_ADDRESS"

option_53_1 = "DHCP_DISCOVER"
option_53_2 = "DHCP_OFFER"
option_53_3 = "DHCP_REQUEST"
option_53_4 = "DHCP_DECLINE"
option_53_5 = "DHCP_ACK"
option_53_6 = "DHCP_NAK"
option_53_7 = "DHCP_RELEASE"
option_53_9 = "DHCP_FORCE_RENEW"

option_55_1 = "REQUEST_SUBNET_MASK"
option_55_3 = "REQUEST_ROUTER"
option_55_6 = "REQUEST_DNS_SERVER"
option_55_15 = "REQUEST_DOMAIN_NAME"


class Dhcp(ABC):
    def __init__(self):
        self.op = 0x01                      # 0x01 is request
        self.hardware_type = 0x01           # 0x01 is Ethernet
        self.hardware_length = 0x06         # 6 bytes for mac address
        self.hops = 0                       # number of hops taken
        self.transaction_id = None          # Set to a random value by client
        self.sec = None                     # time elapsed since send
        self.flags = []
        self.ci_address = None              # Current client IP address (None when DORA -> Discover)
        self.yi_address = None              # Offered client IP Address. Set by DHCP server when replying (DORA - Offer)
        self.si_address = None              # DHCP Server address. Client replies to this (DORA -> Request)
        self.gi_address = None              # Gateway IP address. Used by DHCP Relay Agents
        self.ch_address = None              # Client MAC address. Used for ID and communication
        self.s_name = None                  # DHCP Server name (Can be anything or FQDN, DORA -> Offer, Ack)
        self.file_name = None               # Used by FTP?
        self.options = []

        self.application_identifier = "DHCP"

    def get_application_identifier(self):
        return self.application_identifier

    def get_transaction_id(self):
        return self.transaction_id

    def get_flags(self):
        return self.flags

    def get_ci_address(self):
        return self.ci_address

    def get_yi_address(self):
        return self.yi_address

    def get_si_address(self):
        return self.si_address

    def get_gi_address(self):
        return self.gi_address

    def get_ch_address(self):
        return self.ch_address

    def get_s_name(self):
        return self.s_name

    def get_options(self):
        return self.options


class DhcpDiscover(Dhcp):
    def __init__(self, is_broadcast, preferred_ip):
        super().__init__()

        self.transaction_id = random.getrandbits(16)    # Random 16-bit number (stored as int)
        self.sec = globalVars.internal_clock.get_time() # Time sent

        if is_broadcast:
            self.flags.append(0x01)                     # B set to 1 for broadcast reply
        else:
            self.flags.append(0x00)                     # B set to 0 for unicast reply
        self.flags.append(0b0000000000000000)           # 15 0's. reserved and not used.

        if preferred_ip:
            option_50[1] = preferred_ip

        self.options = [option_53_1, option_50, option_55_1, option_55_3, option_55_6, option_55_15]
        self.dhcp_identifier = "DHCP_DISCOVER"

    def get_dhcp_identifier(self):
        return self.dhcp_identifier


class DhcpOffer(Dhcp):
    def __init__(self, is_broadcast):
        super().__init__()


    def get_application_identifier(self):
        return self.application_identifier

    def get_dhcp_identifier(self):
        return self.dhcp_identifier

class DhcpRequest:
    pass

class DhcpAcknowledge:
    pass

class DhcpRenew:
    pass

class DhcpRelease:
    pass