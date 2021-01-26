from uefiSecurityApi.const import TWO_FACTOR_AUTH_METHODS, API_BASE_URL, API_HEADERS, RESPONSE_ERROR_CODE, ENDPOINT_LOGIN,ENDPOINT_DEVICE_LIST, DEVICE_TYPE, ENDPOINT_STATION_LIST

import logging, requests, json, copy
from datetime import datetime, timedelta #, time as dtTime
from uefiSecurityApi.model import Device
# import time

_LOGGER = logging.getLogger(__name__)
class Api():
    def __init__(self, username=None, password=None, token=None, domain=API_BASE_URL, token_expire_at=None, preferred2FAMethod=TWO_FACTOR_AUTH_METHODS.EMAIL):
        self._username =username
        self._password = password
        self._preferred2FAMethod = preferred2FAMethod
        self._token = token
        self._tokenExpiration = None if token_expire_at is None else datetime.fromtimestamp(token_expire_at)
        self._refreshToken = None
        self.domain = domain
        self.headers = API_HEADERS
        self._LOGGER = logging.getLogger(__name__)
        self.devices = {}
        self.stations = {}
        # self.headers['timezone'] = 
        #    dtTime(dtTime.fromisoformat(time.strptime(time.localtime(), '%HH:%MM'))) - dtTime(dtTime.fromisoformat(time.strptime(time.gmtime(), '%HH:%MM')))
    
    async def authenticate(self):

        if(self._token is None or self._tokenExpiration > datetime.now()):
            response = await self._request('POST', ENDPOINT_LOGIN, {
                'email': self._username,
                'password': self._password
            }, self.headers)
            if(response.status_code != 200):
                self._LOGGER.error('Unexpected response code: %s, on url: %s' % response.status_code, response.request.url)
                raise LoginException('Unexpected response code: %s, on url: %s' % response.status_code, response.request.url)
            dataresult = response.json()
            self._LOGGER.debug('login response: %s' % dataresult)
            # self._LOGGER.debug('%s, %s' % (type(dataresult['code']), dataresult['code']))
            if(RESPONSE_ERROR_CODE(dataresult['code']) == RESPONSE_ERROR_CODE.WHATEVER_ERROR):
                self._token = dataresult['data']['auth_token']
                self._tokenExpiration = datetime.fromtimestamp(dataresult['data']['token_expires_at'])
                if('domain' in dataresult['data'] and dataresult['data']['domain'] != '' and dataresult['data']['domain'] != self.domain):
                    self._token = None
                    self._tokenExpiration = None
                    self.domain = dataresult['data']['domain']
                    self._LOGGER.info('Switching to new domain: %s', self.domain)
                    return await self.authenticate()

                self._LOGGER.debug('Token: %s' %self._token)
                self._LOGGER.debug('Token expire at: %s' % self._tokenExpiration)
                return 'OK'
            elif(RESPONSE_ERROR_CODE(dataresult['code']) == RESPONSE_ERROR_CODE.NEED_VERIFY_CODE):
                self._LOGGER.info('need two factor authentication. Send verification code...')
                #dataresult['data']
                self._token = dataresult['data']['auth_token']
                self._tokenExpiration = datetime.fromtimestamp(dataresult['data']['token_expires_at'])
                self._LOGGER.debug('Token: %s' %self._token)
                self._LOGGER.debug('Token expire at: %s' % self._tokenExpiration)

                await self.send_verify_code()
                return "send_verify_code"
            else:
                message = 'Unexpected API response code %s: %s (%s)' % (dataresult['code'], dataresult['msg'], response.request.url)
                self._LOGGER.error(message)
                raise LoginException(message)
        else:
            return 'OK'
        pass

    async def update(self, device_sn=None):
        if(device_sn is None):
            await self.get_stations()
            await self.get_devices()
        else:
            await self.get_devices(device_sn)


    async def get_devices(self, device_sn=None):
        data = {}
        if(device_sn is not None):
            data['device_sn'] = device_sn
        response = await self._request('POST', ENDPOINT_DEVICE_LIST, data, self.headers)
        if(response.status_code != 200):
            self._LOGGER.error('Unexpected response code: %s, on url: %s' % (response.status_code, response.request.url))
            raise LoginException('Unexpected response code: %s, on url: %s' % (response.status_code, response.request.url))
        dataresult = response.json()
        self._LOGGER.debug('get_devices response: %s' % dataresult)
        if(RESPONSE_ERROR_CODE(dataresult['code']) != RESPONSE_ERROR_CODE.WHATEVER_ERROR):
            message = 'Unexpected API response code %s: %s' % (dataresult['code'], dataresult['msg'])
            self._LOGGER.error(message)
            raise ApiException(message)
        for device in dataresult['data']:
            try:
                deviceType = DEVICE_TYPE(device['device_type'])
                if(device['device_sn'] not in self.devices):
                    self.devices[device['device_sn']] = Device.fromType(self, deviceType)
                    self.devices[device['device_sn']].init(device)
                else:
                    self.devices[device['device_sn']].update(device)
            except Exception as e:
                self._LOGGER.exception(e)
        return self.devices

    async def get_stations(self):
        response = await self._request('POST', ENDPOINT_STATION_LIST, {}, self.headers)
        if(response.status_code != 200):
            self._LOGGER.error('Unexpected response code: %s, on url: %s' % (response.status_code, response.request.url))
            raise LoginException('Unexpected response code: %s, on url: %s' % (response.status_code, response.request.url))
        dataresult = response.json()
        self._LOGGER.debug('get_stations response: %s' % dataresult)
        if(RESPONSE_ERROR_CODE(dataresult['code']) != RESPONSE_ERROR_CODE.WHATEVER_ERROR):
            message = 'Unexpected API response code %s: %s' % (dataresult['code'], dataresult['msg'])
            self._LOGGER.error(message)
            raise ApiException(message)
        for device in dataresult['data']:
            try:
                deviceType = DEVICE_TYPE(device['device_type'])
                self.stations[device['station_sn']] = Device.fromType(self, deviceType)
                self.stations[device['station_sn']].init(device)
            except Exception as e:
                self._LOGGER.exception(e)
        return self.stations

    async def get_device(self, deviceId):
        pass

    async def refresh_token(self):
        pass

    async def invalidate_token(self):
        self._token = None
        self._refreshToken = None
        self._tokenExpiration = None
        pass

    async def send_verify_code(self):
        response = await self._request('POST', 'sms/send/verify_code', {
            'message_type': self._preferred2FAMethod
        }, self.headers)
        if(response.status_code != 200):
            self._LOGGER.error('Unexpected response code: %s, on url: %s' % response.status_code, response.request.url)
            raise ApiException('Unexpected response code: %s, on url: %s' % response.status_code, response.request.url)
        dataresult = response.json()
        self._LOGGER.debug('login response: %s' % dataresult)
        if(RESPONSE_ERROR_CODE(dataresult['code']) != RESPONSE_ERROR_CODE.WHATEVER_ERROR):
            message = 'Unexpected API response code %s: %s' % (dataresult['code'], dataresult['msg'])
            self._LOGGER.error(message)
            raise ApiException(message)
        return 'OK'

    @property
    def connected(self):
        return self._token != None
    
    @property
    def base_url(self):
        return ('https://%s/v1' % self.domain)


    async def _request(self, method, url, data, headers={}) -> requests.Response:
        call = None
        if(method == 'GET'):
            call = requests.get
        elif(method == 'POST'):
            call = requests.post
        else:
            raise ApiException('Unsupported operation: %s' % method)
        url = self.base_url + url
        
        newHeaders = copy.copy(headers)
        if(url != ENDPOINT_LOGIN):
            newHeaders['X-Auth-Token'] = self._token
        
        
        self._LOGGER.debug('method: %s' % method)
        self._LOGGER.debug('url: %s' % url)
        self._LOGGER.debug('data: %s' % data)
        self._LOGGER.debug('headers: %s' % newHeaders)
        response = call(url, json=data, headers=newHeaders)
        return response



class ApiException(Exception):
    pass

class LoginException(ApiException):
    pass