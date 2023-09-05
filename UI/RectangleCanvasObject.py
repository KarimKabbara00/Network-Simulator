import globalVars

class RectangleCanvasObject:
    def __init__(self, canvas, color_code, rect_id, load=False):
        self.canvas = canvas
        self.block_name = rect_id

        # Rectangle object
        self.rectangle_object = None
        self.temp_rectangle = None
        # Rectangle object

        # Rectangle coordinates
        self.is_set = False
        self.x = None
        self.y = None
        self.a = None
        self.b = None
        # Rectangle coordinates

        # Button Bindings
        if not load:  # When loading a saved file, skip these
            self.color_code = color_code[1]
            self.canvas.bind('<B1-Motion>', self.start)  # When creating the object
            self.canvas.bind('<ButtonRelease-1>', self.end)  # When creating the object
            self.canvas.config(cursor="pencil")
        else:
            self.color_code = color_code
        # Button Bindings

    def start(self, event):
        if not self.is_set:
            self.x = event.x
            self.y = event.y
            self.temp_rectangle = self.canvas.create_rectangle(self.canvas.canvasx(self.x), self.canvas.canvasy(self.y),
                                                               self.canvas.canvasx(event.x),
                                                               self.canvas.canvasy(event.y), outline="black",
                                                               fill=self.color_code, width=1.2,
                                                               tags=(self.block_name, "Rectangle"))
            self.is_set = True

        self.canvas.tag_lower(self.block_name)
        self.canvas.coords(self.block_name, self.canvas.canvasx(self.x), self.canvas.canvasy(self.y),
                           self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        return

    def end(self, event):
        self.a = event.x
        self.b = event.y
        self.canvas.unbind('<B1-Motion>')  # When creating the object
        self.canvas.unbind('<ButtonRelease-1>')  # When creating the object
        self.canvas.delete(self.temp_rectangle)
        self.rectangle_object = self.canvas.create_rectangle(self.canvas.canvasx(self.x), self.canvas.canvasy(self.y),
                                                             self.canvas.canvasx(self.a), self.canvas.canvasy(self.b),
                                                             outline="black", fill=self.color_code, width=1.2,
                                                             tags=(self.block_name, "Rectangle"))
        self.canvas.tag_lower(self.block_name)
        self.canvas.config(cursor="")
        return

    def delete(self):
        self.canvas.delete(self.rectangle_object)

    def get_block_name(self):
        return self.block_name

    # -------------------------- Save & Load Methods -------------------------- #
    def get_save_info(self):
        return [self.color_code, self.block_name, self.x, self.y, self.a, self.b]

    def set_is_set(self, is_set):
        self.is_set = is_set

    def set_coords(self, x, y, a, b):
        self.x = x
        self.y = y
        self.a = a
        self.b = b
        self.rectangle_object = self.canvas.create_rectangle(self.canvas.canvasx(self.x),
                                                             self.canvas.canvasy(self.y),
                                                             self.canvas.canvasx(self.a),
                                                             self.canvas.canvasy(self.b),
                                                             outline="black", fill=self.color_code, width=1.2,
                                                             tags=(self.block_name, "Rectangle"))
        self.canvas.tag_lower(self.block_name)
        self.is_set = True
    # -------------------------- Save & Load Methods -------------------------- #

