#These are the default values if not specified

start = 0              # [0, inf) seconds 
#start = 1-04:00:00    # day-hour:min:sec also works, day=1 is the first day

temperature = 26 # optimal
humidity = 40 # too low, should not turn fan on
smoist = 300 # too low, should not turn fan on
wlevel = 140
tankwater = 0

wpump = off
fan = off
led = 0


leaf_droop = 0          # [0, 1]
lankiness = 0           # [0, 1] (determines the lankiness of the plant) (only really matters if time is large enough) 
plant_health = 1        # [0, 1] (does not affect growth prior to simulation start)

