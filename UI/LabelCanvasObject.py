from operations import globalVars
import UI.helper_functions as hf


class LabelCanvasObject:
    def __init__(self, canvas, label_id, text, load=False):
        self.canvas = canvas
        self.block_name = label_id
        self.text = text
        self.delete_tag = 'Label_Delete'

        if not load:
            # Label Stuff
            x = self.canvas.canvasx(805)  # hard coded coordinates because it's easier that way
            y = self.canvas.canvasy(368)

            hf.move_mouse_to(805, 410)

            self.label = self.canvas.create_text(x, y, text=self.text, fill="black", font=("Arial", 9),
                                                 tags=(self.block_name, "Label", self.delete_tag))
            self.x = self.canvas.bbox(self.label)[0] - 7
            self.y = self.canvas.bbox(self.label)[1] - 4
            self.a = self.canvas.bbox(self.label)[2] + 7
            self.b = self.canvas.bbox(self.label)[3] + 4

            globalVars.label_state = False  # If a new label is created, the label_state should be true.
            # If it causes a mismatch, a reset will occur, showing all. ^

            self.label_bg = self.canvas.create_rectangle(self.x, self.y, self.a, self.b, fill="gray94",
                                                         tags=(self.block_name + "_bg", "Label_BG", self.delete_tag))
            self.canvas.tag_lower(self.label_bg, self.label)
            self.canvas.tag_lower(self.label, 'all')
            self.canvas.tag_lower(self.label_bg, 'all')

            self.hidden_label = False
            # Label Stuff

        # Button Bindings
        self.canvas.tag_bind(self.block_name, '<B1-Motion>', self.motion)  # After the object is created
        self.canvas.tag_bind(self.block_name + "_bg", '<B1-Motion>', self.motion)  # After the object is created

        # Button Bindings

    def motion(self, event):
        # Move the object
        self.canvas.coords(self.block_name, self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

        self.x = self.canvas.bbox(self.label)[0] - 7
        self.y = self.canvas.bbox(self.label)[1] - 4
        self.a = self.canvas.bbox(self.label)[2] + 7
        self.b = self.canvas.bbox(self.label)[3] + 4

        self.canvas.coords(self.block_name + "_bg", self.x, self.y, self.a, self.b)

        globalVars.prompt_save = True
        return

    def toggle_label(self, reset):
        if not reset:
            self.hidden_label = globalVars.label_state = not self.hidden_label
            if self.hidden_label:
                self.canvas.itemconfigure(self.block_name, state='hidden')
                self.canvas.itemconfigure(self.block_name + "_bg", state='hidden')
            else:
                self.canvas.itemconfigure(self.block_name, state='normal')
                self.canvas.itemconfigure(self.block_name + "_bg", state='normal')
        else:
            self.hidden_label = False
            self.canvas.itemconfigure(self.block_name, state='normal')
            self.canvas.itemconfigure(self.block_name + "_bg", state='normal')

    def delete(self):
        self.canvas.delete(self.label)
        self.canvas.delete(self.label_bg)
        globalVars.prompt_save = True

    def get_block_name(self):
        return self.block_name

    def get_delete_tag(self):
        return self.delete_tag

    # -------------------------- Save & Load Methods -------------------------- #
    def get_save_info(self):
        c = self.canvas.coords(self.label)
        return [self.block_name, self.text, self.x, self.y, self.a, self.b, c[0], c[1]]

    def set_coords(self, x, y, a, b, l_x, l_y):

        self.x = x
        self.y = y
        self.a = a
        self.b = b

        self.label = self.canvas.create_text(l_x, l_y, text=self.text, fill="black", font=("Arial", 10),
                                             tags=(self.block_name, "Label", self.delete_tag))

        self.x = self.canvas.bbox(self.label)[0] - 7
        self.y = self.canvas.bbox(self.label)[1] - 4
        self.a = self.canvas.bbox(self.label)[2] + 7
        self.b = self.canvas.bbox(self.label)[3] + 4

        self.label_bg = self.canvas.create_rectangle(self.x, self.y, self.a, self.b, fill="gray94",
                                                     tags=(self.block_name, "Label_BG", self.delete_tag))

        self.canvas.tag_lower(self.label_bg, self.label)
        self.canvas.tag_lower(self.label, 'all')
        self.canvas.tag_lower(self.label_bg, 'all')

        self.hidden_label = globalVars.label_state
        if self.hidden_label:
            self.canvas.itemconfigure(self.block_name, state='hidden')
            self.canvas.itemconfigure(self.block_name + "_bg", state='hidden')
        else:
            self.canvas.itemconfigure(self.block_name, state='normal')
            self.canvas.itemconfigure(self.block_name + "_bg", state='normal')
    # -------------------------- Save & Load Methods -------------------------- #
