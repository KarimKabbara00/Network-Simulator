class LabelCanvasObject:
    def __init__(self, canvas, label_id, text):
        self.canvas = canvas
        self.block_name = label_id

        # Label Stuff
        x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()  # Current Cursor Location
        y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()  # Current Cursor Location
        self.label = self.canvas.create_text(x, y, text=text, fill="black", font=("Arial", 10),
                                             tags=(self.block_name, "Label"))

        x1 = self.canvas.bbox(self.label)[0] - 10
        y1 = self.canvas.bbox(self.label)[1] - 8
        x2 = self.canvas.bbox(self.label)[2] + 10
        y2 = self.canvas.bbox(self.label)[3] + 8

        self.label_bg = self.canvas.create_rectangle(x1, y1, x2, y2, fill="gray94",
                                                     tags=(self.block_name + "_bg", "Label"))
        self.canvas.tag_lower(self.label_bg, self.label)

        self.hidden_label = False
        # Label Stuff

        # Button Bindings
        self.canvas.tag_bind(self.block_name, '<Motion>', self.motion)  # When creating the object
        self.canvas.tag_bind(self.block_name, '<Button-1>', self.motion)  # When creating the object
        self.canvas.tag_bind(self.block_name, '<B1-Motion>', self.motion)  # After the object is created
        self.canvas.tag_bind(self.block_name + "_bg", '<B1-Motion>', self.motion)  # After the object is created
        # Button Bindings

    def motion(self, event):
        # Move the object
        self.canvas.coords(self.block_name, self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

        x1 = self.canvas.bbox(self.label)[0] - 10
        y1 = self.canvas.bbox(self.label)[1] - 8
        x2 = self.canvas.bbox(self.label)[2] + 10
        y2 = self.canvas.bbox(self.label)[3] + 8

        self.canvas.coords(self.block_name + "_bg", x1, y1, x2, y2)

        # Unbind after created
        if str(event.type) == "4":
            self.canvas.tag_unbind(self.block_name, "<Motion>")
            self.canvas.tag_unbind(self.block_name, "<Button-1>")
        return

    def toggle_label(self, reset):
        if not reset:
            self.hidden_label = not self.hidden_label
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

    def get_block_name(self):
        return self.block_name
