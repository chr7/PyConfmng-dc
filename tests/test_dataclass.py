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
    level: ConfigItem = ConfigItem(des='level of logging verbossity', std='INFO')
    filename: ConfigItem = ConfigItem(None, 'output.log', None, 'file name of the log file')

#--------------------------------------------------------------------------------------------------
@dataclass
class ApplicationItem(ConfigurationBase):
    url: ConfigItem
    suite: ConfigItem
    type: ConfigItem

@dataclass
class ApplicationConfiguration(ConfigurationBase):
    trackSpace: ApplicationItem = ApplicationItem(
        url=ConfigItem(std='https://trackspace.lhsystems.com', des='URL of the application'),
        suite=ConfigItem(std='trackSpace', des='suite the application belongs to'),
        type=ConfigItem(std='jira', des='type of the application')
    )
    docSpace: ApplicationItem = ApplicationItem(
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
        conf = confmng_single.logging.to_dict(category)

        # Assert
        assert conf == expected

    #----------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("category,expected", [
            ('usr', {'level':'DEBUG', 'filename':'app.log'}),
        ])
    def test_setModConfigFromDict(self, confmng_single, category, expected):
        # Arrange

        # Act
        confmng_single.logging.from_dict(category, expected)
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
        conf = confmng_single.to_dict(category)

        # Assert
        assert conf == expected

    #----------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("category,expected", [
            ('usr', {'logging':{'level':'DEBUG', 'filename':'app.log'}}),
        ])
    def test_setConfigManagerSingleFromDict(self, confmng_single, category, expected):
        # Arrange

        # Act
        confmng_single.from_dict(category, expected)
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

