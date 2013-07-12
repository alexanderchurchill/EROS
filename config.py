"""
All parameters for an evolutionary run
are stored in here
"""

#####################
# GA parameters
#####################
pop_size = 10
mutation_rate = 0.05
small_mutation_rate = 0.01
crossover_rate = 0.00
max_generations = 1000
robot_system = "aruduino"
use_brain_archive = False
use_run_archive = False
use_sensory_conditions = False
draw_molecules = True
#####################
# Simulation parameters
#####################
time_step_length = 0.2
time_steps_per_evaluation = 40

#####################
# Atom parameters
#####################

min_message_delay = 1
max_message_delay = 20

min_time_active = 1
max_time_active = 40

min_sensors_in_s_atom = 1
max_sensors_in_s_atom = 3
min_motors_in_m_atom = 1
max_motors_in_m_atom = 4

LWPR = False

#####################
# Nao parameters
#####################
robot_port = 9560
gps_server_port = 13375
gps_client_port = 1025
use_distance = True
nao_starting_position = "suppine"

#####################
# Webots parameters
#####################
webots_timestep_length = 200

#####################
# Arduino parameters
#####################
arduino_address = '/dev/tty.usbmodem1421'
arduino_output_pins = [1,2,3,4]
arduino_input_pins = [0,1,2]
arduino_limit = False
arduino_normalise = True

sensor_normalisation_values = {
								0:[400,700],
								1:[400,700],
								2:[400,700]
								}
motor_normalisation_values = {
								0:[20,100],
								1:[20,100],
								2:[20,100],
								3:[20,100],
								}

