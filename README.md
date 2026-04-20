# CellSim
Simple Python cell simulator using pymunk and pyglet. CellSim is an easy-to-use cell simulator
that can help you to better understand 

# Usage
To use CellSim, run the following on the command line within the py_cell_sim directory:
~~~
python cellsim.py <config_file>
~~~

Where the config file must have the following json format:
~~~json
{
    "height" : int,
    "width" : int,
    "Solution Molarity" : list[float],
    "pH" : float,
    "channels" : list[str],
    "receptors" : list[str],
    "receptor_kds" : dict[str, float]
}
~~~

height: An integer of the height of the defined in-game window
width: An integer of the width of the defined in-game window
Solution Molarity: A 
pH: 
channels:
receptors:
receptor_kds: 
