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
import gtk.gdk
import logging
import keybindingwidget
import configuration

TEXT_KEYBINDING = "Keybinding:"
TEXT_TITLE = "Configure python code completion"
DEFAULT_WINDOW_WIDTH = 370
DEFAULT_WINDOW_HEIGHT = 0
LOG_NAME = "ConfigurationDialog"

log = logging.getLogger(LOG_NAME)

class ConfigurationDialog(gtk.Dialog):
    def __init__(self):
        gtk.Dialog.__init__(self)
        self.set_border_width(5)
        self.set_title(TEXT_TITLE)
        self.set_default_size(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        self.changes = []
        keybinding = configuration.getKeybindingComplete()
        log.info("Got keybinding from gconf %s" % str(keybinding))
        self.__setKeybinding(keybinding)
        
        self.table = gtk.Table(2, 2, homogeneous=False)
        self.table.set_row_spacings(4)
        self.table.set_col_spacings(4)
        self.vbox.pack_start(self.table, expand=False, fill=False, padding=4) 
        
        lblKeybinding = gtk.Label()
        lblKeybinding.set_text(TEXT_KEYBINDING)
        self.table.attach(lblKeybinding, 0, 1, 0, 1, xoptions=False, yoptions=False)        
        
        self.__kbWidget = keybindingwidget.KeybindingWidget()
        self.__kbWidget.setKeybinding(keybinding)
        self.table.attach(self.__kbWidget, 1, 2, 0, 1, xoptions=False, yoptions=False)
        
        # Buttons in the action area
        btnClose = gtk.Button(stock=gtk.STOCK_CLOSE)
        self.__btnApply = gtk.Button(stock=gtk.STOCK_APPLY)
        self.__btnApply.set_sensitive(False)
        btnClear =  gtk.Button(stock=gtk.STOCK_CLEAR)
        self.action_area.add(btnClear)
        self.action_area.add(self.__btnApply)
        self.action_area.add(btnClose)
        
        # Connect all signals
        self.__kbWidget.connect("keybinding-changed", self.on_keybinding_changed)
        btnClose.connect("clicked", self.close)
        self.__btnApply.connect("clicked", self.applyChanges)
        btnClear.connect("clicked", self.clearChanges)
        self.connect('delete-event', self.close)
        
        self.show_all()
    
    def __getKeybinding(self):
        return self.__keybinding
        
    def __setKeybinding(self, keybinding):
        self.__keybinding = keybinding
        
    def on_keybinding_changed(self, widget, keybinding):
        log.info("on_keybinding_changed")
        log.info("New keybinding is %s" % str(keybinding))
        change1 = (configuration.setKeybindingComplete, keybinding)
        change2 = (self.__setKeybinding, keybinding)
        self.changes.append(change1)
        self.changes.append(change2)
        
        self.__btnApply.set_sensitive(True)
        
    def clearChanges(self, widget):
        log.info("clearChanges")
        self.changes = []
        self.__kbWidget.setKeybinding(self.__getKeybinding())
        self.__btnApply.set_sensitive(False)
    
    def applyChanges(self, widget):
        log.info("applyChanges")
        # Commit changes (function pointer, data)
        for change in self.changes:
            change[0](change[1])
        
        self.__btnApply.set_sensitive(False)
        
    def close(self, widget, *event):
        log.info("close")
        self.hide()
        self.destroy()
        
if __name__ == '__main__':
    logging.basicConfig()
    log.setLevel(logging.DEBUG)
    
    dlg = ConfigurationDialog()

    gtk.main()
