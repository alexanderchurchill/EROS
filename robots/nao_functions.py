from naoqi import *
import math
import almath
from time import time, sleep
import random
import config
import socket
import json

class Client():
  def __init__(self,server_port,receive_port):
    self.data_request = {'get_position':True,}
    self.server_port = server_port
    self.receive_port = receive_port

  def request(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', self.server_port))
    s.send(json.dumps(self.data_request))
    result = json.loads(s.recv(self.receive_port))
    return result

class NaoMotorFunction(ALModule):
  """
  Create a basic motor function instance
  """
  
  def __init__(self,name,ip="ctf.local"):
    ALModule.__init__(self,name)
    self.isRunning=True
    self.motion = ALProxy("ALMotion", ip, config.robot_port)
    self.Body = self.motion.getLimits("Body")
    self.set_stiffness(1.0)
    if config.nao_starting_position == "prone":
      self.postureProxy = ALProxy("ALRobotPosture", ip, config.robot_port)

  def set_stiffness(self, val):
         self.motion.setStiffnesses("Body", val)
    
  def rest(self):
    fractionMaxSpeed  = 1.0
    if config.nao_starting_position == "prone":
      self.postureProxy.goToPosture("LyingBelly", 0.5)
    else:
      bodyLyingDefaultAngles = [-0.20406389236450195, 0.16256213188171387, 1.5784441232681274,
                               0.2469320297241211, 0.5199840068817139, -0.052114009857177734,
                               -1.1029877662658691, 0.1711999773979187, 0.013848066329956055,
                               0.13503408432006836, 0.0061779022216796875, 0.47856616973876953,
                               0.9225810170173645, 0.04912996292114258, 0.013848066329956055,
                               -0.14568805694580078, 0.3021559715270996, -0.09232791513204575,
                               0.9320058226585388, 0.0031099319458007812, 1.7718119621276855,
                               -0.13503408432006836, 1.515550136566162, 0.12429594993591309,
                               1.348344087600708, 0.14719998836517334]
      motorAngles = bodyLyingDefaultAngles
         
      #Check that the specified angles are within limits
      for index,i in enumerate(self.Body):
        if motorAngles[index] < i[0]/2:
          motorAngles[index] = i[0]/2
        if motorAngles[index] > i[1]/2:
          motorAngles[index] = i[1]/2
                   
      self.motion.setAngles("Body", motorAngles, fractionMaxSpeed)
      sleep(0.3)

 
  def start(self):
    """Start basic motor function module"""
    try:
        pass
    except:
        pass
   
  def finish(self):
    """module bla"""
    try:
        pass
    except:
        pass
    self.isRunning = False

  def exit(self):
    print "Exit basic motor function module"
    try:
        pass
    except:
        pass
    self.isRunning=False
    ALModule.exit(self)

class NaoMemory(ALModule):
  """Create memoryManagerClass instance"""
  
  def __init__(self,name):
    ALModule.__init__(self,name)
    self.isRunning=True
    self.memory = ALProxy("ALMemory")
    self.motion = ALProxy("ALMotion")
    if config.use_distance:
      self.client = Client(config.gps_server_port,config.gps_client_port)
      self.starting_gps_position = self.client.request()
      self.current_gps_position = self.starting_gps_position
      self.gps_distances = {'x':0.0,'y':0.0,'z':0.0}
    #Get the position of robot top camera and write it to sensor Memory
    name            = "CameraTop"
    space           = motion.FRAME_WORLD
    useSensorValues = True
    result          = self.motion.getPosition(name, space, useSensorValues)
    self.memory.insertData("PositionCamera", result)
    

    #Converts a genotype number to a data name in ALMemory 
    self.numToSensor = {1: "Device/SubDeviceList/ChestBoard/Button/Sensor/Value",
                   2: "Device/SubDeviceList/LFoot/Bumper/Left/Sensor/Value",
                   3: "Device/SubDeviceList/LFoot/Bumper/Right/Sensor/Value",
                   4: "Device/SubDeviceList/RFoot/Bumper/Left/Sensor/Value",
                   5: "Device/SubDeviceList/RFoot/Bumper/Right/Sensor/Value",
                   6: "Device/SubDeviceList/HeadPitch/Position/Actuator/Value",
                   7: "Device/SubDeviceList/HeadYaw/Position/Actuator/Value",
                   8: "Device/SubDeviceList/LAnklePitch/Position/Actuator/Value",
                   9: "Device/SubDeviceList/LAnkleRoll/Position/Actuator/Value",
                   10: "Device/SubDeviceList/LElbowRoll/Position/Actuator/Value",
                   11: "Device/SubDeviceList/LElbowYaw/Position/Actuator/Value",
                   12: "Device/SubDeviceList/LHand/Position/Actuator/Value",
                   13: "Device/SubDeviceList/LHipPitch/Position/Actuator/Value",
                   14: "Device/SubDeviceList/LHipRoll/Position/Actuator/Value",
                   15: "Device/SubDeviceList/LHipYawPitch/Position/Actuator/Value",
                   16: "Device/SubDeviceList/LKneePitch/Position/Actuator/Value",
                   17: "Device/SubDeviceList/LShoulderPitch/Position/Actuator/Value",
                   18: "Device/SubDeviceList/LShoulderRoll/Position/Actuator/Value",
                   19: "Device/SubDeviceList/LWristYaw/Position/Actuator/Value",
                   20: "Device/SubDeviceList/RAnklePitch/Position/Actuator/Value",
                   21: "Device/SubDeviceList/RAnkleRoll/Position/Actuator/Value",
                   22: "Device/SubDeviceList/RElbowRoll/Position/Actuator/Value",
                   23: "Device/SubDeviceList/RElbowYaw/Position/Actuator/Value",
                   24: "Device/SubDeviceList/RHand/Position/Actuator/Value",
                   25: "Device/SubDeviceList/RHipPitch/Position/Actuator/Value",
                   26: "Device/SubDeviceList/RHipRoll/Position/Actuator/Value",
                   27: "Device/SubDeviceList/RHipRoll/Position/Actuator/Value",
                   28: "Device/SubDeviceList/RKneePitch/Position/Actuator/Value",
                   29: "Device/SubDeviceList/RShoulderPitch/Position/Actuator/Value",
                   30: "Device/SubDeviceList/RShoulderRoll/Position/Actuator/Value",
                   31: "Device/SubDeviceList/RWristYaw/Position/Actuator/Value",
                   32: "Device/SubDeviceList/HeadPitch/Hardness/Actuator/Value",
                   33: "Device/SubDeviceList/HeadYaw/Hardness/Actuator/Value",
                   34: "Device/SubDeviceList/LAnklePitch/Hardness/Actuator/Value",
                   35: "Device/SubDeviceList/LAnkleRoll/Hardness/Actuator/Value",
                   36: "Device/SubDeviceList/LElbowRoll/Hardness/Actuator/Value",
                   37: "Device/SubDeviceList/LElbowYaw/Hardness/Actuator/Value",
                   38: "Device/SubDeviceList/LHand/Hardness/Actuator/Value",
                   39: "Device/SubDeviceList/LHipPitch/Hardness/Actuator/Value",
                   40: "Device/SubDeviceList/LHipRoll/Hardness/Actuator/Value",
                   41: "Device/SubDeviceList/LHipYawPitch/Hardness/Actuator/Value",
                   42: "Device/SubDeviceList/LKneePitch/Hardness/Actuator/Value",
                   43: "Device/SubDeviceList/LShoulderPitch/Hardness/Actuator/Value",
                   44: "Device/SubDeviceList/LShoulderRoll/Hardness/Actuator/Value",
                   45: "Device/SubDeviceList/LWristYaw/Hardness/Actuator/Value",
                   46: "Device/SubDeviceList/RAnklePitch/Hardness/Actuator/Value",
                   47: "Device/SubDeviceList/RAnkleRoll/Hardness/Actuator/Value",
                   48: "Device/SubDeviceList/RElbowRoll/Hardness/Actuator/Value",
                   49: "Device/SubDeviceList/RElbowYaw/Hardness/Actuator/Value",
                   50: "Device/SubDeviceList/RHand/Hardness/Actuator/Value",
                   51: "Device/SubDeviceList/RHipPitch/Hardness/Actuator/Value",
                   52: "Device/SubDeviceList/RHipRoll/Hardness/Actuator/Value",
                   53: "Device/SubDeviceList/RHipRoll/Hardness/Actuator/Value",
                   54: "Device/SubDeviceList/RKneePitch/Hardness/Actuator/Value",
                   55: "Device/SubDeviceList/RShoulderPitch/Hardness/Actuator/Value",
                   56: "Device/SubDeviceList/RShoulderRoll/Hardness/Actuator/Value",
                   57: "Device/SubDeviceList/RWristYaw/Hardness/Actuator/Value",
                   58: "Device/SubDeviceList/HeadPitch/Position/Sensor/Value",
                   59: "Device/SubDeviceList/HeadYaw/Position/Sensor/Value",
                   60: "Device/SubDeviceList/LAnklePitch/Position/Sensor/Value",
                   61: "Device/SubDeviceList/LAnkleRoll/Position/Sensor/Value",
                   62: "Device/SubDeviceList/LElbowRoll/Position/Sensor/Value",
                   63: "Device/SubDeviceList/LElbowYaw/Position/Sensor/Value",
                   64: "Device/SubDeviceList/LHand/Position/Sensor/Value",
                   65: "Device/SubDeviceList/LHipPitch/Position/Sensor/Value",
                   66: "Device/SubDeviceList/LHipRoll/Position/Sensor/Value",
                   67: "Device/SubDeviceList/LHipYawPitch/Position/Sensor/Value",
                   68: "Device/SubDeviceList/LKneePitch/Position/Sensor/Value",
                   69: "Device/SubDeviceList/LShoulderPitch/Position/Sensor/Value",
                   70: "Device/SubDeviceList/LShoulderRoll/Position/Sensor/Value",
                   71: "Device/SubDeviceList/LWristYaw/Position/Sensor/Value",
                   72: "Device/SubDeviceList/RAnklePitch/Position/Sensor/Value",
                   73: "Device/SubDeviceList/RAnkleRoll/Position/Sensor/Value",
                   74: "Device/SubDeviceList/RElbowRoll/Position/Sensor/Value",
                   75: "Device/SubDeviceList/RElbowYaw/Position/Sensor/Value",
                   76: "Device/SubDeviceList/RHand/Position/Sensor/Value",
                   77: "Device/SubDeviceList/RHipPitch/Position/Sensor/Value",
                   78: "Device/SubDeviceList/RHipRoll/Position/Sensor/Value",
                   79: "Device/SubDeviceList/RHipRoll/Position/Sensor/Value",
                   80: "Device/SubDeviceList/RKneePitch/Position/Sensor/Value",
                   81: "Device/SubDeviceList/RShoulderPitch/Position/Sensor/Value",
                   82: "Device/SubDeviceList/RShoulderRoll/Position/Sensor/Value",
                   83: "Device/SubDeviceList/RWristYaw/Position/Sensor/Value",
                   84: "Device/SubDeviceList/HeadPitch/ElectricCurrent/Sensor/Value",
                   85: "Device/SubDeviceList/HeadYaw/ElectricCurrent/Sensor/Value",
                   86: "Device/SubDeviceList/LAnklePitch/ElectricCurrent/Sensor/Value",
                   87: "Device/SubDeviceList/LAnkleRoll/ElectricCurrent/Sensor/Value",
                   88: "Device/SubDeviceList/LElbowRoll/ElectricCurrent/Sensor/Value",
                   89: "Device/SubDeviceList/LElbowYaw/ElectricCurrent/Sensor/Value",
                   90: "Device/SubDeviceList/LHand/ElectricCurrent/Sensor/Value",
                   91: "Device/SubDeviceList/LHipPitch/ElectricCurrent/Sensor/Value",
                   92: "Device/SubDeviceList/LHipRoll/ElectricCurrent/Sensor/Value",
                   93: "Device/SubDeviceList/LHipYawPitch/ElectricCurrent/Sensor/Value",
                   94: "Device/SubDeviceList/LKneePitch/ElectricCurrent/Sensor/Value",
                   95: "Device/SubDeviceList/LShoulderPitch/ElectricCurrent/Sensor/Value",
                   96: "Device/SubDeviceList/LShoulderRoll/ElectricCurrent/Sensor/Value",
                   97: "Device/SubDeviceList/LWristYaw/ElectricCurrent/Sensor/Value",
                   98: "Device/SubDeviceList/RAnklePitch/ElectricCurrent/Sensor/Value",
                   99: "Device/SubDeviceList/RAnkleRoll/ElectricCurrent/Sensor/Value",
                   100: "Device/SubDeviceList/RElbowRoll/ElectricCurrent/Sensor/Value",
                   101: "Device/SubDeviceList/RElbowYaw/ElectricCurrent/Sensor/Value",
                   102: "Device/SubDeviceList/RHand/ElectricCurrent/Sensor/Value",
                   103: "Device/SubDeviceList/RHipPitch/ElectricCurrent/Sensor/Value",
                   104: "Device/SubDeviceList/RHipRoll/ElectricCurrent/Sensor/Value",
                   105: "Device/SubDeviceList/RHipRoll/ElectricCurrent/Sensor/Value",
                   106: "Device/SubDeviceList/RKneePitch/ElectricCurrent/Sensor/Value",
                   107: "Device/SubDeviceList/RShoulderPitch/ElectricCurrent/Sensor/Value",
                   108: "Device/SubDeviceList/RShoulderRoll/ElectricCurrent/Sensor/Value",
                   109: "Device/SubDeviceList/RWristYaw/ElectricCurrent/Sensor/Value",
                   110: "Device/SubDeviceList/HeadPitch/Temperature/Sensor/Value",
                   111: "Device/SubDeviceList/HeadYaw/Temperature/Sensor/Value",
                   112: "Device/SubDeviceList/LAnklePitch/Temperature/Sensor/Value",
                   113: "Device/SubDeviceList/LAnkleRoll/Temperature/Sensor/Value",
                   114: "Device/SubDeviceList/LElbowRoll/Temperature/Sensor/Value",
                   115: "Device/SubDeviceList/LElbowYaw/Temperature/Sensor/Value",
                   116: "Device/SubDeviceList/LHand/Temperature/Sensor/Value",
                   117: "Device/SubDeviceList/LHipPitch/Temperature/Sensor/Value",
                   118: "Device/SubDeviceList/LHipRoll/Temperature/Sensor/Value",
                   119: "Device/SubDeviceList/LHipYawPitch/Temperature/Sensor/Value",
                   120: "Device/SubDeviceList/LKneePitch/Temperature/Sensor/Value",
                   121: "Device/SubDeviceList/LShoulderPitch/Temperature/Sensor/Value",
                   122: "Device/SubDeviceList/LShoulderRoll/Temperature/Sensor/Value",
                   123: "Device/SubDeviceList/LWristYaw/Temperature/Sensor/Value",
                   124: "Device/SubDeviceList/RAnklePitch/Temperature/Sensor/Value",
                   125: "Device/SubDeviceList/RAnkleRoll/Temperature/Sensor/Value",
                   126: "Device/SubDeviceList/RElbowRoll/Temperature/Sensor/Value",
                   127: "Device/SubDeviceList/RElbowYaw/Temperature/Sensor/Value",
                   128: "Device/SubDeviceList/RHand/Temperature/Sensor/Value",
                   129: "Device/SubDeviceList/RHipPitch/Temperature/Sensor/Value",
                   130: "Device/SubDeviceList/RHipRoll/Temperature/Sensor/Value",
                   131: "Device/SubDeviceList/RHipRoll/Temperature/Sensor/Value",
                   132: "Device/SubDeviceList/RKneePitch/Temperature/Sensor/Value",
                   133: "Device/SubDeviceList/RShoulderPitch/Temperature/Sensor/Value",
                   134: "Device/SubDeviceList/RShoulderRoll/Temperature/Sensor/Value",
                   135: "Device/SubDeviceList/RWristYaw/Temperature/Sensor/Value",
                   136: "Device/SubDeviceList/US/Left/Sensor/Value",
                   137: "Device/SubDeviceList/US/Right/Sensor/Value",
                   138: "Device/SubDeviceList/InertialSensor/GyroscopeX/Sensor/Value",
                   139: "Device/SubDeviceList/InertialSensor/GyroscopeY/Sensor/Value",
                   140: "Device/SubDeviceList/InertialSensor/GyroscopeZ/Sensor/Value",
                   141: "Device/SubDeviceList/InertialSensor/AccelerometerX/Sensor/Value",
                   142: "Device/SubDeviceList/InertialSensor/AccelerometerY/Sensor/Value",
                   143: "Device/SubDeviceList/InertialSensor/AccelerometerZ/Sensor/Value",
                   144: "Device/SubDeviceList/InertialSensor/AngleX/Sensor/Value",
                   145: "Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value",
                   146: "Device/SubDeviceList/LFoot/FSR/FrontLeft/Sensor/Value",
                   147: "Device/SubDeviceList/LFoot/FSR/FrontRight/Sensor/Value",
                   148: "Device/SubDeviceList/LFoot/FSR/RearLeft/Sensor/Value",
                   149: "Device/SubDeviceList/LFoot/FSR/RearRight/Sensor/Value",
                   150: "Device/SubDeviceList/LFoot/FSR/TotalWeight/Sensor/Value",
                   151: "Device/SubDeviceList/RFoot/FSR/FrontLeft/Sensor/Value",
                   152: "Device/SubDeviceList/RFoot/FSR/FrontRight/Sensor/Value",
                   153: "Device/SubDeviceList/RFoot/FSR/RearLeft/Sensor/Value",
                   154: "Device/SubDeviceList/RFoot/FSR/RearRight/Sensor/Value",
                   155: "Device/SubDeviceList/RFoot/FSR/TotalWeight/Sensor/Value",
                   156: "Device/SubDeviceList/LFoot/FSR/CenterOfPressure/X/Sensor/Value",
                   157: "Device/SubDeviceList/LFoot/FSR/CenterOfPressure/Y/Sensor/Value",
                   158: "Device/SubDeviceList/RFoot/FSR/CenterOfPressure/X/Sensor/Value",
                   159: "Device/SubDeviceList/RFoot/FSR/CenterOfPressure/Y/Sensor/Value",
                   160: "Device/SubDeviceList/Head/Touch/Front/Sensor/Value",
                   161: "Device/SubDeviceList/Head/Touch/Middle/Sensor/Value",
                   162: "Device/SubDeviceList/Head/Touch/Rear/Sensor/Value",
                   163: "Device/SubDeviceList/LHand/Touch/Back/Sensor/Value",
                   164: "Device/SubDeviceList/LHand/Touch/Left/Sensor/Value",
                   165: "Device/SubDeviceList/LHand/Touch/Right/Sensor/Value",
                   166: "Device/SubDeviceList/RHand/Touch/Back/Sensor/Value",
                   167: "Device/SubDeviceList/RHand/Touch/Left/Sensor/Value",
                   168: "Device/SubDeviceList/RHand/Touch/Right/Sensor/Value",
                   169: "footContact",
                   170: "leftFootContact",
                   171: "rightFootContact",
                   172: "leftFootTotalWeight",
                   173: "rightFootTotalWeight",
                   174: "BodyStiffnessChanged",
                   175: "RightBumperPressed",
                   176: "LeftBumperPressed",
                   177: "ChestButtonPressed",
                   178: "FrontTactilTouched",
                   179: "RearTactilTouched",
                   180: "MiddleTactilTouched",
                   181: "HotJoinDetected",
                   182: "HandRightBackTouched",
                   183: "HandRightLeftTouched",
                   184: "HandRightRightTouched",
                   185: "HandLeftBackTouched",
                   186: "HandLeftLeftTouched",
                   187: "HandLeftRightTouched",
                   188: "PositionCamera"} #,
 #                  188: "WordRecognized"}

    self.sensorNormalisationList = {1: "Device/SubDeviceList/ChestBoard/Button/Sensor/",
           2: "Device/SubDeviceList/LFoot/Bumper/Left/Sensor/",
           3: "Device/SubDeviceList/LFoot/Bumper/Right/Sensor/",
           4: "Device/SubDeviceList/RFoot/Bumper/Left/Sensor/",
           5: "Device/SubDeviceList/RFoot/Bumper/Right/Sensor/",
           6: "Device/SubDeviceList/HeadPitch/Position/Actuator/",
           7: "Device/SubDeviceList/HeadYaw/Position/Actuator/",
           8: "Device/SubDeviceList/LAnklePitch/Position/Actuator/",
           9: "Device/SubDeviceList/LAnkleRoll/Position/Actuator/",
           10: "Device/SubDeviceList/LElbowRoll/Position/Actuator/",
           11: "Device/SubDeviceList/LElbowYaw/Position/Actuator/",
           12: "Device/SubDeviceList/LHand/Position/Actuator/",
           13: "Device/SubDeviceList/LHipPitch/Position/Actuator/",
           14: "Device/SubDeviceList/LHipRoll/Position/Actuator/",
           15: "Device/SubDeviceList/LHipYawPitch/Position/Actuator/",
           16: "Device/SubDeviceList/LKneePitch/Position/Actuator/",
           17: "Device/SubDeviceList/LShoulderPitch/Position/Actuator/",
           18: "Device/SubDeviceList/LShoulderRoll/Position/Actuator/",
           19: "Device/SubDeviceList/LWristYaw/Position/Actuator/",
           20: "Device/SubDeviceList/RAnklePitch/Position/Actuator/",
           21: "Device/SubDeviceList/RAnkleRoll/Position/Actuator/",
           22: "Device/SubDeviceList/RElbowRoll/Position/Actuator/",
           23: "Device/SubDeviceList/RElbowYaw/Position/Actuator/",
           24: "Device/SubDeviceList/RHand/Position/Actuator/",
           25: "Device/SubDeviceList/RHipPitch/Position/Actuator/",
           26: "Device/SubDeviceList/RHipRoll/Position/Actuator/",
           27: "Device/SubDeviceList/RHipRoll/Position/Actuator/",
           28: "Device/SubDeviceList/RKneePitch/Position/Actuator/",
           29: "Device/SubDeviceList/RShoulderPitch/Position/Actuator/",
           30: "Device/SubDeviceList/RShoulderRoll/Position/Actuator/",
           31: "Device/SubDeviceList/RWristYaw/Position/Actuator/",
           32: "Device/SubDeviceList/HeadPitch/Hardness/Actuator/",
           33: "Device/SubDeviceList/HeadYaw/Hardness/Actuator/",
           34: "Device/SubDeviceList/LAnklePitch/Hardness/Actuator/",
           35: "Device/SubDeviceList/LAnkleRoll/Hardness/Actuator/",
           36: "Device/SubDeviceList/LElbowRoll/Hardness/Actuator/",
           37: "Device/SubDeviceList/LElbowYaw/Hardness/Actuator/",
           38: "Device/SubDeviceList/LHand/Hardness/Actuator/",
           39: "Device/SubDeviceList/LHipPitch/Hardness/Actuator/",
           40: "Device/SubDeviceList/LHipRoll/Hardness/Actuator/",
           41: "Device/SubDeviceList/LHipYawPitch/Hardness/Actuator/",
           42: "Device/SubDeviceList/LKneePitch/Hardness/Actuator/",
           43: "Device/SubDeviceList/LShoulderPitch/Hardness/Actuator/",
           44: "Device/SubDeviceList/LShoulderRoll/Hardness/Actuator/",
           45: "Device/SubDeviceList/LWristYaw/Hardness/Actuator/",
           46: "Device/SubDeviceList/RAnklePitch/Hardness/Actuator/",
           47: "Device/SubDeviceList/RAnkleRoll/Hardness/Actuator/",
           48: "Device/SubDeviceList/RElbowRoll/Hardness/Actuator/",
           49: "Device/SubDeviceList/RElbowYaw/Hardness/Actuator/",
           50: "Device/SubDeviceList/RHand/Hardness/Actuator/",
           51: "Device/SubDeviceList/RHipPitch/Hardness/Actuator/",
           52: "Device/SubDeviceList/RHipRoll/Hardness/Actuator/",
           53: "Device/SubDeviceList/RHipRoll/Hardness/Actuator/",
           54: "Device/SubDeviceList/RKneePitch/Hardness/Actuator/",
           55: "Device/SubDeviceList/RShoulderPitch/Hardness/Actuator/",
           56: "Device/SubDeviceList/RShoulderRoll/Hardness/Actuator/",
           57: "Device/SubDeviceList/RWristYaw/Hardness/Actuator/",
           58: "Device/SubDeviceList/HeadPitch/Position/Sensor/",
           59: "Device/SubDeviceList/HeadYaw/Position/Sensor/",
           60: "Device/SubDeviceList/LAnklePitch/Position/Sensor/",
           61: "Device/SubDeviceList/LAnkleRoll/Position/Sensor/",
           62: "Device/SubDeviceList/LElbowRoll/Position/Sensor/",
           63: "Device/SubDeviceList/LElbowYaw/Position/Sensor/",
           64: "Device/SubDeviceList/LHand/Position/Sensor/",
           65: "Device/SubDeviceList/LHipPitch/Position/Sensor/",
           66: "Device/SubDeviceList/LHipRoll/Position/Sensor/",
           67: "Device/SubDeviceList/LHipYawPitch/Position/Sensor/",
           68: "Device/SubDeviceList/LKneePitch/Position/Sensor/",
           69: "Device/SubDeviceList/LShoulderPitch/Position/Sensor/",
           70: "Device/SubDeviceList/LShoulderRoll/Position/Sensor/",
           71: "Device/SubDeviceList/LWristYaw/Position/Sensor/",
           72: "Device/SubDeviceList/RAnklePitch/Position/Sensor/",
           73: "Device/SubDeviceList/RAnkleRoll/Position/Sensor/",
           74: "Device/SubDeviceList/RElbowRoll/Position/Sensor/",
           75: "Device/SubDeviceList/RElbowYaw/Position/Sensor/",
           76: "Device/SubDeviceList/RHand/Position/Sensor/",
           77: "Device/SubDeviceList/RHipPitch/Position/Sensor/",
           78: "Device/SubDeviceList/RHipRoll/Position/Sensor/",
           79: "Device/SubDeviceList/RHipRoll/Position/Sensor/",
           80: "Device/SubDeviceList/RKneePitch/Position/Sensor/",
           81: "Device/SubDeviceList/RShoulderPitch/Position/Sensor/",
           82: "Device/SubDeviceList/RShoulderRoll/Position/Sensor/",
           83: "Device/SubDeviceList/RWristYaw/Position/Sensor/",
           84: "Device/SubDeviceList/HeadPitch/ElectricCurrent/Sensor/",
           85: "Device/SubDeviceList/HeadYaw/ElectricCurrent/Sensor/",
           86: "Device/SubDeviceList/LAnklePitch/ElectricCurrent/Sensor/",
           87: "Device/SubDeviceList/LAnkleRoll/ElectricCurrent/Sensor/",
           88: "Device/SubDeviceList/LElbowRoll/ElectricCurrent/Sensor/",
           89: "Device/SubDeviceList/LElbowYaw/ElectricCurrent/Sensor/",
           90: "Device/SubDeviceList/LHand/ElectricCurrent/Sensor/",
           91: "Device/SubDeviceList/LHipPitch/ElectricCurrent/Sensor/",
           92: "Device/SubDeviceList/LHipRoll/ElectricCurrent/Sensor/",
           93: "Device/SubDeviceList/LHipYawPitch/ElectricCurrent/Sensor/",
           94: "Device/SubDeviceList/LKneePitch/ElectricCurrent/Sensor/",
           95: "Device/SubDeviceList/LShoulderPitch/ElectricCurrent/Sensor/",
           96: "Device/SubDeviceList/LShoulderRoll/ElectricCurrent/Sensor/",
           97: "Device/SubDeviceList/LWristYaw/ElectricCurrent/Sensor/",
           98: "Device/SubDeviceList/RAnklePitch/ElectricCurrent/Sensor/",
           99: "Device/SubDeviceList/RAnkleRoll/ElectricCurrent/Sensor/",
           100: "Device/SubDeviceList/RElbowRoll/ElectricCurrent/Sensor/",
           101: "Device/SubDeviceList/RElbowYaw/ElectricCurrent/Sensor/",
           102: "Device/SubDeviceList/RHand/ElectricCurrent/Sensor/",
           103: "Device/SubDeviceList/RHipPitch/ElectricCurrent/Sensor/",
           104: "Device/SubDeviceList/RHipRoll/ElectricCurrent/Sensor/",
           105: "Device/SubDeviceList/RHipRoll/ElectricCurrent/Sensor/",
           106: "Device/SubDeviceList/RKneePitch/ElectricCurrent/Sensor/",
           107: "Device/SubDeviceList/RShoulderPitch/ElectricCurrent/Sensor/",
           108: "Device/SubDeviceList/RShoulderRoll/ElectricCurrent/Sensor/",
           109: "Device/SubDeviceList/RWristYaw/ElectricCurrent/Sensor/",
           110: "Device/SubDeviceList/HeadPitch/Temperature/Sensor/",
           111: "Device/SubDeviceList/HeadYaw/Temperature/Sensor/",
           112: "Device/SubDeviceList/LAnklePitch/Temperature/Sensor/",
           113: "Device/SubDeviceList/LAnkleRoll/Temperature/Sensor/",
           114: "Device/SubDeviceList/LElbowRoll/Temperature/Sensor/",
           115: "Device/SubDeviceList/LElbowYaw/Temperature/Sensor/",
           116: "Device/SubDeviceList/LHand/Temperature/Sensor/",
           117: "Device/SubDeviceList/LHipPitch/Temperature/Sensor/",
           118: "Device/SubDeviceList/LHipRoll/Temperature/Sensor/",
           119: "Device/SubDeviceList/LHipYawPitch/Temperature/Sensor/",
           120: "Device/SubDeviceList/LKneePitch/Temperature/Sensor/",
           121: "Device/SubDeviceList/LShoulderPitch/Temperature/Sensor/",
           122: "Device/SubDeviceList/LShoulderRoll/Temperature/Sensor/",
           123: "Device/SubDeviceList/LWristYaw/Temperature/Sensor/",
           124: "Device/SubDeviceList/RAnklePitch/Temperature/Sensor/",
           125: "Device/SubDeviceList/RAnkleRoll/Temperature/Sensor/",
           126: "Device/SubDeviceList/RElbowRoll/Temperature/Sensor/",
           127: "Device/SubDeviceList/RElbowYaw/Temperature/Sensor/",
           128: "Device/SubDeviceList/RHand/Temperature/Sensor/",
           129: "Device/SubDeviceList/RHipPitch/Temperature/Sensor/",
           130: "Device/SubDeviceList/RHipRoll/Temperature/Sensor/",
           131: "Device/SubDeviceList/RHipRoll/Temperature/Sensor/",
           132: "Device/SubDeviceList/RKneePitch/Temperature/Sensor/",
           133: "Device/SubDeviceList/RShoulderPitch/Temperature/Sensor/",
           134: "Device/SubDeviceList/RShoulderRoll/Temperature/Sensor/",
           135: "Device/SubDeviceList/RWristYaw/Temperature/Sensor/",
           136: "Device/SubDeviceList/US/Left/Sensor/",
           137: "Device/SubDeviceList/US/Right/Sensor/",
           138: "Device/SubDeviceList/InertialSensor/GyroscopeX/Sensor/",
           139: "Device/SubDeviceList/InertialSensor/GyroscopeY/Sensor/",
           140: "Device/SubDeviceList/InertialSensor/GyroscopeZ/Sensor/",
           141: "Device/SubDeviceList/InertialSensor/AccelerometerX/Sensor/",
           142: "Device/SubDeviceList/InertialSensor/AccelerometerY/Sensor/",
           143: "Device/SubDeviceList/InertialSensor/AccelerometerZ/Sensor/",
           144: "Device/SubDeviceList/InertialSensor/AngleX/Sensor/",
           145: "Device/SubDeviceList/InertialSensor/AngleY/Sensor/",
           146: "Device/SubDeviceList/LFoot/FSR/FrontLeft/Sensor/",
           147: "Device/SubDeviceList/LFoot/FSR/FrontRight/Sensor/",
           148: "Device/SubDeviceList/LFoot/FSR/RearLeft/Sensor/",
           149: "Device/SubDeviceList/LFoot/FSR/RearRight/Sensor/",
           150: "Device/SubDeviceList/LFoot/FSR/TotalWeight/Sensor/",
           151: "Device/SubDeviceList/RFoot/FSR/FrontLeft/Sensor/",
           152: "Device/SubDeviceList/RFoot/FSR/FrontRight/Sensor/",
           153: "Device/SubDeviceList/RFoot/FSR/RearLeft/Sensor/",
           154: "Device/SubDeviceList/RFoot/FSR/RearRight/Sensor/",
           155: "Device/SubDeviceList/RFoot/FSR/TotalWeight/Sensor/",
           156: "Device/SubDeviceList/LFoot/FSR/CenterOfPressure/X/Sensor/",
           157: "Device/SubDeviceList/LFoot/FSR/CenterOfPressure/Y/Sensor/",
           158: "Device/SubDeviceList/RFoot/FSR/CenterOfPressure/X/Sensor/",
           159: "Device/SubDeviceList/RFoot/FSR/CenterOfPressure/Y/Sensor/",
           160: "Device/SubDeviceList/Head/Touch/Front/Sensor/",
           161: "Device/SubDeviceList/Head/Touch/Middle/Sensor/",
           162: "Device/SubDeviceList/Head/Touch/Rear/Sensor/",
           163: "Device/SubDeviceList/LHand/Touch/Back/Sensor/",
           164: "Device/SubDeviceList/LHand/Touch/Left/Sensor/",
           165: "Device/SubDeviceList/LHand/Touch/Right/Sensor/",
           166: "Device/SubDeviceList/RHand/Touch/Back/Sensor/",
           167: "Device/SubDeviceList/RHand/Touch/Left/Sensor/",
           168: "Device/SubDeviceList/RHand/Touch/Right/Sensor/",
    }

    # id:[min,max]
    self.sensor_normalisation_values = {
      1:[0.0,1.0],
      2:[0.0,1.0],
      3:[0.0,1.0],
      4:[0.0,1.0],
      5:[0.0,1.0],
      6:[-0.67199999094,0.514900028706],
      7:[-2.0857000351,2.0857000351],
      8:[-1.1895159483,0.922747015953],
      9:[-0.397879987955,0.76900100708],
      10:[-1.56210005283,-0.00870000012219],
      11:[-2.08559989929,2.08559989929],
      12:[0.0,1.0],
      13:[-1.77391195297,0.484090000391],
      14:[-0.379471987486,0.790476977825],
      15:[-1.14530301094,0.740809977055],
      16:[-0.0923459976912,2.11252808571],
      17:[-2.08559989929,2.08559989929],
      18:[0.00870000012219,1.6493999958],
      19:[-1.82379996777,1.82379996777],
      20:[-1.18644797802,0.932056009769],
      21:[-0.785875022411,0.38867598772],
      22:[0.00870000012219,1.56210005283],
      23:[-2.08559989929,2.08559989929],
      24:[0.0,1.0],
      25:[-1.77230799198,0.485623985529],
      26:[-0.738321006298,0.414754003286],
      27:[-0.738321006298,0.414754003286],
      28:[-0.103082999587,2.1201980114],
      29:[-2.08559989929,2.08559989929],
      30:[-1.6493999958,-0.00870000012219],
      31:[-1.82379996777,1.82379996777],
      32:[-1.0,1.0],
      33:[-1.0,1.0],
      34:[-1.0,1.0],
      35:[-1.0,1.0],
      36:[-1.0,1.0],
      37:[-1.0,1.0],
      38:[-1.0,0.5],
      39:[-1.0,1.0],
      40:[-1.0,1.0],
      41:[-1.0,1.0],
      42:[-1.0,1.0],
      43:[-1.0,1.0],
      44:[-1.0,1.0],
      45:[-1.0,1.0],
      46:[-1.0,1.0],
      47:[-1.0,1.0],
      48:[-1.0,1.0],
      49:[-1.0,1.0],
      50:[-1.0,0.5],
      51:[-1.0,1.0],
      52:[-1.0,1.0],
      53:[-1.0,1.0],
      54:[-1.0,1.0],
      55:[-1.0,1.0],
      56:[-1.0,1.0],
      57:[-1.0,1.0],
      58:[-3.14159011841,3.14159011841],
      59:[-3.14159011841,3.14159011841],
      60:[-3.14159011841,3.14159011841],
      61:[-3.14159011841,3.14159011841],
      62:[-3.14159011841,3.14159011841],
      63:[-3.14159011841,3.14159011841],
      64:[0.0,1.0],
      65:[-3.14159011841,3.14159011841],
      66:[-3.14159011841,3.14159011841],
      67:[-3.14159011841,3.14159011841],
      68:[-3.14159011841,3.14159011841],
      69:[-3.14159011841,3.14159011841],
      70:[0.00870000012219,1.6493999958],
      71:[-3.14159011841,3.14159011841],
      72:[-3.14159011841,3.14159011841],
      73:[-3.14159011841,3.14159011841],
      74:[-3.14159011841,3.14159011841],
      75:[-3.14159011841,3.14159011841],
      76:[0.0,1.0],
      77:[-3.14159011841,3.14159011841],
      78:[-3.14159011841,3.14159011841],
      79:[-3.14159011841,3.14159011841],
      80:[-3.14159011841,3.14159011841],
      81:[-3.14159011841,3.14159011841],
      82:[-1.6493999958,-0.00870000012219],
      83:[-3.14159011841,3.14159011841],
      84:[0.0,0.639999985695],
      85:[0.0,0.740000009537],
      86:[0.0,1.5],
      87:[0.0,1.14999997616],
      88:[0.0,0.639999985695],
      89:[0.0,0.740000009537],
      90:[0.0,0.0900000035763],
      91:[0.0,1.5],
      92:[0.0,1.14999997616],
      93:[0.0,1.14999997616],
      94:[0.0,1.5],
      95:[0.0,0.639999985695],
      96:[0.0,0.740000009537],
      97:[0.0,0.0900000035763],
      98:[0.0,1.5],
      99:[0.0,1.14999997616],
      100:[0.0,0.639999985695],
      101:[0.0,0.740000009537],
      102:[0.0,0.0900000035763],
      103:[0.0,1.5],
      104:[0.0,1.14999997616],
      105:[0.0,1.14999997616],
      106:[0.0,1.5],
      107:[0.0,0.639999985695],
      108:[0.0,0.740000009537],
      109:[0.0,0.0900000035763],
      110:[0.0,255.0],
      111:[0.0,255.0],
      112:[0.0,255.0],
      113:[0.0,255.0],
      114:[0.0,255.0],
      115:[0.0,255.0],
      116:[0.0,255.0],
      117:[0.0,255.0],
      118:[0.0,255.0],
      119:[0.0,255.0],
      120:[0.0,255.0],
      121:[0.0,255.0],
      122:[0.0,255.0],
      123:[0.0,255.0],
      124:[0.0,255.0],
      125:[0.0,255.0],
      126:[0.0,255.0],
      127:[0.0,255.0],
      128:[0.0,255.0],
      129:[0.0,255.0],
      130:[0.0,255.0],
      131:[0.0,255.0],
      132:[0.0,255.0],
      133:[0.0,255.0],
      134:[0.0,255.0],
      135:[0.0,255.0],
      136:[0.0,2.54999995232],
      137:[0.0,2.54999995232],
      138:[-8.72664642334,8.72664642334],
      139:[-8.72664642334,8.72664642334],
      140:[-8.72664642334,8.72664642334],
      141:[-19.6200008392,19.6200008392],
      142:[-19.6200008392,19.6200008392],
      143:[-19.6200008392,19.6200008392],
      144:[-6.28318548203,6.28318548203],
      145:[-6.28318548203,6.28318548203],
      146:[0.0,10.0],
      147:[0.0,10.0],
      148:[0.0,10.0],
      149:[0.0,10.0],
      150:[0.0,30.0],
      151:[0.0,10.0],
      152:[0.0,10.0],
      153:[0.0,10.0],
      154:[0.0,10.0],
      155:[0.0,30.0],
      156:[-10.0,10.0],
      157:[-10.0,10.0],
      158:[-10.0,10.0],
      159:[-10.0,10.0],
      160:[0.0,1.0],
      161:[0.0,1.0],
      162:[0.0,1.0],
      163:[0.0,1.0],
      164:[0.0,1.0],
      165:[0.0,1.0],
      166:[0.0,1.0],
      167:[0.0,1.0],
      168:[0.0,1.0],
      }

    self.motor_normalisation_values = {
      0:[-2.08566856384,2.08566856384],
      1:[-0.671951770782,0.514872133732],
      2:[-2.08566856384,2.08566856384],
      3:[-0.314159274101,1.32645022869],
      4:[-2.08566856384,2.08566856384],
      5:[-1.54461634159,-0.0349065847695],
      6:[-1.82386910915,1.82386910915],
      7:[0.0,1.0],
      8:[-1.14528501034,0.740717709064],
      9:[-0.379434585571,0.790459632874],
      10:[-1.77377808094,0.483979791403],
      11:[-0.092327915132,2.11254644394],
      12:[-1.18944191933,0.922581017017],
      13:[-0.768992066383,0.397760540247],
      14:[-1.14528501034,0.740717709064],
      15:[-0.738274276257,0.449596822262],
      16:[-1.77377808094,0.483979791403],
      17:[-0.092327915132,2.11254644394],
      18:[-1.18630027771,0.932005822659],
      19:[-0.38868483901,0.785921752453],
      20:[-2.08566856384,2.08566856384],
      21:[-1.32645022869,0.314159274101],
      22:[-2.08566856384,2.08566856384],
      23:[0.0349065847695,1.54461634159],
      24:[-1.82386910915,1.82386910915],
      25:[0.0,1.0],
    }


    if config.use_distance:
      self.allowed_sensors = [i for i in range(58,84)] + [i for i in range(138,145)]
    else:
      self.allowed_sensors = [i for i in range(58,84)] + [i for i in range(138,145)]
    bodyNames = self.motion.getBodyNames("Body")
    self.numToMotor = {}
    j = 1
# 0:HeadYaw
# 1:HeadPitch
# 2:LShoulderPitch
# 3:LShoulderRoll
# 4:LElbowYaw
# 5:LElbowRoll
# 6:LWristYaw
# 7:LHand
# 8:LHipYawPitch
# 9:LHipRoll
# 10:LHipPitch
# 11:LKneePitch
# 12:LAnklePitch
# 13:LAnkleRoll
# 14:RHipYawPitch
# 15:RHipRoll
# 16:RHipPitch
# 17:RKneePitch
# 18:RAnklePitch
# 19:RAnkleRoll
# 20:RShoulderPitch
# 21:RShoulderRoll
# 22:RElbowYaw
# 23:RElbowRoll
# 24:RWristYaw
# 25:RHand

    for index, i in enumerate(bodyNames):
      self.numToMotor[index] = i
   

  def getRandomMotor(self):
      return random.randint(0,25)

  def getRandomSensor(self):
      return random.choice(self.allowed_sensors)
      
  def putMemory(self, ident, value):
      self.memory.insertData(str(ident), value)

  def putGameMemory(self, ident, value):
      self.memory.insertData("g" + str(ident), value)
      
  def getSensorValue(self, num):
      if num < 200:
        return self.get_normalised_sensor_value(num,self.memory.getData(self.numToSensor[num]))
      else:
        return self.get_gps_position_as_sensor(num)

  def get_normalised_sensor_value(self,num,value):
    _min = self.sensor_normalisation_values[num][0]
    _max = self.sensor_normalisation_values[num][1]
    return (value + (-1*_min))/((-1*_min)+_max)

  def get_normalised_motor_value(self,num,value):
    _min = self.motor_normalisation_values[num][0]
    _max = self.motor_normalisation_values[num][1]
    return (value + (-1*_min))/((-1*_min)+_max)

  def get_real_motor_value(self,num,normalised_value):
    _min = self.motor_normalisation_values[num][0]
    _max = self.motor_normalisation_values[num][1]
    return (normalised_value*((-1*_min)+_max)) - (-1*_min)

  def update_gps_position(self):
    self.current_gps_position = self.client.request()
    # print "self.current_gps_position:",self.current_gps_position

  def update_gps_distance_from_start(self):
    for coord in ['x','y','z']:
      self.gps_distances[coord] = self.current_gps_position[coord] - self.starting_gps_position[coord]

  def get_gps_position_as_sensor(self,num):
    self.update_gps_position()
    self.update_gps_distance_from_start()
    if num == 200:
      return self.current_gps_position['x']
    elif num == 201:
      return self.current_gps_position['y']
    elif num == 202:
      return self.current_gps_position['z']
    elif num == 203:
      return self.gps_distances['x']
    elif num == 204:
      return self.gps_distances['y']
    elif num == 205:
      return self.gps_distances['z']

  def reset_gps_position(self):
    self.starting_gps_position = self.client.request()
  def getMessageValue(self, num):
      return self.memory.getData(str(num))

  def getMotorName(self, num):
      return self.numToMotor[num]

  def exit(self):
    print "Exiting sharedData"
    try:
        pass
    except:
        pass
    self.isRunning=False
    ALModule.exit(self)

  def get_normalisation_sensor_data(self):
    print "{"
    for i in self.sensorNormalisationList.keys():
      print "{0}:[{1},{2}],".format(i,self.memory.getData(self.sensorNormalisationList[i]+"Min"),self.memory.getData(self.sensorNormalisationList[i]+"Max"))
    print "}"

  def get_normalisation_motor_data(self,motion):
    print "{"
    for i in self.numToMotor.keys():
      print "{0}:[{1},{2}],".format(i,motion.getLimits(self.numToMotor[i])[0][0],motion.getLimits(self.numToMotor[i])[0][1])
    print "}"


