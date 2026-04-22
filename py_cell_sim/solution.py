import pymunk
import pyglet
from sim_utils import get_vertices_from_img
from random import randint

class Solution:
    """Class representing the solution in which the simulation exists.
    Defined by particular molarity of solutes, etc.
    """
    # TODO: This could have preset solutions that are sub-classes of this solution superclass.
    # TODO: A grid of specific solution/nutrient params? - Need to pass in height and width
    
    # Defining images
    SODIUM_IMG = "images/sodium.png"
    sodium_img = pyglet.resource.image(SODIUM_IMG)
    sodium_img.anchor_x = sodium_img.width // 2 
    sodium_img.anchor_y = sodium_img.height // 2

    POTASSIUM_IMG = "images/potassium.png"
    potassium_img = pyglet.resource.image(POTASSIUM_IMG)
    potassium_img.anchor_x = potassium_img.width // 2 
    potassium_img.anchor_y = potassium_img.height // 2

    CALCIUM_IMG = "images/calcium.png"
    calcium_img = pyglet.resource.image(CALCIUM_IMG)
    calcium_img.anchor_x = calcium_img.width // 2 
    calcium_img.anchor_y = calcium_img.height // 2
    
    CHLORIDE_IMG = "images/chloride.png"
    chloride_img = pyglet.resource.image(CHLORIDE_IMG)
    chloride_img.anchor_x = chloride_img.width // 2 
    chloride_img.anchor_y = chloride_img.height // 2

    def __init__(
        self,
        space, # For interfacing with the simulation
        env_objects,
        object_batch,
        env_settings,
        na_molarity,
        cl_molarity,
        k_molarity,
        ca_molarity,
        ph
    ):
        self.space = space
        self.env_objects = env_objects
        self.object_batch = object_batch
        self.env_settings = env_settings
        self.na_molarity = na_molarity
        self.cl_molarity = cl_molarity
        self.k_molarity = k_molarity
        self.ca_molarity = ca_molarity
        self.ph = ph

    @property
    def molarity(self):
        return self.na_molarity + self.cl_molarity + self.k_molarity + self.ca_molarity

    def change_solution(self, na, cl, k, ca):
        """Changes the solution state."""
        self.na_molarity = na
        self.cl_molarity = cl
        self.k_molarity = k
        self.ca_molarity = ca

    def change_ph(self, ph):
        """Changes pH of the solution"""
        self.ph = ph

    def spawn_solutes(self):
        """Spawns specific solutes based on the molarity of the solution."""
        # Lots of different ways to approach this problem.
        # My naive approach here is to multiply the molarity by 100 and then multiply this number by 6
        # and generate that many molecules in the solution

        na_molecules = int(self.na_molarity * 100 * 6)
        cl_molecules = int(self.cl_molarity * 100 * 6)
        k_molecules = int(self.k_molarity * 100 * 6)
        ca_molecules = int(self.ca_molarity * 100 * 6)

        for na in range(na_molecules):
            self._spawn_molecule(
                randint(0, self.env_settings["width"]), 
                randint(0, self.env_settings["height"]),
                0,
                self.SODIUM_IMG,
                self.sodium_img
            )

        for cl in range(cl_molecules):
            self._spawn_molecule(
                randint(0, self.env_settings["width"]), 
                randint(0, self.env_settings["height"]),
                0,
                self.CHLORIDE_IMG,
                self.chloride_img
            )

        for k in range(k_molecules):
            self._spawn_molecule(
                randint(0, self.env_settings["width"]), 
                randint(0, self.env_settings["height"]),
                0,
                self.POTASSIUM_IMG,
                self.potassium_img
            )

        for ca in range(ca_molecules):
            self._spawn_molecule(
                randint(0, self.env_settings["width"]), 
                randint(0, self.env_settings["height"]),
                0,
                self.CALCIUM_IMG,
                self.calcium_img
            )

    def _spawn_molecule(self, x, y, angle, img_path, img, mass=1) -> pymunk.Body:
        vertices = get_vertices_from_img(img_path, 1)
        
        moment = pymunk.moment_for_poly(mass, vertices)
        new_body = pymunk.Body(mass, moment)
        new_body.position = x, y
        new_body.angular_velocity_limit = 5.0
        new_body.velocity_limit = 200
        new_body.angle = angle
        poly = pymunk.Poly(new_body, vertices)
        molecule = pyglet.sprite.Sprite(img=img, x=x, y=y, batch=self.object_batch)
        molecule.anchor_x = img.width // 2
        molecule.anchor_y = img.height // 2
        
        new_body.visual_shape = molecule
        self.env_objects.append(new_body)
        self.space.add(new_body, poly)
        return new_body
