import pdb
import inspect

class Setting():
    def __init__(self, value, default):
        self._value = value
        self.default = default

    def __call__(self):
        print("Calling object...")
        return self._value

    @property
    def value(self):
        print("Getting value...")
        return self._value

    @value.setter
    def value(self, value):
        print("Setting value...")
        self._value = value

log = Setting(True, False)

# seeting value
log.value = True
# getting value
print(log())

print(log.default)
