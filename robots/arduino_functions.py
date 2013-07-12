from robots.arduino import Arduino
import time,random
import config

class ArduinoController(object):
    """Arduino Controller"""
    def __init__(self):
        super(ArduinoController, self).__init__()
        self.arduino_serial_interface = Arduino(config.arduino_address)
        self.output_pins = config.arduino_output_pins #Motor output numbers 
        self.input_pins = config.arduino_input_pins #Sensor input numbers
        #declare output pins as a list/tuple
        self.arduino_serial_interface.output(self.output_pins)

        try:
            self.motor_normalisation_values = config.motor_normalisation_values
        except:
            self.motor_normalisation_values = None
        try:
            self.sensor_normalisation_values = config.sensor_normalisation_values
        except:
            self.sensor_normalisation_values = None

    def get_random_sensor(self):
        return random.randint(0,len(self.input_pins)-1)

    def get_sensor_value(self,s):
        try:
            sensor_value = float(self.arduino_serial_interface.analogRead(self.input_pins[s]))
        except:
            sensor_value = 0.0
        time.sleep(0.1)
        if self.sensor_normalisation_values is not None:
            return self.get_normalised_sensor_value(s,sensor_value)
        else:
            return sensor_value

    def get_random_motor(self):
        return random.randint(0,len(self.output_pins)-1)

    def move_servo(self,motor,value):
        if config.arduino_limit:
            value = self.limit_value(value)
        elif config.arduino_normalise:
            value = self.get_real_motor_value(motor,value)
        self.arduino_serial_interface.moveServo(motor, int(value))
        time.sleep(0.1)

    def get_normalised_sensor_value(self,s,value):
        _min = self.sensor_normalisation_values[s][0]
        _max = self.sensor_normalisation_values[s][1]
        return self._normalise(_min,_max,value)

    def get_normalised_motor_value(self,m,value):
        _min = self.motor_normalisation_values[m][0]
        _max = self.motor_normalisation_values[m][1]
        return self._normalise(_min,_max,value)

    def get_real_motor_value(self,m,normalised_value):
        _min = self.motor_normalisation_values[m][0]
        _max = self.motor_normalisation_values[m][1]
        return self._denormalise(_min,_max,normalised_value)

    def _limit_value(self,motor,value):
        try:
            limits = self.motor_normalisation_values[motor]
        except:
            return value
        hi = limits[0]
        lo = limits[1]
        if value > hi:
            value = hi
        elif value < lo:
            value = lo
        return value

    def _normalise(self,_min,_max,value):
        return (value + (-1*_min))/((-1*_min)+_max)

    def _denormalise(self,_min,_max,value):
        return (value*((-1*_min)+_max)) - (-1*_min)

if __name__ == '__main__':
    a = ArduinoController()
    x = 0
    while x < 10:
        for i in range(0,3):
            print "sensor:",a.get_sensor_value(i)
        a.move_servo(random.randint(0,4),random.randint(20,30))
        time.sleep(0.5)
        x += 1
    x= 0
    while x < 10:
        for i in range(0,3):
            print "sensor:",a.get_sensor_value(i)
        a.move_servo(random.randint(0,4),random.randint(20,30))
        time.sleep(0.5)
        x += 1

