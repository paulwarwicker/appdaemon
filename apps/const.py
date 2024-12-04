# -*- coding: utf-8 -*-

from adapi import ADAPI # type: ignore # pylint: disable=E0401 disable=E0611

class AutomationConstants:
    """Documentation for AutomationConstants"""

    # announcer
    START_HOUR = 8 # :30
    END_HOUR = 21 # :30
    ALL_ENTITY_ID = ['media_player.bedroom', 'media_player.study', 'media_player.dining_room', 'media_player.kitchen']
    SECONDS_PER_CHARACTER = 0.15
    MINIMUM_MESSAGE_LENGTH = 5

    # car
    LOCK_ENTITY_ID = 'lock.skoda_karoq_door_lock'
    DEVICE_TRACKER_ID = 'device_tracker.skoda_karoq_position'
    SENSOR_ENTITY_ID = 'binary_sensor.skoda_karoq_vehicle_locked'
    SENSOR_ENTITY_LIST = ['binary_sensor.skoda_karoq_doors_locked', 'binary_sensor.skoda_karoq_bonnet', 'binary_sensor.skoda_karoq_vehicle_locked',
                          'binary_sensor.skoda_karoq_doors_open', 'binary_sensor.skoda_karoq_windows', 'binary_sensor.skoda_karoq_trunk']

    # automation
    MODULES = ["alarms", "timers", "timestamp", "announcer", "location", "sonos",
              "starling", "motion", "lighting", "tap", "weather", "garage", "car"]

    # front_door
    APP_THREADS = 20

    # lighting
    LOFT = 'light.loft'
    LUMIE = 'light.lumie'
    STUDY = 'light.study'
    GARDEN = 'light.garden_light'
    GARAGE = 'light.garage'  # group
    DINING1 = 'light.dining_room_1'
    DINING2 = 'light.dining_room_2'
    UTILITY = 'light.utility_room_1'
    KITCHEN = 'light.kitchen'  # group
    LANDING = 'light.hallway_3'
    RADIATOR = 'light.radiator'
    HALLWAY1 = 'light.hallway_1'
    HALLWAY2 = 'light.hallway_2'
    BEDROOM1 = 'light.lumie'
    BEDROOM2 = 'light.bedroom_2'
    BEDROOM3 = 'light.bedroom_3'
    UPSTAIRS = 'light.upstairs'
    BANNISTER = 'light.bannister'
    TABLE_LAMP = 'light.table_lamp_1'
    FRONT_DOOR = 'light.front_door_1'
    DOWNSTAIRS = 'light.downstairs'
    STANDARD_LAMP = 'light.standard_lamp_1'
    KITCHEN_FLOOR = 'light.kitchen_floor'  # group

    COOKER_LIGHTS = 'switch.cooker_lights'

    DINING_LIGHTS = [DINING1, DINING2]
    BEDROOM_LIGHTS = [BEDROOM1, BEDROOM2, BEDROOM3]
    HALLWAY_LIGHTS = [HALLWAY1, HALLWAY1]

    OUTSIDE_LIGHTS = [GARAGE, FRONT_DOOR, GARDEN]
    WELCOME_LIGHTS = [HALLWAY1, FRONT_DOOR, STANDARD_LAMP]
    NIGHTTIME_LIGHTS = [HALLWAY1, BANNISTER]
    LIVING_ROOM_LIGHTS = [RADIATOR, TABLE_LAMP, STANDARD_LAMP]
    HALLWAY_GARAGE_LIGHTS = [HALLWAY1, GARAGE, FRONT_DOOR]
    FRONT_DOOR_DING_LIGHTS = [HALLWAY1, FRONT_DOOR]

    # ALL_LIGHTS = [RADIATOR, TABLE_LAMP, STANDARD_LAMP, BANNISTER, HALLWAY1, HALLWAY2, DINING1, DINING2, FRONT_DOOR, UTILITY, LANDING, LUMIE, GARAGE, KITCHEN, KITCHEN_FLOOR, LOFT, STUDY, BEDROOM1, BEDROOM2, BEDROOM3, GARDEN]  # type: ignore # pylint: disable=C0301
    ALL_LIGHTS = [UPSTAIRS, DOWNSTAIRS]

    N_HALLWAY_ENTITIES = 3
    N_KITCHEN_ENTITIES = 6
    N_KITCHEN_FLOOR_ENTITIES = 2

    # alarms
    NIGHT_DELIVER = [5, 3]
    NIGHT_COLLECT = [5, 23]
    DEFAULT = [11, 0]
    STUDY_SPEAKER = 'media_player.study'
    KITCHEN_SPEAKER = 'media_player.kitchen'
    BEDROOM_SPEAKER = 'media_player.bedroom'
    BEDROOM2_SPEAKER = 'media_player.bedroom2'
    BATHROOM_SPEAKER = 'media_player.bathroom'
    SOUNDBAR_SPEAKER = 'media_player.living_room'

    BACKUP_STREAM = 'aac://http://prem2.zenradio.com:80/zrperfectsunsets_aac?5fba91be81f6da5b573f89c1'
    TARGET_VOLUME = 50
    ATTEMPTS = 5
    PLAY_DELAY = 0.75
    NORMAL_ALARM = ['aac://http://prem2.di.fm:80/progressive?5fba91be81f6da5b573f89c1']

    # 'x-sonos-spotify:spotify%3atrack%3a3K3cxx8ntQp8DZbPpltwr4?sid=9&flags=8224&sn=1', # birdsong garden morning
    # 'x-sonos-spotify:spotify%3atrack%3a1r4QKeqpv1ov8FkrgKDxQ7?sid=9&flags=8224&sn=1', # a gentle thunderstorm
    # 'x-sonos-spotify:spotify%3atrack%3a2T5Lipk1QTtvt76Xjcwrxc?sid=9&flags=8224&sn=1', # heavy thunderstorm sounds
    # 'x-sonos-spotify:spotify%3atrack%3a1E0jvxVMYcnZbjvrs03Yay?sid=9&flags=8224&sn=1', # thunderstorm sounds with rain and loud claps of thunder for all isomniacs
    # 'x-sonos-spotify:spotify%3atrack%3a49kbhMUlsVPp0fOdTOCgNM?sid=9&flags=8224&sn=1', # extreme thunderstorm soubnds with torrential rain & very loud thunder claps
    # 'x-sonos-spotify:spotify%3atrack%3a2cwKtKEhPn6ZnJmlzbmpLQ?sid=9&flags=8224&sn=1', # the early morning rain
    # 'x-sonos-spotify:spotify%3atrack%3a4G6Lz9Et6dhLKydPyY4N9a?sid=9&flags=8224&sn=1', # rain drops dancing on a tin roof
    # 'x-sonos-spotify:spotify%3atrack%3a16D3zoIJWuEbXFfkzXSIqs?sid=9&flags=8224&sn=1', # an angry thunderstorm
    # 'x-sonos-spotify:spotify%3atrack%3a6H5aGE9xZEPkpeEAn4f7b8?sid=9&flags=8224&sn=1', # thunderstorm
    # 'x-sonos-spotify:spotify%3atrack%3a3UdClX9rDMiYUOIl6JWaRo?sid=9&flags=8224&sn=1', # heavy thunderstorm

    EARLY_ALARM = [
                    'aac://http://prem2.zenradio.com:80/zroceansounds_aac?5fba91be81f6da5b573f89c1',
                    'aac://http://prem2.zenradio.com:80/zrnativeamericanflute_aac?5fba91be81f6da5b573f89c1',
                    'aac://http://prem2.zenradio.com:80/zrsoundsofrain_aac?5fba91be81f6da5b573f89c1',
                    'aac://http://prem2.zenradio.com:80/zrrelaxation_aac?5fba91be81f6da5b573f89c1',
                    'aac://http://prem2.zenradio.com:80/zrrelaxingspanmassage_aac?5fba91be81f6da5b573f89c1',
                    'aac://http://prem2.zenradio.com:80/zrshamanicmusic_aac?5fba91be81f6da5b573f89c1',
                    'aac://http://prem2.zenradio.com:80/zrperfectsunsets_aac?5fba91be81f6da5b573f89c1',
                    'aac://http://prem2.zenradio.com:80/zrnature_aac?5fba91be81f6da5b573f89c1',
                    'aac://http://prem2.zenradio.com:80/zrtibetanmusic_aac?5fba91be81f6da5b573f89c1',
                    'aac://http://prem2.zenradio.com:80/zrsleeprelaxation_aac?5fba91be81f6da5b573f89c1',
                    'aac://http://prem2.zenradio.com:80/zrchillout_aac?5fba91be81f6da5b573f89c1',
                    'aac://http://prem2.zenradio.com:80/zratmosphericdreams_aac?5fba91be81f6da5b573f89c1',
                    'aac://http://prem2.zenradio.com:80/zrspacedreams_aac?5fba91be81f6da5b573f89c1',
                ]

    # garage
    GARAGE_ENTITY_ID = 'cover.remootio_device_host_192_168_1_13_s_n_30c92235df30xupwfafu_none'

    # location
    MAX_ENTITY_ID = 'device_tracker.maxine_iphone'
    PAUL_ENTITY_ID = 'device_tracker.paulw_iphone'

    LOCATIONS = {
        'proximity.ds_smith_fordham': ['ds_smith_fordham','DS Smith Fordhem'],
        'proximity.ds_smith_warboys': ['ds_smith_warboys','DS Smith Warboys'],
        'proximity.pilates': ['pilates','Pilates Longstanton'],
        'proximity.pilates2': ['pilates2','Pilates Bar Hill'],
        'proximity.pilates3': ['pilates3','Pilates Northstowe'],
        'proximity.pilates4': ['pilates4','Pilates Northstowe'],
        'proximity.karen_wax': ['karen_wax','Karen waxing'],
        'proximity.karen_smith': ['karen_smith','Karen Smith'],
        'proximity.karen_nail': ['karen_nail','Karen nails'],
        'proximity.indian_ocean': ['indian_ocean','Indian Ocean'],
        'proximity.newmarket': ['newmarket','Newmarket junction'],
        'proximity.bar_hill': ['bar_hill','Bar Hill junction'],
        'proximity.village': ['village','Max is in the village'],
        'proximity.sainsburys_eddington': ['sainsburys_eddington','Sainsburys Eddington'],
        'proximity.waitrose_trumpington': ['waitrose_trumpington','Waitrose Trumpington'],
        'proximity.morrisons_stives': ['morrisons_st_ives','Morrisons St Ives'],
        'proximity.gay_kellaway_racing': ['gay_kellaway_racing','Gay Kellaway Racing'],
        'proximity.martyn_tracey': ['martyn_tracey','Martyn and Tracey'],
        'proximity.papworth': ['papworth','Papworh Hospital'],
        'proximity.home': ['home', 'Max is home'],
    }

    # tap
    DAILY_WATERING_MINUTES = 30

# ConstantsManagement class
class ConstantsManagement:
    """Documentation for ConstantsManagement"""

    def __init__(self, adapi: ADAPI) -> None:
        # Set constants from separate classes as attributes
        for cls in [AutomationConstants]:
            for key, value in cls.__dict__.items():
                if not key.startswith("__"):
                    self.__dict__.update(**{key: value})

    def __setattr__(self, name, value):
        raise TypeError("Constants are immutable")

# # Create an instance of ConstantsManagement
# constants_manager = ConstantsManagement()

# # Accessing constants
# print(constants_manager.PI)  # Output: 3.14159
# print(constants_manager.MAX_SIZE)  # Output: 100

# # Attempting to modify constants raises a TypeError
# #constants_manager.PI = 3.14  # Raises TypeError: Constants are immutable
