from pyglet.math import Mat4

class Camera():
    """Class for simulation camera."""
    def __init__(self, position=[0,0], zoom=1.0):
        self.position = position
        self.zoom = zoom

    def apply(self, window):
        view_matrix = Mat4()
        view_matrix = view_matrix.scale((self.zoom, self.zoom, 1))
        view_matrix = view_matrix.translate((-self.position[0], -self.position[1], 0))
        window.view = view_matrix

    def screen_to_world(self, x, y):
        world_x = (x / self.zoom) + self.position[0]
        world_y = (y / self.zoom) + self.position[1]
        return world_x, world_y