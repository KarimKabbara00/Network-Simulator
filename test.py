# from UI.helper_functions import get_network_portion_ipv4
#
# ip_address = '192.168.1.0'
# subnet = '255.255.255.128'
#
# network_portion = get_network_portion_ipv4(ip_address, subnet).strip('.0')
# intermediate_ip_pool = []  # IPs that are being built are stored here
# ip_pool = []  # IPs that are complete are stored here
#
# print(network_portion)
#
# zero_count = subnet.count('0')
# count = -1
#
# for s in subnet.split('.'):
#
#     count += 1
#
#     if s == '255':
#         continue
#
#     if s != '0':
#
#         if int(ip_address.split('.')[count]) < int(subnet.split('.')[count]):
#             for j in range(255 - int(s)):
#                 if zero_count == 0:
#                     ip_pool.append(network_portion + '.' + str(j))
#                 else:
#                     intermediate_ip_pool.append(network_portion + '.' + str(j))
#
#         else:
#             network_portion = '.'.join(network_portion.split('.')[:count])
#             for j in range(int(s) + 1, 255):
#                 if zero_count == 0:
#                     ip_pool.append(network_portion + '.' + str(j))
#                 else:
#                     intermediate_ip_pool.append(network_portion + '.' + str(j))
#
#     if s == '0':
#
#         if not intermediate_ip_pool:
#             intermediate_ip_pool = [network_portion]
#
#         for ip in range(len(intermediate_ip_pool)):
#             if zero_count == 1:
#                 print('here!')
#                 for i in range(1, 255):
#                     new_ip = intermediate_ip_pool[ip] + '.' + str(i)
#                     ip_pool.append(new_ip)
#
#             elif zero_count == 2:
#                 print('here!!')
#                 for i in range(256):
#                     for j in range (1, 255):
#                         new_ip = intermediate_ip_pool[ip] + '.' + str(i) + '.' + str(j)
#                         ip_pool.append(new_ip)
#
#             elif zero_count == 3 or zero_count == 4:
#                 raise Exception('Pool too large!')
#
#         break