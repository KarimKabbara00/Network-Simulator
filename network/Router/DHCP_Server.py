import UI.helper_functions as hf
import network.Router.DHCP_Pool
import network.network_functions as nf
from network.Application_Protocols import DHCP


class DHCP_Server:
    def __init__(self, class_object):
        self.class_object = class_object
        self.dhcp_pools = []
        self.dhcp_excluded_ip_ranges = []

        self.transaction_ids = {}

    def add_dhcp_pool(self, pool):
        for i in self.dhcp_pools:
            if pool.get_name() == i.get_name():
                return

        self.dhcp_pools.append(pool)

    def exclude_ip_range_from_dhcp_pools(self, start_ip, end_ip, is_range):
        if is_range:
            for ip in hf.get_ip_range_from_to(start_ip, end_ip):
                if ip not in self.dhcp_excluded_ip_ranges:
                    self.dhcp_excluded_ip_ranges.append(ip)
        else:
            if start_ip not in self.dhcp_excluded_ip_ranges:
                self.dhcp_excluded_ip_ranges.append(start_ip)

    def get_dhcp_pool_by_network_address(self, receiving_interface):

        receiving_interface_ip_address = receiving_interface.get_ipv4_address()
        receiving_interface_netmask = receiving_interface.get_netmask()

        for pool in self.dhcp_pools:
            try:
                if hf.is_same_subnet(receiving_interface_ip_address, receiving_interface_netmask, pool.get_pool()[0]):
                    return pool
            except IndexError:
                pass
            return None

    def get_dhcp_pools(self):
        return self.dhcp_pools

    def create_offer(self, receiving_interface, data: DHCP.Dhcp, source_mac):

        working_dhcp_pool: network.Router.DHCP_Pool.DHCPpool = self.get_dhcp_pool_by_network_address(
            receiving_interface)

        flags = data.get_flags()
        options = data.get_options()

        ci_address = None
        si_address = receiving_interface.get_ipv4_address()
        gi_address = None
        ch_address = source_mac
        transaction_id = data.get_transaction_id()
        self.transaction_ids[transaction_id] = hf.build_tid_table()
        # ---------------------------- DHCP OPTIONS ---------------------------- #
        try:
            yi_address = working_dhcp_pool.get_ip_from_pool(options["PREFERRED_IP"], self.dhcp_excluded_ip_ranges)
        except KeyError:
            yi_address = working_dhcp_pool.get_ip_from_pool(None, self.dhcp_excluded_ip_ranges)
        self.transaction_ids[transaction_id]['REQUEST_SUBNET_MASK'] = working_dhcp_pool.get_subnet()
        self.transaction_ids[transaction_id]['REQUEST_ROUTER'] = working_dhcp_pool.get_default_gateway()
        self.transaction_ids[transaction_id]['REQUEST_DNS_SERVER'] = working_dhcp_pool.get_dns_servers()
        self.transaction_ids[transaction_id]['REQUEST_DOMAIN_NAME'] = working_dhcp_pool.get_domain_name()
        self.transaction_ids[transaction_id]['DHCP_IP_ADDRESS'] = receiving_interface.get_ipv4_address()
        self.transaction_ids[transaction_id]['LEASE_TIME'] = working_dhcp_pool.get_lease_time()
        # ---------------------------- DHCP OPTIONS ---------------------------- #

        # Exhausted IP Pool
        if not yi_address:
            pass
            # return nf.create_dhcp_nak()

        return nf.create_dhcp_offer(receiving_interface.get_ipv4_address(), source_mac, flags, ci_address, yi_address,
                                    si_address, gi_address, ch_address, transaction_id)

    def create_ack(self, receiving_interface, data, source_mac):
        working_dhcp_pool: network.Router.DHCP_Pool.DHCPpool = self.get_dhcp_pool_by_network_address(
            receiving_interface)

        flags = data.get_flags()
        ci_address = None
        yi_address = data.get_options()['PREFERRED_IP']
        si_address = receiving_interface.get_ipv4_address()
        gi_address = None
        ch_address = source_mac
        transaction_id = data.get_transaction_id()
        requested_options = self.transaction_ids[transaction_id]
        self.transaction_ids.pop(transaction_id)

        working_dhcp_pool.remove_ip_from_hold(yi_address, assigned=True)  # False if NAK

        return nf.create_dhcp_ack(receiving_interface.get_ipv4_address(), source_mac, flags, ci_address, yi_address,
                                  si_address, gi_address, ch_address, transaction_id, requested_options)
