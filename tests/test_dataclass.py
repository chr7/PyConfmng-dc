"""===========================================================================
   Test classes for the config class manager based on dataclass
   ---------------------------------------------------------------------------
   Copyright (C) 2021 Christian Horn (U408667)
   ===========================================================================
"""

from dataclasses import dataclass, field

import pytest
from confmng_dataclass import ConfigItem, ConfigManagerBase, ConfigurationBase


#--------------------------------------------------------------------------------------------------
@dataclass
class LoggingConfiguration(ConfigurationBase):
    level: ConfigItem = None
    filename: ConfigItem = None

    #----------------------------------------------------------------------------------------------
    def __post_init__(self):
        self.level = ConfigItem(std='INFO', des='level of logging verbossity')
        self.filename = ConfigItem(None, 'output.log', None, 'file name of the log file')

#-------------------------------------------------------------------------------------------------
@dataclass
class ApplicationItem(ConfigurationBase):
    url: ConfigItem = None
    suite: ConfigItem = None
    type: ConfigItem = None

@dataclass
class ApplicationConfiguration(ConfigurationBase):
    trackSpace: ApplicationItem = None
    docSpace: ApplicationItem = None

    #----------------------------------------------------------------------------------------------
    def __post_init__(self):
        self.trackSpace = ApplicationItem(
            url=ConfigItem(std='https://trackspace.lhsystems.com', des='URL of the application'),
            suite=ConfigItem(std='trackSpace', des='suite the application belongs to'),
            type=ConfigItem(std='jira', des='type of the application')
        )
        self.docSpace = ApplicationItem(
            url=ConfigItem(std='https://docspace.lhsystems.com', des='URL of the application'),
            suite=ConfigItem(std='trackSpace', des='suite the application belongs to'),
            type=ConfigItem(std='confluence', des='type of the application')
        )


#--------------------------------------------------------------------------------------------------
@pytest.fixture
def confmng_single():

    @dataclass
    class ConfigManager(ConfigManagerBase):
        logging: LoggingConfiguration = field(default_factory=LoggingConfiguration)

    return ConfigManager()

#--------------------------------------------------------------------------------------------------
@pytest.fixture
def confmng_multi():

    @dataclass
    class ConfigManager(ConfigManagerBase):
        logging: LoggingConfiguration = field(default_factory=LoggingConfiguration)
        applications: ApplicationConfiguration = field(default_factory=ApplicationConfiguration)

    return ConfigManager()

#--------------------------------------------------------------------------------------------------
class Logging:

    #----------------------------------------------------------------------------------------------
    def __init__(self, conf: LoggingConfiguration) -> None:
        self._conf = conf
        self._level = self._conf.level.cur

#--------------------------------------------------------------------------------------------------
class TestConfigManager:

    #----------------------------------------------------------------------------------------------
    def test_initCurrent(self, confmng_single):
        # Arrange

        # Act
        logging = Logging(confmng_single.logging)

        # Assert
        assert logging._level == 'INFO'

    #----------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("category,expected", [
            ('usr', {'level':None, 'filename':None}),
            ('std', {'level':'INFO', 'filename':'output.log'}),
            ('cur', {'level':'INFO', 'filename':'output.log'})
        ])
    def test_getModConfigAsDict(self, confmng_single, category, expected):
        # Arrange

        # Act
        conf = confmng_single.logging.to_dict(category, True)

        # Assert
        assert conf == expected

    #----------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("category,expected", [
            ('usr', {'level':'DEBUG', 'filename':'app.log'}),
        ])
    def test_setModConfigFromDict(self, confmng_single, category, expected):
        # Arrange

        # Act
        confmng_single.logging.from_dict(expected, category)
        conf = confmng_single.logging.to_dict(category)

        # Assert
        assert conf == expected

    #----------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("category,expected", [
            ('usr', {'logging':{'level':None, 'filename':None}}),
            ('std', {'logging':{'level':'INFO', 'filename':'output.log'}})
        ])
    def test_getConfigManagerSingleAsDict(self, confmng_single, category, expected):
        # Arrange

        # Act
        conf = confmng_single.to_dict(category, include_none=True)

        # Assert
        assert conf == expected

    #----------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("category,expected", [
            ('usr', {'logging':{'level':'DEBUG', 'filename':'app.log'}}),
        ])
    def test_setConfigManagerSingleFromDict(self, confmng_single, category, expected):
        # Arrange

        # Act
        confmng_single.from_dict(expected, category)
        conf = confmng_single.to_dict(category)

        # Assert
        assert conf == expected

    #----------------------------------------------------------------------------------------------
    def test_getConfigManagerMultiAsDict(self, confmng_multi):
        # Arrange

        # Act
        conf = confmng_multi.to_dict('std')

        # Assert
        assert conf == {
            'logging':{'level':'INFO', 'filename':'output.log'},
            'applications':{
                'trackSpace':{
                    'url':'https://trackspace.lhsystems.com',
                    'suite':'trackSpace',
                    'type':'jira'
                },
                'docSpace':{
                    'url':'https://docspace.lhsystems.com',
                    'suite':'trackSpace',
                    'type':'confluence'
                }
            }
        }

    #----------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("category,include_none, expected", [
            ('usr', False, {'logging':{
                                    'level':'DEBUG', 'filename':'app.log'
                                },
                            'applications':{
                                    'trackSpace':{'type':'Jira'},
                                    'docSpace':{'suite':'trackSpace suite'},
                                }
                            }
            ),
            ('usr', True, {'logging':{
                                    'level':'DEBUG', 'filename':'app.log'
                                },
                            'applications':{
                                    'trackSpace':{'url':None, 'suite':None, 'type':'Jira'},
                                    'docSpace':{'url':None,'suite':'trackSpace suite', 'type':None},
                                }
                            }
            ),
        ])
    def test_setConfigManagerMultiFromDict(self, confmng_multi, category, include_none, expected):
        # Arrange

        # Act
        confmng_multi.from_dict(expected, category)
        conf = confmng_multi.to_dict('usr', include_none)

        # Assert
        assert conf == expected

    #----------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("category,to_category, include_none, usr_settings, expected", [
            ('usr', 'cur', False,
                {
                    'logging':{
                        'level':'DEBUG', 'filename':'app.log'
                    },
                },
                {
                    'logging':{
                        'level':'DEBUG', 'filename':'app.log'
                    },
                    'applications':{
                        'trackSpace':{'url':'https://trackspace.lhsystems.com', 'suite':'trackSpace', 'type':'jira'},
                        'docSpace':{'url':'https://docspace.lhsystems.com','suite':'trackSpace', 'type':'confluence'},
                    }
                }
            ),
        ])
    def test_copyCategory(self, confmng_multi, category, to_category, include_none, usr_settings, expected):
        # Arrange
        from_category = category

        # Act
        confmng_multi.from_dict(usr_settings, category)
        confmng_multi.copy_category(from_category, to_category)
        conf = confmng_multi.to_dict('cur', include_none)

        # Assert
        assert conf == expected
