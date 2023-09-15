class DHCP:

    def __init__(self, class_object, name):
        self.class_object = class_object
        self.pool_name = name
        self.ip_pool = []
        self.excluded_ip_pool = []
        self.dns_server = None
        self.domain_name = None
        self.default_gateway = None
        self.lease_time = 0

    def set_pool(self, ip, subnet, is_prefix):
        pass
