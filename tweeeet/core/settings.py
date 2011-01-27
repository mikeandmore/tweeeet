import gconf
import tweepy
from utils import singleton_new



class Settings(object):
    SETTINGS_DIR = '/apps/tweeeet'
    
    __new__ = singleton_new

    def __init__(self):
        self._client = gconf.Client()
        if not self._client.dir_exists(self.SETTINGS_DIR):
            self._client.add_dir(self.SETTINGS_DIR, gconf.CLIENT_PRELOAD_ONELEVEL)
        # add default settings
        self.set_init_value('username', '')
        self.set_init_value('password', '')
        self.set_init_value('host', tweepy.api.host)
        self.set_init_value('prefix', tweepy.api.api_root)
        self.set_init_value('timeout', 10)

    def set_init_value(self, key, val):
        if self[key] is None:
            self[key] = val

    def __getitem__(self, key):
        val = self._client.get(self.SETTINGS_DIR + '/' + key)
        
        if val.type == gconf.VALUE_BOOL:
            return val.get_bool()
        if val.type == gconf.VALUE_INT:
            return val.get_int()
        if val.type == gconf.VALUE_STRING:
            return val.get_string()
        
        return None

    def __setitem__(self, key, val):
        key = self.SETTINGS_DIR + '/' + key
        if type(val) == bool:
            self._client.set_bool(key, val)
        if type(val) == int:
            self._client.set_int(key, val)
        if type(val) == str:
            self._client.set_string(key, val)

