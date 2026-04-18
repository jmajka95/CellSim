import pymunk
import pyglet
from sim_utils import get_vertices_from_img

class Ligand:
    """Class representing a ligand. Ligands interact with receptors to affect the cell."""
    
    ligands = ["A", "B"]

    ligand_imgs = {
        "A" : "images/ligand_a.png",
        "B" : "images/ligand_b.png",
    }

    def __init__(
        self,
        space,
        env_objects,
        object_batch,
        ligand
    ):
        self.space = space
        self.env_objects = env_objects
        self.object_batch = object_batch
        if ligand not in self.ligands:
            raise Exception(f"Must choose from following ligands to initialize: {self.ligands}.")
        self.ligand = ligand
        self.image = pyglet.resource.image(self.ligand_imgs[ligand])
        self.image.anchor_x = self.image.width // 2
        self.image.anchor_y = self.image.height // 2

    def spawn(self, x, y, angle=0, mass=1) -> pymunk.Body:
        """Spawns a nucleus."""
        vertices = get_vertices_from_img(self.ligand_imgs[self.ligand], 1)
        
        moment = pymunk.moment_for_poly(mass, vertices)
        new_body = pymunk.Body(mass, moment)
        new_body.position = x, y
        new_body.angular_velocity_limit = 5.0
        new_body.velocity_limit = 200
        new_body.angle = angle
        poly = pymunk.Poly(new_body, vertices)
        ligand = pyglet.sprite.Sprite(img=self.image, x=x, y=y, batch=self.object_batch)
        ligand.anchor_x = self.image.width // 2
        ligand.anchor_y = self.image.height // 2
        
        new_body.visual_shape = ligand
        self.body = new_body
        self.env_objects.append(new_body)
        self.space.add(new_body, poly)
        return new_body
    
    def get_center(self) -> tuple[float, float]:
        """Gets the center of the object."""
        return self.body.position.x, self.body.position.y
    