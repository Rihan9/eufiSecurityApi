from enum import Enum

class TWO_FACTOR_AUTH_METHODS(Enum):
    SMS = 0,
    PUSH = 1,
    EMAIL = 2

API_BASE_URL = 'mysecurity.eufylife.com/api'
ENDPOINT_LOGIN = '/passport/login'
ENDPOINT_DEVICE_LIST = '/app/get_devs_list'

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
    VERIFY_CODE_ERROR       = 26050
    VERIFY_CODE_EXPIRED     = 26051
    NEED_VERIFY_CODE        = 26052
    VERIFY_CODE_MAX         = 26053
    VERIFY_CODE_NONE_MATCH  = 26054
    VERIFY_PASSWORD_ERROR   = 26055
    PHONE_NONE_SUPPORT      = 26058
    TOO_MANY_LOGIN_ATTEMPTS = 100028