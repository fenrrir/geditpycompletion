"""
A widget for defining key combinations, e.g. Ctr+Alt+space.

Signals: key-combination-changed
"""
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

import gtk
from gtk import gdk
import gobject
import pygtk

import logging

COMBINATION_ACTIVATED_TEXT = "Press new key combination..."
LOG_NAME = "KeyCombinationWidget"
COLOR_FOCUS_IN = "white"
DEFAULT_COMBINATION_TEXT = "None set"
WIDTH_CHARS = 18

class KeyCombinationWidget(gtk.EventBox):
    def __init__(self, verbose=True):
        gtk.EventBox.__init__(self)
        self.setupLogging(verbose)
        self._log.debug("Initializing KeyCombinationWidget.")
        
        self._label = gtk.Label()
        self._label.set_text(DEFAULT_COMBINATION_TEXT)
        self._label.set_width_chars(WIDTH_CHARS)
        self._label.set_alignment(0.0, 0.5)
        self._label.unset_flags(gtk.CAN_FOCUS)
        self.add(self._label)
        
        events = gdk.BUTTON_PRESS_MASK | gdk.KEY_PRESS_MASK | gdk.FOCUS_CHANGE_MASK
        self.add_events(events)
        
        self.active = False
    
    def getKeyCombination(self):
        return self._keyCombination
    
    def setKeyCombination(self, keyCombination):
        self._keyCombination = keyCombination
    
    def setupLogging(self, verbose):
        logging.basicConfig(level=logging.DEBUG,
                    format='%(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='/tmp/KeyCombinationWidget.log',
                    filemode='w')

        console = logging.StreamHandler()
        if verbose:
            console.setLevel(logging.DEBUG)
        else:
            console.setLevel(logging.WARNING)

        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)

        logging.getLogger("").addHandler(console)
        self._log = logging.getLogger(LOG_NAME)
    
    def do_button_press_event(self, event):
        self._log.debug("do_button_press_event()")
        self._log.debug("Grabbing focus.")
        self.set_flags(gtk.CAN_FOCUS)
        self.grab_focus()
        self.modify_bg(gtk.STATE_NORMAL, gdk.color_parse(COLOR_FOCUS_IN))
        self.active = True

    def do_key_press_event(self, event):
        if not self.active:
            return False
        self._log.debug("do_key_press_event()")
        key_name = gdk.keyval_name(event.keyval)
        self._log.debug("key_name = " + str(key_name))
        
        # Deactivate on Escape
        if key_name == "Escape":
            self.deactivate()
            return True
        
        value_of_A = gtk.gdk.keyval_from_name('A')
        value_of_z = gtk.gdk.keyval_from_name('z')
        
        keyCombination = []
        
        # FIXME Doesn't work with any super combination
        # FIXME What if keys are already used by another plugin?
        if key_name == "space" or key_name == "Tab" \
            or (event.keyval >= value_of_A and event.keyval <= value_of_z):
            # Check for Ctrl
            if event.state & gdk.CONTROL_MASK:
                self._log.debug("Ctrl held down.")
                keyCombination.append("Ctrl")
            # Check for Alt
            if event.state & gdk.MOD1_MASK:
                self._log.debug("Alt held down.")
                keyCombination.append("Alt")
            # Check for Shift
            if event.state & gdk.SHIFT_MASK:
                self._log.debug("Shift held down.")
                keyCombination.append("Shift")

            keyCombination.append(key_name.lower())
            self._log.debug("Setting key combination to " + '+'.join(keyCombination))
            self._label.set_text('+'.join(keyCombination))
            self.setKeyCombination(keyCombination)
            self.deactivate()
            self.emit("key-combination-changed", self.getKeyCombination())
            
    def do_focus_out_event(self, event):
        self._log.debug("do_focus_out_event()")
        self.deactivate()
        
    def deactivate(self):
        # Revert color back to normal
        default_bg_color = self.parent.get_style().bg[gtk.STATE_NORMAL]
        self.modify_bg(gtk.STATE_NORMAL, default_bg_color)
        self.unset_flags(gtk.CAN_FOCUS)
        self.active = False
        keyCombination = self.getKeyCombination()
        
        if not keyCombination:
            self._label.set_text(DEFAULT_COMBINATION_TEXT)
        else:
            self._label.set_text('+'.join(keyCombination))
        

gobject.type_register(KeyCombinationWidget)
gobject.signal_new("key-combination-changed", KeyCombinationWidget,
                       gobject.SIGNAL_RUN_LAST,
                       gobject.TYPE_NONE,
                       (gobject.TYPE_PYOBJECT,))

# Tests below

def on_key_combination_changed(widget, keyCombination):
    print "on_key_combination_changed()"
    print "New key combination is", keyCombination

if __name__ == '__main__':
    win = gtk.Window()
    win.set_border_width(5)
    win.set_title('KeyCombinationWidget test')
    win.connect('delete-event', gtk.main_quit)

    hbox = gtk.HBox(False, 4)
    win.add(hbox)

    lbl = gtk.Label()
    lbl.set_text("Key combination:")
    hbox.add(lbl)
    
    kcw = KeyCombinationWidget()
    hbox.add(kcw)
    kcw.connect("key-combination-changed", on_key_combination_changed)

    entry = gtk.Entry()
    hbox.add(entry)

    win.show_all()

    gtk.main()
