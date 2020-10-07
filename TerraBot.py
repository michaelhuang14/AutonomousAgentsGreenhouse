#!/usr/bin/env python
import os
import sys, glob, select, signal
import subprocess as sp
from std_msgs.msg import Int32,Bool,Float32,String,Int32MultiArray,Float32MultiArray, String
import argparse, time, getpass
from shutil import copyfile
import rospy, rosgraph
from lib import topic_def as tdef
from lib import interference as interf_mod
from lib import tester as tester_mod
from lib import send_email
from lib import sim_camera as cam
from lib.terrabot_utils import clock_time
from lib.baseline import Baseline
from os.path import abspath

### Default values for the optional variables
verbose = False
grade = False
log = False
simulate = False
still_running = True
run_agent = True
#tick_interval = 0.01
tick_interval = 0.5
#clock_time = rospy.Time(0)
interference = None
tester = None

#lists which will be populated based on the topic_def.py
log_files = {}
publishers = {}
subscribers = {}

def gen_log_files():
    global log_files

    prefix = time.strftime("%Y%m%d_%H%M%S") + ("_sim" if simulate else "")
    os.makedirs("Log/Log_%s" % prefix)

    for name in tdef.sensor_names + tdef.actuator_names:
        file_name = "Log/Log_%s/%s_log.csv" % (prefix, name)
        log_files[name] = open(file_name, 'w+', 0)

def log_print(string):
    print("%s%s"%(time.strftime("[%Y%m%d %H:%M:%S]: "),string))

def generate_publishers():
    global publishers

    for name in tdef.sensor_names:
        pub_name = name + "_output"
        publishers[name] = rospy.Publisher(
                            pub_name, tdef.sensor_types[name],
                            latch = True, queue_size = 1)

    for name in tdef.actuator_names:
        pub_name = name + "_raw"
        publishers[name] = rospy.Publisher(
                            pub_name, tdef.actuator_types[name],
                            latch = True, queue_size = 1)

light_total = 0
last_light_reading = 0

def cb_generic(name, data):
    global now, interference
    original = data.data
    edited = data
    edited.data = (original if not interference else
                   interference.edit(name, original))

    tester_update_var(name, original)

    if (name == 'light'): # Integrate light levels
        global last_light_reading, light_total
        now = rospy.get_time()
        if (last_light_reading > 0):
            light_total += ((now - last_light_reading) *\
                            ((original[0] + original[1])/2)/3600.0)
            #print("LT: %.2f %d %.2f" %(light_total, (original[0] + original[1])/2,(now - last_light_reading)))
        last_light_reading = now

    publishers[name].publish(edited)
    if (log):
        log_file = log_files[name]
        log_file.write(clock_time(now) + ", internal: " +
                       str(original) + ", edited: " + str(edited.data) + "\n")
        log_file.flush()
        if (verbose):
            log_print ("Logging %s data" % name)

def generate_cb(name):
    return (lambda data: cb_generic(name, data))

def generate_subscribers():
    global subscribers
    for name in tdef.sensor_names:
        sub_name = name + "_raw"
        cb = generate_cb(name)
        subscribers[name] = rospy.Subscriber(sub_name, tdef.sensor_types[name], cb)

    for name in tdef.actuator_names:
        sub_name = name + "_input"
        cb = generate_cb(name)
        subscribers[name] = rospy.Subscriber(sub_name, tdef.actuator_types[name], cb)

###Start of program
parser = argparse.ArgumentParser(description = "TerraBot arg parser")
parser.add_argument('-v', '--verbose', action = 'store_true')
parser.add_argument('-l', '--log', action = 'store_true')
parser.add_argument('-m', '--mode', default = "serial",
        choices = ['serial', 'sim'],
        help = "if no mode given, serial is used")
parser.add_argument('-g', '--graphics', default = False, action='store_true')
parser.add_argument('-s', '--speedup', default = 1, type = float)
parser.add_argument('-b', '--baseline', default = None)
parser.add_argument('-i', '--interference', default = None)
parser.add_argument('-t','--test', default = None,
        help = "test execution using given tester file")
parser.add_argument('-a', '--agent', default = 'none',
        help = "if agent is 'none', agent must be run externally")
parser.add_argument('-e', '--email', default = None,
        help = "email address to notify if restarting frequently")
parser.add_argument('-p', '--password', default = None,
        help = "email address password")

args = parser.parse_args()

verbose = args.verbose
log = args.log
mode = args.mode
tester_file = args.test
simulate = mode == "sim"
run_agent = (args.agent != "None") and (args.agent != "none")
password = args.password

num_restarts = 0
max_restarts = 5

### Notify user when agent crashes or hangs multiple times
def notify_user():
    global args, password, num_restarts
    if (args.email != None):
        print("Sending email regarding restarts to " + args.email)
        send_email.send("autoterrabot@gmail.com", password, args.email,
                        "Problem with your TerraBot agent",
                        ("Your autonomous agent has had to be restarted %d times.  The current Terrabot time is %s.\r\n\r\nYou should probably contact the instructors to upload a new version.\r\n\r\nSincerely,\r\nTerraBot\r\n"
                         %(num_restarts, clock_time(rospy.get_time()))))

if (args.email != None and password == None):
    password = getpass.getpass("Password please for autoterrabot@gmail.com: ")

def terminate (process, log_file):
    if (log_file != None): log_file.close()
    if (process.poll() == None):
        process.terminate()
        process.wait()

def terminate_core():
    global core_p, core_log
    if (core_p != None):
        print("Terminating roscore")
        terminate(core_p, core_log)
        core_p = None; core_log = None

def terminate_sim():
    global sim_p, sim_log
    if (sim_p != None):
        print("Terminating sim")
        terminate(sim_p, sim_log)
        sim_p = None; sim_log = None

def terminate_serial():
    global serial_p, serial_log
    if (serial_p != None):
        print("Turning off actuators")
        publishers['led'].publish(0)
        publishers['wpump'].publish(0)
        publishers['fan'].publish(0)

        print("Terminating serial")
        terminate(serial_p, serial_log)
        serial_p = None; serial_log = None

def terminate_agent():
    global agent_p, agent_log
    if (agent_p != None):
        print("Terminating agent")
        terminate(agent_p, agent_log)
        agent_p = None; agent_log = None

def terminate_gracefully():
    terminate_agent()
    terminate_sim()
    terminate_serial()
    terminate_core()
    sys.exit()

if log:
    gen_log_files()

### Open log file for roscore
core_log = open("Log/roscore.log", "a+", 0)

### Start up roscore, redirecting output to logging files
core_p = sp.Popen("roscore", stdout = core_log, stderr = core_log)

### Begin relay node
if simulate: # Use simulated time if starting simulator
    while not rosgraph.is_master_online():
        rospy.sleep(1) # Wait for roscore to start up
    rospy.set_param("use_sim_time", True)
rospy.init_node('TerraBot', anonymous = True)

generate_publishers()
generate_subscribers()

### Health Ping callback function
### Records the most recent ping
def ping_cb(data):
    global last_ping
    last_ping = rospy.get_time()
    #print("  PING! %s" %clock_time(last_ping))
    tester_update_var('ping', True)

ping_sub = rospy.Subscriber('ping', Bool, ping_cb)

images = None
image_start_time = 1735000 # Should be in baseline
### Camera callback - take a picture and store in the given location
def camera_cb(data):
    global simulate, images
    
    if simulate:
        publishers['cam'].publish(data.data)
    else:
        print("Taking an image, storing it in %s" %data.data)
#        sp.call("raspistill -n -md 2 -awb off -awbg 1,1 -ss 30000 -o %s"
        sp.call("raspistill -n -md 4 -awb auto -ss 30000 -rot 180 -o %s"
                % data.data, shell = True)

camera_sub = rospy.Subscriber('camera', String, camera_cb)

### Spawn subprocesses

sim_p = None
sim_log = None
agent_p = None
agent_log = None
serial_p = None
serial_log = None

### Initiates the Simulator and redirects output
def start_simulator():
    global sim_p, sim_log, args
    if (sim_log == None): sim_log = open("Log/simulator.log", "a+", 0)
    fard_args = ["--speedup", str(args.speedup)]
    if args.graphics: fard_args += ["--graphics"]
    if args.baseline: 
        try: # In case of syntax errors, try parsing here first
            Baseline(abspath(args.baseline))
        except Exception as inst:
            print(inst.args)
            terminate_gracefully()
        fard_args += ["--baseline", args.baseline]
    if log: fard_args = fard_args + ["-l"]
    sim_p = sp.Popen(["python", "lib/farduino.py"] + fard_args,
                     stdout = sim_log, stderr = sim_log)
    time.sleep(1) # chance to get started
    
def start_agent():
    global agent_p, agent_log, args
    if (agent_log == None): agent_log = open("Log/agent.log", "a+", 0)
    agent_p = sp.Popen(["python", args.agent], bufsize=0,
                       stdout = agent_log, stderr = agent_log)
    time.sleep(1) # chance to get started
    last_ping = rospy.get_time()

### Initiates the Arduino and redirects output
def start_serial():
    global serial_p, serial_log
    if (serial_log == None): serial_log = open("Log/rosserial.log", "a+", 0)
    serial_p = sp.Popen(["rosrun", "rosserial_arduino",
                         "serial_node.py", "/dev/ttyACM0"],
                        stdout = serial_log, stderr = serial_log)
    time.sleep(1) # chance to get started

### Update tester variables, if necessary
var_translations = {'smoist' : 'smoist',      'cur' : 'current',
                    'light'  : 'light',       'level' : 'wlevel',
                    'temp'   : 'temperature', 'humid' : 'humidity',
                    'led'    : 'led',         'wpump' : 'wpump',
                    'fan'    : 'fan',         'camera' : 'camera',
                    'ping'   : 'ping'}
def tester_update_var(var, value):
    global tester, var_translations
    if (tester):
        tester.vars[var_translations[var]] = value
        #print(var, value, tester.vars)

### Start up arduino/simulator
print("Waiting for nodes")
if simulate:
    print("  Starting simulator")
    start_simulator()
else:
    print("  Starting hardware")
    start_serial()
# Wait for clock to start up correctly
while rospy.get_time() == 0: rospy.sleep(0.1)
now = rospy.get_time()

### Initiates the Agent file and redirects output
if run_agent: 
    print("  Starting agent")
    start_agent()
print("System started")

if tester_file:
    tester = tester_mod.Tester()
    try:
        tester.parse_file(tester_file)
    except Exception as inst:
        print(inst.args)
        terminate_gracefully()
    #tester.display()
    tester.init_constraints(now)
    dirname = os.path.dirname(tester_file) + "/"
    args.baseline = (None if not tester.baseline_file else
                     dirname + tester.baseline_file)
    args.interference = (None if not tester.interf_file else
                         dirname + tester.interf_file)

if (args.interference):
    interference = interf_mod.Interference(args.interference, now)

### We must begin health ping
last_ping = now

### Main loop
while not rospy.core.is_shutdown():
    ### Check for input
    if sys.stdin in select.select([sys.stdin],[],[],0)[0]:
        input = sys.stdin.readline()
        if input[0] == 'q':
            terminate_gracefully()
        else:
            print("Usage: q (quit)")

    now = rospy.get_time()
    if (interference): interference.update(now)
    if tester:
        tester.process_constraints(now)
        tester_update_var('ping', False) # Ping should not be latched
        if tester.finished(now):
            print("Done testing!")
            if (tester.end_status() == 'QUIT'): terminate_gracefully()
            else: tester = None

    # Ping at least once every 6 minutes, but need to adjust if speedup
    if  run_agent and ((now - last_ping) > max(360, 2*args.speedup)):
        log_print("no ping since %d (%d seconds), terminating..."
                  %(last_ping, now - last_ping))
        last_ping = now
        num_restarts += 1
        # For safety, make sure the pump is off
        publishers['wpump'].publish(False)
        if (num_restarts < max_restarts): # Send just once
            terminate(agent_p, None); agent_p = None
        else:
            notify_user()
            terminate_gracefully()

    if (run_agent and agent_p != None and agent_p.poll() != None):
        log_print("agent died")
        num_restarts += 1
        # For safety, make sure the pump is off
        publishers['wpump'].publish(False)
        if (num_restarts >= max_restarts): # Send just once
            notify_user()
            terminate_gracefully()

    if (run_agent and (agent_p == None or agent_p.poll() != None)):
        log_print("agent restarting...")
        start_agent()

    rospy.sleep(tick_interval)
    # End while loop


