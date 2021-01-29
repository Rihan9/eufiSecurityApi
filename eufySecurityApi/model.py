from eufySecurityApi.const import PARAM_TYPE, DEVICE_TYPE, DEVICE_STATE, MOTION_DETECTION_COOLDOWN_MS, EXCLUDED_ROOT_PROPERTY
import logging, traceback, asyncio
from datetime import datetime, timedelta
from eufySecurityApi.utils import getUniqueId

class AttributeWrapper(dict):
    def __init__(self):
        self._internalDict = {}
    def __setitem__(self, key, value):
        if(not isinstance(key, PARAM_TYPE)):
            try:
                key = PARAM_TYPE(key)
            except:
               raise AttributeError('Key is not a PARAM_TYPE value') 
        frameStack = traceback.extract_stack(limit=2)[0]
        if(not(frameStack.name in self.__dir__() and frameStack.filename == __file__)):
            raise AttributeError('Attribute is read only')
        self._internalDict[key] = value

    def __getitem__(self, key):
        if(isinstance(key, PARAM_TYPE)):
            return self._internalDict[key]
        else:
            return self._internalDict[PARAM_TYPE(key)]

    def __setattr__(self, key, value):
        frameStack = traceback.extract_stack(limit=2)[0]
        if(not(frameStack.name in self.__dir__() and frameStack.filename == __file__)):
            raise AttributeError('Attribute is read only')
        else:
            self.__dict__[key] = value

    def __getattr__(self, key):
        raise KeyError('Unhautorized')

class callbackStruct(object):
    def __init__(self, cId, attributes, callback):
        self.cId = cId
        self.attributes = attributes
        self.call = callback

class Device(object):

    deviceType= DEVICE_TYPE(-1)
    def __init__(self, api):
        self.api = api
        self._logger  = logging.getLogger(__name__)
        # self._attribute = {}
        self._notRecognizedAttribute = {}
        self._attribute = AttributeWrapper()
    
    def __setattr__(self, key, value):
        frameStack = traceback.extract_stack(limit=2)[0]
        if(not(frameStack.name in self.__dir__() and frameStack.filename == __file__)):
            raise AttributeError('Device is read only')
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
        self._callbacks = {}
        for attribute in apiDict['params']:
            try:
                self._attribute[PARAM_TYPE(attribute['param_type'])] = attribute['param_value']
            except:
                self._notRecognizedAttribute[attribute['param_type']] = attribute['param_value']
                self._logger.debug('%s: attribute type \'%s\' is not recognized: %s' % (self.model, attribute['param_type'], attribute['param_value']))
        
        for key in apiDict.keys():
            if key not in EXCLUDED_ROOT_PROPERTY:
                try:
                    self._attribute[PARAM_TYPE(key)] = apiDict[key]
                except:
                    self.__dict__[key] = apiDict[key]
                    pass
        # self.deviceType = DEVICE_TYPE(apiDict['device_type'])
    
    def update(self, apiDict):
        updatedAttributes = []
        for key in apiDict.keys():
            if key not in EXCLUDED_ROOT_PROPERTY:
                if(key in self.__dict__ and self.__dict__[key] != apiDict[key]):
                    self._logger.info('%s updated %s: %s -> %s' %(self.name, key, self.__dict__[key], apiDict[key]))
                    self.__dict__[key] = apiDict[key]
                try:
                    if(PARAM_TYPE(key) in self._attribute and self._attribute[PARAM_TYPE(key)] != apiDict[key]):
                        self._logger.info('%s updated %s: %s -> %s' %(self.name, PARAM_TYPE(key), self._attribute[PARAM_TYPE(key)], apiDict[key]))
                        updatedAttributes.append((PARAM_TYPE(key), self._attribute[PARAM_TYPE(key)], apiDict[key]))
                        self._attribute[PARAM_TYPE(key)] = apiDict[key]
                    elif(PARAM_TYPE(key) not in self._attribute):
                        self._logger.info('%s new attribute %s: %s -> %s' %(self.name, PARAM_TYPE(key), self._attribute[PARAM_TYPE(key)], apiDict[key]))
                        updatedAttributes.append((PARAM_TYPE(key), self._attribute[PARAM_TYPE(key)], apiDict[key]))
                        self._attribute[PARAM_TYPE(key)] = apiDict[key]
                except:
                    pass
                
        for attribute in apiDict['params']:
            try:
                if(PARAM_TYPE(attribute['param_type']) in self._attribute and self._attribute[PARAM_TYPE(attribute['param_type'])] != attribute['param_value']):
                    updatedAttributes.append((PARAM_TYPE(attribute['param_type']), self._attribute[PARAM_TYPE(attribute['param_type'])], attribute['param_value']))
                    self._logger.info('%s updated %s: %s -> %s' %(self.name, PARAM_TYPE(attribute['param_type']), self._attribute[PARAM_TYPE(attribute['param_type'])], attribute['param_value']))
                    self._attribute[PARAM_TYPE(attribute['param_type'])] = attribute['param_value']
                elif(PARAM_TYPE(attribute['param_type']) not in self._attribute):
                    updatedAttributes.append((PARAM_TYPE(attribute['param_type']), self._attribute[PARAM_TYPE(attribute['param_type'])], attribute['param_value']))
                    self._attribute[PARAM_TYPE(attribute['param_type'])] = attribute['param_value']
                    self._logger.info('%s new attribute %s: %s' % (self.name, PARAM_TYPE(attribute['param_type']), attribute['param_value']))
            except:
                if(attribute['param_type'] in self._notRecognizedAttribute and self._notRecognizedAttribute[attribute['param_type']] != attribute['param_value']):
                    self._logger.info('%s updated %s: %s -> %s' %(self.name, attribute['param_type'], self._notRecognizedAttribute[attribute['param_type']], attribute['param_value']))
                    self._notRecognizedAttribute[attribute['param_type']] = attribute['param_value']
                elif(attribute['param_type'] not in self._notRecognizedAttribute):
                    self._notRecognizedAttribute[attribute['param_type']] = attribute['param_value']
                    self._logger.info('%s new attribute %s: %s' % (self.name, attribute['param_type'], attribute['param_value']))

        if(len(updatedAttributes) > 0):
            self._call(updatedAttributes)
    
    def _call(self, updatedAttributes):
        for cId in self._callbacks:
            data = []
            for attributeTuple in updatedAttributes:
                if (attributeTuple[0] in self._callbacks[cId].attributes or len(self._callbacks[cId].attributes) == 0):
                    data.append(attributeTuple)
            if(len(data) > 0):
                asyncio.create_task(self._callbacks[cId].call(data))
        pass
    
    def subscribe(self, attributes: [PARAM_TYPE], callback):
        cId = getUniqueId(callback)
        if(cId in self._callbacks):
            self._callbacks[cId].attributes = list(set(self._callbacks[cId].attributes + attributes))
        else:
            self._callbacks[cId] = callbackStruct(cId, attributes, callback)
        return 'OK'
    
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

    @property
    def attribute(self):
        return self._attribute

    @property
    def state(self):
        return self._attribute[PARAM_TYPE.PROP_STATUS].name.replace('_', ' ').lower()

    @property
    def hasbattery(self):
        return PARAM_TYPE.BATTERY_LEVEL in self._attribute

    @property
    def battery_level(self):
        return self._attribute[PARAM_TYPE.BATTERY_LEVEL] if self.hasbattery else None
    
    @property
    def isCamera(self):
        return self._type in [
            DEVICE_TYPE.CAMERA_E,
            DEVICE_TYPE.CAMERA,
            DEVICE_TYPE.CAMERA2_PRO,
            DEVICE_TYPE.CAMERA2C_PRO,
            DEVICE_TYPE.CAMERA2C,
            DEVICE_TYPE.CAMERA2,
            DEVICE_TYPE.INDOOR_CAMERA_1080,
            DEVICE_TYPE.INDOOR_PT_CAMERA_1080,
            DEVICE_TYPE.SOLO_CAMERA_PRO,
            DEVICE_TYPE.SOLO_CAMERA,
            DEVICE_TYPE.DOORBELL,
            DEVICE_TYPE.BATTERY_DOORBELL,
            DEVICE_TYPE.BATTERY_DOORBELL_2,
            DEVICE_TYPE.FLOODLIGHT
        ]
    
    @property
    def isMotionSensor(self):
        return self._type in [
            DEVICE_TYPE.MOTION_SENSOR
        ] or self.isCamera
    
    @property
    def isDoorLock(self):
        return self._type in [
            DEVICE_TYPE.LOCK_BASIC,
            DEVICE_TYPE.LOCK_ADVANCED,
            DEVICE_TYPE.LOCK_BASIC_NO_FINGER,
            DEVICE_TYPE.LOCK_ADVANCED_NO_FINGER
        ]


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
        for key in apiDict.keys():
            if key not in EXCLUDED_ROOT_PROPERTY:
                try:
                    self._attribute[PARAM_TYPE(key)] = apiDict[key]
                except:
                    self.__dict__[key] = apiDict[key]
                    pass
        # self.deviceType = DEVICE_TYPE(apiDict['device_type'])


class MotionSensor(Device):
    deviceType = DEVICE_TYPE.MOTION_SENSOR

    @property
    def motionDetected(self):
        lowerWindowLimit = datetime.now()-timedelta(milliseconds=MOTION_DETECTION_COOLDOWN_MS)
        return  lowerWindowLimit <= datetime.fromtimestamp(self._attribute[PARAM_TYPE.PROP_UPDATE_TIME])

    @property
    def state(self):
        if(self.status == DEVICE_STATE.ONLINE):
            return 'motion detected' if self.motionDetected else 'no motion detected'
        else:
            return self._attribute[PARAM_TYPE.PROP_STATUS].name.replace('_', ' ').lower()