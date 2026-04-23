import pymunk
import pyglet
from sim_utils import get_vertices_from_img
import numpy as np
from collections import defaultdict
from ion_channel import IonChannel
from receptor import Receptor
from solution import Solution
from random import randint, shuffle

class Membrane:
    """Class defining the membrane of a cell."""
    
    LIPID_IMG = "images/lipid.png"
    lipid_img = pyglet.resource.image(LIPID_IMG)
    lipid_img.anchor_x = lipid_img.width // 2 # Tells pyglet how to anchor the image for correct visualization
    lipid_img.anchor_y = lipid_img.height // 2

    # Dictionary for classifying spring connections
    spring_anchor_dict = {
        "lipid": [(0,10), (0,-10)],
        "open": [(0,5),(0,-5)],
        "closed": [(0,5),(0,-5)],
        "A": [(0,-12),(0,-15)], # TODO: Any additional optimizations?
        "B": [(0,-12),(0,-15)]
    }

    def __init__(
        self,
        space, # For interfacing with the simulation
        env_objects,
        object_batch,
        solution: Solution,
        channels_to_initialize: list[str],
        receptors_to_initialize: list[str],
        cell,
        stiffness = 25, # For adjusting DampedSpring params
        rest_length = 5, # For adjusting DampedSpring params
        damping = 10, # For adjusting DampedSpring params
        inner_molarity = 0.3, # 0.9% NaCl in H2O ==> 0.15M Na + 0.15M Cl
        lipids_per_layer = 300
    ):
        self.lipids_per_layer = lipids_per_layer
        self.space = space
        self.stiffness = stiffness
        self.rest_length = rest_length
        self.damping = damping
        self.inner_lipids = []
        self.outer_lipids = []
        self.env_objects = env_objects
        self.object_batch = object_batch
        self.solution = solution
        self.inner_molarity = inner_molarity
        self.is_burst = False
        self.cell = cell
        self.constraints = []
        self.constraints_dict = defaultdict(list)
        self.lipid_constraints_dict = defaultdict(list)
        self.lipids_dict = defaultdict(list)
        self.radius = self.lipids_per_layer * 1.125
        self.channels_to_initialize = channels_to_initialize
        self.receptors_to_initialize = receptors_to_initialize
        self.receptors = {}
        self.ion_channels = {}

    def spawn_lipid_membrane(self, x, y) -> tuple[list[pymunk.Body], list[pymunk.Body]]:
        """Spawns a lipid membrane."""
        current_inner_lipids = []
        current_outer_lipids = []

        # Generate positions to add non-lipids to
        non_lipids: list[str] = []
        for channel in self.channels_to_initialize:
            non_lipids.extend([channel]*3)
        for receptor in self.receptors_to_initialize:
            non_lipids.extend([receptor]*3)
        shuffle(non_lipids)

        positions = self._generate_random_position_dict(num_objs=len(non_lipids))

        variant_maps = { # contains (constructor_img_value, distance_scaling_value) as values
            "open" : ("open", 0.01),
            "closed": ("closed", 0.01),
            "A" : ("A", 0.07),
            "B" : ("B", 0.07)
        }

        # Constructor map
        constructors = {
            "open": IonChannel,
            "closed": IonChannel,
            "A": Receptor,
            "B": Receptor,
        }

        iter_count = 0
        objects: list[str] = []

        for i in range(self.lipids_per_layer):
            angle = (i / self.lipids_per_layer) * 2 * np.pi
            if i in positions:
                variant = non_lipids[iter_count]
                obj = constructors[variant](self.space, self.env_objects, self.object_batch, variant_maps[variant][0])
                inner_obj = obj.spawn(
                    x = x + (self.radius + self.radius * variant_maps[variant][1]) * np.sin(angle),
                    y = y + (self.radius + self.radius * variant_maps[variant][1]) * np.cos(angle),
                    angle = 2 * np.pi - angle
                )
                if variant in Receptor.receptors:
                    self.receptors[obj] = variant
                elif variant in IonChannel.states:
                    self.ion_channels[obj] = variant
                outer_obj = inner_obj
                objects.append(variant)
                iter_count += 1
            else:
                inner_obj = self._spawn_lipid(
                    x = x + self.radius * np.sin(angle),
                    y = y + self.radius * np.cos(angle),
                    angle = np.pi - angle
                )
                outer_obj = self._spawn_lipid(
                    x = x + (self.radius + self.radius * 0.05) * np.sin(angle),
                    y = y + (self.radius + self.radius * 0.05) * np.cos(angle),
                    angle = 2 * np.pi - angle
                )
                objects.append("lipid")

            self.inner_lipids.append(inner_obj)
            current_inner_lipids.append(inner_obj)
            self.outer_lipids.append(outer_obj)
            current_outer_lipids.append(outer_obj)

        # Generate constraints and add to constraints dictionary
        for i in range(self.lipids_per_layer):
            # Outer constraints
            c1 = pymunk.DampedSpring(current_outer_lipids[i], current_outer_lipids[i-1], self.spring_anchor_dict[objects[i]][0], self.spring_anchor_dict[objects[i-1]][0], rest_length=self.rest_length, stiffness=self.stiffness, damping=self.damping)
            c2 = pymunk.DampedSpring(current_outer_lipids[i], current_outer_lipids[i-1], self.spring_anchor_dict[objects[i]][1], self.spring_anchor_dict[objects[i-1]][1], rest_length=self.rest_length, stiffness=self.stiffness, damping=self.damping)

            # Inner constraints
            c3 = pymunk.DampedSpring(current_inner_lipids[i], current_inner_lipids[i-1], self.spring_anchor_dict[objects[i]][0], self.spring_anchor_dict[objects[i-1]][0], rest_length=self.rest_length, stiffness=self.stiffness, damping=self.damping)
            c4 = pymunk.DampedSpring(current_inner_lipids[i], current_inner_lipids[i-1], self.spring_anchor_dict[objects[i]][1], self.spring_anchor_dict[objects[i-1]][1], rest_length=self.rest_length, stiffness=self.stiffness, damping=self.damping)

            self.space.add(c1, c2, c3, c4)
            self.constraints.extend([c1, c2, c3, c4])

            self.constraints_dict[c1] = [current_outer_lipids[i]]
            self.constraints_dict[c2] = [current_outer_lipids[i]]
            self.constraints_dict[c3] = [current_inner_lipids[i]]
            self.constraints_dict[c4] = [current_inner_lipids[i]]
            self.lipid_constraints_dict[current_outer_lipids[i]].extend([c1, c2])
            self.lipid_constraints_dict[current_inner_lipids[i]].extend([c3, c4])
            self.lipids_dict[current_outer_lipids[i]].append(current_outer_lipids[i-1])
            self.lipids_dict[current_inner_lipids[i]].append(current_inner_lipids[i-1])

            # Contraints between lipids
            if objects[i] == "lipid":
                c5 = pymunk.DampedSpring(current_outer_lipids[i], current_inner_lipids[i], (0, -5), (0, -5), rest_length=self.rest_length, stiffness=self.stiffness, damping=self.damping)
                self.space.add(c5)
                self.constraints.append(c5)
                self.constraints_dict[c5] = [current_outer_lipids[i]]
                self.lipids_dict[current_outer_lipids[i]].append(current_inner_lipids[i])
                self.lipids_dict[current_inner_lipids[i]].append(current_outer_lipids[i])

        self.resting_area = self._get_membrane_area()
        self.osmotic_pressure = self._calc_osmotic_pressure()

        return self.inner_lipids, self.outer_lipids

    def _spawn_lipid(self, x, y, angle, mass=1) -> pymunk.Body:
        """Spawns a single lipid molecule."""
        vertices = get_vertices_from_img(self.LIPID_IMG, 1)
        
        new_body = pymunk.Body(mass, 1500) # 1500 is arbitrary
        new_body.position = x, y
        new_body.angular_velocity_limit = 5.0
        new_body.velocity_limit = 200
        new_body.angle = angle
        poly = pymunk.Poly(new_body, vertices)
        lipid = pyglet.sprite.Sprite(img=self.lipid_img, x=x, y=y, batch=self.object_batch)
        lipid.anchor_x = self.lipid_img.width // 2
        lipid.anchor_y = self.lipid_img.height // 2
        
        new_body.visual_shape = lipid
        self.env_objects.append(new_body)
        self.space.add(new_body, poly)
        return new_body
    
    def _get_membrane_area(self) -> float:
        """Helper function for _get_osmotic_pressure. Uses shoelace formula."""
        area = 0.0
        n = len(self.inner_lipids)
        for i in range(n):
            j = (i + 1) % n
            body_i = self.inner_lipids[i]
            body_j = self.inner_lipids[j]
            area += body_i.position.x * body_j.position.y
            area -= body_j.position.x * body_i.position.y
        return abs(area) / 2.0

    def _calc_osmotic_pressure(self) -> float:
        """Calculates the osmotic pressure of the membrane
        Here, we use a simplified version of the Van't Hoff equation to calculate osmotic pressure.
        Equation: Pi = n * k / A
        NOTE: k is arbitrary. Adjust as needed for realism
        A difference of 0.2658M should lyse cells (red blood cells)"""
        
        k: int = 27500000
        return (self.solution.molarity - self.inner_molarity) * k / self._get_membrane_area()
    
    def apply_osmotic_forces(self) -> None:
        """Applies osmotic forces to lipids of the membrane."""

        self.osmotic_pressure = self._calc_osmotic_pressure() # Update osmotic pressure

        if not self.is_burst:
            for lipid in self.inner_lipids:
                lipid.apply_force_at_local_point((0, self.osmotic_pressure), (0, 0))

            if self._get_membrane_area() >= 4/3 * self.resting_area: # TODO: Is there a way to more reliably modulate this?
                self.is_burst = True

                # Break membrane at point of highest stress
                max_impulse = 0
                for c in self.constraints:
                    if c.impulse > max_impulse:
                        max_impulse = c.impulse
                        removed_constraint = c
                self.space.remove(removed_constraint)
                self.constraints.remove(removed_constraint)

                # Grab lipid of the broken constraint
                c_lipid = self.constraints_dict[removed_constraint][0]
                for constraint in self.lipid_constraints_dict[c_lipid]:
                    if constraint in self.constraints:
                        self.space.remove(constraint)
                        self.constraints.remove(constraint)

                # Get opposite lipid
                o_lipid = self.lipids_dict[c_lipid][1]
                for constraint in self.lipid_constraints_dict[o_lipid]:
                    self.space.remove(constraint)
                    self.constraints.remove(constraint)
                
        else:
            self.cell.is_alive = False
            self.osmotic_pressure *= 0.90
            for lipid in self.inner_lipids:
                lipid.apply_force_at_local_point((0, self.osmotic_pressure), (0, 0))

    def _generate_random_position_dict(self, num_objs: int) -> list[int]:
        """Generates a dictionary containing random positioning for membrane components
        like channels and receptors."""

        total_members = self.lipids_per_layer
        used_values: list[int] = []

        for i in range(num_objs):
            val = randint(0, total_members)
            while any(abs(val - num) <= 5 for num in used_values) or \
            any(abs(val - num) == self.lipids_per_layer for num in used_values): # 5 is arbitrary
                val = randint(0, total_members)
            used_values.append(val)

        return sorted(used_values)
    
    def get_center(self) -> tuple[float, float]:
        """Returns the location of the center of the object as a tuple (x, y)"""
        return self.inner_lipids[0].position.x, self.inner_lipids[0].position.y - self.radius

    # TODO: Phagocytosis / merging membranes together should be possible
