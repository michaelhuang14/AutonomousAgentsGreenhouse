BASELINE = baseline_watering.bsl

DELAY UNTIL 1-04:30:00

WHENEVER smoist[0] < 450 and not already_watered
  WAIT wpump FOR 60 # Wait one minute for water pump to be on
  SET already_watered = True
  WAIT not wpump FOR 11 # Turn pump off before 11 seconds  have elapsed

  # Wait an hour for both moisture sensors to be above threshold
  #WAIT smoist[0] > 450 and smoist[1] > 450 FOR 3600

WHENEVER 1-04:00:00
  SET aw = False

# Don't let the pump overwater things
WHENEVER wpump
  ENSURE smoist[0] < 600 and smoist[1] < 600 FOR 3600
