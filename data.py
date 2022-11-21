# Create by willimxp
# 中式建筑插件 for blender
# 定义数据结构

import bpy

# 修改数据时，自动调用重绘
def update_func(self, context):
    dataset : CHINARCH_scene_data = \
            context.scene.chinarch_data

    if dataset.is_auto_redraw:
        # 重绘
        bpy.ops.chinarch.build()

# 数据结构
class CHINARCH_scene_data(bpy.types.PropertyGroup):
    x_rooms : bpy.props.IntProperty(
            name="面阔间数",
            default=3, min=1, max=11,step=2,
            update=update_func
        )
    x_1 : bpy.props.FloatProperty(
        name="明间宽度",
        default=3, min=0, max=5,
        update=update_func
    )
    x_2 : bpy.props.FloatProperty(
        name="次间宽度",
        default=3, min=0, max=5,
        update=update_func
    )
    x_3 : bpy.props.FloatProperty(
        name="梢间宽度",
        default=3, min=0, max=5,
        update=update_func
    )
    x_4 : bpy.props.FloatProperty(
        name="尽间宽度",
        default=3, min=0, max=5,
        update=update_func
    )

    y_rooms : bpy.props.IntProperty(
            name="进深间数",
            default=3, min=1, max=5,
            update=update_func
        )
    y_1 : bpy.props.FloatProperty(
        name="明间深度",
        default=3, min=0, max=5,
        update=update_func
    )
    y_2 : bpy.props.FloatProperty(
        name="次间深度",
        default=3, min=0, max=5,
        update=update_func
    )
    y_3 : bpy.props.FloatProperty(
        name="梢间深度",
        default=3, min=0, max=5,
        update=update_func
    )
    z_base : bpy.props.FloatProperty(
            name="台基高度",
            default=1, min=0.0, max=3.0,
            update=update_func
        )
    base_source : bpy.props.StringProperty(
            name="台基",
            default="",
            update=update_func
        )
    step_source : bpy.props.StringProperty(
            name="踏道",
            default="",
            update=update_func
        )
    lane_source : bpy.props.StringProperty(
            name="阑额",
            default="", 
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
    puzuo_piller_source : bpy.props.StringProperty(
            name="柱头铺作",
            default="", 
            update=update_func
        )
    puzuo_fillgap_source : bpy.props.StringProperty(
            name="补间铺作",
            default="", 
            update=update_func
        )
    puzuo_corner_source : bpy.props.StringProperty(
            name="转角铺作",
            default="", 
            update=update_func
        )
    is_auto_redraw : bpy.props.BoolProperty(
            default=True,
            name="是否自动重绘"
        )