import sys, datetime, logging
from coffee_maker import *

def test_smallsize_easy_transitions():
    cm = CoffeeMaker()
    cm.sense({"smallbuttonpressed":True})
    cm.act()
    cm.sense({"podpresent":True})
    cm.act()
    cm.sense({"startbuttonpressed": True})
    cm.act()
    cm.sense({"watertemp": 180})
    cm.act()
    for i in range(30):
        time.sleep(1)
        cm.act()
    cm.sense({"podpresent":False, "smallbuttonpressed":False})
    cm.act()
    #should be back to empty state

def test_medsize_easy_transitions():
    cm = CoffeeMaker()
    cm.sense({"medbuttonpressed":True})
    cm.act()
    cm.sense({"podpresent":True})
    cm.act()
    cm.sense({"startbuttonpressed": True})
    cm.act()
    cm.sense({"watertemp": 180})
    cm.act()
    for i in range(30):
        time.sleep(1)
        cm.act()
    cm.sense({"podpresent":False, "medbuttonpressed":False})
    cm.act()
    #should be back to empty state

def test_largesize_easy_transitions():
    cm = CoffeeMaker()
    cm.sense({"largebuttonpressed":True})
    cm.act()
    cm.sense({"podpresent":True})
    cm.act()
    cm.sense({"startbuttonpressed": True})
    cm.act()
    cm.sense({"watertemp": 180})
    cm.act()
    for i in range(30):
        time.sleep(1)
        cm.act()
    cm.sense({"podpresent":False, "largebuttonpressed":False})
    cm.act()
    #should be back to empty state

def test_smallsize_removepod():
    cm = CoffeeMaker()
    cm.sense({"smallbuttonpressed":True})
    cm.act()
    cm.sense({"podpresent":True})
    cm.act()
    cm.sense({"podpresent":False})
    cm.act()
    cm.sense({"startbuttonpressed": True})
    cm.act()
    cm.sense({"watertemp": 180})
    cm.act()
    for i in range(10):
        time.sleep(1)
        cm.act()
    cm.sense({"podpresent":False, "smallbuttonpressed":False})
    cm.act()
    #should NOT be back to empty state
    #should NOT have brewed


def test_smallsize_podfirst():
    cm = CoffeeMaker()
    cm.sense({"podpresent":True})
    cm.act()
    cm.sense({"smallbuttonpressed":True})
    cm.act()
    cm.sense({"startbuttonpressed": True})
    cm.act()
    cm.sense({"watertemp": 180})
    cm.act()
    for i in range(10):
        time.sleep(1)
        cm.act()
    cm.sense({"podpresent":False, "smallbuttonpressed":False})
    cm.act()
    #should have brewed

def test_nowater():
    cm = CoffeeMaker()
    cm.sense({"podpresent":True})
    cm.act()
    cm.sense({"smallbuttonpressed":True})
    cm.act()
    cm.sense({"startbuttonpressed": True})
    cm.act()
    for i in range(10):
        time.sleep(1)
        cm.act()
    cm.sense({"podpresent":False, "smallbuttonpressed":False})
    cm.act()
    #should NOT be back to empty state
    #should NOT have brewed

def test_waitwater():
    cm = CoffeeMaker()
    cm.sense({"podpresent":True})
    cm.act()
    cm.sense({"smallbuttonpressed":True})
    cm.act()
    cm.sense({"startbuttonpressed": True})
    cm.act()
    for i in range(10):
        time.sleep(.2)
        cm.sense({"watertemp": 60+(i*10)})
        cm.act()
    cm.sense({"watertemp": 180})
    cm.act()
    for i in range(10):
        time.sleep(1)
        cm.act()
    cm.sense({"podpresent":False, "smallbuttonpressed":False})
    cm.act()
    #should be at empty


def test_switchsize():
    cm = CoffeeMaker()
    cm.sense({"smallbuttonpressed":True})
    cm.act()
    cm.sense({"podpresent":True})
    cm.act()
    cm.sense({"smallbuttonpressed":False,"medbuttonpressed":True})
    cm.act()
    cm.sense({"startbuttonpressed": True})
    cm.act()
    cm.sense({"watertemp": 180})
    cm.act()
    for i in range(15):
        time.sleep(1)
        cm.act()
    cm.sense({"podpresent":False, "smallbuttonpressed":False})
    cm.act()
    #should be back in empty

def test_nosize():
    cm = CoffeeMaker()
    cm.sense({"podpresent":True})
    cm.act()
    cm.sense({"startbuttonpressed": True})
    cm.act()
    cm.sense({"watertemp": 180})
    cm.act()
    for i in range(10):
        time.sleep(1)
        cm.act()
    cm.sense({"podpresent":False, "smallbuttonpressed":False})
    cm.act()
    #should be back in empty

def test_smallsize_nopod():
    cm = CoffeeMaker()
    cm.sense({"smallbuttonpressed":True})
    cm.act()
    cm.sense({"startbuttonpressed": True})
    cm.act()
    cm.sense({"watertemp": 180})
    cm.act()
    for i in range(10):
        time.sleep(1)
        cm.act()
    cm.sense({"podpresent":False, "smallbuttonpressed":False})
    cm.act()
    #should NOT be back to empty state
    #should NOT have brewed

def test_smallsize_nostart():
    cm = CoffeeMaker()
    cm.sense({"smallbuttonpressed":True})
    cm.act()
    cm.sense({"podpresent":True})
    cm.act()
    cm.sense({"watertemp": 180})
    cm.act()
    for i in range(10):
        time.sleep(1)
        cm.act()
    cm.sense({"podpresent":False, "smallbuttonpressed":False})
    cm.act()
    #should NOT be back to empty state
    #should NOT have brewed

def coffeetests(testnum):
    file = 'output-cm'+str(datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S"))+'.log'
    logging.basicConfig(filename=file,level=logging.INFO)
    testlogging = logging.getLogger('tests')
    testlogging.setLevel(logging.INFO)
    if testnum <= 0 or testnum == 1:
        testlogging.info("START SMALL SIZE")
        print("Running Small Size Coffee Brew Time Test")
        test_smallsize_easy_transitions()
        testlogging.info("END SMALL SIZE")
    if testnum <= 0 or testnum == 2:
        testlogging.info("START MED SIZE")
        print("Running Medium Size Coffee Brew Time Test")
        test_medsize_easy_transitions()
        testlogging.info("END MED SIZE")
    if testnum <= 0 or testnum == 3:
        testlogging.info("START LARGE SIZE")
        print("Running Large Size Coffee Brew Time Test")
        test_largesize_easy_transitions()
        testlogging.info("END LARGE SIZE")
    if testnum <= 0 or testnum == 4:
        testlogging.info("START NO START")
        print("Running No Start Button Test")
        test_smallsize_nostart()
        testlogging.info("END NO START")
    if testnum <= 0 or testnum == 5:
        testlogging.info("START REMOVE POD")
        print("Running Remove Pod Test")
        test_smallsize_removepod()
        testlogging.info("END REMOVE POD")
    if testnum <= 0 or testnum == 6:
        testlogging.info("START POD FIRST")
        print("Running Pod First Test")
        test_smallsize_podfirst()
        testlogging.info("END POD FIRST")
    if testnum <= 0 or testnum == 7:
        testlogging.info("START NO POD")
        print("Running No Pod Test")
        test_smallsize_nopod()
        testlogging.info("END NO POD")
    if testnum <= 0 or testnum == 8:
        testlogging.info("START NO SIZE")
        print("Running No Size Button Test")
        test_nosize()
        testlogging.info("END NO SIZE")
    if testnum <= 0 or testnum == 9:
        testlogging.info("START SWITCH SIZE")
        print("Running Switch Size Brew Time Test")
        test_switchsize()
        testlogging.info("END SWITCH SIZE")
    if testnum <= 0 or testnum == 10:
        testlogging.info("START WAIT WATER")
        print("Running Wait Water Temp Time Test")
        test_waitwater()
        testlogging.info("END WAIT WATER")
    if testnum <= 0 or testnum == 11:
        testlogging.info("START NO HEAT WATER")
        print("Running No Water Temp Test")
        test_nowater()
        testlogging.info("END NO HEAT WATER")
    return file

def parse_coffee_test(testnum):
    alltests = ["SMALL SIZE","MED SIZE","LARGE SIZE","NO START", "REMOVE POD","POD FIRST","NO POD","NO SIZE","SWITCH SIZE", "WAIT WATER", "NO HEAT WATER"]
    if testnum > 0 and testnum <= len(alltests):
        tests = [alltests[testnum-1]]
    else:
        tests = alltests
    file = coffeetests(testnum)
    actions = {"SMALL SIZE":(True,5,True,5),"MED SIZE":(True,10,True,10),"LARGE SIZE":(True,15,True,15),"NO START":(False,None,False,None), "REMOVE POD":(False,None,False,None),"POD FIRST":(True,5,True,5),"NO POD":(False,None,False,None),"NO SIZE":(False,None,False,None),"SWITCH SIZE":(True,10,True,10), "WAIT WATER":(True,5,True,7), "NO HEAT WATER":(False,None,True,None)}
    for test in tests:
        if testnum <= 0:
            print("Grading Test",tests.index(test)+1, "Name:",test)
        else:
            print("Grading Test", testnum, "Name:",test)
        f = open(file,"r")
        log = f.read()
        lines = log.split("\n")
        i=0
        foundtest = False
        passedtest = True
        while i < len(lines):
            if "START "+test in lines[i]:
                startheating = None
                startdispensing = None
                enddispensing = None
                foundtest = True
                i+=1
                while "END "+test not in lines[i]:
                    if "START HEATING" in lines[i]:
                        startheating = datetime.datetime.strptime(lines[i][lines[i].find("s:")+2:lines[i].find(",")],'%Y-%m-%d %H:%M:%S.%f')
                    if "START DISPENSING" in lines[i]:
                        startdispensing = datetime.datetime.strptime(lines[i][lines[i].find("s:")+2:lines[i].find(",")],'%Y-%m-%d %H:%M:%S.%f')
                    if "DONE DISPENSING" in lines[i]:
                        enddispensing = datetime.datetime.strptime(lines[i][lines[i].find("s:")+2:lines[i].find(",")],'%Y-%m-%d %H:%M:%S.%f')
                    i+= 1
                if actions[test][0] == False and (startdispensing != None or enddispensing != None):
                    print("Found START DISPENSING or END DISPENSING actions in test ",test," when none expected 0/3")
                    passedtest = False
                elif actions[test][0] == True and (startdispensing == None or enddispensing == None):
                    print("Found no START DISPENSING or END DISPENSING actions in test ",test," when they are expected 0/3")
                    passedtest = False
                elif actions[test][2] == True and (startheating == None):
                    print("Found no START HEATING actions in test ",test," when it is expected 0/3")
                    passedtest = False
                elif actions[test][2] == False and (startheating != None):
                    print("Found START HEATING actions in test ",test," when it is not expected 0/3")
                    passedtest = False
                elif actions[test][0] == True and int((enddispensing-startdispensing).total_seconds()) != actions[test][1]:
                    print("Found START DISPENSING and END DISPENSING actions in test ",test," but incorrect time elapsed 0/3")
                    passedtest = False
                elif actions[test][2] == True and actions[test][3] == None and enddispensing != None:
                    print("Found START HEATING and END DISPENSING actions in test ",test," but END DISPENSING not expected")
                    passedtest = False
                elif actions[test][2] == True and actions[test][3] != None and int((enddispensing-startheating).total_seconds()) != actions[test][3]:
                    print("Found START HEATING and END DISPENSING actions in test ",test," but incorrect time elapsed (did not wait for water to heat up?) 0/3")
                    passedtest = False
            i=i+1
        f.close()
        if not foundtest:
            print("Test did not run. Did the FSM crash?")
        if foundtest and passedtest:
            print("Passed Test: ",test, "3/3")
    return

'''
if len(sys.argv) == 1 or "1" in sys.argv[1]:
    from coffeemaker import *
    print("Part 1: Coffee Maker")
    parsecoffeetest(coffeetests())
'''