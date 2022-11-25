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
from . import panel
from . import operator
from . import data

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
    data.CHINARCH_scene_data,

    panel.CHINAARCH_PT_panel_base,
    panel.CHINAARCH_PT_panel_puzuo,
    panel.CHINAARCH_PT_panel_roof,
    panel.CHINAARCH_PT_panel_property,

    operator.CHINARCH_OT_build_piller,
    operator.CHINARCH_OT_build_puzuo,
    operator.CHINARCH_OT_build_roof,
    operator.CHINARCH_OT_piller_net_save,
    operator.CHINARCH_OT_piller_net_reset,
    operator.CHINARCH_OT_level_scale
    )

def register():   
    for cls in classes:
        bpy.utils.register_class(cls)

    # 在scene中添加自定义数据结构
    bpy.types.Scene.chinarch_data = bpy.props.PointerProperty(
            type=data.CHINARCH_scene_data,
            name="中式建筑"
        )

    bpy.types.Object.chinarch_obj = bpy.props.BoolProperty(default=True)
    bpy.types.Object.chinarch_name = bpy.props.StringProperty()
    bpy.types.Object.chinarch_desc = bpy.props.StringProperty()
    bpy.types.Object.chinarch_level = bpy.props.IntProperty()
    bpy.types.Object.chinarch_scale = bpy.props.EnumProperty(
        #name="材份等级 ",
        description="切换构件的材份等级",
        items=[
            ("1","一等材","一等材(9寸x6寸)"),
            ("2","二等材","二等材(8.25寸x5.5寸)"),
            ("3","三等材","三等材(7.5寸x5寸)"),
            ("4","四等材","四等材(7.2寸x4.8寸)"),
            ("5","五等材","五等材(6.6寸x4.4寸)"),
            ("6","六等材","六等材(6寸x4寸)"),
            ("7","七等材","七等材(5.25寸x3.5寸)"),
            ("8","八等材","八等材(4.5寸x3寸)"),
        ],
        options={"ANIMATABLE"},
        update=on_level_change
    )

def unregister():
    del bpy.types.Scene.chinarch_data
    del bpy.types.Object.chinarch_level
    del bpy.types.Object.chinarch_obj
    del bpy.types.Object.chinarch_name
    del bpy.types.Object.chinarch_desc
    del bpy.types.Object.chinarch_scale

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

# 仅用于在blender text editor中测试用途
# 当做为blender addon插件载入时不会触发
if __name__ == "__main__":
    register()

# 材份等级下拉框
def on_level_change(self, context):
    bpy.ops.chinarch.level_scale()
    # print("Level change from " \
    #     + str(context.object.chinarch_level) \
    #     + " to " + context.object.chinarch_scale)

# 材份等级下拉框
def on_level_set(self, context):
    print("Level set")

# 材份等级下拉框
def on_level_get(self, context):
    print("Level get")