import tkinter as tk
from tkinter import messagebox
from UI import helper_functions as hf
import globalVars
from network import Ethernet_Cable


class EthernetCableCanvasObject:

    def __init__(self, canvas, block_name, icon, class_object, master, cursor_pos=(350, 800)):
        self.canvas = canvas
        self.master = master
        self.block_name = block_name
        self.class_object = class_object

        # Current Cursor Location
        # For placing the new widget under the mouse
        hf.move_mouse_to(cursor_pos[0], cursor_pos[1])
        x = self.canvas.canvasx(self.canvas.winfo_pointerx() - self.canvas.winfo_rootx())
        y = self.canvas.canvasy(self.canvas.winfo_pointery() - self.canvas.winfo_rooty())
        # Current Cursor Location

        # Icon Stuff
        self.icon = icon
        # Assigned to canvas_object to allow delete
        self.canvas_object = self.canvas.create_image(x, y, image=self.icon, tags=(self.block_name, "Ethernet"))
        self.canvas.photo = self.icon
        # Icon Stuff

        # Button Bindings
        self.canvas.tag_bind(self.block_name, '<Motion>', self.motion)  # When creating the object
        self.canvas.tag_bind(self.block_name, '<Button-1>', self.motion)  # When creating the object
        # Button Bindings

        # Objects to connect to
        self.canvas_line = None

        self.class_object_1 = None
        self.class_object_2 = None

        self.canvas_object_1 = None
        self.canvas_object_2 = None

        self.obj1_coords = None  # coords of canvas object 1
        self.obj2_coords = None  # coords of canvas object 2

        self.obj1_canvas_tag = None
        self.obj2_canvas_tag = None

        self.cable_end_1 = None  # Interface End 1
        self.cable_end_2 = None  # Interface End 2

        self.existing_line_count = 0
        # Objects to connect to

        # Link Lights
        self.light_1 = None
        self.light_2 = None
        # Link Lights

    @classmethod
    def persistent_cable_connect(cls, c, icon, master, cursor_position):
        cable = cls(c, hf.get_next_cable(c), icon, Ethernet_Cable.EthernetCable(), master, cursor_position)
        globalVars.cable_objects.append(cable)

    def motion(self, event):

        # Move the object
        self.canvas.coords(self.block_name, self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

        # Continuously check object hovering over and assign it to var
        overlap = self.canvas.find_overlapping(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y),
                                               self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        canvas_object_tag = ""
        for i in overlap:
            if i in self.canvas.find_withtag("PC"):
                canvas_object_tag = self.canvas.itemcget(i, "tags").split(" ")[0]

            elif i in self.canvas.find_withtag("Switch"):
                canvas_object_tag = self.canvas.itemcget(i, "tags").split(" ")[0]

            elif i in self.canvas.find_withtag("Router"):
                canvas_object_tag = self.canvas.itemcget(i, "tags").split(" ")[0]

        # On click, check what was clicked, and delete cable
        if str(event.type) == "4":

            # if cable clicked on nothing
            if len(overlap) < 2:
                self.canvas.delete(self.canvas_object)
                self.cable_end_1 = None
                self.cable_end_2 = None
                return

            for i in globalVars.objects:
                if i.get_block_name() == canvas_object_tag:
                    if not self.obj1_coords:
                        self.obj1_coords = self.canvas.coords(canvas_object_tag)  # obj 1 coords
                        self.obj1_canvas_tag = canvas_object_tag  # obj 1 canvas tag
                    else:
                        self.obj2_coords = self.canvas.coords(canvas_object_tag)
                        self.obj2_canvas_tag = canvas_object_tag
                    self.show_interfaces(event, i)
                    break
        return

    def delete_canvas_cable(self):

        l1, l2 = self.canvas_object_1.get_lights(self)

        self.canvas.delete(l1)
        self.canvas.delete(l2)

        # Still needed in case lights never moved
        self.canvas.delete(self.light_1)
        self.canvas.delete(self.light_2)

        self.canvas.delete(self.canvas_line)

        self.canvas_object_1.del_line_connection(self)
        self.canvas_object_2.del_line_connection(self)

        self.cable_end_1.disconnect()
        self.cable_end_2.disconnect()

    def show_interfaces(self, event, host_object):
        submenu = tk.Menu(self.canvas, tearoff=0)

        try:
            for i in host_object.get_class_object().get_interfaces():
                if not i.get_is_connected():
                    submenu.add_command(label=i.__str__(), command=lambda intf=i: self.attach_end(intf))

        except AttributeError:
            self.canvas.delete(self.canvas_object)
            self.cable_end_1 = None
            self.cable_end_2 = None

        submenu.tk_popup(event.x_root, event.y_root)

    def attach_end(self, interface):
        if not self.cable_end_1:
            self.cable_end_1 = interface
        else:
            if self.cable_end_1.get_host() != interface.get_host():
                self.cable_end_2 = interface
            else:
                messagebox.showerror('Invalid Connection', 'Cannot connect cable to same device', parent=self.canvas)

        # If both ends are connected
        if self.cable_end_1 and self.cable_end_2:

            # The class objects
            self.class_object_1 = self.cable_end_1.get_host()
            self.class_object_2 = self.cable_end_2.get_host()

            # The canvas objects
            self.canvas_object_1 = self.class_object_1.get_canvas_object()
            self.canvas_object_2 = self.class_object_2.get_canvas_object()

            self.existing_line_count, lines = self.canvas_object_1.get_line_connection_count(self.obj1_canvas_tag,
                                                                                             self.obj2_canvas_tag)

            # Objects' relation to each other (quadrants)
            if self.obj1_coords[0] < self.obj2_coords[0]:
                x_flag = True
            else:
                x_flag = False
            if self.obj1_coords[1] < self.obj2_coords[1]:
                y_flag = True
            else:
                y_flag = False

            # How to shift the new line based on the line relations
            x_shift = 0
            y_shift = 0
            if x_flag and not y_flag:  # Left and Under
                x_shift = 4 * self.existing_line_count
                y_shift = 4 * self.existing_line_count
            elif x_flag and y_flag:  # Left and Above
                x_shift = 4 * self.existing_line_count
                y_shift = -4 * self.existing_line_count
            elif not x_flag and not y_flag:  # Right and Under
                x_shift = -4 * self.existing_line_count
                y_shift = 4 * self.existing_line_count
            elif not x_flag and y_flag:  # Right and Above
                x_shift = -4 * self.existing_line_count
                y_shift = -4 * self.existing_line_count

            # Draw Line
            self.canvas_line = self.canvas.create_line(self.obj1_coords[0] + x_shift, self.obj1_coords[1] + y_shift,
                                                       self.obj2_coords[0] + x_shift,
                                                       self.obj2_coords[1] + y_shift, fill="black", width=2,
                                                       tags=(
                                                           self.obj1_canvas_tag + "_line_" + self.obj2_canvas_tag +
                                                           "_" + str(self.existing_line_count),
                                                           self.obj2_canvas_tag + "_line_" + self.obj1_canvas_tag +
                                                           "_" + str(self.existing_line_count), 'line'))

            self.light_1 = hf.draw_circle(self.obj1_coords[0] + x_shift, self.obj1_coords[1] + y_shift,
                                          self.obj2_coords[0] + x_shift, self.obj2_coords[1] + y_shift, 4,
                                          self.canvas, self.obj1_canvas_tag + "_light_" + self.obj2_canvas_tag +
                                          "_" + str(self.existing_line_count))

            self.light_2 = hf.draw_circle(self.obj2_coords[0] + x_shift, self.obj2_coords[1] + y_shift,
                                          self.obj1_coords[0] + x_shift, self.obj1_coords[1] + y_shift, 4,
                                          self.canvas, self.obj2_canvas_tag + "_light_" + self.obj1_canvas_tag +
                                          "_" + str(self.existing_line_count))

            # Lower line and lights one layer to underlap the hover menu and canvas object
            for light in self.canvas.find_withtag('light'):
                self.canvas.tag_lower(light)

            for line in self.canvas.find_withtag('line'):
                self.canvas.tag_lower(line)

            for rectangle in self.canvas.find_withtag('Rectangle'):
                self.canvas.tag_lower(rectangle)

            # Add each light to the cable class
            self.cable_end_1.set_canvas_object(self)
            self.cable_end_2.set_canvas_object(self)

            # Each canvas object adds this connection to their own dictionary of connections
            self.canvas_object_1.add_line_connection(self.obj1_canvas_tag, self.obj2_canvas_tag, self.light_1,
                                                     self.light_2, self)
            self.canvas_object_2.add_line_connection(self.obj1_canvas_tag, self.obj2_canvas_tag, self.light_1,
                                                     self.light_2, self)

            # Pass the interfaces that are connected to each canvas object

            self.canvas_object_1.set_interfaces(self.canvas_line, self.cable_end_1, self.cable_end_2)
            self.canvas_object_2.set_interfaces(self.canvas_line, self.cable_end_2, self.cable_end_1)

            # Logically connect the nodes
            self.class_object.connect(self.class_object_1, self.cable_end_1, self.class_object_2, self.cable_end_2)

            # Set interfaces as connected and operational
            self.cable_end_1.set_is_connected(True)
            self.cable_end_2.set_is_connected(True)

            # Routers are down by default
            if self.class_object_1.get_model() == "R94X":
                self.cable_end_1.set_operational(False)
                self.cable_end_2.set_operational(True)
            elif self.class_object_2.get_model() == "R94X":
                self.cable_end_2.set_operational(False)
                self.cable_end_1.set_operational(True)
            else:
                self.cable_end_1.set_operational(True)
                self.cable_end_2.set_operational(True)

            if not globalVars.show_link_lights:
                self.canvas.itemconfig(self.light_1, state='hidden')
                self.canvas.itemconfig(self.light_2, state='hidden')

            self.canvas.delete(self.canvas_object)

            # If persistent cable connect, create a new instance of this class
            if globalVars.persistent_cable_connect:
                cursor_x = self.master.winfo_pointerx() - self.master.winfo_rootx()
                cursor_y = self.master.winfo_pointery() - self.master.winfo_rooty()
                EthernetCableCanvasObject.persistent_cable_connect(self.canvas, self.icon, self.master,
                                                                   (cursor_x, cursor_y + 45))

    def set_light(self, color, side):
        if self.canvas.find_withtag(side + "_light_" + self.obj1_canvas_tag + "_" + str(self.existing_line_count)):
            self.canvas.itemconfig(self.canvas.find_withtag(side + "_light_" + self.obj1_canvas_tag + "_" +
                                                            str(self.existing_line_count)), fill=color)
        elif self.canvas.find_withtag(side + "_light_" + self.obj2_canvas_tag + "_" + str(self.existing_line_count)):
            self.canvas.itemconfig(self.canvas.find_withtag(side + "_light_" + self.obj2_canvas_tag + "_" +
                                                            str(self.existing_line_count)), fill=color)

    def get_obj_1(self):
        return self.canvas_object_1

    def get_obj_2(self):
        return self.canvas_object_2

    def set_lights(self, l1, l2):
        self.light_1 = l1
        self.light_2 = l2

    def get_cable_end_1(self):
        return self.cable_end_1

    def get_cable_end_2(self):
        return self.cable_end_2

    def get_class_object_1(self):
        return self.class_object_1

    def get_class_object_2(self):
        return self.class_object_2

    def get_save_info(self):
        return [self.block_name, self.obj1_coords, self.obj2_coords, self.obj1_canvas_tag, self.obj2_canvas_tag]
