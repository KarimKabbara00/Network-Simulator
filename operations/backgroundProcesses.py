import time
import copy
from operations import globalVars
from datetime import timedelta

def dhcp_ip_leases(internal_clock):


    while True:
        pcs = internal_clock.get_pcs()
        for pc in pcs:

            node = pc.get_class_object()                    # class object
            lease_start = node.get_lease_start()            # ip lease start
            T1 = node.get_lease_time() // 2                 # 50% of lease time
            T2 = node.get_lease_time() * 0.875              # 87.5% of lease time

            # Attempt to expire lease
            if lease_start and internal_clock.now() > lease_start + timedelta(seconds=node.get_lease_time()):
                node.expire_ip_lease()
            # Attempt to renew at 85% of the lease
            elif lease_start and internal_clock.now() > lease_start + timedelta(seconds=T2):
                pass
            # Attempt to renew at 50% of the lease
            elif lease_start and internal_clock.now() > lease_start + timedelta(seconds=T1):
                pass

        # Keep track of expired leases at DHCP server
        ros = internal_clock.get_routers()
        for ro in ros:
            node = ro.get_class_object()
            for dhcp_pool in node.get_dhcp_server().get_dhcp_pools():
                ip_pool = dhcp_pool.get_leased_ip_pool()
                for ip_lease in copy.copy(ip_pool):
                    if internal_clock.now() > ip_pool[ip_lease] + timedelta(seconds=dhcp_pool.get_lease_time()):
                        ip_pool.pop(ip_lease)
                dhcp_pool.set_leased_ip_pool(ip_pool)
                globalVars.prompt_save = True

        time.sleep(3)

def arp_mac_aging(internal_clock):
    ARP_AGING_TIME = timedelta(seconds=120)  # Dynamic ARP Entry Aging = 2 minutes
    MAC_AGING_TIME = timedelta(seconds=300)  # Dynamic MAC Address Aging = 5 minutes

    while True:

        pcs = internal_clock.get_pcs()
        sws = internal_clock.get_switches()
        ros = internal_clock.get_routers()

        # PCs and routers have ARP tables
        for i in pcs + ros:
            try:
                node = i.get_class_object()
                arp_table = node.get_arp_table()

                for ip in copy.copy(arp_table):  # shallow copy
                    if arp_table[ip][1] == 'DYNAMIC' and internal_clock.now() > arp_table[ip][2] + ARP_AGING_TIME:
                        arp_table.pop(ip)

                node.set_arp_table(arp_table)
                globalVars.prompt_save = True

            except AttributeError:
                pass

        # Switches have MAC tables:
        for i in sws:
            try:
                node = i.get_class_object()
                mac_table = node.get_cam_table()

                for entry in copy.copy(mac_table):
                    if (mac_table[entry][2] == 'DYNAMIC' and internal_clock.now() > mac_table[entry][4] +
                            MAC_AGING_TIME):
                        mac_table.pop(entry)
                        node.set_cam_table(mac_table)
                        globalVars.prompt_save = True

            except AttributeError:
                pass

        time.sleep(5)
