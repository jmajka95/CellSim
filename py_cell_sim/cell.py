from __future__ import annotations

import pymunk
from membrane import Membrane
from nucleus import Nucleus
from rough_er import RoughER
from golgi import Golgi
from mitochondrion import Mitochondrion

import numpy as np

class Cell:
    """Class for defining a cellular unit in the simulation.
    Takes from membrane.py, etc."""
    
    def __init__(
        self,
        space, # For interfacing with the simulation
        env_objects,
        object_batch,
        solution,
        ph = 7.0
    ):
        self.space = space
        self.env_objects = env_objects
        self.object_batch = object_batch
        self.solution = solution
        self.ph = ph # Neutral pH (normal range is 7.0 - 7.2)
        # TODO: Energy? Proteins etc? self.energy = energy / 100 # arbitrary units
        self.constraints = []

    def spawn(self, x, y) -> Cell:
        self.membrane = Membrane(self.space, self.env_objects, self.object_batch, self.solution)
        self.membrane.spawn_lipid_membrane(x, y)
        self.nucleus = Nucleus(self.space, self.env_objects, self.object_batch).spawn(x, y)
        self.rough_er = RoughER(self.space, self.env_objects, self.object_batch).spawn(x, y-40)
        self.golgi = Golgi(self.space, self.env_objects, self.object_batch).spawn(x-70, y+15, angle=2*np.pi/4*3)
        self.mitochondrion = Mitochondrion(self.space, self.env_objects, self.object_batch).spawn(x+100, y+175, angle=2*np.pi/4*3)

        # Cytoskeleton - 8 connections
        c1 = pymunk.DampedSpring(self.nucleus, self.membrane.inner_lipids[0], (0, 0), (0, 0), rest_length=self.membrane.radius, stiffness=1, damping=10)
        c2 = pymunk.DampedSpring(self.nucleus, self.membrane.inner_lipids[len(self.membrane.inner_lipids)//8], (0, 0), (0, 0), rest_length=self.membrane.radius, stiffness=1, damping=10)
        c3 = pymunk.DampedSpring(self.nucleus, self.membrane.inner_lipids[len(self.membrane.inner_lipids)//4], (0, 0), (0, 0), rest_length=self.membrane.radius, stiffness=1, damping=10)
        c4 = pymunk.DampedSpring(self.nucleus, self.membrane.inner_lipids[len(self.membrane.inner_lipids)//8*3], (0, 0), (0, 0), rest_length=self.membrane.radius, stiffness=1, damping=10)
        c5 = pymunk.DampedSpring(self.nucleus, self.membrane.inner_lipids[len(self.membrane.inner_lipids)//2], (0, 0), (0, 0), rest_length=self.membrane.radius, stiffness=1, damping=10)
        c6 = pymunk.DampedSpring(self.nucleus, self.membrane.inner_lipids[len(self.membrane.inner_lipids)//8*5], (0, 0), (0, 0), rest_length=self.membrane.radius, stiffness=1, damping=10)
        c7 = pymunk.DampedSpring(self.nucleus, self.membrane.inner_lipids[len(self.membrane.inner_lipids)//4*3], (0, 0), (0, 0), rest_length=self.membrane.radius, stiffness=1, damping=10)
        c8 = pymunk.DampedSpring(self.nucleus, self.membrane.inner_lipids[len(self.membrane.inner_lipids)//8*7], (0, 0), (0, 0), rest_length=self.membrane.radius, stiffness=1, damping=10)
        self.constraints.extend([c1, c2, c3, c4, c5, c6, c7, c8])
        self.space.add(c1, c2, c3, c4, c5, c6, c7, c8)

        # Rough ER <--> Nucleus Connection
        c1 = pymunk.DampedSpring(self.nucleus, self.rough_er, (0, 0), (0, 0), rest_length=5, stiffness=5, damping=10)
        self.constraints.append(c1)
        self.space.add(c1)

        # Rough ER <--> Golgi Connection
        c1 = pymunk.DampedSpring(self.rough_er, self.golgi, (-50, 0), (0, 0), rest_length=15, stiffness=5, damping=10)
        self.constraints.append(c1)
        self.space.add(c1)

        # Mitochondrion <--> Nucleus Connection
        c1 = pymunk.DampedSpring(self.nucleus, self.mitochondrion, (0, 0), (0, 0), rest_length=np.sqrt((100**2 + 175**2)), stiffness=1, damping=10)
        self.constraints.append(c1)
        self.space.add(c1)

        return self
    
    def _get_center(self) -> tuple[float, float]:
        """Grabs the center of the cell."""
        return self.membrane.inner_lipids[0].position.x, self.membrane.inner_lipids[0].position.y - self.membrane.radius
    