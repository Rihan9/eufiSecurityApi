from enum import Enum

class TWO_FACTOR_AUTH_METHODS(Enum):
    SMS = 0,
    PUSH = 1,
    EMAIL = 2

API_BASE_URL = 'mysecurity.eufylife.com/api'
# API_BASE_URL = 'security-app-eu.eufylife.com'
ENDPOINT_LOGIN = '/passport/login'
ENDPOINT_LOGOUT = '/passport/logout'
ENDPOINT_DEVICE_LIST = '/app/get_devs_list'
ENDPOINT_STATION_LIST = '/app/get_hub_list'

MOTION_DETECTION_COOLDOWN_MS = 3000

API_HEADERS = {
    'app_version': "v2.3.0_792",
    'os_type': "android",
    'os_version': "29",
    'phone_model': "ONEPLUS A3003",
    'country': "IT",
    'language': "en",
    'openudid': "5e4621b0152c0d00",
    'uid': "",
    'net_type': "wifi",
    'mnc': "02",
    'mcc': "262",
    'sn': "75814221ee75",
    'Model_type': "PHONE",
    'timezone': "GMT+01:00",
    'Content-Type': 'application/json'
}

class RESPONSE_ERROR_CODE(Enum):
    WHATEVER_ERROR          = 0
    SESSION_TIMEOUT         = 401
    CONNECT_ERROR           = 997
    NETWORK_ERROR           = 998
    SERVER_ERROR            = 999
    UNVERIFIED_EMAIL        = 26015
    VERIFY_CODE_ERROR       = 26050
    VERIFY_CODE_EXPIRED     = 26051
    NEED_VERIFY_CODE        = 26052
    VERIFY_CODE_MAX         = 26053
    VERIFY_CODE_NONE_MATCH  = 26054
    VERIFY_PASSWORD_ERROR   = 26055
    PHONE_NONE_SUPPORT      = 26058
    TOO_MANY_LOGIN_ATTEMPTS = 100028

class DEVICE_STATE(Enum):
    OFFLINE                 = 0
    ONLINE                  = 1
    MANUALLY_DISABLED       = 2
    OFFLINE_LOWBAT          = 3
    REMOVE_AND_READD        = 4
    RESET_AND_READD         = 5

class DEVICE_TYPE(Enum):
    UNKNOWN                 = -1
    STATION                 = 0
    CAMERA                  = 1
    SENSOR                  = 2
    FLOODLIGHT              = 3
    CAMERA_E                = 4
    DOORBELL                = 5
    BATTERY_DOORBELL        = 7
    CAMERA2C                = 8
    CAMERA2                 = 9
    MOTION_SENSOR           = 10
    KEYPAD                  = 11
    CAMERA2_PRO             = 14
    CAMERA2C_PRO            = 15
    BATTERY_DOORBELL_2      = 16
    INDOOR_CAMERA           = 30
    INDOOR_PT_CAMERA        = 31
    SOLO_CAMERA             = 32
    SOLO_CAMERA_PRO         = 33
    INDOOR_CAMERA_1080      = 34
    INDOOR_PT_CAMERA_1080   = 35
    LOCK_BASIC              = 50
    LOCK_ADVANCED           = 51
    LOCK_BASIC_NO_FINGER    = 52
    LOCK_ADVANCED_NO_FINGER = 53

class PARAM_TYPE(Enum):
    #
    PROP_EVENT_NUM          = 'event_num'
    PROP_UPDATE_TIME        = 'update_time'
    PROP_MAIN_SW_VERSION    = 'main_sw_version'
    PROP_MAIN_HW_VERSION    = 'main_hw_version'
    PROP_SEC_SW_VERSION     = 'sec_sw_version'
    PROP_SEC_HW_VERSION     = 'sec_hw_version'
    PROP_STATUS             = 'status'
    #
    BATTERY_LEVEL                   = 1101 #Maybe? 1177
    DEVICE_UPGRADE_NOW              = 1134
    DEVICE_RSSI                     = 1141
    
    OPEN_DEVICE                     = 2001
    NIGHT_VISUAL                    = 2002
    VOLUME                          = 2003
    DETECT_MODE                     = 2004
    DETECT_MOTION_SENSITIVE         = 2005
    DETECT_ZONE                     = 2006
    UN_DETECT_ZONE                  = 2007
    SDCARD                          = 2010
    CHIME_STATE                     = 2015
    RINGING_VOLUME                  = 2022
    DETECT_EXPOSURE                 = 2023
    DETECT_SWITCH                   = 2027
    DETECT_SCENARIO                 = 2028
    DOORBELL_HDR                    = 2029
    DOORBELL_IR_MODE                = 2030
    DOORBELL_VIDEO_QUALITY          = 2031
    DOORBELL_BRIGHTNESS             = 2032
    DOORBELL_DISTORTION             = 2033
    DOORBELL_RECORD_QUALITY         = 2034
    DOORBELL_MOTION_NOTIFICATION    = 2035
    DOORBELL_NOTIFICATION_OPEN      = 2036
    DOORBELL_SNOOZE_START_TIME      = 2037
    DOORBELL_NOTIFICATION_JUMP_MODE = 2038
    DOORBELL_LED_NIGHT_MODE         = 2039
    DOORBELL_RING_RECORD            = 2040
    DOORBELL_AUDIO_RECODE           = 2042

    WATERMARK_MODE          = 1214              # 1 - hide, 2 - show
    SNOOZE_MODE             = 1271              # The value is base64 encoded
    
    SCHEDULE_MODE           = 1257              # 0 - Away, 1 - Home, 63 - Disarmed
    GUARD_MODE              = 1224              # 0 - Away, 1 - Home, 63 - Disarmed, 2 - SCHEDULE_MODE
    
    FLOODLIGHT_MANUAL_SWITCH        = 1400
    FLOODLIGHT_MANUAL_BRIGHTNESS    = 1401         # The range is 22-100
    FLOODLIGHT_MOTION_BRIGHTNESS    = 1412         # The range is 22-100
    FLOODLIGHT_SCHEDULE_BRIGHTNESS  = 1413       # The range is 22-100
    FLOODLIGHT_MOTION_SENSITIVTY    = 1272         # The range is 1-5
    
    CAMERA_UPGRADE_NOW                  = 1133
    CAMERA_SPEAKER_VOLUME               = 1230
    CAMERA_RECORD_ENABLE_AUDIO          = 1366           # Enable microphone
    CAMERA_RECORD_RETRIGGER_INTERVAL    = 1250     # In seconds
    CAMERA_RECORD_CLIP_LENGTH           = 1249            # In seconds
    CAMERA_IR_CUT                       = 1013
    CAMERA_PIR                          = 1011
    CAMERA_WIFI_RSSI                    = 1142
    CAMERA_MOTION_ZONES                 = 1204

    SENSOR_CONTACT_OPEN                 = 1550  # 0 - Close, 1 - Open
    
    MOTION_SENSOR_ENABLE_LED            = 1607
    MOTION_SENSOR_LAST_EVENT_MS         = 1605
    MOTION_SENSOR_PIR_SENSITIVITY       = 1609
    TEST_1                              = 1608
# 
#     // Set only params?
#     PUSH_MSG_MODE = 1252,                       // 0 to ???
# }
# 


EXCLUDED_ROOT_PROPERTY = ['station_conn', 'member', 'permission', 'params', 'status']