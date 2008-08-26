# Copyright (C) 2006-2007 Osmo Salomaa
# Copyright (C) 2008 Rodrigo Pinheiro Marques de Araujo
# Copyright (C) 2008 Michael Mc Donnell                      
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


"""Complete python code with Ctrl+Alt+Space key combination."""


import gedit
import gobject
import gtk
import re
from complete import complete
import ConfigurationDialog
import Configuration

class CompletionWindow(gtk.Window):

    """Window for displaying a list of completions."""

    def __init__(self, parent, callback):

        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_decorated(False)
        self.store = None
        self.view = None
        self.completions = None
        self.complete_callback = callback
        self.set_transient_for(parent)
        self.set_border_width(1)
        self.text = gtk.TextView()
        self.text_buffer = gtk.TextBuffer()
        self.text.set_buffer(self.text_buffer)
        self.text.set_size_request(300, 200)
        self.text.set_sensitive(False)
        self.init_tree_view()
        self.init_frame()
        self.connect('focus-out-event', self.focus_out_event) 
        self.connect('key-press-event', self.key_press_event)
        self.grab_focus()

    
    def key_press_event(self, widget, event):
        if event.keyval == gtk.keysyms.Escape:
            self.hide()
        elif event.keyval == gtk.keysyms.BackSpace:
            self.hide()
        elif event.keyval in (gtk.keysyms.Return, gtk.keysyms.Tab):
            self.complete()
        elif event.keyval == gtk.keysyms.Up:
            self.select_previous()
        elif event.keyval == gtk.keysyms.Down:
            self.select_next()

    def complete(self):
        self.complete_callback(self.completions[self.get_selected()]['completion'])

    def focus_out_event(self, *args):
        self.hide()
    
    def get_selected(self):
        """Get the selected row."""

        selection = self.view.get_selection()
        return selection.get_selected_rows()[1][0][0]

    def init_frame(self):
        """Initialize the frame and scroller around the tree view."""

        scroller = gtk.ScrolledWindow()
        scroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_NEVER)
        scroller.add(self.view)
        frame = gtk.Frame()
        frame.set_shadow_type(gtk.SHADOW_OUT)
        hbox = gtk.HBox()
        hbox.add(scroller)

        scroller_text = gtk.ScrolledWindow() 
        scroller_text.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroller_text.add(self.text)
        hbox.add(scroller_text)
        frame.add(hbox)
        self.add(frame)

    def init_tree_view(self):
        """Initialize the tree view listing the completions."""

        self.store = gtk.ListStore(gobject.TYPE_STRING)
        self.view = gtk.TreeView(self.store)
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("", renderer, text=0)
        self.view.append_column(column)
        self.view.set_enable_search(False)
        self.view.set_headers_visible(False)
        self.view.set_rules_hint(True)
        selection = self.view.get_selection()
        selection.set_mode(gtk.SELECTION_SINGLE)
        self.view.set_size_request(200, 200)
        self.view.connect('row-activated', self.row_activated)

    def row_activated(self, tree, path, view_column, data = None):
        self.complete()

    def select_next(self):
        """Select the next completion."""

        row = min(self.get_selected() + 1, len(self.store) - 1)
        selection = self.view.get_selection()
        selection.unselect_all()
        selection.select_path(row)
        self.view.scroll_to_cell(row)
        self.text_buffer.set_text(self.completions[self.get_selected()]['info'])

    def select_previous(self):
        """Select the previous completion."""

        row = max(self.get_selected() - 1, 0)
        selection = self.view.get_selection()
        selection.unselect_all()
        selection.select_path(row)
        self.view.scroll_to_cell(row)
        self.text_buffer.set_text(self.completions[self.get_selected()]['info'])

    def set_completions(self, completions):
        """Set the completions to display."""

        self.completions = completions
        self.completions.reverse()
        self.resize(1, 1)
        self.store.clear()
        for completion in completions:
            self.store.append([unicode(completion['abbr'])])
        self.view.columns_autosize()
        self.view.get_selection().select_path(0)
        self.text_buffer.set_text(self.completions[self.get_selected()]['info'])

    def set_font_description(self, font_desc):
        """Set the label's font description."""

        self.view.modify_font(font_desc)


class CompletionPlugin(gedit.Plugin):

    """Complete python code with the tab key."""

    re_alpha = re.compile(r"\w+", re.UNICODE | re.MULTILINE)
    re_non_alpha = re.compile(r"\W+", re.UNICODE | re.MULTILINE)

    def __init__(self):

        gedit.Plugin.__init__(self)
        self.completes = None
        self.completions = None
        self.name = "CompletionPlugin"
        self.popup = None
        self.window = None

    def activate(self, window):
        """Activate plugin."""

        self.window = window
        self.popup = CompletionWindow(window, self.complete)
        handler_ids = []
        callback = self.on_window_tab_added
        handler_id = window.connect("tab-added", callback)
        handler_ids.append(handler_id)
        window.set_data(self.name, handler_ids)
        for view in window.get_views():
            self.connect_view(view)

    def cancel(self):
        """Hide the completion window and return False."""

        self.hide_popup()
        return False

    def complete(self, completion):
        """Complete the current word."""

        doc = self.window.get_active_document()
        index = self.popup.get_selected()
        doc.insert_at_cursor(completion)
        self.hide_popup()
        
    def connect_view(self, view):
        """Connect to view's signals."""

        handler_ids = []
        callback = self.on_view_key_press_event
        handler_id = view.connect("key-press-event", callback)
        handler_ids.append(handler_id)
        view.set_data(self.name, handler_ids)

    def create_configure_dialog(self):
        """Creates and displays a ConfigurationDialog."""
        dlg = ConfigurationDialog.ConfigurationDialog()
        return dlg

    def deactivate(self, window):
        """Deactivate plugin."""

        widgets = [window]
        widgets.append(window.get_views())
        widgets.append(window.get_documents())
        for widget in widgets:
            handler_ids = widget.get_data(self.name)
            for handler_id in handler_ids:
                widget.disconnect(handler_id)
            widget.set_data(self.name, None)
        self.hide_popup()
        self.popup = None
        self.window = None

    def display_completions(self, view, event):
        """Find completions and display them."""

        doc = view.get_buffer()
        insert = doc.get_iter_at_mark(doc.get_insert())
        start = insert.copy()
        while start.backward_char():
            char = unicode(start.get_char())
            if not self.re_alpha.match(char) and not char == ".":
                start.forward_char()
                break
        incomplete = unicode(doc.get_text(start, insert))
        incomplete += unicode(event.string)
        if incomplete.isdigit():
            return self.cancel()
        completes =  complete( doc.get_text(*doc.get_bounds()), incomplete, insert.get_line())
        if not completes:
            return self.cancel()
        self.completes = completes

        if "." in incomplete:
            incompletelist = incomplete.split('.')
            newword = incompletelist[-1]
            self.completions = list(x['abbr'][len(newword):] for x in completes)
            length = len(newword)
        else:
            self.completions = list(x['abbr'][len(incomplete):] for x in completes)
            length = len(incomplete)
        for x in completes:
            x['completion'] = x['abbr'][length:]
        window = gtk.TEXT_WINDOW_TEXT
        rect = view.get_iter_location(insert)
        x, y = view.buffer_to_window_coords(window, rect.x, rect.y)
        x, y = view.translate_coordinates(self.window, x, y)
        self.show_popup(completes, x, y)

    def hide_popup(self):
        """Hide the completion window."""

        self.popup.hide()
        self.completes = None
        self.completions = None

    def is_configurable(self):
        """Show the plugin as configurable in gedits plugin list."""
        return True

    def on_view_key_press_event(self, view, event):
        """Display the completion window or complete the current word."""
        
        if self.window.get_active_document().get_mime_type() != 'text/x-python':
            return self.cancel()

        # FIXME This might result in a clash with other plugins eg. snippets
        # FIXME This code is not portable! 
        #  The "Alt"-key might be mapped to something else
        # TODO Find out which keybinding are already in use.
        keybinding = Configuration.getKeybindingCompleteTuple()
        ctrl_pressed = (event.state & gtk.gdk.CONTROL_MASK) == gtk.gdk.CONTROL_MASK
        alt_pressed = (event.state & gtk.gdk.MOD1_MASK) == gtk.gdk.MOD1_MASK
        shift_pressed = (event.state & gtk.gdk.SHIFT_MASK) == gtk.gdk.SHIFT_MASK
        keyval = gtk.gdk.keyval_from_name(keybinding[Configuration.KEY])
        key_pressed = (event.keyval == keyval)

        # It's ok if a key is pressed and it's needed or
        # if a key is not pressed if it isn't needed.
        ctrl_ok = not (keybinding[Configuration.MODIFIER_CTRL] ^ ctrl_pressed )
        alt_ok =  not (keybinding[Configuration.MODIFIER_ALT] ^ alt_pressed )
        shift_ok = not (keybinding[Configuration.MODIFIER_SHIFT] ^ shift_pressed )

        if ctrl_ok and alt_ok and shift_ok and key_pressed:
            return self.display_completions(view, event)
        
        return self.cancel()

    def on_window_tab_added(self, window, tab):
        """Connect the document and view in tab."""

        context = tab.get_view().get_pango_context()
        font_desc = context.get_font_description()
        self.popup.set_font_description(font_desc)
        self.connect_view(tab.get_view())


    def show_popup(self, completions, x, y):
        """Show the completion window."""

        root_x, root_y = self.window.get_position()
        self.popup.move(root_x + x + 24, root_y + y + 44)
        self.popup.set_completions(completions)
        self.popup.show_all()
        
