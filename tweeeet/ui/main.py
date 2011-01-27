import gtk
import sys
from tabs import TabManager, HomeTimeLinePage, MentionsPage, DialogPage, UserPage
from editor import Editor
from tweeeet.core.settings import Settings
from tweeeet.core.utils import singleton_new
from tweeeet.core.pipeline import Pipeline
from tweeeet.ui import package_path

class MainWindow(object):
    
    __new__ = singleton_new

    class BuilderHelper(object):
        def __init__(self, builder):
            self.builder = builder

        def __getitem__(self, key):
            return self.builder.get_object(key)

    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file(package_path + '/data/ui.xml')
        self.widgets = MainWindow.BuilderHelper(self.builder)
        
        self.window = self.widgets['main_window']
        self.toolbar = self.widgets['toolbar']
        self.scrwindow = self.widgets['scrolledwindow']
        
        self.tab_man = TabManager()
        self.tab_man.set_ui_instance(self)
        self.tab_man.register_tab(HomeTimeLinePage())
        self.tab_man.register_tab(MentionsPage())
        self.tab_man.register_tab(UserPage())
        self.tab_man.register_tab(DialogPage())
        
        self.editor = Editor(self.widgets['send_icon'])

        self.widgets['editor_hbox'].pack_start(self.editor.view)
        self.builder.connect_signals(self, None)

        Pipeline().set_notification_callback(self.show_status)

    def show_status(self, status, message):
        status_icons = ['dialog-warning', 'dialog-ok', 'image-loading']
        status_image = self.widgets['status_image']
        status_image.set_from_icon_name(status_icons[status + 1], gtk.ICON_SIZE_INVALID)
        status_image.set_pixel_size(16)
        self.widgets['statusbar'].push(0, message)

    def on_send_clicked(self, widget):
        self.editor.on_send()

    def on_pref_clicked(self, widget):
        settings = Settings()
        self.widgets['id_entry'].set_text(settings['username'])
        self.widgets['password_entry'].set_text(settings['password'])
        dlg = self.widgets['pref_dialog']
        dlg.run()
        dlg.hide()
        # update the settings
        settings['username'] = self.widgets['id_entry'].get_text()
        settings['password'] = self.widgets['password_entry'].get_text()

    def on_editor_key_press(self, widget, event):
        self.editor.update_state(0)

    def on_quit(self, widget, event):
        gtk.main_quit()

    def on_refresh_clicked(self, widget):
        self.tab_man.refresh_all_tabs()

    def get_tab_manager(self):
        return self.tab_man

    def show(self):
        self.window.show_all()
        self.editor.view.grab_focus()
