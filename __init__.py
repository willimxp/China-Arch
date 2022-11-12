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

# Create by willimxp
# Blender插件，用以创建中式建筑
# 初始化原数据，注入扩展类

import bpy
from . import pt_panel
from . import op_chinarch
from . import chinarch_data

bl_info = {
    "name" : "China Arch",
    "author" : "willimxp",
    "description" : "Generate architecher in chinese style.",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "View3D > Properties > China Arch",
    "tracker_url": "https://github.com/willimxp/China-Arch/issues",
    "doc_url": "https://github.com/willimxp/China-Arch/wiki",
    "category" : "Add Mesh"
}

classes = (
    chinarch_data.ChinarchData,
    pt_panel.CHINAARCH_PT_panel,
    op_chinarch.CHINARCH_OT_build,
    op_chinarch.CHINARCH_OT_piller_net_save,
    op_chinarch.CHINARCH_OT_piller_net_reset,
    )

def register():    
    for cls in classes:
        bpy.utils.register_class(cls)

    # 在scene中添加自定义数据结构
    bpy.types.Scene.chinarch_data = bpy.props.PointerProperty(
            type=chinarch_data.ChinarchData,
            name="中式建筑"
        )

def unregister():
    del bpy.types.Scene.chinarch_data

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

# 仅用于在blender text editor中测试用途
# 当做为blender addon插件载入时不会触发
if __name__ == "__main__":
    register()