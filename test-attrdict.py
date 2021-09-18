import pdb

class Setting(dict):
    def __init__(self, val=None, default=None):
        self['val'] = val
        self['default'] = default

    def __setattr__(self, name, val):
        if name not in self:
            raise KeyError(name)
        self[name] = val

    def __getattr__(self, name):
        return self[name]

    def __delattr__(self, name):
        raise KeyError("Key can't be deleted: "+name)
        
class Settings(dict):
    def __setattr__(self, name, val):
        if type(val) is Setting:
            self[name] = val
        else:
            raise AttributeError(name)

    def __getattr__(self, name):
        if name not in self:
            self[name] = Setting()
        return self[name]

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise KeyError("Key doesn't exist: "+name)
        
class Settings2(dict):
    def __setattr__(self, name, val):
        if type(val) is dict:
            self[name] = val
        elif name in self:
            self[name]['value'] = val
        else:
            self[name] = {'value': val, 'default':None, 'description':None}

    def __getattr__(self, name):
        pdb.set_trace()
        if name in self:
            attr = self[name]
            if type(attr) is dict:
                return attr['value']
            else:
                return attr
        else:
            raise KeyError("Key doesn't exist: "+name)       

    def __getitem__(self, key):
        pdb.set_trace()
        split = key.split('.', 1)
        if len(split) == 1:
            return dict.__getitem__(self, key)
        return dict.__getitem__(self, split[0])[split[1]]
        
empty_ls = Setting(30, 20)
print(empty_ls)

ss = Settings()
print(ss)

ss.max_ls.val = 40
ss.max_ls.default = 22
print(ss)
print(ss.max_ls)
print(ss.max_ls.val)
print(ss.max_ls.default)

s2 = Settings2()
s2.log = {'value': False, 'default': True, 'description': 'Log value'}

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
