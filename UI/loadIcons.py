from PIL import Image, ImageTk


def get_pc_icons():
    pc_icon = Image.open('icons/desktop-computer.png')
    pc_icon = pc_icon.resize((75, 75))
    pc_icon1 = ImageTk.PhotoImage(pc_icon)

    config_icon = Image.open('icons/gear.png')
    config_icon = config_icon.resize((25, 25))
    config_icon1 = ImageTk.PhotoImage(config_icon)

    terminal_icon = Image.open('icons/terminal.png')
    terminal_icon = terminal_icon.resize((25, 25))
    terminal_icon1 = ImageTk.PhotoImage(terminal_icon)

    ethernet_del_icon = Image.open('icons/ethernet_delete.png')
    ethernet_del_icon = ethernet_del_icon.resize((25, 25))
    ethernet_del_icon1 = ImageTk.PhotoImage(ethernet_del_icon)

    x_node_icon = Image.open('icons/delete_node.png')
    x_node_icon = x_node_icon.resize((20, 20))
    x_node_icon1 = ImageTk.PhotoImage(x_node_icon)

    return [pc_icon1, config_icon1, terminal_icon1, ethernet_del_icon1, x_node_icon1]


def get_sw_icons():
    sw_icon = Image.open('icons/switch.png')
    sw_icon = sw_icon.resize((75, 75))
    sw_icon1 = ImageTk.PhotoImage(sw_icon)

    terminal_icon = Image.open('icons/terminal.png')
    terminal_icon = terminal_icon.resize((25, 25))
    terminal_icon1 = ImageTk.PhotoImage(terminal_icon)

    ethernet_del_icon = Image.open('icons/ethernet_delete.png')
    ethernet_del_icon = ethernet_del_icon.resize((25, 25))
    ethernet_del_icon1 = ImageTk.PhotoImage(ethernet_del_icon)

    x_node_icon = Image.open('icons/delete_node.png')
    x_node_icon = x_node_icon.resize((20, 20))
    x_node_icon1 = ImageTk.PhotoImage(x_node_icon)

    return [sw_icon1, terminal_icon1, ethernet_del_icon1, x_node_icon1]
