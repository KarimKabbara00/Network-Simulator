from abc import ABC, abstractmethod
from operations import globalVars

DHCP_options = {
    "PREFERRED_IP": "",             # option_50
    "LEASE_TIME": "",               # option_51
    "DHCP_DISCOVER": "",            # option_53_1
    "DHCP_OFFER": "",               # option_53_2
    "DHCP_REQUEST": "",             # option_53_3
    "DHCP_DECLINE": "",             # option_53_4
    "DHCP_ACK": "",                 # option_53_5
    "DHCP_NAK": "",                 # option_53_6
    "DHCP_RELEASE": "",             # option_53_7
    "DHCP_FORCE_RENEW": "",         # option_53_9
    "DHCP_IP_ADDRESS": "",          # option_54
    "REQUEST_SUBNET_MASK": "",      # option_55_1
    "REQUEST_ROUTER": "",           # option_55_3
    "REQUEST_DNS_SERVER": [],       # option_55_6
    "REQUEST_DOMAIN_NAME": "",      # option_55_15
    "T1_RENEWAL": "",               # option 58
    "T2_RENEWAL": "",               # option 59
    "RELAY_AGENT_INFORMATION": "",  # option_82
}


class Dhcp(ABC):
    def __init__(self):
        self.op = 0x01                  # 0x01 is request
        self.hardware_type = 0x01       # 0x01 is Ethernet
        self.hardware_length = 0x06     # 6 bytes for mac address
        self.hops = 0                   # number of hops taken
        self.transaction_id = None      # Set to a random value by client
        self.sec = None                 # time elapsed since send
        self.flags = []
        self.ci_address = None          # Current client IP address (None when all of DORA)
        self.yi_address = None          # Offered client IP Address. Set by DHCP server when replying (DORA -> Offer)
        self.si_address = None          # DHCP Server address. Client replies to this (DORA -> Request)
        self.gi_address = None          # Gateway IP address. Used by DHCP Relay Agents
        self.ch_address = None          # Client MAC address. Used for ID and communication
        self.s_name = None              # DHCP Server name (Can be anything or FQDN, DORA -> Offer, Ack)
        self.file_name = None           # Used by FTP?
        self.options = {}

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

    @abstractmethod
    def get_options(self):
        return self.options


class DhcpDiscover(Dhcp):
    def __init__(self, is_broadcast, preferred_ip, transaction_id, gi_address=None):
        super().__init__()

        self.transaction_id = transaction_id
        self.sec = globalVars.internal_clock.now()  # Time sent

        if is_broadcast:
            self.flags.append(0x01)  # B set to 1 for broadcast reply
        else:
            self.flags.append(0x00)  # B set to 0 for unicast reply
        self.flags.append(0b0000000000000000)  # 15 0's. reserved and not used.

        if gi_address:
            self.gi_address = gi_address

        self.options = DHCP_options
        self.options['DHCP_DISCOVER'] = True
        if preferred_ip:
            self.options['PREFERRED_IP'] = preferred_ip
        self.options['REQUEST_SUBNET_MASK'] = True
        self.options['REQUEST_ROUTER'] = True
        self.options['REQUEST_DNS_SERVER'] = True
        self.options['REQUEST_DOMAIN_NAME'] = True
        self.options = {i: j for i, j in self.options.items() if j != ""}

        self.dhcp_identifier = "DHCP_DISCOVER"

    def get_dhcp_identifier(self):
        return self.dhcp_identifier

    def get_options(self):
        return self.options

    def set_gi_address(self, gi_address):
        self.gi_address = gi_address


class DhcpOffer(Dhcp):
    def __init__(self, flags, ci_address, yi_address, si_address, gi_address, ch_address, transaction_id):
        super().__init__()

        self.flags = flags
        self.ci_address = ci_address
        self.yi_address = yi_address
        self.si_address = si_address
        self.gi_address = gi_address
        self.ch_address = ch_address
        self.transaction_id = transaction_id

        self.options = DHCP_options
        self.options['DHCP_OFFER'] = True
        self.options = {i: j for i, j in self.options.items() if j != ''}

        self.dhcp_identifier = "DHCP_OFFER"

    def get_dhcp_identifier(self):
        return self.dhcp_identifier

    def get_options(self):
        return self.options


class DhcpRequest(Dhcp):

    def __init__(self, si_address, ch_address, provided_ip, transaction_id, flags):
        super().__init__()

        self.ch_address = ch_address
        self.transaction_id = transaction_id
        self.flags = flags
        self.si_address = si_address

        self.options = DHCP_options
        self.options['DHCP_REQUEST'] = True
        self.options['PREFERRED_IP'] = provided_ip
        self.options['DHCP_IP_ADDRESS'] = si_address
        self.options = {i: j for i, j in self.options.items() if j != ""}

        self.dhcp_identifier = "DHCP_REQUEST"

    def get_dhcp_identifier(self):
        return self.dhcp_identifier

    def get_options(self):
        return self.options


class DhcpAcknowledge(Dhcp):
    def __init__(self, flags, ci_address, yi_address, si_address, gi_address, ch_address, transaction_id, options):
        super().__init__()

        self.flags = flags
        self.ci_address = ci_address
        self.yi_address = yi_address
        self.si_address = si_address
        self.gi_address = gi_address
        self.ch_address = ch_address
        self.transaction_id = transaction_id

        self.options = DHCP_options
        self.options['DHCP_ACK'] = True
        self.options['REQUEST_SUBNET_MASK'] = options['REQUEST_SUBNET_MASK']
        self.options['REQUEST_ROUTER'] = options['REQUEST_ROUTER']
        self.options['LEASE_TIME'] = options['LEASE_TIME']
        self.options['DHCP_IP_ADDRESS'] = options['DHCP_IP_ADDRESS']
        self.options['REQUEST_DNS_SERVER'] = options['REQUEST_DNS_SERVER']
        self.options['REQUEST_DOMAIN_NAME'] = options['REQUEST_DOMAIN_NAME']
        self.options = {i: j for i, j in self.options.items() if j != ''}

        self.dhcp_identifier = "DHCP_ACK"

    def get_dhcp_identifier(self):
        return self.dhcp_identifier

    def get_options(self):
        return self.options


class DhcpRenew(Dhcp):
    def __init__(self, ci_address, si_address, ch_address, flags, is_t1, transaction_id):
        super().__init__()

        self.ci_address = ci_address
        self.ch_address = ch_address
        self.si_address = si_address
        self.transaction_id = transaction_id

        self.options = DHCP_options
        self.options['DHCP_RENEW'] = True
        self.options['PREFERRED_IP'] = ci_address
        self.options['DHCP_IP_ADDRESS'] = si_address
        self.flags = flags  # either unicast or broadcast

        if is_t1:
            self.options['T1_RENEW'] = True
        else:
            self.options['T2_RENEW'] = True

        self.options = {i: j for i, j in self.options.items() if j != ""}

        self.dhcp_identifier = "DHCP_RENEW"

    def get_dhcp_identifier(self):
        return self.dhcp_identifier

    def get_options(self):
        return self.options


class DhcpRelease(Dhcp):
    def __init__(self, ch_address, ci_address, si_address, transaction_id):
        super().__init__()

        self.options['DHCP_RELEASE'] = True
        self.options = {i: j for i, j in self.options.items() if j != ""}

        self.ch_address = ch_address
        self.ci_address = ci_address
        self.si_address = si_address
        self.transaction_id = transaction_id
        self.dhcp_identifier = "DHCP_RELEASE"

    def get_dhcp_identifier(self):
        return self.dhcp_identifier

    def get_options(self):
        return self.options


class DhcpDecline(Dhcp):
    def __init__(self, ch_address, yi_address, si_address, transaction_id):
        super().__init__()

        self.options['DHCP_DECLINE'] = True
        self.options = {i: j for i, j in self.options.items() if j != ""}

        self.ch_address = ch_address
        self.yi_address = yi_address
        self.si_address = si_address
        self.transaction_id = transaction_id
        self.dhcp_identifier = "DHCP_DECLINE"

    def get_dhcp_identifier(self):
        return self.dhcp_identifier

    def get_options(self):
        return self.options


class DhcpNak(Dhcp):
    def __init__(self, ch_address, si_address, transaction_id):
        super().__init__()

        self.ch_address = ch_address
        self.si_address = si_address
        self.transaction_id = transaction_id
        self.dhcp_identifier = "DHCP_NAK"

        self.options['DHCP_NAK'] = True
        self.options = {i: j for i, j in self.options.items() if j != ""}

    def get_dhcp_identifier(self):
        return self.dhcp_identifier

    def get_options(self):
        return self.options
