from uefiSecurityApi.const import PARAM_TYPE, DEVICE_TYPE, DEVICE_STATE, MOTION_DETECTION_COOLDOWN_MS
import logging
from datetime import datetime, timedelta

class Device(object):
    deviceType= DEVICE_TYPE(-1)
    def __init__(self, api):
        self.api = api
        self._logger  = logging.getLogger(__name__)
        self._attribute = {}
        self._notRecognizedAttribute = {}
    
    def __getattr__(self, key):
        try:
            data = self._attribute.get(PARAM_TYPE(key), None)
            if(data is None):
                raise Exception('no data')
            return data
        except:
            return self.__dict__.get(key)

    def __setattr__(self, key, value):
        try:
            self._attribute[PARAM_TYPE(key)] = value
        except:
            self.__dict__[key] = value

    def __str__(self):
        output = ''
        output += '%s\t(type:%s, model:%s, serial:%s)\t %s \n' % (self.name, self._type, self.model, self.serial, self.status)
        output += '['
        for attributeName, attributeValue in self._attribute.items():
            output += '%s: %s, ' %(attributeName, attributeValue)
        output = output[:-2]
        output += ']'
        return output

    # def __repr__(self):
    #     return self.__str__()

    def init(self, apiDict):
        self.serial = apiDict['device_sn']
        self.name = apiDict['device_name']
        self.model = apiDict['device_model']
        self.status = DEVICE_STATE(apiDict['status'])
        self._type = DEVICE_TYPE(apiDict['device_type'])
        for attribute in apiDict['params']:
            try:
                self._attribute[PARAM_TYPE(attribute['param_type'])] = attribute['param_value']
            except:
                self._notRecognizedAttribute[attribute['param_type']] = attribute['param_value']
                self._logger.debug('%s: attribute type \'%s\' is not recognized: %s' % (self.model, attribute['param_type'], attribute['param_value']))
        
        for key in apiDict.keys():
            if key not in ['station_conn', 'member', 'permission', 'params']:
                self.__dict__[key] = apiDict[key]
        # self.deviceType = DEVICE_TYPE(apiDict['device_type'])
    
    def update(self, apiDict):
        for key in apiDict.keys():
            if key not in ['station_conn', 'member', 'permission', 'params']:
                if(key in self.__dict__ and self.__dict__[key] != apiDict[key]):
                    self._logger.info('%s updated %s: %s -> %s' %(self.name, key, self.__dict__[key], apiDict[key]))
                    self.__dict__[key] = apiDict[key]
        for attribute in apiDict['params']:
            try:
                if(PARAM_TYPE(attribute['param_type']) in self._attribute and self._attribute[PARAM_TYPE(attribute['param_type'])] != attribute['param_value']):
                    self._logger.info('%s updated %s: %s -> %s' %(self.name, PARAM_TYPE(attribute['param_type']), self._attribute[PARAM_TYPE(attribute['param_type'])], attribute['param_value']))
                    self._attribute[PARAM_TYPE(attribute['param_type'])] = attribute['param_value']
                elif(PARAM_TYPE(attribute['param_type']) not in self._attribute):
                    self._attribute[PARAM_TYPE(attribute['param_type'])] = attribute['param_value']
                    self._logger.info('%s new attribute %s: %s' % (self.name, PARAM_TYPE(attribute['param_type']), attribute['param_value']))
            except:
                if(attribute['param_type'] in self._notRecognizedAttribute and self._notRecognizedAttribute[attribute['param_type']] != attribute['param_value']):
                    self._logger.info('%s updated %s: %s -> %s' %(self.name, attribute['param_type'], self._notRecognizedAttribute[attribute['param_type']], attribute['param_value']))
                    self._notRecognizedAttribute[attribute['param_type']] = attribute['param_value']
                elif(attribute['param_type'] not in self._notRecognizedAttribute):
                    self._notRecognizedAttribute[attribute['param_type']] = attribute['param_value']
                    self._logger.info('%s new attribute %s: %s' % (self.name, attribute['param_type'], attribute['param_value']))
# 
    @classmethod
    def fromType(cls, api, deviceType: DEVICE_TYPE):
        if cls.__name__ == 'Device':
            for subclass in cls.__subclasses__():
                if subclass.deviceType == deviceType:
                    return subclass(api)
            return Device(api)
        else:
            return Device.fromType(api, deviceType)
        pass


class Station(Device):
    deviceType= DEVICE_TYPE.STATION

    def init(self, apiDict):
        self.serial = apiDict['station_sn']
        self.name = apiDict['station_name']
        self.model = apiDict['station_model']
        self.status = DEVICE_STATE(apiDict['status'])
        self._type = Station.deviceType
        for attribute in apiDict['params']:
            try:
                self._attribute[PARAM_TYPE(attribute['param_type'])] = attribute['param_value']
            except:
                self._notRecognizedAttribute[attribute['param_type']] = attribute['param_value']
                self._logger.debug('%s: attribute type \'%s\' is not recognized: %s' % (self.model, attribute['param_type'], attribute['param_value']))
        # self.deviceType = DEVICE_TYPE(apiDict['device_type'])


class MotionSensor(Device):
    deviceType = DEVICE_TYPE.MOTION_SENSOR

    @property
    def motionDetected(self):
        lowerWindowLimit = datetime.now()-timedelta(milliseconds=MOTION_DETECTION_COOLDOWN_MS)
        return  lowerWindowLimit <= datetime.fromtimestamp(self.update_time)
