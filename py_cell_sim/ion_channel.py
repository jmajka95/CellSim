import pymunk
import pyglet
from sim_utils import get_vertices_from_img

class IonChannel:
    """Class representing ion channels found in the membrane of a cell."""

    states = ["open", "closed"]

    channel_images = {
        "open" : "images/ion_channel.png",
        "closed" : "images/closed_ion_channel.png"
    }

    def __init__(
        self,
        space,
        env_objects,
        object_batch,
        state
    ):
        self.space = space
        self.env_objects = env_objects
        self.object_batch = object_batch
        if state not in self.states:
            raise Exception(f"Must choose from following states to initialize: {self.states}.")
        self.state = state
        self.image = pyglet.resource.image(self.channel_images[state])
        self.image.anchor_x = self.image.width // 2
        self.image.anchor_y = self.image.height // 2

    def spawn(self, x, y, angle=0, mass=1) -> pymunk.Body:
        """Spawns a nucleus."""
        vertices = get_vertices_from_img(self.channel_images[self.state], 1)
        
        moment = pymunk.moment_for_poly(mass, vertices)
        new_body = pymunk.Body(mass, moment)
        new_body.position = x, y
        new_body.angular_velocity_limit = 5.0
        new_body.velocity_limit = 200
        new_body.angle = angle
        poly = pymunk.Poly(new_body, vertices)
        ion_channel = pyglet.sprite.Sprite(img=self.image, x=x, y=y, batch=self.object_batch)
        ion_channel.anchor_x = self.image.width // 2
        ion_channel.anchor_y = self.image.height // 2
        
        new_body.visual_shape = ion_channel
        self.body = new_body
        self.env_objects.append(new_body)
        self.space.add(new_body, poly)
        return new_body

    def get_center(self) -> tuple[float, float]:
        """Gets the center of the object."""
        return self.body.position.x, self.body.position.y
    