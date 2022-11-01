# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
import bpy
from . import pt_panel
from . import op_chinarch

bl_info = {
    "name" : "China Arch",
    "author" : "willimxp",
    "description" : "Generate architecher in chinese style.",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "View3D > Properties > China Arch",
    "tracker_url": "http://lucky3d.fr/auto-rig-pro/doc/bug_report.html",
    "doc_url": "http://lucky3d.fr/auto-rig-pro/doc/",
    "category" : "Add Mesh"
}

def register():
    bpy.utils.register_class(pt_panel.CHINAARCH_PT_panel)
    bpy.utils.register_class(op_chinarch.CHINARCH_OT_build)

def unregister():
    bpy.utils.unregister_class(pt_panel.CHINAARCH_PT_panel)
    bpy.utils.unregister_class(op_chinarch.CHINARCH_OT_build)

if __name__ == "__main__":
    register()