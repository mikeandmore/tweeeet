import gtk
import sys
import traceback
from timeline import TimeLineList
from tweeeet.core.controller import HomeTimeLineController, MentionsController
from tweeeet.core.pipeline import Pipeline
from tweeeet.core.utils import singleton_new
from tweeeet.ui import package_path
from threading import Thread

class TabManager(object):

    __new__ = singleton_new

    def __init__(self):
        self.tabs = []

    def set_ui_instance(self, ui_instance):
        self.ui = ui_instance

    def register_tab(self, page):
        btn = gtk.RadioToolButton()
        btn.set_icon_name(page.icon)
        
        self.ui.toolbar.insert(btn, len(self.tabs))
        self.tabs.append((btn, page))

        if len(self.tabs) == 1:
            self._group = btn
            self.switch_to(0)
        else:
            btn.set_group(self._group)

        idx = len(self.tabs) - 1
        def cb(radio_btn, event):
            if radio_btn.get_active():
                self.switch_to(idx)
        btn.connect('clicked', cb, None)
        
    def switch_to(self, idx):
        print 'swtich to', idx
        btn, page = self.tabs[idx]
        # change the content of scrolledwindow
        child = self.ui.scrwindow.get_child()
        if child is not None:
            child.hide_all()
            self.ui.scrwindow.remove(child)
            view = child.get_child()
            if view is not None:
                child.remove(view)
        page.on_switched_to()
        page.view.show_all()
        self.ui.scrwindow.add_with_viewport(page.view)
        self.current_idx = idx

    def switch_to_current_tab(self):
        self.switch_to(self.current_idx)

    def refresh_all_tabs(self):
        for btn, page in self.tabs:
            page.on_refresh()
        def ui_refresh():
            gtk.threads_enter()
            self.switch_to_current_tab()
            self.ui.widgets['refresh_btn'].set_sensitive(True)
            gtk.threads_leave()
        self.ui.widgets['refresh_btn'].set_sensitive(False)
        Pipeline().add_handler(ui_refresh)

class TimeLineBasePage(object):
    RETWEET_IMAGE = package_path + '/data/retweet.png'
    REPLY_IMAGE = package_path + '/data/reply.png'
    
    def __init__(self):
        self.list = TimeLineList()
        self.list.hint_icons = [self.reply_image_init, self.retweet_image_init]
        self.list.on_next_clicked = self.on_next
        self.view = self.list.widget()

    def on_switched_to(self):
        self.list.refresh(self.controller.items)
        self.view = self.list.widget()

    def on_next(self, btn, event):
        def pipeline_work():
            self.controller.next()
            
        def pipeline_ui_work():
            gtk.threads_enter()
            self.list.refresh(self.controller.items)
            tabmgr = TabManager()
            cur_adj = tabmgr.ui.scrwindow.get_vadjustment().get_value()
            tabmgr.switch_to_current_tab()
            def hack():
                tabmgr.ui.scrwindow.get_vadjustment().set_value(cur_adj)
            gtk.timeout_add(100, hack)
            gtk.threads_leave()
            
        btn.set_sensitive(False)
        Pipeline().add_handler(pipeline_work)
        Pipeline().add_handler(pipeline_ui_work)
        
    def on_refresh(self):
        def pipeline_work():
            self.controller.refresh()
            gtk.threads_enter()
            self.list.refresh(self.controller.items)
            gtk.threads_leave()
        Pipeline().add_handler(pipeline_work)
        
    def reply_image_init(self, entry):
        def cb(widget, event, author):
            TabManager().ui.editor.reply(entry)
        return self.list.create_image_button(self.REPLY_IMAGE, entry.color, cb, entry)
    
    def retweet_image_init(self, entry):
        def cb(widget, event, entry):
            def pipeline_work():
                self.controller.retweet(entry)
                gtk.threads_enter()
                TabManager().switch_to_current_tab()
                gtk.threads_leave()
            Pipeline().add_handler(pipeline_work)
        return self.list.create_image_button(self.RETWEET_IMAGE, entry.color, cb, entry)
    
class HomeTimeLinePage(TimeLineBasePage):
    def __init__(self):
        TimeLineBasePage.__init__(self)
        self.controller = HomeTimeLineController()
        self.icon = 'gtk-home'
        
class MentionsPage(TimeLineBasePage):
    def __init__(self):
        TimeLineBasePage.__init__(self)
        self.controller = MentionsController()
        self.icon = 'gtk-about'

