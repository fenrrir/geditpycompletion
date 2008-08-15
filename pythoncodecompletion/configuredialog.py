"""
Configuration dialog for python code completion plugin.

This code needs to be cleaned up! The keybinding label should be a custom widget.
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

import sys
import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import configuration

DEBUG = False

buffer = """
<glade-interface>
  <widget class="GtkDialog" id="configure_dialog">
    <property name="width_request">400</property>
    <property name="visible">True</property>
    <property name="border_width">5</property>
    <property name="title" translatable="yes">Configure python code completion</property>
    <property name="modal">True</property>
    <property name="window_position">GTK_WIN_POS_CENTER</property>
    <property name="destroy_with_parent">True</property>
    <property name="type_hint">GDK_WINDOW_TYPE_HINT_DIALOG</property>
    <property name="has_separator">False</property>
    <signal name="close" handler="on_configuration_dialog_close"/>
    <child internal-child="vbox">
      <widget class="GtkVBox" id="vbox">
        <property name="visible">True</property>
        <property name="spacing">2</property>
        <child>
          <widget class="GtkHBox" id="hbox">
            <property name="visible">True</property>
            <property name="spacing">4</property>
            <child>
              <widget class="GtkLabel" id="label_completion_combination">
                <property name="visible">True</property>
                <property name="label" translatable="yes">Completion combination:</property>
              </widget>
              <packing>
                <property name="expand">False</property>
                <property name="fill">False</property>
              </packing>
            </child>
            <child>
              <widget class="GtkEventBox" id="eventbox_completion_combination">
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <signal name="button_press_event" handler="on_eventbox_completion_combination_button_press_event"/>
                <signal name="focus_out_event" handler="on_eventbox_completion_combination_focus_out_event"/>
                <signal name="focus_in_event" handler="on_eventbox_completion_combination_focus_in_event"/>
                <signal name="key_press_event" handler="on_eventbox_completion_combination_key_press_event"/>
                <child>
                  <widget class="GtkLabel" id="eb_label_completion_combination">
                    <property name="visible">True</property>
                    <property name="label" translatable="yes">Ctrl+Alt+space</property>
                  </widget>
                </child>
              </widget>
              <packing>
                <property name="expand">False</property>
                <property name="fill">False</property>
                <property name="position">1</property>
              </packing>
            </child>
          </widget>
          <packing>
            <property name="expand">False</property>
            <property name="fill">False</property>
            <property name="position">1</property>
          </packing>
        </child>
        <child internal-child="action_area">
          <widget class="GtkHButtonBox" id="dialog-action_area">
            <property name="visible">True</property>
            <property name="layout_style">GTK_BUTTONBOX_END</property>
            <child>
              <widget class="GtkButton" id="button_clear">
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="receives_default">True</property>
                <property name="has_tooltip">True</property>
                <property name="tooltip" translatable="yes">Reset to default</property>
                <property name="label" translatable="yes">gtk-clear</property>
                <property name="use_stock">True</property>
                <property name="response_id">0</property>
                <signal name="clicked" handler="on_button_clear_clicked"/>
                <signal name="activate" handler="on_button_clear_activate"/>
              </widget>
            </child>
            <child>
              <widget class="GtkButton" id="button_close">
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="receives_default">True</property>
                <property name="has_tooltip">True</property>
                <property name="tooltip" translatable="yes">Close without saving changes</property>
                <property name="label" translatable="yes">gtk-close</property>
                <property name="use_stock">True</property>
                <property name="response_id">0</property>
                <signal name="clicked" handler="on_button_close_clicked"/>
                <signal name="activate" handler="on_button_close_activate"/>
              </widget>
              <packing>
                <property name="position">1</property>
              </packing>
            </child>
            <child>
              <widget class="GtkButton" id="button_apply">
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="receives_default">True</property>
                <property name="has_tooltip">True</property>
                <property name="tooltip" translatable="yes">Save changes and close</property>
                <property name="label" translatable="yes">gtk-apply</property>
                <property name="use_stock">True</property>
                <property name="response_id">0</property>
                <signal name="clicked" handler="on_button_apply_clicked"/>
                <signal name="activate" handler="on_button_apply_activate"/>
              </widget>
              <packing>
                <property name="position">2</property>
              </packing>
            </child>
          </widget>
          <packing>
            <property name="expand">False</property>
            <property name="pack_type">GTK_PACK_END</property>
          </packing>
        </child>
      </widget>
    </child>
  </widget>
</glade-interface>
"""

class ConfigureDialogController():
    def __init__(self, dlg):
        self.dlg = dlg
        self.old_keybinding = configuration.get_keybinding_complete()
        self.keybinding = self.old_keybinding
        self.completion_combination_is_active = False
        self.changes = []
        
    def _keybinding_to_string(self, keybinding):
        keybinding_str = ""
        if keybinding.has_key(configuration.MODIFIER_CTRL) \
            and keybinding[configuration.MODIFIER_CTRL] == True:
            keybinding_str += "Ctrl+"
        if keybinding.has_key(configuration.MODIFIER_ALT) \
            and keybinding[configuration.MODIFIER_ALT] == True:
            keybinding_str += "Alt+"

        keybinding_str += keybinding[configuration.KEY]
        
        return keybinding_str
    
    def set_label_completion_combination(self, label):
        self.label_completion_combination = label
        self.clear_set_completion_combination()

    def set_eventbox_completion_combination(self, eventbox):
        self.eventbox_completion_combination = eventbox
        self.eventbox_completion_combination_default_color = eventbox.get_style().copy().bg[gtk.STATE_NORMAL]
    
    def clear_set_completion_combination(self):
        keybinding_str = self._keybinding_to_string(self.keybinding)
        self.label_completion_combination.set_text(keybinding_str)
        self.completion_combination_is_active = False
        self.eventbox_completion_combination.modify_bg(gtk.STATE_NORMAL, 
            self.eventbox_completion_combination_default_color)

    def apply(self, widget):
        debug("apply", widget)
        # Commit changes (function pointer, data)
        for change in self.changes:
            change[0](change[1])

        self.close(widget)

    def clear(self, widget):
        debug("clear", widget)
        self.changes = []
        self.keybinding = self.old_keybinding
        self.clear_set_completion_combination()

    def close(self, widget, *event):
        debug("close", widget)
        self.dlg.hide()
        self.dlg.destroy()
    
    def focus_out(self, widget, *event):
        # This is only concerning the keybing widget.
        # TODO Make keybinding label a custom widget!
        self.clear_set_completion_combination()
    
    def key_press(self, widget, event):
        debug("key_press", widget)
        debug("event.key_val =", event.keyval)
        if not self.completion_combination_is_active:
            return False
        
        value_of_A = gtk.gdk.keyval_from_name('A')
        value_of_z = gtk.gdk.keyval_from_name('z')
        
        key_name = gtk.gdk.keyval_name(event.keyval)
        
        keybinding = {}
        
        if self.completion_combination_is_active and key_name == "Escape":
            self.clear_set_completion_combination()
            return True
        
        # FIXME Doesn't work with Shift+space, Shift+Tab or any super
        # FIXME What if keys are already used by another plugin?
        if key_name == "space" or key_name == "Tab" \
            or (event.keyval >= value_of_A and event.keyval <= value_of_z):
            # Check for Ctrl
            if event.state & gtk.gdk.CONTROL_MASK:
                keybinding[configuration.MODIFIER_CTRL] = True
            # Check for Alt
            if event.state & gtk.gdk.MOD1_MASK:
                keybinding[configuration.MODIFIER_ALT] = True
            
            
            keybinding[configuration.KEY] = key_name
            self.changes.append(
                (configuration.set_keybinding_complete, keybinding))
            
            self.keybinding = keybinding
            self.clear_set_completion_combination()
            
            return True

    def new_key_combination(self, widget, event):
        debug(widget)
        # Don't activate if already active        
        if self.completion_combination_is_active:
            return

        self.dlg.set_focus(self.eventbox_completion_combination)
        self.completion_combination_is_active = True
        self.label_completion_combination.set_text("Press a new key combination...")
        self.eventbox_completion_combination.modify_bg(gtk.STATE_NORMAL, 
            gtk.gdk.color_parse("white"))

def debug(msg, *parm):
    if not DEBUG:
        return
    parameters = ""
    if len(parm) > 0:
        parm = [str(p) for p in parm]
        parameters = " ".join(parm)
    print msg, parameters

def create_configure_dialog():
    #gladefile = "./configuredialog.glade"  
    #wTree = gtk.glade.XML(gladefile, "configure_dialog")
    wTree = gtk.glade.xml_new_from_buffer(buffer, len(buffer))
    dlg = wTree.get_widget("configure_dialog")
    label_completion_combination = \
        wTree.get_widget("eb_label_completion_combination")
    eb_completion_combination = \
        wTree.get_widget("eventbox_completion_combination")  

    button_close = wTree.get_widget("button_close")
    dlg.set_focus(button_close)
        

    controller = ConfigureDialogController(dlg)
    controller.set_eventbox_completion_combination(eb_completion_combination)
    controller.set_label_completion_combination(label_completion_combination)

    signals = \
    {   
        "on_configure_dialog_close" : controller.close,
        "on_button_apply_activate" : controller.apply,
        "on_button_apply_clicked" : controller.apply,
        "on_button_close_activate" : controller.close,
        "on_button_close_clicked" : controller.close,
        "on_button_clear_activate" : controller.clear,
        "on_button_clear_clicked" : controller.clear,
        "on_eventbox_completion_combination_button_press_event" :  controller.new_key_combination,
        "on_eventbox_completion_combination_key_press_event" : controller.key_press,
        "on_eventbox_completion_combination_focus_out_event" : controller.focus_out,
        "on_eventbox_completion_combination_focus_in_event" : controller.focus_out,
    }
    wTree.signal_autoconnect(signals)
    
    dlg.connect("destroy", controller.close)
    dlg.connect("delete_event", controller.close)
    
    return dlg
         
if __name__ == "__main__":
    dlg = create_configure_dialog()
    gtk.main()
