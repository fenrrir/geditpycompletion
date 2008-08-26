"""
Read and write gconf entry for python code completion. Uses caching to save
number of look-ups.

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
MODIFIER_CTRL = "ctrl"
MODIFIER_ALT = "alt"
MODIFIER_SHIFT = "shift"
KEY = "key"

__client = gconf.client_get_default ();
#_client.add_dir(GCONF_PLUGIN_PATH, gconf.CLIENT_PRELOAD_NONE)
__client.add_dir("/apps/gedit-2", gconf.CLIENT_PRELOAD_NONE)

# Cached keybinding
__keybindingComplete = ""
__keybindingCompleteTuple = {}

def getKeybindingComplete():
    """
    Returns a string with the keybinding used to do code completion from the
    configuration file, e.g. "ctrl+alt+space"
    """
    global __keybindingComplete
    # Get keybinding from cache, then gconf or else use default.
    if len(__keybindingComplete) == 0:
        keybinding = __client.get_string(GCONF_KEYBINDING_COMPLETE)
        __keybindingCompleteTuple = {} # Invalidate cache
        if len(keybinding) == 0:
            __keybindingComplete = DEFAULT_KEYBINDING_COMPLETE
        else:
            __keybindingComplete = keybinding
    
    return __keybindingComplete
    
def getKeybindingCompleteTuple():
    """
    Returns a tuple with the keybinding used to do code completion from the
    configuration file, e.g. {"alt" : True, "ctrl" : True, "key" : "space"}.
    """
    global __keybindingCompleteTuple
    # Return cached result
    if len(__keybindingCompleteTuple) != 0:
        return __keybindingCompleteTuple
        
    # Parse keybinding
    alt = False
    ctrl = False
    shift = False
    key = ""
    keybinding = getKeybindingComplete().split('+')
    keybindingTuple = {
        MODIFIER_CTRL : False,
        MODIFIER_ALT : False,
        MODIFIER_SHIFT : False,
        KEY : ""
    }
    
    for s in keybinding:
        s = s.lower()
        if s == MODIFIER_ALT:
            keybindingTuple[MODIFIER_ALT] = True
        elif s == MODIFIER_CTRL:
            keybindingTuple[MODIFIER_CTRL] = True
        elif s == MODIFIER_SHIFT:
            keybindingTuple[MODIFIER_SHIFT] = True
        else:
            keybindingTuple[KEY] = s 
    
    __keybindingCompleteTuple = keybindingTuple
    
    return __keybindingCompleteTuple
    
def setKeybindingComplete(keybinding):
    """
    Saves a string with the keybinding used to do code completion to the gconf
    entry, e.g. "ctrl+alt+space".
    """
    global __keybindingComplete
    global __keybindingCompleteTuple
    __client.set_string(GCONF_KEYBINDING_COMPLETE, keybinding)
    __keybindingComplete = keybinding
    __keybindingCompleteTuple = {}
      
if __name__ == "__main__":
    __client.set_string(GCONF_KEYBINDING_COMPLETE, DEFAULT_KEYBINDING_COMPLETE)
    print "Old keybindging was:", getKeybindingComplete()
    print "Old keybindging tuple was:", getKeybindingCompleteTuple()
    newKeybinding = "ctrl+space"
    print "Setting to new keybinding:", newKeybinding
    setKeybindingComplete(newKeybinding)
    print "New keybinding is:", getKeybindingComplete()
    print "New keybinding tuple is:", getKeybindingCompleteTuple()
