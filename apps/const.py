from adapi import ADAPI # pylint: disable=E0401

class AutomationConstants:
    """Manage constants for automation"""

    # announcer
    START_HOUR = 8 # :30
    END_HOUR = 21 # :30
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
              "starling", "motion", "lighting", "tap", "weather", "garage", "car",
              "vacuum"]

    # front_door
    APP_THREADS = 20

    # lighting
    COOKER_LIGHTS = 'switch.cooker_lights'

    LOFT = 'light.loft'
    LUMIE = 'light.lumie'
    STUDY = 'light.study'
    GARDEN = 'light.garden_light'
    GARAGE1 = 'light.garage_1'
    GARAGE2 = 'light.garage_2'
    DINING1 = 'light.dining_room_1'
    DINING2 = 'light.dining_room_2'
    LIVING1 = 'light.living_room_1'
    LIVING2 = 'light.living_room_2'
    LIVING3 = 'light.living_room_3'
    UTILITY = 'light.utility_room_1'
    LANDING = 'light.hallway_3'
    RADIATOR = 'light.radiator'
    HALLWAY1 = 'light.hallway_1'
    HALLWAY2 = 'light.hallway_2'
    HALLWAY3 = 'light.hallway_3'
    BEDROOM1 = 'light.lumie'
    BEDROOM2 = 'light.bedroom_2'
    BEDROOM3 = 'light.bedroom_3'
    UPSTAIRS = 'light.upstairs'
    BANNISTER = 'light.bannister'
    CLOAKROOM = 'light.cloakroom_1'
    TABLE_LAMP = 'light.table_lamp_1'
    FRONT_DOOR = 'light.front_door_1'
    DOWNSTAIRS = 'light.downstairs'
    STANDARD_LAMP = 'light.standard_lamp'

    # groups
    GARAGE_LIGHTS = 'light.garage_lights'
    KITCHEN_LIGHTS = 'light.kitchen_lights'
    BEDROOM_LIGHTS = 'light.bedroom_lights'
    BATHROOM_LIGHTS = 'light.bathroom_lights'
    DINING_ROOM_LIGHTS = 'light.dining_room_lights'
    LIVING_ROOM_LIGHTS = 'light.living_room_lights'
    UTILITY_ROOM_LIGHTS = 'light.utility_room_lights'
    KITCHEN_FLOOR_LIGHTS = 'light.kitchen_floor_lights'
    HOME_LIGHTS = 'light.home'

    LIVING_ROOM = [RADIATOR, TABLE_LAMP, STANDARD_LAMP]

    HALLWAY_LIGHTS = [HALLWAY1, HALLWAY2, HALLWAY3]

    OUTSIDE_LIGHTS = [GARAGE_LIGHTS, FRONT_DOOR, GARDEN]
    WELCOME_LIGHTS = [HALLWAY1, FRONT_DOOR, STANDARD_LAMP]
    NIGHTTIME_LIGHTS = [HALLWAY1, BANNISTER]
    FRONT_DOOR_LIGHTS = [HALLWAY1, FRONT_DOOR]

    UPSTAIR_LIGHTS = [HALLWAY3, BANNISTER]
    DOWNSTAIR_LIGHTS = [HALLWAY1, HALLWAY2, BANNISTER]

    ALL_LIGHTS = [HOME_LIGHTS]

    N_HALLWAY_ENTITIES = 3
    N_KITCHEN_ENTITIES = 6
    N_BATHROOM_ENTITIES = 4
    N_UTILITY_ROOM_ENTITIES = 1
    N_KITCHEN_FLOOR_ENTITIES = 2

    ONEMINUTE = 60
    SHORT_TIMEOUT = ONEMINUTE
    DEFAULT_TIMEOUT = 2*ONEMINUTE
    LONG_TIMEOUT = 5*ONEMINUTE

    LONGER_TIMEOUT = DEFAULT_TIMEOUT + SHORT_TIMEOUT
    WELCOME_TIMEOUT = LONG_TIMEOUT
    KITCHEN_FLOOR_TIMEOUT = LONG_TIMEOUT
    BANNISTER_TIMEOUT = 2*LONG_TIMEOUT

    FULL_ON = 250
    HALF_ON = 128
    QUARTER_ON = 64

    # alarms
    NIGHT_DELIVER = [5, 3]
    NIGHT_COLLECT = [5, 23]
    DEFAULT = [11, 0]
    STUDY_SPEAKER = 'media_player.study'
    DINING_SPEAKER = 'media_player.dining_room'
    KITCHEN_SPEAKER = 'media_player.kitchen'
    BEDROOM_SPEAKER = 'media_player.bedroom'
    BEDROOM2_SPEAKER = 'media_player.bedroom2'
    HALLWAY_SPEAKER = 'media_player.hallway'
    BATHROOM_SPEAKER = 'media_player.bathroom'
    SOUNDBAR_SPEAKER = 'media_player.living_room'
    BROADCAST_ENTITY_ID = [STUDY_SPEAKER, KITCHEN_SPEAKER, BATHROOM_SPEAKER] # , HALLWAY_SPEAKER]
    ALL_SPEAKER_ENTITY_ID = [STUDY_SPEAKER, KITCHEN_SPEAKER, BEDROOM_SPEAKER, HALLWAY_SPEAKER, BATHROOM_SPEAKER, DINING_SPEAKER, SOUNDBAR_SPEAKER, BEDROOM2_SPEAKER]

    BACKUP_STREAM = 'aac://http://prem2.zenradio.com:80/zrperfectsunsets_aac?5fba91be81f6da5b573f89c1'
    TARGET_VOLUME = 40
    ATTEMPTS = 5
    PLAY_DELAY = 0.75
    DEFAULT_VOLUME = 0.15
    ALARM_VOLUME = 0.3

    NORMAL_ALARM = [
        PROGRESSIVE1_STREAM := 'aac://http://prem2.di.fm:80/progressive?5fba91be81f6da5b573f89c1',
        PROGRESSIVE2_STREAM := 'aac://http://prem1.di.fm:80/progressive?5fba91be81f6da5b573f89c1',
        PROGRESSIVE3_STREAM := 'aac://http://prem4.di.fm:80/progressive?5fba91be81f6da5b573f89c1',
    ]

    EARLY_ALARM = [
        OCEANS_STREAM := 'aac://http://prem2.zenradio.com:80/zroceansounds_aac?5fba91be81f6da5b573f89c1',
        NATIVEAMERICAN_STREAM := 'aac://http://prem2.zenradio.com:80/zrnativeamericansounds_aac?5fba91be81f6da5b573f89c1',
        SOUNDSOFRAIN_STREAM := 'aac://http://prem2.zenradio.com:80/zrsoundsofrain_aac?5fba91be81f6da5b573f89c1',
        RELAXATION_STREAM := 'aac://http://prem2.zenradio.com:80/zrrelaxation_aac?5fba91be81f6da5b573f89c1',
        RELAXINGSPA_STREAM := 'aac://http://prem2.zenradio.com:80/zrrelaxingspanmassage_aac?5fba91be81f6da5b573f89c1',
        SHAMANICMUSIC_STREAM := 'aac://http://prem2.zenradio.com:80/zrshamanicmusic_aac?5fba91be81f6da5b573f89c1',
        SUNSETS_STREAM := 'aac://http://prem2.zenradio.com:80/zrperfectsunsets_aac?5fba91be81f6da5b573f89c1',
        NATURE_STREAM := 'aac://http://prem2.zenradio.com:80/zrnature_aac?5fba91be81f6da5b573f89c1',
        TIBETANMUSIC_STREAM := 'aac://http://prem2.zenradio.com:80/zrtibetanmusic_aac?5fba91be81f6da5b573f89c1',
        SLEEPRELAXATION_STREAM := 'aac://http://prem2.zenradio.com:80/zrsleeprelaxation_aac?5fba91be81f6da5b573f89c1',
        CHILLOUT_STREAM := 'aac://http://prem2.zenradio.com:80/zrchillout_aac?5fba91be81f6da5b573f89c1',
        ATMOSPHERICDREAMS_STREAM := 'aac://http://prem2.zenradio.com:80/zratmosphericdreams_aac?5fba91be81f6da5b573f89c1',
        SPACEDREAMS_STREAM := 'aac://http://prem2.zenradio.com:80/zrspacedreams_aac?5fba91be81f6da5b573f89c1',
        BIRDSONG_STREAM := 'x-sonos-spotify:spotify%3atrack%3a3K3cxx8ntQp8DZbPpltwr4?sid=9&flags=8224&sn=1', # birdsong garden morning
        EARLYMORNINGRAIN_STREAM := 'x-sonos-spotify:spotify%3atrack%3a2cwKtKEhPn6ZnJmlzbmpLQ?sid=9&flags=8224&sn=1', # the early morning rain
        RAINDROPSDANCING_STREAM := 'x-sonos-spotify:spotify%3atrack%3a4G6Lz9Et6dhLKydPyY4N9a?sid=9&flags=8224&sn=1', # rain drops dancing on a tin roof
    ]

    BACKUP_STREAM = SUNSETS_STREAM
    PROGRESSIVE_STREAM = PROGRESSIVE1_STREAM

    ALTNEWWAVE_STREAM = 'aac://http://prem2.radiotunes.com:80/80saltnnewwave?5fba91be81f6da5b573f89c1'
    CHRISTMAS_STREAM = 'aac://http://prem2.radiotunes.com:80/popchristmas?5fba91be81f6da5b573f89c1'

    HALLWAY_STREAMS = [
        SUMMER_VIBES_ALBUM := 'spotify:album:37ZeJt50FWCaLkw3HNJB2c',
        SUMMER_VIBES_PLAYLIST := 'spotify:playlist:2hmLDliFT9mW84XHxRUzwx',
        SUMMER_HITS_PLAYLIST := 'spotify:playlist:37i9dQZF1DX4uU3TGzIPXL',
        BOSSANOVA_STREAM := 'aac://http://prem2.radiotunes.com:80/smoothbossanova?5fba91be81f6da5b573f89c1',
    ]

    # ALTNEWWAVE1_STREAM := 'aac://http://prem2.radiotunes.com:80/80saltnnewwave?5fba91be81f6da5b573f89c1',
    # ALTNEWWAVE2_STREAM := 'aac://http://prem4.radiotunes.com:80/80saltnnewwave?5fba91be81f6da5b573f89c1',
    # ALTNEWWAVE3_STREAM := 'aac://http://prem1.radiotunes.com:80/80saltnnewwave?5fba91be81f6da5b573f89c1',
    # SUNSETS1_STREAM := 'aac://http://prem2.zenradio.com:80/zrperfectsunsets_aac?5fba91be81f6da5b573f89c1',
    # SUNSETS2_STREAM := 'aac://http://prem1.zenradio.com:80/zrperfectsunsets_aac?5fba91be81f6da5b573f89c1',
    # SUNSETS3_STREAM := 'aac://http://prem4.zenradio.com:80/zrperfectsunsets_aac?5fba91be81f6da5b573f89c1'
    # 'x-sonos-spotify:spotify%3atrack%3a1r4QKeqpv1ov8FkrgKDxQ7?sid=9&flags=8224&sn=1', # a gentle thunderstorm
    # 'x-sonos-spotify:spotify%3atrack%3a2T5Lipk1QTtvt76Xjcwrxc?sid=9&flags=8224&sn=1', # heavy thunderstorm sounds
    # 'x-sonos-spotify:spotify%3atrack%3a1E0jvxVMYcnZbjvrs03Yay?sid=9&flags=8224&sn=1', # thunderstorm sounds with rain and loud claps of thunder for all isomniacs
    # 'x-sonos-spotify:spotify%3atrack%3a49kbhMUlsVPp0fOdTOCgNM?sid=9&flags=8224&sn=1', # extreme thunderstorm soubnds with torrential rain & very loud thunder claps
    # 'x-sonos-spotify:spotify%3atrack%3a16D3zoIJWuEbXFfkzXSIqs?sid=9&flags=8224&sn=1', # an angry thunderstorm
    # 'x-sonos-spotify:spotify%3atrack%3a6H5aGE9xZEPkpeEAn4f7b8?sid=9&flags=8224&sn=1', # thunderstorm
    # 'x-sonos-spotify:spotify%3atrack%3a3UdClX9rDMiYUOIl6JWaRo?sid=9&flags=8224&sn=1', # heavy thunderstorm

    # garage
    GARAGE_ENTITY_ID = 'cover.remootio_device_host_192_168_1_13_s_n_30c92235df30xupwfafu_none'

    # location
    MAX_ENTITY_ID = 'device_tracker.maxine_iphone'
    PAUL_ENTITY_ID = 'device_tracker.paulw_iphone'

    LOCATIONS = {
        'proximity.ds_smith_fordham': ['ds_smith_fordham','DS Smith Fordem'], # get announcement to sound vaguely right
        'proximity.ds_smith_warboys': ['ds_smith_warboys','DS Smith Warboys'],
        'proximity.pilates': ['pilates','Pilates Longstanton'],
        'proximity.pilates2': ['pilates2','Pilates Bar Hill'],
        'proximity.pilates3': ['pilates3','Pilates Northstowe'],
        'proximity.karen_wax': ['karen_wax','Karen waxing'],
        'proximity.karen_smith': ['karen_smith','Karen Smith'],
        'proximity.karen_nails': ['karen_nails','Karen nails'],
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
        'proximity.jollop_place': ['jollop_place', 'Jollop Place'],
        'proximity.c_r_t': ['c_r_t','C R T Offices'],
        'proximity.c_r_t_offsite': ['c_r_t_offsite','C R T Offsite meeting'],
        'proximity.jan_jim': ['jan_jim','Jan and Jim'],
    }

    # tap
    DAILY_WATERING_MINUTES = 30

    # timestamps initialised in automation
    TIMESTAMPS = [
        'downstairs', 'prev_upstairs', 'upstairs', 'karoq_announce', 'karoq_notification', 'vacuum', 'general', 'travel',
        'tap', 'karoq_home', 'upstairs_motion', 'garage_open', 'garage_close', 'garage_lights_on', 'garage_lights_off',
        'snooze'
        ]

    BEDROOM_BUTTON = 'shellybutton1-C8C9A33CDF09'
    GARAGE_BUTTON = 'shellybutton1-EC64C9C4F038'

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

# constants_manager = ConstantsManagement()
# # Accessing constants
# print(constants_manager.PI)  # Output: 3.14159
# # Attempting to modify constants raises a TypeError
# #constants_manager.PI = 3.14  # Raises TypeError: Constants are immutable
