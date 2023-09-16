import UI.helper_functions as hf
class DHCP:

    def __init__(self, class_object, name):
        self.class_object = class_object
        self.pool_name = name
        self.ip_pool = []
        self.pool_subnet = None
        self.excluded_ip_pool = []
        self.dns_server = None
        self.domain_name = None
        self.default_gateway = None
        self.lease_time = 0

    def set_pool(self, ip, subnet, is_prefix):
        try:
            self.pool_subnet = hf.get_subnet_from_prefix_length(subnet)
        except:  # TODO EXCEPT SOMETHING
            self.pool_subnet = subnet

        self.ip_pool = hf.get_ip_range(ip, subnet, is_prefix)
        print(self.ip_pool)
