import pyglet
import pymunk
from sim_utils import get_vertices_from_img

class Golgi:
    """Class representing the Golgi apparatus."""

    GOLGI_IMG = "images/golgi.png"
    golgi_img = pyglet.resource.image(GOLGI_IMG) # Hard-coded for now
    golgi_img.anchor_x = golgi_img.width // 2
    golgi_img.anchor_y = golgi_img.height // 2

    def __init__(
        self,
        space,
        env_objects,
        object_batch,
    ):
        self.space = space
        self.env_objects = env_objects
        self.object_batch = object_batch

    def spawn(self, x, y, angle, mass=1) -> pymunk.Body:
        """Spawns a nucleus."""
        vertices = get_vertices_from_img(self.GOLGI_IMG, 1)
        
        moment = pymunk.moment_for_poly(mass, vertices)
        new_body = pymunk.Body(mass, moment)
        new_body.position = x, y
        new_body.angular_velocity_limit = 5.0
        new_body.velocity_limit = 200
        new_body.angle = angle
        poly = pymunk.Poly(new_body, vertices)
        golgi = pyglet.sprite.Sprite(img=self.golgi_img, x=x, y=y, batch=self.object_batch)
        golgi.anchor_x = self.golgi_img.width // 2
        golgi.anchor_y = self.golgi_img.height // 2
        
        new_body.visual_shape = golgi
        self.env_objects.append(new_body)
        self.space.add(new_body, poly)
        
        return new_body