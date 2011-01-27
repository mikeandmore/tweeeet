import tweepy
import os
import sys
import gtk
from urllib2 import urlopen
from md5 import md5
from settings import Settings
from utils import singleton_new
from pipeline import Pipeline

class Cache(object):
    CACHE_PATH = '~/.cache/tweeeet'

    __new__ = singleton_new

    def __init__(self):
        self._path = os.path.expanduser(self.CACHE_PATH)
        if not os.path.exists(self._path):
            os.mkdir(self._path)

    @staticmethod
    def hash(url):
        return md5(url).hexdigest()

    def get_file_path(self, url):
        return self._path + '/' + self.hash(url)
    
    def fetch_image(self, url):
        res = urlopen(url)
        with file(self.get_file_path(url), 'w') as f:
            f.write(res.read())
    
    def get_image(self, url):
        for dir_ent in os.listdir(self._path):
            if self.hash(url) == dir_ent:
                return self.get_file_path(url)
        self.fetch_image(url)
        return self.get_file_path(url)
        
def create_api():
    settings = Settings()
    auth = tweepy.BasicAuthHandler(settings['username'], settings['password'])
    api = tweepy.API(auth, timeout=settings['timeout'], compression=True)
    api.host = settings['host']
    api.api_root = settings['prefix']
    return api

class API(object):
    __new__ = singleton_new

    def __init__(self):
        self.api = create_api()

class TimeLineBaseController(object):
    RETWEET_COLOR = gtk.gdk.Color('#C1DBFF')

    def __init__(self):
        self.items = []

    def process_entry(self, item):
        cache = Cache()
        item.color = None
        item.text = tweepy.utils.unescape_html(item.text)
        if hasattr(item, 'retweeted_status'):
            item.color = self.RETWEET_COLOR
            item.retweeted = True
            item.author = item.retweeted_status.author
        item.image_path = cache.get_image(item.author.profile_image_url)
        return item
        
    def process_entries(self, items):
        res = []
        for item in items:
            res.append(self.process_entry(item))
        return res

    def refresh(self):
        self.items = self.process_entries(self.fetch_timeline())

    def next(self):
        last = self.items[-1]
        self.items += self.process_entries(self.fetch_timeline(max_id=last.id))

class HomeTimeLineController(TimeLineBaseController):
    __new__ = singleton_new
    
    def fetch_timeline(self, max_id=None):
        api = API().api
        print 'home_timeline...'
        if max_id is not None: max_id -= 1
        ls = api.home_timeline(max_id=max_id)
        rtls = api.retweeted_by_me(ls[-1].id)
        res = []
        # mix ls and rtls
        p = 0
        q = 0
        for i in xrange(len(ls) + len(rtls)):
            if q == len(rtls) or ls[p].id > rtls[q].id:
                res.append(ls[p])
                p += 1
            else:
                rt = rtls[q]
                rt.retweeted = True
                res.append(rt)
                q += 1
        return res

    def tweet(self, text, reply_entry=None):
        api = API().api
        if reply_entry is None:
            s = api.update_status(text)
        else:
            s = api.update_status(text, reply_entry.id)
        self.items.insert(0, self.process_entry(s))

    def retweet(self, entry):
        rt = API().api.retweet(entry.id)
        print 'retweeted', entry.id
        rt.retweeted = True
        self.items.insert(0, self.process_entry(rt))
        

class MentionsController(TimeLineBaseController):
    __new__ = singleton_new
    
    def fetch_timeline(self, max_id=None):
        api = API().api
        print 'mentions_timeline...'
        if max_id is not None: max_id -= 1
        return api.mentions(max_id=max_id)

class UserController(TimeLineBaseController):
    __new__ = singleton_new

    def __init__(self):
        TimeLineBaseController.__init__(self)
        self.screen_name = None

    def fetch_timeline(self, max_id=None):
        if self.screen_name is None:
            return
        api = API().api
        print 'user_timeline...'
        if max_id is not None: max_id -= 1
        return api.user_timeline(self.screen_name, max_id=max_id)

class DialogController(TimeLineBaseController):
    def refresh(self):
        pass

    def next(self):
        pass

    def list_conversations(self, start_id):
        api = API().api
        print 'fetching dialog'
        entry_id = start_id
        self.items = []
        while True:
            entry = self.process_entry(api.get_status(entry_id))
            self.items.append(entry)
            yield entry
            if entry.in_reply_to_status_id is None:
                break
            entry_id = entry.in_reply_to_status_id

