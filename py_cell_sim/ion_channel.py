import pymunk
import pyglet
from sim_utils import get_vertices_from_img

class IonChannel:
    """Class representing ion channels found in the membrane of a cell."""

    OPEN_CHANNEL_IMG = "images/ion_channel.png"
    open_channel_img = pyglet.resource.image(OPEN_CHANNEL_IMG)
    open_channel_img.anchor_x = open_channel_img.width // 2
    open_channel_img.anchor_y = open_channel_img.height // 2

    # Should be able to modulate between open and closed channels
    CLOSED_CHANNEL_IMG = "images/closed_ion_channel.png"
    closed_channel_img = pyglet.resource.image(CLOSED_CHANNEL_IMG)
    closed_channel_img.anchor_x = open_channel_img.width // 2
    closed_channel_img.anchor_y = open_channel_img.height // 2

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
        vertices = get_vertices_from_img(self.OPEN_CHANNEL_IMG, 1)
        
        moment = pymunk.moment_for_poly(mass, vertices)
        new_body = pymunk.Body(mass, moment)
        new_body.position = x, y
        new_body.angular_velocity_limit = 5.0
        new_body.velocity_limit = 200
        new_body.angle = angle
        poly = pymunk.Poly(new_body, vertices)
        nucleus = pyglet.sprite.Sprite(img=self.open_channel_img, x=x, y=y, batch=self.object_batch)
        nucleus.anchor_x = self.open_channel_img.width // 2
        nucleus.anchor_y = self.open_channel_img.height // 2
        
        new_body.visual_shape = nucleus
        self.env_objects.append(new_body)
        self.space.add(new_body, poly)
        return new_body
