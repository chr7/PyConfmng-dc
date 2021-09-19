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

#--------------------------------------------------------------------------------------------------
class ConfigurationBase:

    #----------------------------------------------------------------------------------------------
    def to_dict(self, category: str='usr'):
        dic = dict()
        for name, item in self.__dict__.items():
            if isinstance(item, ConfigItem):
                dic[name] = eval('item.'+category)
            elif isinstance(item, ConfigurationBase):
                dic[name] = item.to_dict(category)
        return dic

#--------------------------------------------------------------------------------------------------
class ConfigManagerBase:

    #----------------------------------------------------------------------------------------------
    def to_dict(self, category: str='usr'):
        dic = dict()
        for name, item in self.__dict__.items():
            if isinstance(item, ConfigurationBase):
                dic[name] = item.to_dict(category)
        return dic

#-- MAIN ------------------------------------------------------------------------------------------
if __name__ == '__main__':
    pass
