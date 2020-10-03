#These are the default values if not specified

start = 0              # [0, inf) seconds 
#start = 1-00:00:00    # day-hour:min:sec also works, day=1 is the first day

temperature = 27 # starting optimal temperature hot
humidity = 70 # starting at optimal humidity
smoist = 800 # starting too moist, should turn fan on
wlevel = 140
tankwater = 100

wpump = off
fan = on #starting the fan on, so the soil moisture starts dropping immediately, getting rid of early noise for the test condition
led = 0


leaf_droop = 0          # [0, 1]
lankiness = 0           # [0, 1] (determines the lankiness of the plant) (only really matters if time is large enough) 
plant_health = 1        # [0, 1] (does not affect growth prior to simulation start)

