import collections
import weakref
import csv

#--------------------------------------------------------------------------------------------------
class ConfVar(dict):
    """ Represents a dictionary of configuration variables"""

    #----------------------------------------------------------------------------------------------
    def __getattr__(self, key):
        if key[:2] == "__":
            # yaml calls it with key '__getstate__'
            return super().__getattr__(key)
        return super().__getitem__(key)

    #----------------------------------------------------------------------------------------------
    def __setattr__(self, key, value):
        return super().__setitem__(key, value)

#--------------------------------------------------------------------------------------------------
class ConfigManager(collections.OrderedDict):

    #----------------------------------------------------------------------------------------------
    def __getattr__(self, key):
        return weakref.proxy(super().__getitem__(key))

    #----------------------------------------------------------------------------------------------
    def __delattr__(self, key):
        return super().__delitem__(key)

    #----------------------------------------------------------------------------------------------
    def add_category(self, *categories):
        """
        >>> confmng = ConfigManager()
        >>> confmng
        ConfigManager()
        >>> ds, cs = confmng.add_category('default_settings', 'current_settings')
        >>> ds
        <weakproxy at 0x... to ConfVar at 0x...>
        >>> cs
        <weakproxy at 0x... to ConfVar at 0x...>
        >>> confmng
        ConfigManager([('default_settings', {}), ('current_settings', {})])
        """
        ret = tuple()
        for category in categories:
            self[category] = ConfVar()
            ret = ret + tuple((weakref.proxy(self[category]),))
        if len(categories) == 1:
            ret, = ret
        return ret

    #----------------------------------------------------------------------------------------------
    def copy_category(self, from_category, to_category, overwrite=False):
        if overwrite:
            merged_cat = {**self[to_category], **self[from_category]}
            self[to_category] = merged_cat
        else:
            for key, val in self[from_category].items():
                if key in self[to_category]:
                    continue
                else:
                    self[to_category][key] = val
        return self[to_category]

    #----------------------------------------------------------------------------------------------
    def set_values(self, var, *values):
        """
        >>> confmng = ConfigManager()
        >>> confmng
        ConfigManager()
        >>> cs, ds = confmng.add_category('current_settings', 'default_settings')
        >>> cs
        <weakproxy at 0x... to ConfVar at 0x...>
        >>> ds
        <weakproxy at 0x... to ConfVar at 0x...>
        >>> confmng
        ConfigManager([('current_settings', {}), ('default_settings', {})])
        >>> confmng.set_values('delimiter', None, ';')
        >>> confmng
        ConfigManager([('current_settings', {}), ('default_settings', {'delimiter': ';'})])
        """
        if len(values) == 0 or len(values) > len(self.keys()):
            raise TypeError("Number of values is either 0 or exceeds the number of categories.")
        for category, value in (zip(self.keys(), values)):
            if value != None:
                self[category][var] = value

    #----------------------------------------------------------------------------------------------
    def get_values(self, var):
        values = list()
        for category in self.keys():
            values.append(self[category].get(var, None))
        return values

    #----------------------------------------------------------------------------------------------
    def dump(self, cat_file_names={}):
        filenames = dict()
        for category, confvars in self.items():
            if category in cat_file_names:
                filename = cat_file_names[category]
            else:
                filename = category + '.conf'
            filenames[category] = filename
            dump_keyval(filename, confvars)
        return filenames
            
    #----------------------------------------------------------------------------------------------
    def load(self, cat_file_name):
        ret = tuple()
        for category, filename in cat_file_name.items():
            self[category] = load_keyval(filename, ConfVar())
            ret = ret + tuple((weakref.proxy(self[category]),))
        if len(cat_file_name) == 1:
            # don't return a tuple if there is just one value
            ret, = ret
        return ret

    #----------------------------------------------------------------------------------------------
    def dump_into_one(self, filename):
        for category, confvars in self.items():
            with open(filename, mode='a') as fh:
                fh.write('\r\n['+category+']\r\n')
            dump_keyval(filename, confvars, 'a')

    #----------------------------------------------------------------------------------------------
    def dump_category(self, filename, category):
        dump_keyval(filename, category)

#--------------------------------------------------------------------------------------------------
def dump_keyval(filename, dictionary, mode='w'):
    with open(filename, mode=mode) as fh:
        writer = csv.writer(fh, delimiter='=', quoting=csv.QUOTE_MINIMAL)
        for key, val in dictionary.items():
            if isinstance(val, str):
                val = "'{}'".format(val)
            item = (key, val)
            writer.writerow(item)
        fh.close()

#--------------------------------------------------------------------------------------------------
def load_keyval(filename, dictionary=dict()):
    with open(filename) as fh:
        exec(fh.read(), None, dictionary)
    return dictionary

#-- MAIN ------------------------------------------------------------------------------------------
if __name__ == "__main__":
    pass
