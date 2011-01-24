import gtk
import sys
from editor import Highlighter
from tweeeet.ui import package_path

class TimeLineList(object):
    """
    A list for showing the timeline
    """
    RT_TAG_IMAGE = package_path + '/data/rt.png'
    
    def __init__(self):
        self._table = None
        self._color = gtk.gdk.Color('#F3F3F3')
        self._hint_color = gtk.gdk.Color('#a0a0a0')
        self.title_icons = []
        self.hint_icons = []

        self.clear()

    def clear(self):
        self._table = None

    def table(self):
        return self._table

    def widget(self):
        if self._table is None:
            # construct a new widget
            label = gtk.Label()
            label.set_markup('<b>Empty</b>')
            return label
        return self._table
    
    def refresh(self, entry_list):
        self.clear()
        if len(entry_list) == 0:
            return
        self._table = gtk.Table(2, 3 * len(entry_list) + 1, False)
        self._table.set_col_spacing(0, 5)
        self._table.set_border_width(5)
        row = 0
        for entry in entry_list:
            self.attach_entry(entry, row)
            row += 1
        # create a detail button
        more_btn = gtk.Button("More")
        more_btn.connect('clicked', self.on_next_clicked, None)
        self._table.attach(more_btn, 1, 2,
                           3 * len(entry_list), 3 * len(entry_list) + 1,
                           0, 0)

    def create_color_cell(self, wid, color=None):
        if color is None:
            color = self._color
        ebox = gtk.EventBox()
        ebox.modify_bg(gtk.STATE_NORMAL, color)
        ebox.add(wid)
        return ebox

    def compose_profile_image(self, entry):
        orig_buf = gtk.gdk.pixbuf_new_from_file(entry.image_path)
        if entry.retweeted:
            rt_buf = gtk.gdk.pixbuf_new_from_file(self.RT_TAG_IMAGE)
            rt_buf.composite(orig_buf, 0, 0, rt_buf.get_width(), rt_buf.get_height(), 0.0, 0.0, 1.0, 1.0, gtk.gdk.INTERP_NEAREST, 255)
        return gtk.image_new_from_pixbuf(orig_buf)
    
    def attach_entry(self, entry, row):
        row *= 3
        color = self._color
        if hasattr(entry, 'color') and entry.color: color = entry.color
        
        img = self.compose_profile_image(entry)
        img.props.xalign = 0.0
        img.props.yalign = 0.0

        title_box = gtk.HBox()
        title_label = gtk.Label()
        title_label.set_markup('<b>%s</b>' % entry.author.name)
        title_label.props.xalign = 0
        title_time = gtk.Label(str(entry.created_at))
        title_time.props.xalign = 1
        title_time.modify_fg(gtk.STATE_NORMAL, self._hint_color)
        
        title_box.pack_start(title_label, False, False, 3)
        title_box.pack_start(title_time, True, True, 8)
        for init_func in self.title_icons:
            title_box.pack_start(init_func(entry), False, False, 1)

        buf = gtk.TextBuffer()
        buf.set_text(entry.text)
        content = gtk.TextView(buf)
        # highlight it
        Highlighter(buf, content).apply_tags()
        content.set_editable(False)
        content.set_cursor_visible(False)
        content.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        content.modify_base(gtk.STATE_NORMAL, color)
        content.modify_bg(gtk.STATE_NORMAL, color)
        
        hint_box = gtk.HBox()
        hint = 'via ' + entry.source
        if entry.retweeted: hint += ' retweeted by ' + entry.user.name
        hint_label = gtk.Label(hint)
        hint_label.props.xalign = 0
        hint_label.modify_fg(gtk.STATE_NORMAL, self._hint_color)
        
        hint_box.pack_start(hint_label, True, True, 5)
        for init_func in self.hint_icons:
            hint_box.pack_start(init_func(entry), False, False, 1)
        
        self._table.attach(img, 0, 1, row, row + 2, 0, gtk.FILL)
        self._table.attach(self.create_color_cell(title_box, color), 1, 2,
                           row, row + 1, gtk.FILL, gtk.FILL)
        self._table.attach(content, 1, 2, row + 1, row + 2,
                           gtk.FILL, gtk.FILL)
        self._table.attach(self.create_color_cell(hint_box, color), 1, 2,
                           row + 2, row + 3, gtk.FILL, gtk.FILL)

        self._table.set_row_spacing(row + 2, 8)

    def create_image_button(self, image_file, color, cb, data):
        image = gtk.image_new_from_file(image_file)
        box = gtk.EventBox()
        box.add(image)
        if color is not None:
            box.modify_bg(gtk.STATE_NORMAL, color)
        else:
            box.modify_bg(gtk.STATE_NORMAL, self._color)
        box.connect('button-press-event', cb, data)
        return box

