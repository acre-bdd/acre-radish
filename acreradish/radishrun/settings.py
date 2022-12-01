import os
from configobj import ConfigObj
import logging as log


class Settings:
    @staticmethod
    def read(self, settings):
        for setting in reversed(settings):
            sp = setting.split(",")
            for st in reversed(sp):
                filename = st.replace(".", "/")
                self.read_file(filename)

    @staticmethod
    def read_file(self, file):
        sf = f"etc/settings/{file}"
        co = ConfigObj(sf)
        for key, value in co.items():
            if key in os.environ:
                log.warning("key '{key}' already set to {os.environ[key]}, skipping ({value})")
                continue
            os.environ[key] = value
