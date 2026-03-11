# Class for generic buttons/GUI maps
import pyglet

class Button:
    
    def __init__(self, x, y, width, height, text, font_size=12, color=(100,100,100)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.label = pyglet.text.Label(text, x=x + width//2, y=y + height//2, anchor_x='center', anchor_y='center', font_size=font_size)

    def draw(self):
        pyglet.shapes.Rectangle(self.x, self.y, self.width, self.height, color=self.color).draw()
        self.label.draw()

    def is_clicked(self, x, y):
        return self.x < x < self.x + self.width and self.y < y < self.y + self.height
    
    