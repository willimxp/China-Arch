# Create by willimxp
# 中式建筑插件 for blender
# 定义数据结构

import bpy

# 修改数据时，自动调用重绘
def update_piller(self, context):
    dataset : CHINARCH_scene_data = \
            context.scene.chinarch_data

    if dataset.is_auto_redraw:
        # 重绘
        bpy.ops.chinarch.buildpiller()
        bpy.ops.chinarch.buildpuzuo()
        bpy.ops.chinarch.buildroof()

# 修改数据时，自动调用重绘
def update_puzuo(self, context):
    dataset : CHINARCH_scene_data = \
            context.scene.chinarch_data

    if dataset.is_auto_redraw:
        # 重绘
        bpy.ops.chinarch.buildpuzuo()

# 修改数据时，自动调用重绘
def update_roof(self, context):
    dataset : CHINARCH_scene_data = \
            context.scene.chinarch_data

    if dataset.is_auto_redraw:
        # 重绘
        bpy.ops.chinarch.buildroof()

# 数据结构
class CHINARCH_scene_data(bpy.types.PropertyGroup):
    x_rooms : bpy.props.IntProperty(
            name="面阔间数",
            default=3, min=1, max=11,step=2,
            update=update_piller
        )
    x_1 : bpy.props.FloatProperty(
        name="明间宽度",
        default=3, min=0, 
        update=update_piller
    )
    x_2 : bpy.props.FloatProperty(
        name="次间宽度",
        default=3, min=0, 
        update=update_piller
    )
    x_3 : bpy.props.FloatProperty(
        name="梢间宽度",
        default=3, min=0, 
        update=update_piller
    )
    x_4 : bpy.props.FloatProperty(
        name="尽间宽度",
        default=3, min=0, 
        update=update_piller
    )
    y_rooms : bpy.props.IntProperty(
            name="进深间数",
            default=3, min=1, 
            update=update_piller
        )
    y_1 : bpy.props.FloatProperty(
        name="明间深度",
        default=3, min=0, 
        update=update_piller
    )
    y_2 : bpy.props.FloatProperty(
        name="次间深度",
        default=3, min=0, 
        update=update_piller
    )
    y_3 : bpy.props.FloatProperty(
        name="梢间深度",
        default=3, min=0, 
        update=update_piller
    )
    z_base : bpy.props.FloatProperty(
            name="台基高度",
            default=1, min=0.0, max=20.0,
            update=update_piller
        )
    base_source : bpy.props.StringProperty(
            name="台基",
            default="",
            update=update_piller
        )
    step_source : bpy.props.StringProperty(
            name="踏道",
            default="",
            update=update_piller
        )
    lane_source : bpy.props.StringProperty(
            name="阑额",
            default="", 
            update=update_piller
        )
    piller_source : bpy.props.StringProperty(
            name="柱子",
            default="", 
            update=update_piller
        )
    piller_base_source : bpy.props.StringProperty(
            name="柱础",
            default="", 
            update=update_piller
        )
    piller_net : bpy.props.StringProperty(
            name="保存的柱网列表"
        )
    puzuo_piller_source : bpy.props.StringProperty(
            name="柱头铺作",
            default="", 
            update=update_puzuo
        )
    puzuo_fillgap_source : bpy.props.StringProperty(
            name="补间铺作",
            default="", 
            update=update_puzuo
        )
    puzuo_corner_source : bpy.props.StringProperty(
            name="转角铺作",
            default="", 
            update=update_puzuo
        )
    tuan_source : bpy.props.StringProperty(
            name="槫子",
            default="", 
            update=update_roof
        )
    rafter_source : bpy.props.StringProperty(
            name="椽子",
            default="", 
            update=update_roof
        )
    fu_source : bpy.props.StringProperty(
            name="梁栿",
            default="", 
            update=update_roof
        )
    CornerBeam_source : bpy.props.StringProperty(
            name="角梁",
            default="", 
            update=update_roof
        )
    # roof_base : bpy.props.FloatProperty(
    #         name="檐槫高",
    #         default=7.0, 
    #         update=update_roof
    #     )
    roof_height : bpy.props.FloatProperty(
            name="举高",
            default=10.0, 
            update=update_roof
        )
    # roof_extend : bpy.props.FloatProperty(
    #         name="斗栱出跳",
    #         default=0.45, 
    #         update=update_roof
    #     )
    rafter_count : bpy.props.IntProperty(
            name="椽架数",
            default=8, 
            step=2,max=10,min=2,
            update=update_roof
        )
    is_auto_redraw : bpy.props.BoolProperty(
            default=True,
            name="是否自动重绘"
        )
    rafter_count_select : bpy.props.EnumProperty(
            name="椽架数",
            description="椽架数量",
            items=[
                ("2","2","2"),
                ("4","4","4"),
                ("6","6","6"),
                ("8","8","8"),
                ("10","10","10")
            ],
            options={"ANIMATABLE"},
            update=update_roof
        )
    eave_extend : bpy.props.FloatProperty(
            name="檐椽出跳",
            default=1.2, 
            update=update_roof
    )
    feizi_extend : bpy.props.FloatProperty(
            name="飞子出跳",
            default=0.72, 
            update=update_roof
    )
    hill_extend : bpy.props.FloatProperty(
            name="两厦出际",
            default=1.5, 
            update=update_roof
    )
    qiqiao: bpy.props.IntProperty(
            name="起翘(椽径倍数)",
            default=4, 
            update=update_roof
    )
    chong: bpy.props.IntProperty(
            name="出冲(椽径倍数)",
            default=3, 
            update=update_roof
    )
    shengqi: bpy.props.IntProperty(
            name="生起(椽径倍数)",
            default=1, 
            update=update_roof
    )
    tile_source : bpy.props.StringProperty(
            name="瓦片",
            default="", 
            update=update_roof
    )
    eave_tile_source : bpy.props.StringProperty(
            name="瓦当",
            default="", 
            update=update_roof
    )
    ridge_source : bpy.props.StringProperty(
            name="屋脊",
            default="", 
            update=update_roof
    )
    chiwen_source : bpy.props.StringProperty(
            name="鸱吻",
            default="", 
            update=update_roof
    )
    wall_source : bpy.props.StringProperty(
            name="墙体",
            default="", 
            update=update_roof
    )
    
