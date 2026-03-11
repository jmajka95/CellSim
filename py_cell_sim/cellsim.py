import pymunk
import pyglet
from pymunk.pyglet_util import DrawOptions
from camera import Camera
from button import Button
from pyglet.math import Mat4
from pyglet.window import key
from pyglet import gui
import math
import numpy as np
import sys
import json

from membrane import Membrane
from nucleus import Nucleus
from rough_er import RoughER
from solution import Solution
from cell import Cell
from sim_utils import apply_brownian_motion


# TODO:
# 1. Cell cycle simulation?
# IDEA: Native, simple genome that confers specific traits that can be randomly mutated and selected on based on the environment (Steve's model thing he shared: is that worth using?)
# ATP --> lipids grow and bud off each other --> cell divides at some point
# 2. Document WORK! Make a Google Doc that can be accessed. Also push to github. Time to make this public :^)
# 3. In line with Nick Lane, would be absolutely sick to generate a really complex simulator that could simulate Alkaline vents forming the first cells of sorts

def generate_border(len, height, space, thickness, batch):
    floor_body = pymunk.Segment(space.static_body, (0, 0), (len, 0), thickness)
    floor_body_upper = pymunk.Segment(space.static_body, (0, height), (len, height), thickness)
    floor_body_right = pymunk.Segment(space.static_body, (len, height), (len, 0), thickness)
    left_wall = pymunk.Segment(space.static_body, (0, 0), (0, height), thickness)
    floor_body.elasticity = 0.95
    left_wall.elasticity = 0.95
    floor_body_upper.elasticity = 0.95
    floor_body_right.elasticity = 0.95
    space.add(floor_body)
    space.add(floor_body_upper)
    space.add(floor_body_right)
    space.add(left_wall)

    line = pyglet.shapes.Line(0, 0, len, 0, thickness=thickness, batch=batch)
    line2 = pyglet.shapes.Line(0, height, len, height, thickness=thickness, batch=batch)
    line3 = pyglet.shapes.Line(len, height, len, 0, thickness=thickness, batch=batch)
    line4 = pyglet.shapes.Line(0, 0, 0, height, thickness=thickness, batch=batch)

    return [line, line2, line3, line4]

# User-config (json/yaml?)
env_settings = {
    "camera_mode": True,
    "setup mode": True, # For modulating config
    "Solution Molarity": [0.15, 0.15, 0, 0], # Defaults to 0.15M Na, 0.15M Cl, 0M K, 0M, Ca
    "pH": 7.0,
    "x_gravity": 0,
    "y_gravity": 0,
    "height": 1000,
    "width": 1800,
    "damping": 0.85
}

env_objects = []
membranes = []

# pyglet
def main():
    if len(sys.argv) < 2:
        print("Usage: python cellsim.py <config json file>")
        sys.exit(1)

    # Load config file
    with open(sys.argv[1], "r") as f:
        config_file = json.load(f)

    # Set up config
    env_settings["Solution Molarity"] = config_file["molarity"]
    env_settings["height"] = config_file["height"]
    env_settings["width"] = config_file["width"]
    env_settings["pH"] = config_file["pH"]

    window = pyglet.window.Window(1260, 720, "CellSim Testing", resizable=False)
    draw_options = pymunk.pyglet_util.DrawOptions()
    camera = Camera()
    options = DrawOptions()
    keys = key.KeyStateHandler()
    object_batch = pyglet.graphics.Batch()
    gui_batch = pyglet.graphics.Batch()

    # GUI for initialization
    frame = gui.Frame(window, order=4)

    def update_field(text):
        try:
            text_value = float(text)
        except ValueError:
            print("Invalid input! Please enter a number.")

    # Add this near your gui_label
    bg_rect = pyglet.shapes.Rectangle(1000, 450, 475, 500, color=(40, 40, 40), batch=gui_batch)
    gui_label = pyglet.text.Label("CellSim", x=1050, y=850, font_size=40, batch=gui_batch)
    version_label = pyglet.text.Label("v0.0", x=1050, y=820, font_size=20, batch=gui_batch)
    height_field = gui.TextEntry(f"Height: {env_settings["height"]}", x=1050, y=750, width=300, batch=gui_batch)
    width_field = gui.TextEntry(f"Width: {env_settings["width"]}", x=1050, y=725, width=300, batch=gui_batch)
    solution_field = gui.TextEntry(f"Solution Molarity: {env_settings["Solution Molarity"]}", x=1050, y=700, width=300, batch=gui_batch)
    ph_field = gui.TextEntry(f"Solution pH: {env_settings["pH"]}", x=1050, y=675, width=300, batch=gui_batch)
    frame.add_widget(height_field)
    frame.add_widget(width_field)
    frame.add_widget(solution_field)
    frame.add_widget(ph_field)

    start_button = Button(1050, 525, 200, 40, "START")

    space = pymunk.Space()
    space.iterations = 10
    space.gravity = env_settings["x_gravity"], env_settings["y_gravity"]
    space.damping = env_settings["damping"] # Viscosity of the space

    solution = Solution(space, env_objects, object_batch, env_settings, *env_settings["Solution Molarity"], env_settings["pH"])

    fps_display = pyglet.window.FPSDisplay(window=window)

    lines = generate_border(env_settings["width"], env_settings["height"], space, 5, object_batch)

    camera_button = Button(50, 1050, 200, 40, "CAMERA MODE SWITCH")

    na_button = Button(50, 650, 200, 40, f"SODIUM MOLARITY")
    na_counter = Button(260, 650, 40, 40, f"{env_settings["Solution Molarity"][0]}")
    na_plus_button = Button(310, 650, 40, 40, "+", font_size=18)
    na_minus_button = Button(360, 650, 40, 40, "-", font_size=18)

    k_button = Button(50, 700, 200, 40, f"POTASSIUM MOLARITY")
    k_counter = Button(260, 700, 40, 40, f"{env_settings["Solution Molarity"][1]}")
    k_plus_button = Button(310, 700, 40, 40, "+", font_size=18)
    k_minus_button = Button(360, 700, 40, 40, "-", font_size=18)

    ca_button = Button(50, 750, 200, 40, f"CALCIUM MOLARITY")
    ca_counter = Button(260, 750, 40, 40, f"{env_settings["Solution Molarity"][2]}")
    ca_plus_button = Button(310, 750, 40, 40, "+", font_size=18)
    ca_minus_button = Button(360, 750, 40, 40, "-", font_size=18)

    cl_button = Button(50, 800, 200, 40, f"CHLORIDE MOLARITY")
    cl_counter = Button(260, 800, 40, 40, f"{env_settings["Solution Molarity"][3]}")
    cl_plus_button = Button(310, 800, 40, 40, "+", font_size=18)
    cl_minus_button = Button(360, 800, 40, 40, "-", font_size=18)

    lipid_counter = pyglet.text.Label(
        text="Total Objects: 0",
        font_size=15,
        x=50,
        y=500,
        color=(255,255,255,255)
    )

    camera_mode_text = pyglet.text.Label(
        text="Camera Mode: On",
        font_size=15,
        x=50,
        y=450,
        color=(255,255,255,255)
    )

    def update(dt):
        # apply_dipole_forces(boxes) # Optional for now
        apply_brownian_motion(env_objects)
        solution.change_solution(*env_settings["Solution Molarity"])

        if membranes:
            for membrane in membranes:
                membrane.apply_osmotic_forces()

        substeps = 2
        for _ in range(substeps): # Substeps help micro-updates occur
            space.step(dt / substeps)

    @window.event
    def on_draw():
        if not env_settings["setup mode"]:
            window.clear()
            camera.apply(window)
            object_batch.draw()
            window.view = Mat4()
            
            # space.debug_draw(draw_options) # For debugging
            camera_button.draw()

            na_button.draw()
            na_counter.draw()
            na_plus_button.draw()
            na_minus_button.draw()

            k_button.draw()
            k_counter.draw()
            k_plus_button.draw()
            k_minus_button.draw()

            ca_button.draw()
            ca_counter.draw()
            ca_plus_button.draw()
            ca_minus_button.draw()

            cl_button.draw()
            cl_counter.draw()
            cl_plus_button.draw()
            cl_minus_button.draw()

            lipid_counter.draw()
            camera_mode_text.draw()
            fps_display.draw()

            for box in env_objects:
                box.visual_shape.x = box.position.x
                box.visual_shape.y = box.position.y
                box.visual_shape.rotation = -math.degrees(box.angle)

            lipid_counter.text = f"Total Objects: {len(env_objects)}"
            na_counter.label.text = f"{abs(env_settings["Solution Molarity"][0]):.2f}"
            k_counter.label.text = f"{abs(env_settings["Solution Molarity"][1]):.2f}"
            ca_counter.label.text = f"{abs(env_settings["Solution Molarity"][2]):.2f}"
            cl_counter.label.text = f"{abs(env_settings["Solution Molarity"][3]):.2f}"

            if env_settings["camera_mode"]:
                camera_mode_text.text = "Camera Mode: On"
            else:
                camera_mode_text.text = "Camera Mode: Off"
        else:
            gui_batch.draw()
            start_button.draw()

    @window.event
    def on_mouse_scroll(x, y, scroll_x, scroll_y):
        if not env_settings["setup mode"]:
            mouse_world_before = camera.screen_to_world(x, y)
            
            camera.zoom *= (1 + scroll_y * 0.05)
            camera.zoom = max(0.01, camera.zoom)

            mouse_world_after = camera.screen_to_world(x, y)

            camera.position[0] += (mouse_world_before[0] - mouse_world_after[0])
            camera.position[1] += (mouse_world_before[1] - mouse_world_after[1])

    @window.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        if not env_settings["setup mode"]:
            camera.position = [
                camera.position[0] - dx, 
                camera.position[1] - dy
            ]

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        if not env_settings["setup mode"]:
            if camera_button.is_clicked(x, y):
                env_settings["camera_mode"] = not env_settings["camera_mode"]
            elif na_plus_button.is_clicked(x, y):
                env_settings["Solution Molarity"][0] += 0.01
            elif na_minus_button.is_clicked(x, y):
                if env_settings["Solution Molarity"][0] > 0:
                    env_settings["Solution Molarity"][0] -= 0.01
            elif k_plus_button.is_clicked(x, y):
                env_settings["Solution Molarity"][1] += 0.01
            elif k_minus_button.is_clicked(x, y):
                if env_settings["Solution Molarity"][1] > 0:
                    env_settings["Solution Molarity"][1] -= 0.01
            elif ca_plus_button.is_clicked(x, y):
                env_settings["Solution Molarity"][2] += 0.01
            elif ca_minus_button.is_clicked(x, y):
                if env_settings["Solution Molarity"][2] > 0:
                    env_settings["Solution Molarity"][2] -= 0.01
            elif cl_plus_button.is_clicked(x, y):
                env_settings["Solution Molarity"][3] += 0.01
            elif cl_minus_button.is_clicked(x, y):
                if env_settings["Solution Molarity"][3] > 0:
                    env_settings["Solution Molarity"][3] -= 0.01
            else:
                world_coords = camera.screen_to_world(x, y)
                if not env_settings["camera_mode"]:
                    if world_coords[0] >= 0 and world_coords[0] <= env_settings["width"] \
                    and world_coords[1] >= 0 and world_coords[1] <= env_settings["height"]:
                        cell = Cell(space, env_objects, object_batch, solution).spawn(world_coords[0], world_coords[1])
                        membranes.append(cell.membrane)
        else:
            if start_button.is_clicked(x, y):
                env_settings["setup mode"] = not env_settings["setup mode"]
                # solution.spawn_solutes() # Optional if we want to visualize solutes, maybe a cool "toggle mode" thing?
        
    @window.event
    def on_key_press(symbol, modifiers):
        if not env_settings["setup mode"]:
            if symbol == key.C:
                for box in env_objects:
                    box.visual_shape.delete()
                env_objects.clear()
                
                # Reset space
                for c in list(space.constraints):
                    space.remove(c)
                for s in list(space.shapes):
                    space.remove(s)
                for b in list(space.bodies):
                    space.remove(b)

    pyglet.clock.schedule_interval(update, 1/30)
    pyglet.app.run()

if __name__ == "__main__":
    main()

# def apply_forces(space):
    #     """Applies forces to objects in the environment."""
    #     max_dist = 200
    #     strength = 5000
    #     if len(boxes) < 2:
    #         return
        
    #     pos = np.array([b.position for b in boxes])

    #     diff = pos[:, np.newaxis, :] - pos[np.newaxis, :, :]
    #     dist_sq = np.sum(diff**2, axis=-1)

    #     mask = (dist_sq > 25) & (dist_sq < max_dist**2)

    #     safe_dist_sq = np.where(mask, dist_sq, 1.0)
    #     inv_dist = np.where(mask, 1.0 / np.sqrt(safe_dist_sq), 0.0)
    #     force_mag = np.where(mask, strength / (dist_sq + 100), 0.0)
    #     combined_mag = -force_mag * inv_dist

    #     total_forces = np.sum(diff * combined_mag[..., np.newaxis], axis=1)

    #     for i, body in enumerate(boxes):
    #         body.apply_force_at_world_point(tuple(total_forces[i]), body.position)

# # TODO: Is this useful?
# def apply_dipole_forces(boxes, strength=100, pole_offset=15):
#     """Function for applying forces like dipoles"""
#     if len(boxes) < 2: 
#         return
    
#     pos = np.fromiter((c for b in boxes for c in b.position), dtype=float).reshape(-1, 2)
#     angles = np.array([b.angle for b in boxes])

#     dir_vectors = np.column_stack([np.cos(angles + np.pi/2), np.sin(angles + np.pi/2)])
#     top_poles = pos + dir_vectors * pole_offset
#     bottom_poles = pos - dir_vectors * pole_offset

#     def get_force(p1, p2, is_attracted):
#         diff = p2[:, np.newaxis, :] - p1[np.newaxis, :, :]
#         dist_sq = np.sum(diff**2, axis=-1)

#         mask = (dist_sq > 10) & (dist_sq < 1000)
#         safe_dist_sq = np.where(mask, dist_sq, 1.0)

#         softening = 1000.0
#         mag = strength / (safe_dist_sq * np.sqrt(safe_dist_sq) + softening)
#         if not is_attracted:
#             mag *= -1

#         force_vecs = diff * (np.where(mask, mag, 0.0)[..., np.newaxis])
#         return np.sum(force_vecs, axis=1)

#     f_top = get_force(top_poles, top_poles, True) #+ get_force(top_poles, bottom_poles, False)
#     f_bottom = get_force(bottom_poles, bottom_poles, False) + get_force(bottom_poles, top_poles, False)

#     for i, b in enumerate(boxes):
#         b.apply_force_at_local_point(tuple(f_top[i]), (0, pole_offset))
#         # b.apply_force_at_local_point(tuple(f_bottom[i]), (0, -pole_offset))