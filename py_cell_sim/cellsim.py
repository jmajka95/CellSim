import pymunk
import pyglet
from pymunk.pyglet_util import DrawOptions
from camera import Camera
from button import Button
from pyglet.math import Mat4
from pyglet.window import key
from pyglet import gui
import math
import sys
import json

from ligand import Ligand
from receptor import Receptor
from solution import Solution
from receptor import Receptor
from ion_channel import IonChannel
from cell import Cell
from sim_utils import apply_brownian_motion, generate_border


# User-config
env_settings = {
    "camera_mode": True,
    "setup mode": True, # For modulating config
    "Ligand A" : False,
    "Ligand B" : False,
    "Solution Molarity": [0.15, 0.15, 0, 0], # Defaults to 0.15M Na, 0.15M Cl, 0M K, 0M, Ca
    "pH": 7.0,
    "x_gravity": 0,
    "y_gravity": 0,
    "height": 1000,
    "width": 1800,
    "damping": 0.85,
    "channels": [], # For saving channels to use
    "receptors" : [], # For saving receptors to use
    "receptor_kds" : {} # For saving receptor kds for interaction strength
}

env_objects = []
cells = []
ligands = {
    "A": [],
    "B": []
}
receptors = {}
channels = {}

def main():
    if len(sys.argv) < 2:
        print("Usage: python cellsim.py <config json file>")
        sys.exit(1)

    # Load config file
    with open(sys.argv[1], "r") as f:
        config_file = json.load(f)
            
    # Validate channels and receptors
    if config_file["channels"]:
        if not all(channel in IonChannel.states for channel in config_file["channels"]):
            raise ValueError(f"Invalid channel provided. Must be one of the following: {IonChannel.states}")
    if config_file["receptors"]:
        if not all(receptor in Receptor.receptors for receptor in config_file["receptors"]):
            raise ValueError(f"Invalid receptor provided. Must be one of the following: {Receptor.receptors}")

    if config_file["receptor_kds"]:
        if not all(key in Receptor.receptors for key in config_file["receptor_kds"].keys()):
            raise ValueError(f"Must use one of the following valid receptors as keys: {Receptor.receptors}")

    # Set up config
    env_settings["Solution Molarity"] = config_file["molarity"]
    env_settings["height"] = config_file["height"]
    env_settings["width"] = config_file["width"]
    env_settings["pH"] = config_file["pH"]
    env_settings["channels"] = config_file["channels"]
    env_settings["receptors"] = config_file["receptors"]
    env_settings["receptor_kds"] = config_file["receptor_kds"]

    window = pyglet.window.Window(1260, 720, "CellSim Testing", resizable=False)
    draw_options = pymunk.pyglet_util.DrawOptions()
    camera = Camera()
    options = DrawOptions()
    keys = key.KeyStateHandler()
    object_batch = pyglet.graphics.Batch()
    gui_batch = pyglet.graphics.Batch()

    # GUI for initialization
    frame = gui.Frame(window, order=4)

    # Add this near your gui_label
    bg_rect = pyglet.shapes.Rectangle(1000, 450, 475, 500, color=(40, 40, 40), batch=gui_batch)
    gui_label = pyglet.text.Label("CellSim", x=1050, y=850, font_size=40, batch=gui_batch)
    version_label = pyglet.text.Label("v0.0", x=1050, y=820, font_size=20, batch=gui_batch)
    height_field = gui.TextEntry(f"Height: {env_settings["height"]}", x=1050, y=750, width=300, batch=gui_batch)
    width_field = gui.TextEntry(f"Width: {env_settings["width"]}", x=1050, y=725, width=300, batch=gui_batch)
    solution_field = gui.TextEntry(f"Solution Molarity: {env_settings["Solution Molarity"]}", x=1050, y=700, width=300, batch=gui_batch)
    ph_field = gui.TextEntry(f"Solution pH: {env_settings["pH"]}", x=1050, y=675, width=300, batch=gui_batch)
    channel_field = gui.TextEntry(f"Channels: {env_settings["channels"]}", x=1050, y=650, width=300, batch=gui_batch)
    receptor_field = gui.TextEntry(f"Receptors: {env_settings["receptors"]}", x=1050, y=625, width=300, batch=gui_batch)
    frame.add_widget(height_field)
    frame.add_widget(width_field)
    frame.add_widget(solution_field)
    frame.add_widget(ph_field)
    frame.add_widget(channel_field)
    frame.add_widget(receptor_field)

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

    ligand_a_button = Button(50, 550, 200, 40, "Ligand A", font_size=18)
    ligand_b_button = Button(50, 500, 200, 40, "Ligand B", font_size=18)

    lipid_counter = pyglet.text.Label(
        text="Total Objects: 0",
        font_size=15,
        x=50,
        y=250,
        color=(255,255,255,255)
    )

    camera_mode_text = pyglet.text.Label(
        text="Camera Mode: On",
        font_size=15,
        x=50,
        y=200,
        color=(255,255,255,255)
    )

    ligand_mode_text = pyglet.text.Label(
        text="Ligand Mode: Off",
        font_size=15,
        x=50,
        y=300,
        color=(255,255,255,255)
    )

    def update(dt):
        apply_brownian_motion(env_objects)
        solution.change_solution(*env_settings["Solution Molarity"])

        if receptors:
            for rec in receptors.keys():
                rec.calc_ligand_forces(ligands, env_settings["receptor_kds"][receptors[rec]])

        if cells:
            for cell in cells:
                cell.membrane.apply_osmotic_forces()
                # TODO: Here, Increment/Decrement energy

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

            ligand_a_button.draw()
            ligand_b_button.draw()

            lipid_counter.draw()
            camera_mode_text.draw()
            ligand_mode_text.draw()
            fps_display.draw()

            for obj in env_objects:
                obj.visual_shape.x = obj.position.x
                obj.visual_shape.y = obj.position.y
                obj.visual_shape.rotation = -math.degrees(obj.angle)

            lipid_counter.text = f"Total Objects: {len(env_objects)}"
            na_counter.label.text = f"{abs(env_settings["Solution Molarity"][0]):.2f}"
            k_counter.label.text = f"{abs(env_settings["Solution Molarity"][1]):.2f}"
            ca_counter.label.text = f"{abs(env_settings["Solution Molarity"][2]):.2f}"
            cl_counter.label.text = f"{abs(env_settings["Solution Molarity"][3]):.2f}"

            if env_settings["camera_mode"]:
                camera_mode_text.text = "Camera Mode: On"
            else:
                camera_mode_text.text = "Camera Mode: Off"

            if env_settings["Ligand A"]:
                ligand_mode_text.text = "Ligand Mode: A"
            elif env_settings["Ligand B"]:
                ligand_mode_text.text = "Ligand Mode: B"
            else:
                ligand_mode_text.text = "Ligand Mode: Off"
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
                camera.position[0] - dx, # TODO: Update to make faster and smoother
                camera.position[1] - dy
            ]

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        if not env_settings["setup mode"]:
            if camera_button.is_clicked(x, y):
                env_settings["camera_mode"] = not env_settings["camera_mode"]
                if env_settings["Ligand A"]:
                    env_settings["Ligand A"] = not env_settings["Ligand A"]
                if env_settings["Ligand B"]:
                    env_settings["Ligand B"] = not env_settings["Ligand B"]
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
            elif ligand_a_button.is_clicked(x, y):
                env_settings["Ligand A"] = not env_settings["Ligand A"]
                if env_settings["camera_mode"]:
                    env_settings["camera_mode"] = not env_settings["camera_mode"]
                if env_settings["Ligand B"]:
                    env_settings["Ligand B"] = not env_settings["Ligand B"]
            elif ligand_b_button.is_clicked(x, y):
                env_settings["Ligand B"] = not env_settings["Ligand B"]
                if env_settings["camera_mode"]:
                    env_settings["camera_mode"] = not env_settings["camera_mode"]
                if env_settings["Ligand A"]:
                    env_settings["Ligand A"] = not env_settings["Ligand A"]
            else:
                world_coords = camera.screen_to_world(x, y)
                if not env_settings["camera_mode"]:
                    if world_coords[0] >= 0 and world_coords[0] <= env_settings["width"] \
                    and world_coords[1] >= 0 and world_coords[1] <= env_settings["height"]:
                        if not env_settings["Ligand A"] and not env_settings["Ligand B"]:
                            cell = Cell(
                                space, env_objects, object_batch, solution, 7.0, 100,
                                env_settings["channels"], env_settings["receptors"]
                            ).spawn(world_coords[0], world_coords[1])
                            cells.append(cell)
                            receptors.update(cell.membrane.receptors)
                            channels.update(cell.membrane.ion_channels)
                        elif env_settings["Ligand A"]:
                            ligand = Ligand(space, env_objects, object_batch, "A").spawn(world_coords[0], world_coords[1])
                            ligands["A"].append(ligand)
                        else:
                            ligand = Ligand(space, env_objects, object_batch, "B").spawn(world_coords[0], world_coords[1])
                            ligands["B"].append(ligand)
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

    pyglet.clock.schedule_interval(update, 1/30) # 30 FPS
    pyglet.app.run()

if __name__ == "__main__":
    main()
