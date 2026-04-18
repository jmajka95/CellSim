import pyglet
import pymunk
from sim_utils import get_vertices_from_img

class RoughER:
    """Class representing the rough endoplasmic reticulum."""

    ROUGH_ER_IMG = "images/rough_er.png"
    rough_er_img = pyglet.resource.image(ROUGH_ER_IMG) # Hard-coded for now
    rough_er_img.anchor_x = rough_er_img.width // 2
    rough_er_img.anchor_y = rough_er_img.height // 2

    def __init__(
        self,
        space,
        env_objects,
        object_batch,
    ):
        self.space = space
        self.env_objects = env_objects
        self.object_batch = object_batch

    def spawn(self, x, y, angle=0, mass=1) -> pymunk.Body:
        """Spawns a nucleus."""
        vertices = get_vertices_from_img(self.ROUGH_ER_IMG, 1)
        
        moment = pymunk.moment_for_poly(mass, vertices)
        new_body = pymunk.Body(mass, moment)
        new_body.position = x, y
        new_body.angular_velocity_limit = 5.0
        new_body.velocity_limit = 200
        new_body.angle = angle
        poly = pymunk.Poly(new_body, vertices)
        rough_er = pyglet.sprite.Sprite(img=self.rough_er_img, x=x, y=y, batch=self.object_batch)
        rough_er.anchor_x = self.rough_er_img.width // 2
        rough_er.anchor_y = self.rough_er_img.height // 2
        
        new_body.visual_shape = rough_er
        self.body = new_body
        self.env_objects.append(new_body)
        self.space.add(new_body, poly)
        
        return new_body
    
    def get_center(self) -> tuple[float, float]:
        """Gets the center of the object."""
        return self.body.position.x, self.body.position.y
    