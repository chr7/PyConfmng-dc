from confmng import *
from utils import unindent
import os
import pytest

#--------------------------------------------------------------------------------------------------
def test_attr_access():
    cfgmng = ConfigManager()
    cs = cfgmng.add_category('current_settings')
    cs.log = False
    #print(cfgmng)
    assert str(cfgmng) == "ConfigManager([('current_settings', {'log': False})])"

#--------------------------------------------------------------------------------------------------
class TestConfVar:

    #-----------------------------------------------------------------------------------------------
    def test_access(self):
        confvar = ConfVar()
        assert str(confvar) == "{}"
        confvar.log = False
        assert str(confvar) == "{'log': False}"
        assert confvar.log == False
        confvar['log_level'] = 0
        assert str(confvar) == "{'log': False, 'log_level': 0}"
        assert confvar['log_level'] == 0

#--------------------------------------------------------------------------------------------------
class TestConfigManager:

    #-----------------------------------------------------------------------------------------------
    @pytest.fixture
    def base_cfgmng(self):
        cfgmng = ConfigManager()
        cfgmng.add_category('default_settings', 'current_settings')
        return cfgmng

    #-----------------------------------------------------------------------------------------------
    @pytest.fixture
    def filled_cfgmng(self):
        cfgmng = ConfigManager()
        cfgmng.add_category('current_settings', 'default_settings', 'description')
        cfgmng.set_values('log', True, False, 'Enable/disable logging')
        cfgmng.set_values('log_level', 5, 1, 'Logging verbosity')
        cfgmng.set_values('log_file', 'my.log')
        return cfgmng

    #-----------------------------------------------------------------------------------------------
    def test_instantiate(self):
        cfgmng = ConfigManager()
        assert str(cfgmng) == "ConfigManager()"
        ds, cs = cfgmng.add_category('default_settings', 'current_settings')
        assert str(cfgmng) == "ConfigManager([('default_settings', {}), ('current_settings', {})])"
        assert str(ds) == "{}"
        assert str(cs) == "{}"

    #-----------------------------------------------------------------------------------------------
    def test_attr_access(self, base_cfgmng):
        ds = base_cfgmng.default_settings
        assert str(ds) == "{}"
        cs = base_cfgmng['current_settings']
        assert str(cs) == "{}"
        ds.log = False
        cs.log = True
        assert str(base_cfgmng) == "ConfigManager([('default_settings', {'log': False}), ('current_settings', {'log': True})])"
        assert cs.log == True

    #-----------------------------------------------------------------------------------------------
    def test_add_one_category(self, base_cfgmng):
        base_cfgmng.add_category('description')
        assert str(base_cfgmng) == "ConfigManager([('default_settings', {}), ('current_settings', {}), ('description', {})])"

    #-----------------------------------------------------------------------------------------------
    def test_add_two_categories(self, base_cfgmng):
        base_cfgmng.add_category('description', 'unit')
        assert str(base_cfgmng) == "ConfigManager([('default_settings', {}), ('current_settings', {}), ('description', {}), ('unit', {})])"

    #-----------------------------------------------------------------------------------------------
    def test_copy_category_no_overwrite(self, base_cfgmng):
        # Arrange
        base_cfgmng.set_values('log', False, True)
        base_cfgmng.set_values('log_file', 'default.log')
        # Test
        res = base_cfgmng.copy_category('default_settings', 'current_settings')
        # Assure
        assert str(base_cfgmng) == "ConfigManager([('default_settings', {'log': False, 'log_file': 'default.log'}), ('current_settings', {'log': True, 'log_file': 'default.log'})])"

    #-----------------------------------------------------------------------------------------------
    def test_copy_category_overwrite(self, base_cfgmng):
        # Arrange
        base_cfgmng.set_values('log', False, True)
        base_cfgmng.set_values('log_file', 'default.log')
        # Test
        res = base_cfgmng.copy_category('default_settings', 'current_settings', overwrite=True)
        # Assure
        assert str(base_cfgmng) == "ConfigManager([('default_settings', {'log': False, 'log_file': 'default.log'}), ('current_settings', {'log': False, 'log_file': 'default.log'})])"

    #-----------------------------------------------------------------------------------------------
    def test_copy_category_not_found(self, base_cfgmng):
        # Arrange
        pass
        # Test
        with pytest.raises(KeyError):
            res = base_cfgmng.copy_category('default_settings', 'settings')
        # Assure
        pass

        # Arrange
        pass
        # Test
        with pytest.raises(KeyError):
            res = base_cfgmng.copy_category('default_settings', 'settings', overwrite=True)
        # Assure
        pass

    #-----------------------------------------------------------------------------------------------
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

    #-----------------------------------------------------------------------------------------------
    def test_set_values(self, base_cfgmng):
        base_cfgmng.set_values('log_file', 'default.log', 'my.log')
        assert str(base_cfgmng) == "ConfigManager([('default_settings', {'log_file': 'default.log'}), ('current_settings', {'log_file': 'my.log'})])"

        # if no value is given (None) then the original value is kept, otherwise overwritten
        base_cfgmng.set_values('log_file', None, 'foo.log')
        assert str(base_cfgmng) == "ConfigManager([('default_settings', {'log_file': 'default.log'}), ('current_settings', {'log_file': 'foo.log'})])"

        base_cfgmng.set_values('log', 'False')
        assert str(base_cfgmng) == "ConfigManager([('default_settings', {'log_file': 'default.log', 'log': 'False'}), ('current_settings', {'log_file': 'foo.log'})])"

        with pytest.raises(TypeError):
            base_cfgmng.set_values('log_level')

        with pytest.raises(TypeError):
            base_cfgmng.set_values('log_file', 'foo.log', 'my_log.log', 'Name of the log file')

    #-----------------------------------------------------------------------------------------------
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

#--------------------------------------------------------------------------------------------------
class TestExportImport:

    #-----------------------------------------------------------------------------------------------
    @pytest.fixture
    def filled_cfgmng(self):
        cfgmng = ConfigManager()
        cfgmng.add_category('current_settings', 'default_settings', 'description')
        cfgmng.set_values('log', True, False, 'Enable/disable logging')
        cfgmng.set_values('log_level', 5, 1, 'Logging verbosity')
        cfgmng.set_values('log_file', 'my.log')
        return cfgmng

    #-----------------------------------------------------------------------------------------------
    @pytest.fixture
    def empty_cfgmng(self):
        cfgmng = ConfigManager()
        cfgmng.add_category('default_settings', 'current_settings')
        return cfgmng

    #-----------------------------------------------------------------------------------------------
    @pytest.fixture(scope="session")
    def conf_file_current_settings(self, tmp_path_factory):
        filename = os.path.join(tmp_path_factory.mktemp("data"), 'current_settings.conf')
        with open(filename, "w") as fh:
            data = unindent("""
                log=True
                log_level=5
                log_file='my.log'
            """,True)
            fh.write(data)
            fh.close()
            return filename

    #-----------------------------------------------------------------------------------------------
    def test_yaml_export(self, filled_cfgmng):
        import yaml
        dump = unindent("""
            !!python/object/apply:{0}.ConfigManager
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
        """,True).format('confmng')
        assert yaml.dump(filled_cfgmng) == dump

    #-----------------------------------------------------------------------------------------------
    def test_json_export(self, filled_cfgmng):
        import  json
        dump = """{"current_settings": {"log": true, "log_level": 5, "log_file": "my.log"}, "default_settings": {"log": false, "log_level": 1}, "description": {"log": "Enable/disable logging", "log_level": "Logging verbosity"}}"""
        assert json.dumps(filled_cfgmng) == dump

    #-----------------------------------------------------------------------------------------------
    def test_keyval_export(self, filled_cfgmng, tmp_path):
        filename = os.path.join(tmp_path,'current_settings.conf')
        dump_keyval(filename, filled_cfgmng.current_settings)
        with open(filename) as fh:
            data = ""
            for line in fh:
                data = data + line
        assert data == unindent("""
            log=True
            log_level=5
            log_file='my.log'
        """, True)

    #-----------------------------------------------------------------------------------------------
    def test_keyval_import(self, mocker, empty_cfgmng):
        # Arrange
        data = unindent("""
            log=True
            log_level=5
            log_file='my.log'
        """)
        mock_open = mocker.mock_open(read_data=data)
        mocker.patch('builtins.open', mock_open)
        # Test
        load_keyval('current_settings.conf', empty_cfgmng.current_settings)
        # Assert
        mock_open.assert_called_once_with('current_settings.conf')
        assert str(empty_cfgmng) == "ConfigManager([('default_settings', {}), ('current_settings', {'log': True, 'log_level': 5, 'log_file': 'my.log'})])"

    #-----------------------------------------------------------------------------------------------
    def test_dump(self, filled_cfgmng, tmp_path):
        # Arrange
        filenames = dict()
        for category in filled_cfgmng.keys():
            filenames[category] = os.path.join(tmp_path, category+'.conf')
        # Test
        filenames = filled_cfgmng.dump(filenames)
        # Assert
        for filename in filenames.values():
            assert os.path.exists(filename)
            assert os.stat(filename).st_size > 0

    #-----------------------------------------------------------------------------------------------
    def test_load(self, mocker):
        # Arrange
        data = [
            unindent("""
                log=True
                log_level=5
                log_file='my.log'
            """, True),
            unindent("""
                log=False
                log_level=1
            """, True)
        ]
        cfgmng = ConfigManager()

        filenames = {'current_settings': 'current_settings.conf',
            'default_settings': 'default_settings.conf'}
        print(cfgmng)
        from mock_open import MockOpen
        mock_open = MockOpen()
        mock_open["current_settings.conf"].read_data = data[0]
        mock_open["default_settings.conf"].read_data = data[1]
        mocker.patch('builtins.open', mock_open)
        # Test
        ret = cfgmng.load(filenames)
        # Assert
        print(ret)
        print(cfgmng)
        assert str(cfgmng) == "ConfigManager([('current_settings', {'log': True, 'log_level': 5, 'log_file': 'my.log'}), ('default_settings', {'log': False, 'log_level': 1})])"

    #-----------------------------------------------------------------------------------------------
    def test_dump_into_one(self, filled_cfgmng, tmp_path):
        # Arrange
        filename = os.path.join(tmp_path, 'foo.conf')
        # Test
        filled_cfgmng.dump_into_one(filename)
        # Assert
        with open(filename) as fh:
            data = ""
            for line in fh:
                data = data + line
        assert data == unindent("""
            [current_settings]
            log=True
            log_level=5
            log_file='my.log'

            [default_settings]
            log=False
            log_level=1

            [description]
            log='Enable/disable logging'
            log_level='Logging verbosity'
        """)
