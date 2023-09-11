from operations.InternalClock import InternalTime

# ------- Screen Dimensions ------- #
screen_width = 0
screen_height = 0
# ------- Screen Dimensions ------- #

# ------------ Object Lists ------------ #
objects = []
pc_objects = []
sw_objects = []
ro_objects = []
fw_objects = []
cable_objects = []
canvas_rectangles = []
canvas_labels = []
node_number = 0
internal_clock = InternalTime()
# ------------ Object Lists ------------ #

# ------------ States ------------ #
light_state = True      # True as in showing
label_state = False     # False as in not hiding
prompt_save = False     # Has anything changed
# ------------ States ------------ #

# ------------ Pop up variables to ensure only 1 of the same window is open at a time ------------ #
open_TL_pc = False
TL_pc = None

open_TL_sw = False
TL_sw = None

open_TL_ro = False
TL_ro = None

open_TL_fw = False
tl_fw = None

open_TL_lb = False
tl_lb = None
# ------------ Pop up variables to ensure only 1 of the same window is open at a time ------------ #

# ------------ Preference Variables ------------ #
ask_before_delete = True
ask_before_quick_delete = True
show_link_lights = True
persistent_cable_connect = True
# ------------ Preference Variables ------------ #

# ---------- File Stuff ---------- #
file_directory = "/"
working_file = ''
# ---------- File Stuff ---------- #


# ------------ Reset Canvas ------------ #
def clear_all_objects():
    global objects, pc_objects, sw_objects, ro_objects, fw_objects, cable_objects, \
        canvas_rectangles, canvas_labels, node_number, open_TL_pc, TL_pc, open_TL_sw, TL_sw, \
        open_TL_ro, TL_ro, open_TL_fw, tl_fw, open_TL_lb, tl_lb

    for i in objects:
        i.menu_delete(None, True, reset=True)

    for i in canvas_rectangles:
        i.delete()

    for i in canvas_labels:
        i.delete()

    try:
        # Won't be None if load_save.open() is called two times in the same window
        TL_pc.destroy()
        TL_sw.destroy()
        TL_ro.destroy()
        tl_fw.destroy()
        tl_lb.destroy()

    except AttributeError:
        pass

    objects = []
    pc_objects = []
    sw_objects = []
    ro_objects = []
    fw_objects = []
    cable_objects = []
    canvas_rectangles = []
    canvas_labels = []
    node_number = 0

    open_TL_pc = False
    TL_pc = None

    open_TL_sw = False
    TL_sw = None

    open_TL_ro = False
    TL_ro = None

    open_TL_fw = False
    tl_fw = None

    open_TL_lb = False
    tl_lb = None
# ------------ Reset Canvas ------------ #