from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from solution import Solution
    import pyglet
    import pymunk

import pymunk
from membrane import Membrane
from nucleus import Nucleus
from rough_er import RoughER
from golgi import Golgi
from solution import Solution
from mitochondrion import Mitochondrion
from receptor import Receptor
from ion_channel import IonChannel

import numpy as np

class Cell:
    """Class for defining a cellular unit in the simulation.
    Takes from membrane.py, etc.
    """
    
    def __init__(
        self,
        space: pymunk.Space, # For interfacing with the simulation
        env_objects: list[pymunk.Body],
        object_batch: pyglet.graphics.Batch,
        solution: Solution,
        ph: float, 
        energy: int,
        channels: list[str],
        receptors: list[str]
    ):
        self.space = space
        self.env_objects = env_objects
        self.object_batch = object_batch
        self.solution = solution
        self.ph = ph # Neutral pH (normal range is 7.0 - 7.2)
        self.energy = energy # TODO: Energy? Proteins etc? self.energy = energy / 100 # arbitrary units
        self.is_alive = True
        self.constraints = []
        self.channels = channels
        self.receptors = receptors

    def spawn(self, x, y) -> Cell:
        self.membrane = Membrane(self.space, self.env_objects, self.object_batch, self.solution, self.receptors, self.channels, self)
        self.membrane.spawn_lipid_membrane(x, y)
        self.nucleus = Nucleus(self.space, self.env_objects, self.object_batch).spawn(x, y)
        self.rough_er = RoughER(self.space, self.env_objects, self.object_batch).spawn(x, y-40)
        self.golgi = Golgi(self.space, self.env_objects, self.object_batch).spawn(x-70, y+15, angle=2*np.pi/4*3)
        self.mitochondrion = Mitochondrion(self.space, self.env_objects, self.object_batch, self).spawn(x+100, y+175, angle=2*np.pi/4*3)

        # Cytoskeleton - 8 connections
        for i in range(8):
            c = pymunk.DampedSpring(self.nucleus, self.membrane.inner_lipids[len(self.membrane.inner_lipids)*i//8], (0, 0), (0, 0), rest_length=self.membrane.radius, stiffness=1, damping=10)
            self.constraints.append(c)
            self.space.add(c)

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
        return self.membrane.get_center()
    
    def update_energy(self) -> None:
        """Updates the cell's energy based on its environment."""
        raise NotImplementedError
    
    def check_life_status(self) -> bool:
        """Checks whether or not the cell is still alive of the cell, 
        switching self.is_alive to False if energy <= 0. Returns the result is a boolean."""

        if self.energy <= 0: self.is_alive = False
        return self.is_alive
    