import pdb

# this class represents a single setting
class Setting():
    def __init__(self, name, val, default=None):
        self.name = name
        self.val = val
        self.default= default

    def __call__(self):
        # ok but you have to add brackets to the instance
        return self.val

    def __repr__(self):
        # unfortuantely this function has to return a string
        # thus this doesn't work:
        # return self.val
        return "Setting({}, {}, {})".\
               format(self.name, self.val, self.default)
    
    #def __str__(self):
    #    return "name: {}; val: {}; default: {}".\
    #           format(self.name, self.val, self.default)

settings = dict()
settings['empty_ls'] = Setting('empty_ls', 31)

class objdict(dict):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, val):
        self[name] = Setting(name, val)

    def __delattr__(self, name):
        del self[name]

class Setting2(dict):
    def __init__(self, val, default=None):
        self['val'] = val
        self['default'] = default
        
    def __getattr__(self, name):
        return self[name]

    def __setattr(self, name, value):
        self[name] = value
        
class objdict2(dict):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, val, default=None):
        self[name] = Setting2(val, default)


objsettings = objdict()
objsettings.empty_ls = 30

mc = Setting('empty_ls', 30)
print(mc())

o2 = objdict2()
o2.empty_ls = 30
