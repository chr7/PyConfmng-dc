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
    def from_dict(self, category: str, value: any):
        self.__dict__[category] = value

#--------------------------------------------------------------------------------------------------
class ConfigurationBase:

    #----------------------------------------------------------------------------------------------
    def to_dict(self, category: str='usr', include_none: bool=False):
        dic = dict()
        for name, item in self.__dict__.items():
            if isinstance(item, ConfigItem):
                val = eval('item.'+category)
                if include_none or val is not None:
                    dic[name] = val
            elif isinstance(item, ConfigurationBase):
                dic[name] = item.to_dict(category, include_none)
        return dic

    #----------------------------------------------------------------------------------------------
    def from_dict(self, category: str, values: dict):
        for key, value in values.items():
            eval('self.'+key).from_dict(category, value)

#--------------------------------------------------------------------------------------------------
class ConfigManagerBase:

    #----------------------------------------------------------------------------------------------
    def to_dict(self, category: str='usr', include_none: bool=False):
        dic = dict()
        for name, item in self.__dict__.items():
            if isinstance(item, ConfigurationBase):
                dic[name] = item.to_dict(category, include_none)
        return dic

    #----------------------------------------------------------------------------------------------
    def from_dict(self, category: str, values: dict):
        for key, value in values.items():
            eval('self.'+key).from_dict(category, value)

#-- MAIN ------------------------------------------------------------------------------------------
if __name__ == '__main__':
    pass
