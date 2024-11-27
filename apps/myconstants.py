# RADIATOR = ['light.radiator']
# TABLE_LAMP = ['light.table_lamp_1']
# STANDARD_LAMP = ['light.standard_lamp_1']
# BANNISTER = ['light.bannister']
# HALLWAY = ['light.hallway_1']
# FRONT_DOOR = ['light.front_door_1']
# UTILITY = ['light.utility_room_1']
# LANDING = ['light.hallway_3']
# LUMIE = ['light.lumie']

# GARAGE_LIGHTS = ['light.garage'] # group
# KITCHEN_LIGHTS = ['light.kitchen'] # group
# KITCHEN_FLOOR_LIGHTS = ['light.kitchen_floor'] # group
# UPSTAIRS_DOWNSTAIRS_LIGHTS = ['light.upstairs', 'light.downstairs']

# OUTSIDE_LIGHTS = GARAGE_LIGHTS + FRONT_DOOR
# WELCOME_LIGHTS = HALLWAY + FRONT_DOOR + STANDARD_LAMP
# NIGHTTIME_LIGHTS = HALLWAY + BANNISTER
# LIVING_ROOM_LIGHTS = RADIATOR + TABLE_LAMP + STANDARD_LAMP
# HALLWAY_GARAGE_LIGHTS = HALLWAY + GARAGE_LIGHTS + FRONT_DOOR
# FRONT_DOOR_DING_LIGHTS = HALLWAY + FRONT_DOOR

# N_KITCHEN_ENTITIES = 6
# N_KITCHEN_FLOOR_ENTITIES = 2
# N_HALLWAY_ENTITIES = 3

LOCK_ENTITY_ID = 'lock.skoda_karoq_door_lock'
SENSOR_ENTITY_ID = 'binary_sensor.skoda_karoq_vehicle_locked'
SENSOR_ENTITY_LIST = [
  'binary_sensor.skoda_karoq_doors_locked','binary_sensor.skoda_karoq_bonnet',
  'binary_sensor.skoda_karoq_vehicle_locked','binary_sensor.skoda_karoq_doors_open',
  'binary_sensor.skoda_karoq_windows','binary_sensor.skoda_karoq_trunk'
]
DEVICE_TRACKER_ID = 'device_tracker.skoda_karoq_position'
