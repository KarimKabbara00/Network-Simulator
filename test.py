ip = '192.168.1.0'
subnet = '255.255.240.0'

ip_range = []
x = ''

count = -1
for i in subnet.split('.'):

    count += 1

    if i == '255':
        x += ip.split('.')[count] + '.'
        continue

    for n in range(int(i)):
        ip_range.append(x + str(n))

count = subnet.split('.').count('0')
print(count)
if count == 1:
    for i in ip_range:
        for j in range(256):
            i += '.' + str(j)

if count == 2:
    x = x[:-4]
    for i in range(256):
        for j in range(256):
            ip_range.append(x + '.' + str(i) + '.' + str(j))
