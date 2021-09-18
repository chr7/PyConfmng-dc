import collections
import os
import weakref
import pytest
import csv

class ConfVar(dict):
    """ Represents a dictionary of configuration variables"""
    def __getattr__(self, key):
        if key[:2] == "__":
            # yaml calls it with key '__getstate__'
            return super().__getattr__(key)
        return super().__getitem__(key)

    def __setattr__(self, key, value):
        return super().__setitem__(key, value)

class ConfigManager(collections.OrderedDict):
    def __getattr__(self, key):
        return weakref.proxy(super().__getitem__(key))

    def __delattr__(self, key):
        return super().__delitem__(key)

    def add_category(self, *categories):
        """
        >>> settings = ConfigManager()
        >>> settings
        ConfigManager()
        >>> ds, cs = settings.add_category('default_settings', 'current_settings')
        >>> ds
        <weakproxy at 0x... to ConfVar at 0x...>
        >>> cs
        <weakproxy at 0x... to ConfVar at 0x...>
        >>> settings
        ConfigManager([('default_settings', {}), ('current_settings', {})])
        """
        ret = tuple()
        for category in categories:
            self[category] = ConfVar()
            ret = ret + tuple((weakref.proxy(self[category]),))
        if len(categories) == 1:
            ret, = ret
        return ret

    def set_values(self, var, *values):
        """
        >>> settings = ConfigManager()
        >>> settings
        ConfigManager()
        >>> ds, cs = settings.add_category('default_settings', 'current_settings')
        >>> ds
        <weakproxy at 0x... to ConfVar at 0x...>
        >>> cs
        <weakproxy at 0x... to ConfVar at 0x...>
        >>> settings
        ConfigManager([('default_settings', {}), ('current_settings', {})])
        >>> settings.set_values('delimiter', ',', ';')
        >>> settings
        ConfigManager([('default_settings', {'delimiter': ','}), ('current_settings', {'delimiter': ';'})])
        """
        if len(values) == 0 or len(values) > len(self.keys()):
            raise TypeError("Number of values is either 0 or exceeds the number of categories.")
        for category, value in (zip(self.keys(), values)):
            self[category][var] = value

    def get_values(self, var):
        values = list()
        for category in self.keys():
            values.append(self[category].get(var, None))
        return values
            
def dump_keyval(filename, dictionary):
    with open(filename, "w") as fh:
        writer = csv.writer(fh, delimiter='=', quoting=csv.QUOTE_MINIMAL)
        for key, val in dictionary.items():
            if isinstance(val, str):
                val = "'{}'".format(val)
            item = (key, val)
            writer.writerow(item)
        fh.close()

def load_keyval(filename, dictionary):
    with open(filename) as fh:
        exec(fh.read(), None, dictionary)

def test_attr_access():
    cfgmng = ConfigManager()
    cs = cfgmng.add_category('current_settings')
    cs.log = False
    #print(cfgmng)
    assert str(cfgmng) == "ConfigManager([('current_settings', {'log': False})])"

class TestConfVar:
    def test_access(self):
        confvar = ConfVar()
        assert str(confvar) == "{}"
        confvar.log = False
        assert str(confvar) == "{'log': False}"
        assert confvar.log == False
        confvar['log_level'] = 0
        assert str(confvar) == "{'log': False, 'log_level': 0}"
        assert confvar['log_level'] == 0

class TestConfigManager:
    @pytest.fixture
    def cfgmng(self):
        cfgmng = ConfigManager()
        cfgmng.add_category('default_settings', 'current_settings')
        return cfgmng

    @pytest.fixture
    def filled_cfgmng(self):
        cfgmng = ConfigManager()
        cfgmng.add_category('current_settings', 'default_settings', 'description')
        cfgmng.set_values('log', True, False, 'Enable/disable logging')
        cfgmng.set_values('log_level', 5, 1, 'Logging verbosity')
        cfgmng.set_values('log_file', 'my.log')
        return cfgmng

    def test_instantiate(self):
        cfgmng = ConfigManager()
        assert str(cfgmng) == "ConfigManager()"
        ds, cs = cfgmng.add_category('default_settings', 'current_settings')
        assert str(cfgmng) == "ConfigManager([('default_settings', {}), ('current_settings', {})])"
        assert str(ds) == "{}"
        assert str(cs) == "{}"

    def test_attr_access(self, cfgmng):
        ds = cfgmng.default_settings
        assert str(ds) == "{}"
        cs = cfgmng['current_settings']
        assert str(cs) == "{}"
        ds.log = False
        cs.log = True
        assert str(cfgmng) == "ConfigManager([('default_settings', {'log': False}), ('current_settings', {'log': True})])"
        assert cs.log == True

    def test_add_one_category(self, cfgmng):
        cfgmng.add_category('description')
        assert str(cfgmng) == "ConfigManager([('default_settings', {}), ('current_settings', {}), ('description', {})])"

    def test_add_two_categories(self, cfgmng):
        cfgmng.add_category('description', 'unit')
        assert str(cfgmng) == "ConfigManager([('default_settings', {}), ('current_settings', {}), ('description', {}), ('unit', {})])"

    def test_set_values(self, cfgmng):
        cfgmng.set_values('log_file', 'default.log', 'my.log')
        assert str(cfgmng) == "ConfigManager([('default_settings', {'log_file': 'default.log'}), ('current_settings', {'log_file': 'my.log'})])"

        cfgmng.set_values('log_file', 'None', 'foo.log')
        assert str(cfgmng) == "ConfigManager([('default_settings', {'log_file': 'None'}), ('current_settings', {'log_file': 'foo.log'})])"

        cfgmng.set_values('log', 'False')
        assert str(cfgmng) == "ConfigManager([('default_settings', {'log_file': 'None', 'log': 'False'}), ('current_settings', {'log_file': 'foo.log'})])"

        with pytest.raises(TypeError):
            cfgmng.set_values('log_level')

        with pytest.raises(TypeError):
            cfgmng.set_values('log_file', 'foo.log', 'my_log.log', 'Name of the log file')

    def test_get_values(self, filled_cfgmng):
        fc = filled_cfgmng
        a, b, c = fc.get_values('log')
        assert a == True
        assert b == False
        assert c == "Enable/disable logging"

        a, b, c = fc.get_values('log_file')
        assert a == "my.log"
        assert b == None
        assert c == None

    def test_del_category(self, filled_cfgmng):
        fc = filled_cfgmng
        cs = filled_cfgmng.current_settings
        assert cs.log == True
        del filled_cfgmng['current_settings']
        assert str(filled_cfgmng) == "ConfigManager([('default_settings', {'log': False, 'log_level': 1}), ('description', {'log': 'Enable/disable logging', 'log_level': 'Logging verbosity'})])"

        with pytest.raises(ReferenceError):
            cs.log

        with pytest.raises(ReferenceError):
            cs['log']

class TestExportImport:
    @pytest.fixture
    def filled_cfgmng(self):
        cfgmng = ConfigManager()
        cfgmng.add_category('current_settings', 'default_settings', 'description')
        cfgmng.set_values('log', True, False, 'Enable/disable logging')
        cfgmng.set_values('log_level', 5, 1, 'Logging verbosity')
        cfgmng.set_values('log_file', 'my.log')
        return cfgmng

    @pytest.fixture
    def empty_cfgmng(self):
        cfgmng = ConfigManager()
        cfgmng.add_category('default_settings', 'current_settings')
        return cfgmng

    def test_yaml_export(self, filled_cfgmng):
        import yaml
        dump = """!!python/object/apply:{0}.ConfigManager
dictitems:
  current_settings: !!python/object/new:{0}.ConfVar
    dictitems:
      log: true
      log_file: my.log
      log_level: 5
  default_settings: !!python/object/new:{0}.ConfVar
    dictitems:
      log: false
      log_level: 1
  description: !!python/object/new:{0}.ConfVar
    dictitems:
      log: Enable/disable logging
      log_level: Logging verbosity
""".format(__name__)
        assert yaml.dump(filled_cfgmng) == dump

    def test_json_export(self, filled_cfgmng):
        import json
        dump = """{"current_settings": {"log": true, "log_level": 5, "log_file": "my.log"}, "default_settings": {"log": false, "log_level": 1}, "description": {"log": "Enable/disable logging", "log_level": "Logging verbosity"}}"""
        assert json.dumps(filled_cfgmng) == dump

    def test_keyval_export(self, filled_cfgmng, tmp_path):
        filename = os.path.join(tmp_path,'current_settings.conf')
        dump_keyval(filename, filled_cfgmng.current_settings)
        with open(filename) as fh:
            data = ""
            for line in fh:
                data = data + line
        assert data == """log=True
log_level=5
log_file='my.log'
"""

    @pytest.fixture(scope="session")
    def conf_file(self, tmp_path_factory):
        filename = os.path.join(tmp_path_factory.mktemp("data"), 'current_settings.conf')
        with open(filename, "w") as fh:
            data = """log=True
log_level=5
log_file='my.log'
"""
            fh.write(data)
            fh.close()
            return filename

    def test_keyval_import(self, empty_cfgmng, filled_cfgmng, conf_file):
        assert str(empty_cfgmng) == "ConfigManager([('default_settings', {}), ('current_settings', {})])"
        load_keyval(conf_file, empty_cfgmng.current_settings)
        assert str(empty_cfgmng) == "ConfigManager([('default_settings', {}), ('current_settings', {'log': True, 'log_level': 5, 'log_file': 'my.log'})])"

#-- MAIN ------------------------------------------------------------------------------------------
if __name__ == "__main__":
    pass
