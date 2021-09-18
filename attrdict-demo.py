import pdb

class Setting(dict):
    def __init__(self, value=None, default=None):
        self.value = value
        self.default = default
        
    def __getattr__(self, item):
        print('__getattr__: '+item)
        ret = self.__dict__[item]
        return ret

    def __getattribute__(self, item):
        print('__getattribute__: '+item)
        ret = super().__getattribute__(item)
        if isinstance(ret, Setting):
            return ret.value
        return ret

class Settings():
    def __init__(self):
        self.save = Setting(False, True)

    def __getitem__(self, item):
        print('__getitem__: '+item)
        split = item.split('.', 1)
        pdb.set_trace()
        if len(split) ==1:
            return self.__dict__[item]
        else:
            return self.__dict__[split[0]][split[1]]

    def __setattr__(self, attr, value):
        self.__dict__[attr] = value
        
    def __getattr__(self, item):
        print('__getattr__: '+item)
        ret = self.__dict__[item]
        return ret

    def __get__(self, item):
        pdb.set_trace()
        
    def __getattribute__(self, item):
        print('__getattribute__: '+item)
        ret = super().__getattribute__(item)
        #if isinstance(ret, Setting):
        #    return ret.value
        return ret
        
# what I want to have:
# >>> s = Settings()
# >>> s.log = {'value':True, 'default':False, 'description':'Enable/disable logging'}
# even better:
# >>> s.log = (True, False, 'Enable/disable logging')
# alternative:
# >>> s.log = Setting(True, False, 'Enable/disable logging')
# >>> s.log
# True
# >>> s.log.default
# False

s = Settings()
print(s.save)
print(s.save.default)

s2 = Setting(True, False)
print(s2)
