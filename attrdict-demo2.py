import pdb

class Setting():
    def __init__(self, value, default):
        self.value = value
        self.default = default

    def __getitem__(self, item):
        print('Setting::__getitem__: '+item)
        ret = eval('self.'+item)
        return ret

class Settings(dict):

    def __getitem__(self, item):
        print('Settings::__getitem__: '+item)
        split = item.split('.', 1)
        if len(split) == 1:
            try:
                ret = super().__getitem__(item)
            except:
                print('Settings::__getitem__ exception: '+item)
            return ret
        return super().__getitem__(split[0])[split[1]]
           
    def __getattr__(self, item):
        print('Settings::__getattr__: '+item)
        try:
            #ret = self[item].value
            ret = super().__getitem__(item).value
        except:
            print('Settings::__getattr__ exception')
            ret = None
        return ret
       
    def getattribute__(self, item):
        print('Settings::__getattribute__: '+item)
        #ret = super().__getattribute__(item)
        ret = super().__dict__[item]
        return ret
        try:
            ret = super().__getattribute__(item)
            #ret = super().__dict__[item]
        except AttributeError:
            print('Settings::__getattribute__ exception: '+item)
            ret = super().__dict__[item]
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

s = Settings({'log':Setting(True, False)})
print(s.log)
print(s['log.default'])
#pdb.set_trace()
try:
    val = s.log.default
except AttributeError:
    val = s['log.default']
print(val)
