"""
Read and write gconf entry for python code completion.

This code is alpha, it doesn't do very much input validation!
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

import gconf

GCONF_PLUGIN_PATH = "/apps/gedit-2/plugins/pythoncodecompletion/"
GCONF_KEYBINDING_COMPLETE = GCONF_PLUGIN_PATH + "keybindings/complete"
DEFAULT_KEYBINDING_COMPLETE = "ctrl+alt+space"
MODIFIER_ALT = "alt"
MODIFIER_CTRL = "ctrl"
KEY = "key"

_client = gconf.client_get_default ();
#_client.add_dir(GCONF_PLUGIN_PATH, gconf.CLIENT_PRELOAD_NONE)
_client.add_dir("/apps/gedit-2", gconf.CLIENT_PRELOAD_NONE)

def _str_to_bool(bool_str):
    """Can't use built-in bool function?"""
    if bool_str.strip().lower() == "true":
        return True
    elif bool_str.strip().lower() == "false":
        return False
    else:
        raise Exception("Can't convert string to boolean!")
        
def get_keybinding_complete():
    """
    Returns a tuple with the keybinding used to do code completion from the
    configuration file, e.g. {"alt" : True, "ctrl" : True, "key" : "space"}.
    """
    
    # Get keybinding from gconf or use default if none found.
    keybinding = _client.get_string(GCONF_KEYBINDING_COMPLETE)
    if not keybinding:
        keybinding = DEFAULT_KEYBINDING_COMPLETE
        
    # Parse keybinding
    alt = False
    ctrl = False
    key = ""
    for s in keybinding.split('+'):
        s = s.lower()
        if s == MODIFIER_ALT:
            alt = True
        elif s == MODIFIER_CTRL:
            ctrl = True
        else:
            key = s 
             
    return {MODIFIER_ALT : alt, MODIFIER_CTRL : ctrl, KEY : key}
    
def set_keybinding_complete(keybinding):
    """
    Saves a tuple with the shorcut used to do code completion to the gconf entry, 
    e.g. {"alt" : True, "ctrl" : True, "key" : "space"} is saved as "ctrl+alt+space".
    """
    entry = ""
    
    if keybinding.has_key(MODIFIER_CTRL) and keybinding[MODIFIER_CTRL]:
        entry += MODIFIER_CTRL + "+"

    if keybinding.has_key(MODIFIER_ALT) and keybinding[MODIFIER_ALT]:
        entry += MODIFIER_ALT + "+"

    if keybinding.has_key(KEY) and keybinding[KEY]:
        entry += keybinding[KEY]
    else:
        raise Exception("A keybinding must contain one 'normal' key!")
    
    _client.set_string(GCONF_KEYBINDING_COMPLETE, entry)
        
if __name__ == "__main__":
    print "Old keybinging was:", get_keybinding_complete()
    new_keybinding = {MODIFIER_ALT : False, MODIFIER_CTRL : True, KEY : "space"}
    print "Setting to new keybinding:", new_keybinding
    set_keybinding_complete(new_keybinding)
    print "New keybinding is:", get_keybinding_complete()
