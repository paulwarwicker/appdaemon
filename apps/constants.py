from typing import Final
# from enum import Enum

# GLOBAL_VAR = "Hello, World!"

# class ModeSelect(Enum):
#     MODE_A = 'mode_a'
#     MODE_B = 'mode_b'
#     MODE_C = 'mode_c'

# GLOBAL_MODE = ModeSelect.MODE_B

# SENSOR_IDS: Final[tuple[str, ...]] = ("sensor.a", "sensor.b")

# announcer
START_HOUR: Final[int] = 8 # :30
END_HOUR: Final[int] = 22 # :30
BEDROOM_WINDOW_ON_HOUR: Final[int] = 23
SECONDS_PER_CHARACTER: Final[float] = 0.15
MINIMUM_MESSAGE_LENGTH: Final[int] = 5

# car
LOCK_ENTITY_ID: Final[str] = 'lock.skoda_karoq_door_lock'
DEVICE_TRACKER_ID: Final[str] = 'device_tracker.skoda_karoq_position'
SENSOR_ENTITY_ID: Final[str] = 'binary_sensor.skoda_karoq_vehicle_locked'
SENSOR_ENTITY_LIST: Final[list[str]] = ['binary_sensor.skoda_karoq_doors_locked', 'binary_sensor.skoda_karoq_bonnet', 'binary_sensor.skoda_karoq_vehicle_locked',
                      'binary_sensor.skoda_karoq_doors_open', 'binary_sensor.skoda_karoq_windows', 'binary_sensor.skoda_karoq_trunk']

# automation
# "starling", "tap", "weather", "garage", "car", "vacuum"
MODULES: Final[list[str]] = ["automationlib", "automation", "timers", "timestamp", "announcer", "motion", "lighting", "alarms", "location", "sonos"]

# front_door
APP_THREADS: Final[int] = 20

# lighting
COOKER_LIGHTS: Final[str] = 'switch.cooker_lights'

LOFT: Final[str] = 'light.loft'
LUMIE: Final[str] = 'light.lumie'
STUDY: Final[str] = 'light.study'
GARDEN: Final[str] = 'light.garden_light'
GARAGE1: Final[str] = 'light.garage_1'
GARAGE2: Final[str] = 'light.garage_2'
DINING1: Final[str] = 'light.dining_room_1'
DINING2: Final[str] = 'light.dining_room_2'
LIVING1: Final[str] = 'light.living_room_1'
LIVING2: Final[str] = 'light.living_room_2'
LIVING3: Final[str] = 'light.living_room_3'
UTILITY: Final[str] = 'light.utility_room_1'
LANDING: Final[str] = 'light.hallway_3'
RADIATOR: Final[str] = 'light.radiator'
HALLWAY1: Final[str] = 'light.hallway_1'
HALLWAY2: Final[str] = 'light.hallway_2'
HALLWAY3: Final[str] = 'light.hallway_3'
BEDROOM1: Final[str] = 'light.lumie'
BEDROOM2: Final[str] = 'light.bedroom_2'
BEDROOM3: Final[str] = 'light.bedroom_3'
UPSTAIRS: Final[str] = 'light.upstairs'
BANNISTER: Final[str] = 'light.bannister'
CLOAKROOM: Final[str] = 'light.cloakroom_1'
TABLE_LAMP: Final[str] = 'light.table_lamp_1'
FRONT_DOOR: Final[str] = 'light.front_door_1'
DOWNSTAIRS: Final[str] = 'light.downstairs'
STANDARD_LAMP: Final[str] = 'light.standard_lamp'

# groups
GARAGE_LIGHTS: Final[str] = 'light.garage_lights'
KITCHEN_LIGHTS: Final[str] = 'light.kitchen_lights'
BEDROOM_LIGHTS: Final[str] = 'light.bedroom_lights'
BATHROOM_LIGHTS: Final[str] = 'light.bathroom_lights'
DINING_ROOM_LIGHTS: Final[str] = 'light.dining_room_lights'
LIVING_ROOM_LIGHTS: Final[str] = 'light.living_room_lights'
UTILITY_ROOM_LIGHTS: Final[str] = 'light.utility_room_lights'
KITCHEN_FLOOR_LIGHTS: Final[str] = 'light.kitchen_floor_lights'
HOME_LIGHTS: Final[str] = 'light.home'

LIVING_ROOM: Final[list[str]] = [RADIATOR, TABLE_LAMP, STANDARD_LAMP]

HALLWAY_LIGHTS: Final[list[str]] = [HALLWAY1, HALLWAY2, HALLWAY3]
OUTSIDE_LIGHTS: Final[list[str]] = [GARAGE_LIGHTS, FRONT_DOOR, GARDEN]
WELCOME_LIGHTS: Final[list[str]] = [HALLWAY1, FRONT_DOOR, STANDARD_LAMP]
NIGHTTIME_LIGHTS: Final[list[str]] = [HALLWAY1, BANNISTER]
FRONT_DOOR_LIGHTS: Final[list[str]] = [HALLWAY1, FRONT_DOOR]
UPSTAIR_LIGHTS: Final[list[str]] = [HALLWAY3, BANNISTER]
DOWNSTAIR_LIGHTS: Final[list[str]] = [HALLWAY1, HALLWAY2, BANNISTER]

ALL_LIGHTS: Final[list[str]] = [HOME_LIGHTS]
N_HALLWAY_ENTITIES: Final[int] = 3
N_KITCHEN_ENTITIES: Final[int] = 6
N_BATHROOM_ENTITIES: Final[int] = 4
N_CLOAKROOM_ENTITIES: Final[int] = 1
N_UTILITY_ROOM_ENTITIES: Final[int] = 1
N_KITCHEN_FLOOR_ENTITIES: Final[int] = 2

# class Timeouts(Enum):
#     ONE: Final[int] = 60
#     TWO: Final[int] = 60*2
#     FIVE: Final[int] = 60*5
#     TEN: Final[int] = 60*10

# GLOBAL_MODE = Timeouts.FIVE

ONEMINUTE: Final[int] = 60
TWOMINUTES: Final[int] = 2*ONEMINUTE
FIVEMINUTES: Final[int] = 5*ONEMINUTE
TENMINUTES: Final[int] = 10*ONEMINUTE

SHORT_TIMEOUT: Final[int] = TWOMINUTES
DEFAULT_TIMEOUT: Final[int] = FIVEMINUTES
LONG_TIMEOUT: Final[int] = TENMINUTES

LONGER_TIMEOUT: Final[int] = DEFAULT_TIMEOUT + SHORT_TIMEOUT
WELCOME_TIMEOUT: Final[int] = LONG_TIMEOUT
KITCHEN_FLOOR_TIMEOUT: Final[int] = LONG_TIMEOUT
BANNISTER_TIMEOUT: Final[int] = LONG_TIMEOUT

FULL_ON_THRESHOLD: Final[int] = 250
HALF_ON: Final[int] = 128
QUARTER_ON: Final[int] = 64
FULL_ON: Final[int] = 255

# alarms
NIGHT_DELIVER: Final[list[int]] = [5, 3]
NIGHT_COLLECT: Final[list[int]] = [5, 23]
DEFAULT: Final[list[int]] = [11, 0]
STUDY_SPEAKER: Final[str] = 'media_player.study'
DINING_SPEAKER: Final[str] = 'media_player.dining_room'
KITCHEN_SPEAKER: Final[str] = 'media_player.kitchen'
BEDROOM_SPEAKER: Final[str] = 'media_player.bedroom'
BEDROOM2_SPEAKER: Final[str] = 'media_player.bedroom2'
HALLWAY_SPEAKER: Final[str] = 'media_player.hallway'
BATHROOM_SPEAKER: Final[str] = 'media_player.bathroom'
SOUNDBAR_SPEAKER: Final[str] = 'media_player.living_room'
BROADCAST_ENTITY_ID: Final[list[str]] = [STUDY_SPEAKER, KITCHEN_SPEAKER, BATHROOM_SPEAKER] # , HALLWAY_SPEAKER]
ALL_SPEAKER_ENTITY_ID: Final[list[str]] = [STUDY_SPEAKER, KITCHEN_SPEAKER, BEDROOM_SPEAKER, HALLWAY_SPEAKER, BATHROOM_SPEAKER, DINING_SPEAKER, SOUNDBAR_SPEAKER, BEDROOM2_SPEAKER]

TARGET_VOLUME: Final[int] = 40
ATTEMPTS: Final[int] = 5
RAMP_TIME: Final[int] = 20
PLAY_DELAY: Final[float] = 0.75
DEFAULT_VOLUME: Final[float] = 0.15
ALARM_VOLUME: Final[float] = 0.3
ANNOUNCE_VOLUME: Final[float] = 0.5
STUDY_ANNOUNCE_VOLUME: Final[float] = 0.1
STUDY_ANNOUNCE_VOLUME_LOW: Final[float] = 0.2
EARLY_ALARM_TIME: Final[str] = '07:00:00'
NORMAL_ALARM_TIME: Final[str] = '07:45:00'
LATE_ALARM_TIME: Final[str] = '10:00:00'

NORMAL_ALARM: Final[list[str]]  = [
    PROGRESSIVE1_STREAM := 'aac://http://prem2.di.fm:80/progressive?5fba91be81f6da5b573f89c1',
    PROGRESSIVE2_STREAM := 'aac://http://prem1.di.fm:80/progressive?5fba91be81f6da5b573f89c1',
    PROGRESSIVE3_STREAM := 'aac://http://prem4.di.fm:80/progressive?5fba91be81f6da5b573f89c1',
]

EARLY_ALARM: Final[list[str]] = [
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

BACKUP_STREAM: Final[str] = SUNSETS_STREAM
PROGRESSIVE_STREAM: Final[str] = PROGRESSIVE1_STREAM

ALTNEWWAVE_STREAM: Final[str] = 'aac://http://prem2.radiotunes.com:80/80saltnnewwave?5fba91be81f6da5b573f89c1'
CHRISTMAS_STREAM: Final[str] = 'aac://http://prem2.radiotunes.com:80/popchristmas?5fba91be81f6da5b573f89c1'
HALLWAY_STREAMS: Final[list[str]] = [
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
GARAGE_ENTITY_ID: Final[str] = 'cover.remootio_device_host_192_168_1_13_s_n_30c92235df30xupwfafu_none'

# location
MAX_ENTITY_ID: Final[str] = 'device_tracker.maxine_iphone'
PAUL_ENTITY_ID: Final[str] = 'device_tracker.paulw_iphone'

LOCATIONS: Final[dict[str, list[str]]] = {
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
DAILY_WATERING_MINUTES: Final[int] = 30

# timestamps initialised in automation
TIMESTAMPS: Final[list[str]] = [
    'downstairs', 'prev_upstairs', 'upstairs', 'karoq_announce', 'karoq_notification', 'vacuum', 'general', 'travel',
    'tap', 'karoq_home', 'upstairs_motion', 'garage_open', 'garage_close', 'garage_lights_on', 'garage_lights_off',
    'snooze'
    ]

BEDROOM_BUTTON: Final[str] = 'shellybutton1-C8C9A33CDF09'
GARAGE_BUTTON: Final[str] = 'shellybutton1-EC64C9C4F038'
