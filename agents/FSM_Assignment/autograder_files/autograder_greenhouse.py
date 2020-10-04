import sys

def checkBehavData(fsm,outfilenew,outfileold):
    fold = open(outfileold,"r")
    fnew  = open(outfilenew, "r")
    behaviors = ["'RaiseTempBehavior'","'LowerTempBehavior'","'LightBehavior'","'LowerHumidBehavior'","'RaiseMoistBehavior'","'LowerMoistBehavior'", "'PingBehavior'"]
    state = {"led":0, "wpump": False, "fan":False}
    correct = {}
    correct["Light"] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 40, 60, 80, 100, 120, 140, 160, 160, 140, 120, 100, 100, 100, 120, 140, 160, 180, 200, 220, 240, 255, 255, 255, 255, 255, 255, 255, 0, 0, 0, 0]
    correct["RaiseTemp"] = [200, 200, 200, 200, 200, 200, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 200, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    correct["LowerTemp"] = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, True, True, True, True, True, False, False, True, True, True, True, True, True, True, True, True, True, True, True, False, False, False, False, False, False, False, False, False, False]
    correct["LowerHumid"] = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, True, True, True, True, True, True, True, True, True, True, True, True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
    correct["RaiseSMoist"] = [True, True, True, True, False, False, False, False, True, True, False, False, False, False, False, False, True, True, False, False, False, False, False, False, False, False, False, False, True, True, False, False, False, False, False, False, True, True, False, False, False, False, False, False, False, False, True, True]
    correct["LowerSMoist"] = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
    correct["Ping"] = [True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True]
    actuator = {}
    actuator["Light"] = "led"
    actuator["RaiseTemp"] = "led"
    actuator["LowerTemp"] = "fan"
    actuator["LowerHumid"] = "fan"
    actuator["RaiseSMoist"] = "wpump"
    actuator["LowerSMoist"] = "fan"
    actuator["Ping"] = "ping"
    t = 0
    dtime = 1800
    for line in fnew:
        parts = line[1:-2].split(",")
        while int(parts[1]) > t*dtime:
            if state[actuator[fsm]] == correct[fsm][t]:
                #print("CORRECT", state[actuator[fsm]])
                pass
            else:
                print("ERROR t=",t*dtime, "CURRENT STATE OF "+actuator[fsm], state[actuator[fsm]], "CORRECT VALUE", correct[fsm][t])
                print("Fail Test 0/5")
                return False
            t += 1
        if int(parts[1]) == t*dtime:
            if not ": "+str(correct[fsm][t])+"}" in line:
                print("ERROR t=", t*dtime, "ACTUATOR COMMAND", line, "CORRECT VALUE",correct[fsm][t])
                print("Fail Test 0/5")
                return False
            else:
                state[actuator[fsm]] = correct[fsm][t]
                t += 1
                #print("CORRECT", line)
    while t < len(correct[fsm]):
        if state[actuator[fsm]] == correct[fsm][t]:
            #print("CORRECT", state[actuator[fsm]])
            pass
        else:
            print("ERROR t=",t*dtime, "CURRENT STATE OF "+actuator[fsm], state[actuator[fsm]], "CORRECT VALUE", correct[fsm][t])
            print("Fail Test 0/5")
            return False
        t += 1
    fnew.close()
    print("PASS 5/5")
    return True


def constructActuatorTrace(filename, behaviors):
    trace = {}
    with open(filename, "r") as f:
        for line in f.readlines():
            parts = line[1:-2].split(",")
            if (not parts[0] in behaviors):
                print("No such behavior: ", oldline)
                return None
            time = int(parts[1])
            command = parts[2][2:-1].split(":")
            actuator = command[0][1:-1]
            if (not time in trace): trace[time] = {}
            trace[time][actuator] = command[1].strip(' ')
    #print(trace)
    return trace

def checkTrace(trace, state, correct):
    # Make sure that every item in correct matches a corresponding item in the trace, and update state
    errors = 0
    for time in correct:
        if (not time in trace):
            print("No output found at time %d" %time)
            errors += 1
        else:
            for actuator in correct[time]:
                command = correct[time][actuator]
                state[actuator] = command
                if (not actuator in trace[time]):
                    print("Command for %s not found at time %d" %(actuator, time))
                    errors += 1
                elif (not str(command) == trace[time][actuator]):
                    print("Command for %s at time %d was %s, should be %s" \
                          %(actuator, time, trace[time][actuator], command))
                    errors += 1
            for actuator in trace[time]:
                command = trace[time][actuator]
                if (command != str(state[actuator]) and not actuator in correct[time]):
                    print("Command for %s at time %d was %s, should have been %s" \
                          %(actuator, time, command, state[actuator]))
                    errors += 1
    return errors

def checkLayerData(outfilenew,outfileold):
    correct = {0: {'ping': 'True', 'led': '0'}, 1800: {'fan': 'False', 'ping': 'True'}, 3600: {'ping': 'True'}, 5400: {'fan': 'False', 'ping': 'True'}, 7200: {'ping': 'True'}, 9000: {'fan': 'False', 'ping': 'True'}, 10800: {'ping': 'True'}, 12600: {'fan': 'False', 'ping': 'True'}, 14400: {'led': '0', 'ping': 'True'}, 16200: {'fan': 'False', 'ping': 'True', 'wpump': 'True'}, 18000: {'led': '0', 'wpump': 'False', 'ping': 'True'}, 19800: {'fan': 'False', 'ping': 'True'}, 21600: {'fan': 'False', 'ping': 'True'}, 23400: {'fan': 'False', 'ping': 'True'}, 25200: {'fan': 'False', 'ping': 'True'}, 27000: {'fan': 'False', 'ping': 'True'}, 28800: {'led': '0', 'ping': 'True'}, 30600: {'fan': 'False', 'ping': 'True', 'wpump': 'True'}, 32400: {'led': '20', 'wpump': 'False', 'ping': 'True'}, 34200: {'fan': 'True', 'ping': 'True', 'led': '40'}, 36000: {'fan': 'True', 'ping': 'True', 'led': '60'}, 37800: {'fan': 'False', 'ping': 'True', 'led': '80'}, 39600: {'fan': 'True', 'ping': 'True', 'led': '100'}, 41400: {'fan': 'False', 'ping': 'True', 'led': '120'}, 43200: {'led': '0', 'ping': 'True', 'fan': 'True'}, 45000: {'fan': 'False', 'ping': 'True'}, 46800: {'led': '20', 'wpump': 'False', 'ping': 'True', 'fan': 'True'}, 48600: {'fan': 'True', 'ping': 'True', 'led': '40'}, 50400: {'fan': 'True', 'ping': 'True', 'led': '60'}, 52200: {'fan': 'False', 'ping': 'True', 'led': '80'}, 54000: {'fan': 'True', 'ping': 'True', 'led': '100'}, 55800: {'fan': 'False', 'ping': 'True', 'led': '120'}, 57600: {'led': '0', 'ping': 'True', 'fan': 'True'}, 59400: {'fan': 'False', 'ping': 'True'}, 61200: {'led': '20', 'wpump': 'False', 'ping': 'True'}, 63000: {'fan': 'True', 'ping': 'True', 'led': '40'}, 64800: {'fan': 'False', 'ping': 'True', 'led': '60'}, 66600: {'fan': 'False', 'ping': 'True', 'led': '80'}, 68400: {'fan': 'False', 'ping': 'True', 'led': '100'}, 70200: {'fan': 'False', 'ping': 'True', 'led': '120'}, 72000: {'led': '0', 'ping': 'True'}, 73800: {'fan': 'False', 'ping': 'True'}, 75600: {'led': '20', 'wpump': 'False', 'ping': 'True'}, 77400: {'fan': 'False', 'ping': 'True', 'led': '40'}, 79200: {'fan': 'False', 'ping': 'True', 'led': '0'}, 81000: {'fan': 'False', 'ping': 'True'}, 82800: {'fan': 'False', 'ping': 'True'}, 84600: {'fan': 'False', 'ping': 'True'}}
    behaviors = ["'RaiseTempBehavior'","'LowerTempBehavior'","'LightBehavior'","'LowerHumidBehavior'","'RaiseMoistBehavior'","'LowerMoistBehavior'", "'PingBehavior'"]
    state = {"led": 0, "wpump": False, "fan": False}
    oldtrace = constructActuatorTrace(outfileold, behaviors)
    newtrace = constructActuatorTrace(outfilenew, behaviors)
    if (not oldtrace or not newtrace): return False # Error in parsing
    print("Checking old trace")
    errors = checkTrace(oldtrace, state, correct)
    if (errors > 0):
        print("Something is very wrong - the old agent failed with %d errors" %errors)
    state = {"led": 0, "wpump": False, "fan": False}
    print("Checking new trace")
    errors = checkTrace(newtrace, state, correct)
    total_points = 20
    print("PASS %d/%d" %(max(0, total_points - errors), total_points))
    return (errors == 0)


def checkOneBehavior(fsm):
    import greenhouse_behaviors, ping_behavior
    from autograder_files import greenhouse_behaviors_no_fsm
    from autograder_files import file_greenhouse_agent
    if fsm == "Light":
        bnew = greenhouse_behaviors.Light()
        bold = greenhouse_behaviors_no_fsm.Light()
    elif fsm == "RaiseTemp":
        bnew = greenhouse_behaviors.RaiseTemp()
        bold = greenhouse_behaviors_no_fsm.RaiseTemp()
    elif fsm == "LowerTemp":
        bnew = greenhouse_behaviors.LowerTemp()
        bold = greenhouse_behaviors_no_fsm.LowerTemp()
    elif fsm == "LowerHumid":
        bnew = greenhouse_behaviors.LowerHumid()
        bold = greenhouse_behaviors_no_fsm.LowerHumid()
    elif fsm == "RaiseSMoist":
        bnew = greenhouse_behaviors.RaiseSMoist()
        bold = greenhouse_behaviors_no_fsm.RaiseSMoist()
    elif fsm == "LowerSMoist":
        bnew = greenhouse_behaviors.LowerSMoist()
        bold = greenhouse_behaviors_no_fsm.LowerSMoist()
    elif fsm == "Ping":
        bnew = ping_behavior.Ping()
        bold = greenhouse_behaviors_no_fsm.Ping()
    newagent = file_greenhouse_agent.BehavioralGreenhouseAgent("greenhouse_sensor_data_q2.txt","output-greenhouseNEW"+fsm+".txt",[bnew])
    oldagent = file_greenhouse_agent.BehavioralGreenhouseAgent("greenhouse_sensor_data_q2.txt","output-greenhouseOLD"+fsm+".txt",[bold])
    newagent.main()
    oldagent.main()
    checkBehavData(fsm,"output-greenhouseNEW"+fsm+".txt","output-greenhouseOLD"+fsm+".txt")


def checkLayeredBehavior():
    import greenhouse_behaviors, ping_behavior
    from autograder_files import greenhouse_behaviors_no_fsm
    from autograder_files import file_greenhouse_agent
    rtempnew = greenhouse_behaviors.RaiseTemp()
    ltempnew = greenhouse_behaviors.LowerTemp()
    lightnew = greenhouse_behaviors.Light()
    humidnew = greenhouse_behaviors.LowerHumid()
    rsmoistnew = greenhouse_behaviors.RaiseSMoist()
    lsmoistnew = greenhouse_behaviors.LowerSMoist()
    pingnew = ping_behavior.Ping()
    newfsmlist = [rtempnew,ltempnew,lightnew,humidnew,rsmoistnew,lsmoistnew,pingnew]
    newagent = file_greenhouse_agent.LayeredGreenhouseAgent("greenhouse_sensor_data_q3.txt","greenhouse_schedule.txt","output-greenhouselayerNEW.txt",newfsmlist)
    print("RUNNING NEW")
    newagent.main()
    print("DONE NEW, RUNNING OLD")
    rtempold = greenhouse_behaviors_no_fsm.RaiseTemp()
    ltempold = greenhouse_behaviors_no_fsm.LowerTemp()
    lightold = greenhouse_behaviors_no_fsm.Light()
    humidold = greenhouse_behaviors_no_fsm.LowerHumid()
    rsmoistold = greenhouse_behaviors_no_fsm.RaiseSMoist()
    lsmoistold = greenhouse_behaviors_no_fsm.LowerSMoist()
    pingold = greenhouse_behaviors_no_fsm.Ping()
    oldfsmlist = [rtempold,ltempold,lightold,humidold,rsmoistold,lsmoistold,pingold]
    oldagent = file_greenhouse_agent.LayeredGreenhouseAgent("greenhouse_sensor_data_q3.txt","greenhouse_schedule.txt","output-greenhouselayerOLD.txt",oldfsmlist)
    oldagent.main()
    print("DONE OLD, CHECKING OUTPUT")
    checkLayerData("output-greenhouselayerNEW.txt","output-greenhouselayerOLD.txt")
