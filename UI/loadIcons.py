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


def get_router_icons():
    ro_icon = Image.open('icons/router.png')
    ro_icon = ro_icon.resize((75, 75))
    ro_icon1 = ImageTk.PhotoImage(ro_icon)

    terminal_icon = Image.open('icons/terminal.png')
    terminal_icon = terminal_icon.resize((25, 25))
    terminal_icon1 = ImageTk.PhotoImage(terminal_icon)

    ethernet_del_icon = Image.open('icons/ethernet_delete.png')
    ethernet_del_icon = ethernet_del_icon.resize((25, 25))
    ethernet_del_icon1 = ImageTk.PhotoImage(ethernet_del_icon)

    x_node_icon = Image.open('icons/delete_node.png')
    x_node_icon = x_node_icon.resize((20, 20))
    x_node_icon1 = ImageTk.PhotoImage(x_node_icon)

    return [ro_icon1, terminal_icon1, ethernet_del_icon1, x_node_icon1]


def get_ethernet_icon():
    eth_icon = Image.open("icons/ethernet.png")
    eth_icon = eth_icon.resize((50, 50))
    eth_icon1 = ImageTk.PhotoImage(eth_icon)

    return [eth_icon1]


def get_label_icon():
    label_icon = Image.open('icons/label.png')
    label_icon = label_icon.resize((75, 75))
    label_icon1 = ImageTk.PhotoImage(label_icon)

    return [label_icon1]


def get_tooltip_icon():
    tooltip_icon = Image.open('icons/tooltip.png')
    tooltip_icon = tooltip_icon.resize((20, 20))
    tooltip_icon1 = ImageTk.PhotoImage(tooltip_icon)

    return [tooltip_icon1]


def get_preferences_icon():
    preferences_icon = Image.open('icons/preferences.png')
    preferences_icon = preferences_icon.resize((25, 25))
    preferences_icon1 = ImageTk.PhotoImage(preferences_icon)

    return [preferences_icon1]


def get_help_menu_icon():
    help_menu_icon = Image.open('icons/help.png')
    help_menu_icon = help_menu_icon.resize((25, 25))
    help_menu_icon1 = ImageTk.PhotoImage(help_menu_icon)

    return [help_menu_icon1]


def get_app_icon():
    app_icon = Image.open('./icons/net-sim.png')
    app_icon = app_icon.resize((25, 25))
    app_icon1 = ImageTk.PhotoImage(app_icon)
    return [app_icon1]
