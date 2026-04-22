import pyglet
import pymunk
from sim_utils import get_vertices_from_img
from atp import ATP

class Mitochondrion:
    """Class representing a mitochondrion."""

    MITO_IMG = "images/mitochondrion.png"
    mito_img = pyglet.resource.image(MITO_IMG) # Hard-coded for now
    mito_img.anchor_x = mito_img.width // 2
    mito_img.anchor_y = mito_img.height // 2

    def __init__(
        self,
        space,
        env_objects,
        object_batch,
        cell,
        is_alive = True,
        energy = 100
    ):
        self.space = space
        self.env_objects = env_objects
        self.object_batch = object_batch
        self.cell = cell
        self.is_alive = is_alive
        self.energy = energy

    def spawn(self, x, y, angle=0, mass=1) -> pymunk.Body:
        """Spawns a nucleus."""
        vertices = get_vertices_from_img(self.MITO_IMG, 1)
        
        moment = pymunk.moment_for_poly(mass, vertices)
        new_body = pymunk.Body(mass, moment)
        new_body.position = x, y
        new_body.angular_velocity_limit = 5.0
        new_body.velocity_limit = 200
        new_body.angle = angle
        poly = pymunk.Poly(new_body, vertices)
        mitochondrion = pyglet.sprite.Sprite(img=self.mito_img, x=x, y=y, batch=self.object_batch)
        mitochondrion.anchor_x = self.mito_img.width // 2
        mitochondrion.anchor_y = self.mito_img.height // 2
        
        new_body.visual_shape = mitochondrion
        self.body = new_body
        self.env_objects.append(new_body)
        self.space.add(new_body, poly)

        return new_body
    
    def spawn_atp(self) -> pymunk.Body:
        """Spawns an ATP molecule."""
        self.cell.energy -= 1 # Decrement for energy consumption
        x, y = self.get_center()
        return ATP(self.space, self.env_objects, self.object_batch, "atp").spawn(x, y)
    
    def get_center(self) -> tuple[float, float]:
        """Gets the center of the object."""
        return self.body.position.x, self.body.position.y
    