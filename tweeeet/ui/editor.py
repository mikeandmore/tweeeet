import gtk
import pango
import gconf
import re
import os
from tweeeet.core.pipeline import Pipeline
from tweeeet.core.controller import API, HomeTimeLineController

class Highlighter(object):
    def __init__(self, buf, view):
        self.buf = buf
        self.mention_tag = buf.create_tag(None, weight=pango.WEIGHT_BOLD)
        self.link_tag = buf.create_tag(None, foreground="blue", underline=pango.UNDERLINE_SINGLE)

        self.mention_pattern = re.compile('@[a-zA-Z0-9]+')
        self.link_pattern = re.compile('http://[^ ]*')
        
        def click_cb(widget, event):
            if event.type != gtk.gdk.BUTTON_RELEASE:
                return False
            x, y = widget.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET,
                                                int(event.x), int(event.y))
            it = widget.get_iter_at_location(x, y)
            url = self.get_link_address(it)
            if url is not None:
                client = gconf.Client()
                browser = client.get_string('/desktop/gnome/applications/browser/exec')
                os.system('%s %s&' % (browser, url))
            mention = self.get_user_mention(it)
            if mention is not None:
                from tabs import TabManager, UserPage
                idx, page = TabManager().find_tab(UserPage)
                page.set_user(mention[1:])
                page.show_user_tweets()
            return False
        
        view.connect('event-after', click_cb)

    def get_link_address(self, it):
        return self.get_tag_text(it, self.link_tag)

    def get_user_mention(self, it):
        return self.get_tag_text(it, self.mention_tag)

    def get_tag_text(self, it, tag):
        if not it.has_tag(tag):
            return None
        start_it = it.copy()
        start_it.backward_to_tag_toggle(tag)
        end_it = it.copy()
        end_it.forward_to_tag_toggle(tag)
        return self.buf.get_text(start_it, end_it)

    def clear_tags(self):
        start_it = self.buf.get_iter_at_offset(0)
        end_it = self.buf.get_iter_at_offset(-1)
        self.buf.remove_all_tags(start_it, end_it)

    def apply_tags(self):
        text = unicode(self.buf.get_text(self.buf.get_iter_at_offset(0),
                                         self.buf.get_iter_at_offset(-1)))
        def apply_pattern(pattern, tag):
            for m in re.finditer(pattern, text):
                span = m.span()
                self.buf.apply_tag(tag, self.buf.get_iter_at_offset(span[0]),
                                   self.buf.get_iter_at_offset(span[1]))
        apply_pattern(self.mention_pattern, self.mention_tag)
        apply_pattern(self.link_pattern, self.link_tag)

class Editor(object):
    def __init__(self, send_icon):
        self.buffer = gtk.TextBuffer()
        self.view = gtk.TextView(self.buffer)
        self.highlighter = Highlighter(self.buffer, self.view)
        self.view.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        self.view.connect('key-press-event', self.on_key_press, None)
        self.view.connect('key-release-event', self.on_key_release, None)

        self._keep_refresh_highlighter = False

        self.icon = send_icon
        self.update_state(0)

    def on_key_press(self, widget, event, data):
        if event.keyval == 65307:
            self.update_state(0)
            return False
        elif event.keyval == 65293 and event.state & gtk.gdk.CONTROL_MASK:
            self.on_send()
            return True
        return False

    def on_key_release(self, widget, event, data):
        self.highlighter.clear_tags()
        self.highlighter.apply_tags()
        return False

    def send(self, text):
        state = self.state
        reply_entry = self.reply_entry
        controller = HomeTimeLineController()
        def pipeline_work():
            api = API().api
            while True:
                try:
                    if state == 1: # reply
                        controller.tweet(text, reply_entry)
                    else:
                        controller.tweet(text)
                except Exception, e:
                    print e
                    continue
                break
            gtk.threads_enter()
            self.view.set_sensitive(True)
            from tabs import TabManager
            TabManager().switch_to_current_tab()
            gtk.threads_leave()
            
        self.view.set_sensitive(False)
        self.update_state(0)
        Pipeline().add_handler(pipeline_work, 'sending message...')
    
    def on_send(self):
        start_it = self.buffer.get_iter_at_offset(0)
        end_it = self.buffer.get_iter_at_offset(-1)
        self.send(self.buffer.get_text(start_it, end_it))

    def reply(self, entry):
        self.view.grab_focus()
        self.update_state(1)
        self.buffer.set_text('@'+entry.user.screen_name+' ')
        self.reply_entry = entry
        self.highlighter.apply_tags()

    def update_state(self, state):
        self.state = state
        self.reply_entry = None
        if state == 0:
            self.icon.set_from_stock(gtk.STOCK_OK, 'button')
        else:
            self.icon.set_from_stock(gtk.STOCK_REDO, 'button')
        self.buffer.set_text('')
            



