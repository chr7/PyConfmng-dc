"""===========================================================================
   Configuration Manager based on Python dataclass
   ---------------------------------------------------------------------------
   Copyright (C) 2021 Christian Horn (U408667)
   ===========================================================================
"""

from dataclasses import dataclass, field
from typing import Any


#--------------------------------------------------------------------------------------------------
@dataclass
class ConfigItem:
    cur: Any = field(default=None)
    std: Any = field(default=None)
    usr: Any = field(default=None)
    des: str = field(default=None, compare=False)

    #----------------------------------------------------------------------------------------------
    def __post_init__(self):
        if self.cur is None:
            self.cur = self.std

    #----------------------------------------------------------------------------------------------
    def from_dict(self, value: any, category: str):
        self.__dict__[category] = value

    #----------------------------------------------------------------------------------------------
    def copy_category(self, from_category: str, to_category: str, include_none: bool = False):
        if include_none or self.__dict__[from_category] is not None:
            self.__dict__[to_category] = self.__dict__[from_category]


#--------------------------------------------------------------------------------------------------
class ConfigurationBase:

    #----------------------------------------------------------------------------------------------
    def to_dict(self, category: str = 'usr', include_none: bool = False):
        dic = dict()
        for name, item in self.__dict__.items():
            if isinstance(item, ConfigItem):
                val = eval('item.' + category)
                if include_none or val is not None:
                    dic[name] = val
            elif isinstance(item, ConfigurationBase):
                dic[name] = item.to_dict(category, include_none)
        return dic

    #----------------------------------------------------------------------------------------------
    def from_dict(self, values: dict, category: str):
        for key, value in values.items():
            eval('self.' + key).from_dict(value, category)

    #----------------------------------------------------------------------------------------------
    def copy_category(self, from_category: str, to_category: str, include_none: bool = False):
        for name, item in self.__dict__.items():
            if isinstance(item, ConfigItem):
                item.copy_category(from_category, to_category, include_none)
            elif isinstance(item, ConfigurationBase):
                item.copy_category(from_category, to_category, include_none)


#--------------------------------------------------------------------------------------------------
class ConfigManagerBase:

    #----------------------------------------------------------------------------------------------
    def to_dict(self, category: str = 'usr', include_none: bool = False):
        dic = dict()
        for name, item in self.__dict__.items():
            if isinstance(item, ConfigurationBase):
                dic[name] = item.to_dict(category, include_none)
        return dic

    #----------------------------------------------------------------------------------------------
    def from_dict(self, values: dict, category: str):
        for key, value in values.items():
            eval('self.' + key).from_dict(value, category)

    #----------------------------------------------------------------------------------------------
    def copy_category(self, from_category: str, to_category: str, include_none: bool = False):
        for name, item in self.__dict__.items():
            if isinstance(item, ConfigurationBase):
                item.copy_category(from_category, to_category, include_none)


#-- MAIN ------------------------------------------------------------------------------------------
if __name__ == '__main__':
    pass
