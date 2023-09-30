import json
import math
import random
import re
import tkinter as tk
from itertools import groupby
from operator import itemgetter
from textwrap import wrap
from tkinter import filedialog
import numpy as np
from UI import loadIcons
from operations import globalVars
import tkinterweb
from datetime import datetime


def button_enter(event, btn):
    btn.config(background='gray89', relief=tk.SUNKEN)


def button_leave(event, btn):
    btn.config(background='SystemButtonFace', relief=tk.GROOVE)


def window_closed(window):

    match window:
        case globalVars.TL_pc:
            globalVars.open_TL_pc = False
            globalVars.TL_pc.destroy()

        case globalVars.TL_sw:
            globalVars.open_TL_sw = False
            globalVars.TL_sw.destroy()

        case globalVars.TL_ro:
            globalVars.open_TL_ro = False
            globalVars.TL_ro.destroy()

        # case globalVars.TL_fw:
        #     globalVars.open_TL_fw = False
        #     globalVars.TL_fw.destroy

        case globalVars.tl_lb:
            globalVars.open_TL_lb = False
            globalVars.tl_lb.destroy()

def get_next_number():
    globalVars.node_number += 1
    return globalVars.node_number


def get_next_pc(generation):
    return generation + "_PC_" + str(get_next_number())


def get_next_switch():
    return "SW_" + str(get_next_number())


def get_next_router():
    return "Router_" + str(get_next_number())


def get_next_cable(canvas):
    return "Eth_" + str(len(canvas.find_withtag('Ethernet')) + 1)


def get_next_rectangle(canvas):
    return "Rectangle_" + str(len(canvas.find_withtag('Rectangle')) + 1)


def get_next_label(canvas):
    return "Label_" + str(len(canvas.find_withtag('Label')) + 1)


def get_node_by_name(name):
    for node in globalVars.objects:
        if node.get_block_name() == name:
            return node


def draw_circle(x, y, a, b, r, canvas, tag):  # center coordinates, radius

    line_length = math.sqrt((abs(x - a) ** 2 + abs(y - b) ** 2))

    multiplier = 0.12
    if line_length < 300:
        multiplier *= 2

    x_range = abs(x - a) * multiplier
    y_range = abs(y - b) * multiplier

    # top right and top left
    if x + x_range > a:
        x -= x_range
    else:
        x += x_range

    if y + y_range > b:
        y -= y_range
    else:
        y += y_range

    x0 = x - r
    y0 = y - r
    x1 = x + r
    y1 = y + r

    return canvas.create_oval(x0, y0, x1, y1, tags=(tag, 'light'))


def get_color_from_op(op):
    if op:
        return "Green"
    else:
        return "Red"


# Moves the mouse to an absolute location on the screen
def move_mouse_to(x, y):
    # Create a new temporary root
    temp_root = tk.Tk()
    # Move it to +0+0 and remove the title bar
    temp_root.overrideredirect(True)
    # Make sure the window appears on the screen and handles the `overrideredirect`
    temp_root.update()
    # Generate the event as @abarnert did
    temp_root.event_generate("<Motion>", warp=True, x=x, y=y)
    # Make sure that tcl handles the event
    temp_root.update()
    # Destroy the root
    temp_root.destroy()


def generate_mac_address():
    oui = "AF:0E:CD:"
    mac = oui
    chars = ['A', 'B', 'C', 'D', 'E', 'F', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    n = 1
    while n <= 3:
        mac += random.choice(chars)
        mac += random.choice(chars)
        if n != 3:
            mac += ':'
        n += 1

    return mac


def check_mac_address(mac_address):
    mac = mac_address.split(':')
    for m in mac:
        if any(c not in '0123456789ABCDEFabcdef' for c in m) or len(m) != 2:
            return False
    return True


def is_broadcast_mac(mac_address):
    mac = mac_address.split(':')
    return all(x == 'FF' for x in mac)


def get_broadcast_ipv4(dest_ip, source_netmask):
    broadcast_address = ''
    for x in range(4):
        if source_netmask.split('.')[x] == '255':
            broadcast_address += dest_ip.split('.')[x] + '.'
            continue
        elif source_netmask.split('.')[x] == '0':
            broadcast_address += '255' + '.'
        else:
            broadcast_address += str(int(str(bin(int(dest_ip.split('.')[x]))[2:].zfill(8)[
                                             :bin(int(source_netmask.split('.')[x]))[2:].rfind("1") + 1]) + '1' * (
                                                     8 - bin(int(source_netmask.split('.')[x]))[2:].rfind("1") - 1),
                                         2)) + '.'
    return broadcast_address[:-1]


def check_ipv4(ip):
    x = ip.split('.')
    ip_address = ''

    if len(x) != 4:
        return False

    for i in x:
        try:
            if 0 <= int(i) <= 255:
                ip_address += bin(int(i))[2:].zfill(8)
            else:
                return False
        except ValueError:
            return False

    return True


def bin_to_ipv4(binary):
    octets = wrap(binary, 8)
    ipv4 = ""
    for i in octets:
        ipv4 += str(int(i, 2)) + "."
    return ipv4[:-1]


def bin_to_hex(binary):
    hexa = hex(int(binary, 2))[2:].upper()  # convert bin to hex
    hexa = ':'.join(a + b for a, b in zip(hexa[::2], hexa[1::2]))  # add . between 2 digits
    return hexa


def check_subnet_mask(subnet_mask):
    possible_subnets = ["0", "128", "192", "224", "240", "248", "252", "254", "255"]

    if not subnet_mask:
        return False

    subnet_mask = subnet_mask.split(".")

    flag = False
    for x in subnet_mask:
        if flag and int(x) != 0 or x not in possible_subnets:
            return False

        if int(x) < 255:
            flag = True

    return True


def get_network_portion_ipv4(ip_address, subnet_mask):
    i = ip_address.split(".")
    m = subnet_mask.split(".")
    network_portion = ""

    for x in range(4):
        if m[x] == "255":
            network_portion += (i[x] + ".")
        elif m[x] == "0":
            network_portion += "0."
        else:
            n_part_last_index = bin(int(m[x]))[2:].rfind("1")
            network_portion += (str((int(bin(int(i[x]))[2:].zfill(8)[:n_part_last_index + 1].ljust(8, '0'), 2))) + ".")

    return network_portion[:-1]


def get_possible_commands(command, file_name):
    command = command.lower()
    possible_commands = []

    with open(file_name) as file:
        lines = [line.rstrip() for line in file]

    rex = re.compile(r'\b' + r'\S*' + re.escape(command) + r'\S*')

    for i in lines:
        if i.count(" ") == command.count(" "):
            z = rex.findall(i.lower())
            if z:
                if " " in z[0]:
                    possible_commands.append(z[0].rsplit(' ')[-1])
                else:
                    possible_commands.append(z[0])

    return list(set(possible_commands))  # Set makes the values unique


def is_same_subnet(source_ip, subnet_mask, destination_ip):
    a = get_network_portion_ipv4(source_ip, subnet_mask)
    b = get_network_portion_ipv4(destination_ip, subnet_mask)
    return a == b


def same_subnet_interface(interfaces, subnet_mask, destination_ip):
    same_subnet_interfaces = []
    for intf in interfaces:
        if intf.get_ipv4_address():
            if is_same_subnet(intf.get_ipv4_address(), get_subnet_from_prefix_length(subnet_mask), destination_ip):
                same_subnet_interfaces.append(intf)

    try:
        return same_subnet_interfaces[0]
    except KeyError:
        return None


def get_subnet_from_prefix_length(prefix):
    subnet = ''
    x = int(prefix) // 8
    z = int(prefix) % 8
    c = 0

    for i in range(0, z):
        c += (128 // 2 ** i)

    for i in range(x):
        subnet += '255.'
    subnet += str(c) + '.'

    for i in range(4 - subnet.count('.')):
        subnet += '0.'

    return subnet[:-1]

def get_ipv4_prefix_length(subnet_mask):
    prefix = 0

    for i in subnet_mask.split("."):
        prefix += str(bin(int(i))[2:]).count("1")
    return str(prefix)


def match_dest_ip_to_route(destination_ip, routes):
    dest_split = destination_ip.split(".")
    matches = []

    def bin_ipv4(s):
        v = ""
        v += bin(int(s[0]))[2:].zfill(8)
        v += bin(int(s[1]))[2:].zfill(8)
        v += bin(int(s[2]))[2:].zfill(8)
        v += bin(int(s[3]))[2:].zfill(8)
        v = v[:int(prefix)].ljust(int(rounded_prefix), '0')
        return v

    for i in routes:

        prefix = i.split("/")[1]
        split = i.split("/")[0].split(".")

        if 0 < int(prefix) <= 8:
            rounded_prefix = "8"
        elif 8 < int(prefix) <= 16:
            rounded_prefix = "16"
        elif 16 < int(prefix) <= 24:
            rounded_prefix = "24"
        else:
            rounded_prefix = "32"

        x = bin_ipv4(split)
        y = bin_ipv4(dest_split)

        if x == y:
            matches.append(i)

    z = 0
    longest_match = ""
    for i in matches:
        if int(i.split("/")[1]) > z:
            z = int(i.split("/")[1])
            longest_match = i

    return longest_match


def get_longest_consecutive_numbers(numbers):
    idx = max(
        (
            list(map(itemgetter(0), g))
            for i, g in groupby(enumerate(np.diff(numbers) == 1), itemgetter(1))
            if i
        ),
        key=len
    )
    return idx[0], idx[-1] + 1


def is_valid_ipv6(ipv6):
    x = ipv6.lower().split(":")

    if len(x) > 8 or len(x) < 0:
        return False

    for i in x:
        if len(i) > 4 or len(i) < 0:
            return False

        elif not all((c in 'abcdef1234567890') for c in i):
            return False

    return True


def shorten_ipv6(ipv6):
    x = ipv6.split(":")

    # 0's
    for j, i in enumerate(x):

        # Collapse 0000's
        if i == '0000':
            x[j] = '0'
            continue

        # Remove leading 0's
        if i[0] == '0':
            x[j] = i.lstrip('0')

    # Get the longest sequence of 0:, and collapse it to ::
    indices = [i for i, j in enumerate(x) if j == '0']
    if len(indices) > 1:
        longest = get_longest_consecutive_numbers(indices)
        start = indices[longest[0]]
        end = indices[longest[1]]
        x = x[:start] + x[end:]
        x[start] = ''

    # Rebuild address from list
    shortened = ''
    for i in x:
        shortened += i + ':'

    return shortened[:-1].lower()


def lengthen_ipv6(ipv6):
    x = ipv6.split(':')

    for i, j in enumerate(x):
        if len(j) == 4:
            continue

        if not j:
            x[i] = j.zfill(4)
            continue

        x[i] = j.zfill(4)

    lengthened = ''
    for i in x:
        lengthened += i + ':'

    return lengthened[:-1].lower()


def is_valid_ipv6_prefix(ipv6_prefix):
    return 0 < int(ipv6_prefix) <= 128


def get_network_portion_ipv6(ipv6, prefix):
    if prefix == 128:
        return ipv6.lower()

    section = prefix // 16
    x = ipv6.split(':')
    network_portion = x[:section]
    network_address = ''

    bit_difference = prefix - (section * 16)
    if bit_difference > 0:
        y = x[section]
        y = bin(int(y, 16))[2:].zfill(16)
        y = hex(int(y[:bit_difference].ljust(16, '0'), 2))[2:].zfill(4)

        network_portion.append(y)

        for i in network_portion:
            network_address += i + ':'
        network_address += ':'

    return network_address.lower()


def compute_ping_stats(ping_rtt_times, dest_ipv4_address, count, received_ping_count, canvas, host):
    min_time = "0ms"
    max_time = "0ms"
    average_time = "0ms"
    try:
        if min(ping_rtt_times) > 0.001:
            min_time = str(round(min(ping_rtt_times), 1))
        if max(ping_rtt_times) > 0.001:
            max_time = str(round(max(ping_rtt_times), 1))
        if sum(ping_rtt_times) / len(ping_rtt_times) > 0.001:
            average_time = str(round(sum(ping_rtt_times) / len(ping_rtt_times), 1))
    except ValueError:
        pass

    ping_stats = "\nPing Statistics for " + str(
        dest_ipv4_address) + ":\n\tPackets: Sent = " + str(count) + ", Received = " + str(
        received_ping_count) + ", Lost = " + str(count - received_ping_count) + " (" + str(
        100 - (received_ping_count / count) * 100) + "% loss),\n"
    ping_rtt_stats = "Approximate round trip times in milli-seconds:\n\tMinimum = " + min_time + ", Maximum = " + \
                     max_time + ", Average = " + average_time

    canvas.get_info(info=ping_stats + ping_rtt_stats, linebreak=True, last=True)
    canvas.toggle_cli_busy()
    host.reset_ping_count(0)


def create_tooltip(canvas, button, text, tag, pos=(0, 0), text_offset=(0, 0)):
    if button.cget('relief') == 'sunken':
        x = pos[0]
        y = pos[1]

        tooltip_icon = loadIcons.get_tooltip_icon()[0]

        tooltip_text = canvas.create_text(x + 105 + text_offset[0], y + 12 + text_offset[1], text=text, fill="black",
                                          font=("Arial", 10), tags=tag)
        tooltip_bg = canvas.create_polygon(x + 40, y + 13, x + 50, y + 8, x + 50, y - 1, x + 162 + (text_offset[0] * 2),
                                           y - 1 + (text_offset[1] * 2),
                                           x + 162 + (text_offset[0] * 2), y + 24 + (text_offset[1] * 2), x + 50,
                                           y + 24,
                                           x + 50, y + 16,
                                           fill="#fefec3", tags=tag, outline="black")

        canvas.create_image(x + 167 + (text_offset[0] * 2), y - 1 + (text_offset[1] * 2), image=tooltip_icon, tag=tag)
        canvas.photo = tooltip_icon

        canvas.tag_lower(tooltip_bg, tooltip_text)


def open_folder_dialogue(preferences_menu, path):
    globalVars.file_directory = filedialog.askdirectory(initialdir=globalVars.file_directory, title="Select a File")

    # Save preferences when anything changes
    with open('../preferences.json', 'w') as F:
        F.write(json.dumps([globalVars.file_directory, globalVars.ask_before_delete, globalVars.ask_before_quick_delete,
                            globalVars.show_link_lights, globalVars.persistent_cable_connect]))

    path.configure(state='normal')
    path.delete("1.0", "end")
    path.insert('end', globalVars.file_directory)
    path.configure(state='disabled')
    preferences_menu.focus_set()


def show_info(selected_item, help_menu):

    file = ''
    match selected_item:
        case 'Network Simulator':
            file = './markdown_files/Network_Simulator.html'
        case 'PCs':
            file = './markdown_files/PC.html'
        case 'Switches':
            file = './markdown_files/Switch.html'
        case 'Routers':
            file = './markdown_files/Router.html'
        case 'Firewalls':
            file = './markdown_files/Firewall.html'
        case 'Connecting Nodes':
            file = './markdown_files/Connecting_Nodes.html'
        case 'Areas':
            file = './markdown_files/Areas.html'
        case 'Labels':
            file = './markdown_files/Labels.html'
        case 'Deleting Things':
            file = './markdown_files/Deleting_Things.html'
        case _:
            info = None

    if file:
        with open(file, 'r') as f:
            info = f.read()

    info_box = tkinterweb.HtmlFrame(help_menu, messages_enabled=False)
    if info:
        info_box.load_html(info)
    else:
        info_box.load_html('')

    info_box.grid(row=0, column=1, sticky="nsew", pady=6, padx=10)
    help_menu.columnconfigure(1, weight=1)


def clean_up_ui(dont_close, canvas):

    for eth in globalVars.cable_objects:
        if not eth.get_cable_end_1():
            eth.self_delete_on_duplicate()

    for q in canvas.find_withtag('Quick_Delete'):
        canvas.delete(q)

    match dont_close:
        case "PC":
            try:
                globalVars.TL_ro.destroy()
            except AttributeError:
                pass

            try:
                globalVars.TL_sw.destroy()
            except AttributeError:
                pass

            try:
                globalVars.tl_lb.destroy()
            except AttributeError:
                pass

        case "SW":
            try:
                globalVars.TL_ro.destroy()
            except AttributeError:
                pass

            try:
                globalVars.TL_pc.destroy()
            except AttributeError:
                pass

            try:
                globalVars.tl_lb.destroy()
            except AttributeError:
                pass

        case "RO":
            try:
                globalVars.TL_sw.destroy()
            except AttributeError:
                pass

            try:
                globalVars.TL_pc.destroy()
            except AttributeError:
                pass

            try:
                globalVars.tl_lb.destroy()
            except AttributeError:
                pass

        case "LB":
            try:
                globalVars.TL_ro.destroy()
            except AttributeError:
                pass

            try:
                globalVars.TL_pc.destroy()
            except AttributeError:
                pass

            try:
                globalVars.TL_sw.destroy()
            except AttributeError:
                pass

        case "ALL":
            try:
                globalVars.TL_ro.destroy()
            except AttributeError:
                pass

            try:
                globalVars.TL_pc.destroy()
            except AttributeError:
                pass

            try:
                globalVars.TL_sw.destroy()
            except AttributeError:
                pass

            try:
                globalVars.tl_lb.destroy()
            except AttributeError:
                pass

        case _:
            pass


def set_layers(canvas):

    for i in canvas.find_withtag('Rectangle'):
        canvas.tag_lower(i, 'all')

    for i in canvas.find_withtag('light'):
        [canvas.tag_lower(i, node) for node in canvas.find_withtag('Node')]
        [canvas.tag_raise(i, line) for line in canvas.find_withtag('Ethernet')]

    for i in canvas.find_withtag('Node'):
        canvas.tag_raise(i, 'all')

    for i in canvas.find_withtag('Hover_Menus'):
        canvas.tag_raise(i, 'all')

    for i in canvas.find_withtag('Menu_Button'):
        canvas.tag_raise(i, 'all')


def get_ip_range(network_address, subnet_or_prefix, is_prefix):

    if is_prefix:
        subnet = get_subnet_from_prefix_length(subnet_or_prefix)
    else:
        subnet = subnet_or_prefix

    network_portion = get_network_portion_ipv4(network_address, subnet).strip('.0')
    intermediate_ip_pool = []  # IPs that are being built are stored here
    ip_pool = []  # IPs that are complete are stored here

    zero_count = subnet.count('0')
    count = -1

    for s in subnet.split('.'):

        count += 1

        if s == '255':
            continue

        if s != '0':

            if int(network_address.split('.')[count]) < int(subnet.split('.')[count]):
                for j in range(255 - int(s)):
                    if zero_count == 0:
                        ip_pool.append(network_portion + '.' + str(j))
                    else:
                        intermediate_ip_pool.append(network_portion + '.' + str(j))

            else:
                network_portion = '.'.join(network_portion.split('.')[:count])
                for j in range(int(s) + 1, 255):
                    if zero_count == 0:
                        ip_pool.append(network_portion + '.' + str(j))
                    else:
                        intermediate_ip_pool.append(network_portion + '.' + str(j))

        if s == '0':
            if not intermediate_ip_pool:
                intermediate_ip_pool = [network_portion]

            for ip in range(len(intermediate_ip_pool)):
                if zero_count == 1:
                    for i in range(1, 255):
                        new_ip = intermediate_ip_pool[ip] + '.' + str(i)
                        ip_pool.append(new_ip)

                elif zero_count == 2:
                    for i in range(256):
                        for j in range(1, 255):
                            new_ip = intermediate_ip_pool[ip] + '.' + str(i) + '.' + str(j)
                            ip_pool.append(new_ip)

                elif zero_count == 3 or zero_count == 4:
                    raise Exception('Pool too large!')

            break

    return ip_pool


def get_ip_range_from_to(start_ip, end_ip):

    network_portion = ''

    intermediate_ip_pool = []  # IPs that are being built are stored here
    ip_pool = []  # IPs that are complete are stored here

    for a, b in zip(start_ip.split('.'), end_ip.split('.')):
        if a == b:
            network_portion += a + '.'


    subnet = '255.' * network_portion.count('.')
    network_portion = network_portion[:-1]
    ip_address = network_portion

    for i in range(4 - subnet.count('.')):
        subnet += '0.'
        ip_address += '0.'

    subnet = subnet[:-1]
    ip_address = ip_address[:-1]

    zero_count = subnet.count('0')
    count = -1
    stop = False
    for s in subnet.split('.'):

        count += 1

        if s == '255':
            continue

        if s != '0' and not stop:
            if int(ip_address.split('.')[count]) < int(subnet.split('.')[count]):
                for j in range(255 - int(s)):
                    if not stop:
                        if zero_count == 0:
                            ip_pool.append(network_portion + '.' + str(j))
                            if network_portion + '.' + str(j) == end_ip:
                                stop = True
                        else:
                            intermediate_ip_pool.append(network_portion + '.' + str(j))
                    else:
                        break

            else:
                network_portion = '.'.join(network_portion.split('.')[:count])
                for j in range(int(s) + 1, 255):
                    if not stop:
                        if zero_count == 0:
                            ip_pool.append(network_portion + '.' + str(j))
                            if network_portion + '.' + str(j) == end_ip:
                                stop = True
                        else:
                            intermediate_ip_pool.append(network_portion + '.' + str(j))
                    else:
                        break

        if s == '0':
            if not intermediate_ip_pool:
                intermediate_ip_pool = [network_portion]

            for ip in range(len(intermediate_ip_pool)):
                if zero_count == 1:
                    for i in range(1, 255):

                        if not stop:
                            new_ip = intermediate_ip_pool[ip] + '.' + str(i)
                            ip_pool.append(new_ip)
                            if new_ip == end_ip:
                                stop = True
                        else:
                            break

                elif zero_count == 2:
                    for i in range(256):
                        for j in range (1, 255):
                            if not stop:
                                new_ip = intermediate_ip_pool[ip] + '.' + str(i) + '.' + str(j)
                                ip_pool.append(new_ip)
                                if new_ip == end_ip:
                                    stop = True
                            else:
                                break

                elif zero_count == 3 or zero_count == 4:
                    raise Exception('Pool too large!')

            break

    return ip_pool


def get_lease_time(lease_time):
    days_as_seconds = int(lease_time[0]) * 24 * 3600
    hours_as_seconds = int(lease_time[1]) * 3600
    minutes_as_seconds = int(lease_time[2]) * 60
    return days_as_seconds + hours_as_seconds + minutes_as_seconds


def build_tid_table():
    return {"REQUEST_SUBNET_MASK": '', 'REQUEST_ROUTER': '', 'REQUEST_DNS_SERVER': '', 'REQUEST_DOMAIN_NAME': '',
            'LEASE_TIME': '', 'DHCP_IP_ADDRESS': ''}


def build_ip_config_line(description, value):
    while len(description) < 34:
        if len(description) % 2 == 0:
            description += '. '
        else:
            description += ' '
    return description + ': ' + value

def month_name_to_number(name):
    match name:
        case 'January': return 1
        case 'February': return 2
        case 'March': return 3
        case 'April': return 4
        case 'May': return 5
        case 'June': return 6
        case 'July': return 7
        case 'August': return 8
        case 'September': return 9
        case 'October': return 10
        case 'November': return 11
        case 'December': return 12


def str_time_to_datetime(t):

    time = t.replace(',', '').split(' ')
    year = int(time[3])
    month = month_name_to_number(time[1])
    day = int(time[2])

    hms = time[4].split(':')
    am_pm = time[5]

    if am_pm == 'PM':
        hour = int(hms[0]) + 12
    else:
        hour = int(hms[0])

    minute = int(hms[1])
    second = int(hms[2])

    return datetime(year, month, day, hour, minute, second)