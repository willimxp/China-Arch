# Create by willimxp
# 中式建筑插件 for blender
# 定义数据结构

import bpy

# 修改数据时，自动调用重绘
def update_func(self, context):
    dataset : ChinarchData = \
            context.scene.chinarch_data

    if dataset.is_auto_redraw:
        # 重绘
        bpy.ops.chinarch.build()

# 数据结构
class ChinarchData(bpy.types.PropertyGroup):
    x_rooms : bpy.props.IntProperty(
            name="面阔间数",
            default=3, min=1, max=9,
            update=update_func
        )
    y_rooms : bpy.props.IntProperty(
            name="进深间数",
            default=3, min=1, max=9,
            update=update_func
        )
    z_base : bpy.props.FloatProperty(
            name="台基高度",
            default=0.5, min=0.0, max=3.0,
            update=update_func
        )
    piller_source : bpy.props.StringProperty(
            name="柱子",
            default="", 
            update=update_func
        )
    piller_base_source : bpy.props.StringProperty(
            name="柱础",
            default="", 
            update=update_func
        )
    piller_net : bpy.props.StringProperty(
            name="保存的柱网列表"
        )
    is_auto_redraw : bpy.props.BoolProperty(
            default=True,
            name="是否自动重绘"
        )

