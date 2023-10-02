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
                if (hf.is_same_subnet(receiving_interface_ip_address, receiving_interface_netmask, pool.get_pool()[0]) and
                        receiving_interface_netmask == pool.get_subnet()):
                    return pool
            except IndexError:
                pass

        return None

    def get_dhcp_pools(self):
        return self.dhcp_pools

    def create_offer(self, receiving_interface, data: DHCP.Dhcp, source_mac):
        working_dhcp_pool: network.Router.DHCP_Pool.DHCPpool = self.get_dhcp_pool_by_network_address(receiving_interface)

        flags = data.get_flags()
        options = data.get_options()
        ci_address = None
        si_address = receiving_interface.get_ipv4_address()
        gi_address = None
        ch_address = source_mac
        transaction_id = data.get_transaction_id()
        self.transaction_ids[transaction_id] = hf.build_tid_table()

        if working_dhcp_pool:

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
            self.transaction_ids[transaction_id]['OFFERED_IP_ADDRESS'] = yi_address
            # ---------------------------- DHCP OPTIONS ---------------------------- #

            # Exhausted IP Pool
            if not yi_address: # TODO:
                print('exhausted!')
                # return nf.create_dhcp_nak()

            return nf.create_dhcp_offer(receiving_interface.get_ipv4_address(), source_mac, flags, ci_address, yi_address,
                                        si_address, gi_address, ch_address, transaction_id)
        else:
            return None

    def create_ack(self, receiving_interface, source_mac, data, original_sender_mac, dhcp_renew):
        working_dhcp_pool: network.Router.DHCP_Pool.DHCPpool = self.get_dhcp_pool_by_network_address(receiving_interface)

        flags = data.get_flags()
        ci_address = data.get_ci_address()
        yi_address = data.get_options()['PREFERRED_IP']
        si_address = receiving_interface.get_ipv4_address()
        gi_address = None
        ch_address = original_sender_mac
        transaction_id = data.get_transaction_id()
        requested_options = self.transaction_ids[transaction_id]
        # self.transaction_ids.pop(transaction_id)

        if working_dhcp_pool:
            if not dhcp_renew:  # The IP is not on hold when a dhcp renew is received
                working_dhcp_pool.remove_ip_from_hold(yi_address, assigned=True)  # True if offer accepted
                dest_ip = '255.255.255.255'
            else:
                dest_ip = ci_address

            return nf.create_dhcp_ack(receiving_interface.get_ipv4_address(), source_mac, flags, ci_address, yi_address,
                                      si_address, gi_address, ch_address, dest_ip, transaction_id, requested_options)
        else:
            return None

    def release_ip_assignment(self, receiving_interface, data):
        working_dhcp_pool: network.Router.DHCP_Pool.DHCPpool = self.get_dhcp_pool_by_network_address(receiving_interface)

        transaction_id = data.get_transaction_id()
        ci_address = data.get_ci_address()
        working_dhcp_pool.release_ip_assignment(ci_address)
        self.transaction_ids.pop(transaction_id)

    def process_dhcp_decline(self, receiving_interface, data):
        working_dhcp_pool: network.Router.DHCP_Pool.DHCPpool = self.get_dhcp_pool_by_network_address(receiving_interface)
        yi_address = data.get_yi_address()
        transaction_id = data.get_transaction_id()
        working_dhcp_pool.unknown_ip_assignment(yi_address)
        self.transaction_ids.pop(transaction_id)

    def revoke_offer(self, receiving_interface, data):
        working_dhcp_pool: network.Router.DHCP_Pool.DHCPpool = self.get_dhcp_pool_by_network_address(receiving_interface)

        if working_dhcp_pool:
            transaction_id = data.get_transaction_id()

            # TODO: START HERE!!! This causes a key error.
            #   Load tset_2 -> configure dhcp: r1 with network 192.168.1.0 /25 and r2 with network 192.168.1.128 /25
            offered_ip_to_be_revoked = self.transaction_ids[transaction_id]['OFFERED_IP_ADDRESS']

            working_dhcp_pool.remove_ip_from_hold(offered_ip_to_be_revoked, assigned=False)  # False if offer revoked
            self.transaction_ids.pop(transaction_id)

    def clear_expired_transaction_ids(self, transaction_ids): # Called only when lease expires
        for t_id in transaction_ids:
            try:
                self.transaction_ids.pop(t_id)
            except KeyError:
                pass
