import time
import copy


def count_time(internal_clock):
    while True:
        time.sleep(1)
        internal_clock.increment_time()

        # print(internal_clock.get_time())


def arp_mac_aging(internal_clock):
    ARP_AGING_TIME = 120  # Dynamic ARP Entry Aging = 2 minutes
    MAC_AGING_TIME = 100  # Dynamic MAC Address Aging = 5 minutes

    while True:

        pcs = internal_clock.get_pcs()
        sws = internal_clock.get_switches()
        ros = internal_clock.get_routers()

        # PCs and routers have ARP tables
        for i in pcs + ros:
            node = i.get_class_object()
            arp_table = node.get_arp_table_actual()

            for ip in copy.copy(arp_table):  # shallow copy
                if arp_table[ip][1] == 'DYNAMIC' and internal_clock.get_time() > arp_table[ip][2] + ARP_AGING_TIME:
                    arp_table.pop(ip)
                    node.set_arp_table(arp_table)

        # Switches have MAC tables:
        for i in sws:
            node = i.get_class_object()
            mac_table = node.get_cam_table()

            for entry in copy.copy(mac_table):
                if mac_table[entry][2] == 'DYNAMIC' and internal_clock.get_time() > mac_table[entry][
                    4] + MAC_AGING_TIME:
                    mac_table.pop(entry)
                    node.set_cam_table(mac_table)

        time.sleep(5)
