# Wiggle Bones Add-on for Blender, maintained by Hans-Xwh
# 
# Based on jurassicjordan's fork of Labhatorian's fork of the original Wiggle 2 by shteeve3d.
#
# Licensed under the GNU General Public License, Version 3 (GPLv3).
# See the LICENSE file for the full license.


from . import properties
from . import operators
from . import wiggle_ui
from . import physics_engine

import bpy

# properties -> operators -> ui -> phys
def register():
    properties.register()
    operators.register()
    wiggle_ui.register()
    physics_engine.register()

    print("\nWiggle Bones registered")

def unregister():
    physics_engine.unregister()
    wiggle_ui.unregister()
    operators.unregister()
    properties.unregister()

    print("Wiggle Bones unregistered")