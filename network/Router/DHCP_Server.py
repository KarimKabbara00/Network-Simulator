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
                if (hf.is_same_subnet(receiving_interface_ip_address, receiving_interface_netmask, pool.get_example_ip()) and
                        receiving_interface_netmask == pool.get_subnet()):
                    return pool
            except IndexError:
                pass
        return None

    def get_dhcp_pool_by_gi_address(self, receiving_interface, gi_address):
        receiving_interface_netmask = receiving_interface.get_netmask()
        for pool in self.dhcp_pools:
            try:
                if (hf.is_same_subnet(gi_address, pool.get_subnet(), pool.get_example_ip()) and
                        receiving_interface_netmask == pool.get_subnet()):
                    return pool
            except IndexError:
                pass
        return None

    def get_dhcp_pools(self):
        return self.dhcp_pools

    def create_offer(self, receiving_interface, data: DHCP.Dhcp, original_sender_mac, source_mac):
        if not data.get_gi_address():   # Assuming that no GI_ADDR means the DHCP server is in the same subnet
            working_dhcp_pool: network.Router.DHCP_Pool.DHCPpool = self.get_dhcp_pool_by_network_address(receiving_interface)
        else:
            working_dhcp_pool: network.Router.DHCP_Pool.DHCPpool = self.get_dhcp_pool_by_gi_address(receiving_interface, data.get_gi_address())

        flags = data.get_flags()
        options = data.get_options()

        # Check if requested configurations match the pool's configurations
        try:
            if not hf.is_same_subnet(options['PREFERRED_IP'], working_dhcp_pool.get_subnet(), working_dhcp_pool.get_example_ip()):
                return self.create_nak(receiving_interface, source_mac, data, original_sender_mac)
        except KeyError:    # No preferred IP
            pass

        ci_address = None
        si_address = receiving_interface.get_ipv4_address()
        gi_address = None
        ch_address = original_sender_mac
        transaction_id = data.get_transaction_id()
        self.transaction_ids[transaction_id] = hf.build_tid_table()

        if working_dhcp_pool:
            # ---------------------------- DHCP OPTIONS ---------------------------- #
            try:
                yi_address = working_dhcp_pool.get_ip_from_pool(options["PREFERRED_IP"])
            except KeyError:
                yi_address = working_dhcp_pool.get_ip_from_pool(None)
            self.transaction_ids[transaction_id]['REQUEST_SUBNET_MASK'] = working_dhcp_pool.get_subnet()
            self.transaction_ids[transaction_id]['REQUEST_ROUTER'] = working_dhcp_pool.get_default_gateway()
            self.transaction_ids[transaction_id]['REQUEST_DNS_SERVER'] = working_dhcp_pool.get_dns_servers()
            self.transaction_ids[transaction_id]['REQUEST_DOMAIN_NAME'] = working_dhcp_pool.get_domain_name()
            self.transaction_ids[transaction_id]['DHCP_IP_ADDRESS'] = receiving_interface.get_ipv4_address()
            self.transaction_ids[transaction_id]['LEASE_TIME'] = working_dhcp_pool.get_lease_time()
            self.transaction_ids[transaction_id]['OFFERED_IP_ADDRESS'] = yi_address
            # ---------------------------- DHCP OPTIONS ---------------------------- #

            if not yi_address:
                return self.create_nak(receiving_interface, source_mac, data, original_sender_mac)

            return nf.create_dhcp_offer(receiving_interface.get_ipv4_address(), source_mac, flags, ci_address, yi_address,
                                        si_address, gi_address, ch_address, transaction_id)
        else:
            return None

    def create_ack(self, receiving_interface, source_mac, data, original_sender_mac, dhcp_renew):
        if not data.get_gi_address():   # Assuming that no GI_ADDR means the DHCP server is in the same subnet
            working_dhcp_pool: network.Router.DHCP_Pool.DHCPpool = self.get_dhcp_pool_by_network_address(receiving_interface)
        else:
            working_dhcp_pool: network.Router.DHCP_Pool.DHCPpool = self.get_dhcp_pool_by_gi_address(receiving_interface, data.get_gi_address())

        flags = data.get_flags()
        ci_address = data.get_ci_address()
        yi_address = data.get_options()['PREFERRED_IP']
        si_address = receiving_interface.get_ipv4_address()
        gi_address = None
        ch_address = original_sender_mac
        transaction_id = data.get_transaction_id()
        try:
            requested_options = self.transaction_ids[transaction_id]
        except KeyError:
            # Offer revoked or transaction ID is no longer found
            return self.create_nak(receiving_interface, source_mac, data, original_sender_mac)

        # Checked again here for DHCP Renew
        # Check if requested configurations match the pool's configurations
        try:
            if not hf.is_same_subnet(requested_options['PREFERRED_IP'], working_dhcp_pool.get_subnet(), working_dhcp_pool.get_example_ip()):
                # TODO: RELAY AGENT. Must set gi_address here
                # if options['PREFERRED_IP'], check routing table for same subnet preferred IP and configured external dhcp address
                #   if yes, route somehow
                #   else: NAK
                return self.create_nak(receiving_interface, source_mac, data, original_sender_mac)
        except KeyError:
            pass    # No preferred IP

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

    def create_nak(self, receiving_interface, source_mac, data, original_sender_mac):
        working_dhcp_pool: network.Router.DHCP_Pool.DHCPpool = self.get_dhcp_pool_by_network_address(receiving_interface)
        transaction_id = data.get_transaction_id()
        return nf.create_dhcp_nak(receiving_interface.get_ipv4_address(), original_sender_mac, transaction_id, source_mac,
                                  receiving_interface.get_ipv4_address(), '255.255.255.255')

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

            # TODO: TSET_2: R1 DHCP: network 192.168.1.0 /25 ----- R2 DHCP: network 192.168.1.128 /25
            '''
                Switches may need to use threads to broadcast frames. Broadcast frames will arrive to destinations one at
                a time as opposed to all at 'once'. 
                
                The Problem: The entire DORA process completes with the first DHCP server. 
                    - One level into the stack trace:
                        * The second DHCP server receives a REQUEST not destined to it (destined to the first server), then tries to revoke 
                            the offer it made.
                        * However, it never had the chance to make an offer, because going back up the stacktrace, the very first 
                            broadcast DISCOVER hasn't yet made it to the second server to create an entry in the transaction ID dictionary.
                    - Again, this happens because each broadcast frame is sent sequentially, as opposed to at the same time.
            '''
            try:
                offered_ip_to_be_revoked = self.transaction_ids[transaction_id]['OFFERED_IP_ADDRESS']
                working_dhcp_pool.remove_ip_from_hold(offered_ip_to_be_revoked, assigned=False)  # False if offer revoked
                self.transaction_ids.pop(transaction_id)
                print('offer revoked')
            except KeyError:
                pass

    def clear_expired_transaction_ids(self, transaction_ids): # Called only when lease expires
        for t_id in transaction_ids:
            try:
                self.transaction_ids.pop(t_id)
            except KeyError:
                pass

    def get_excluded_addresses(self):
        return self.dhcp_excluded_ip_ranges