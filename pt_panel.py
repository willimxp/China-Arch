# Create by willimxp
# Blender插件，用以创建中式建筑

import bpy

#   创建插件面板
class CHINAARCH_PT_panel(bpy.types.Panel):
    bl_idname = "CHINAARCH_PT_panel"
    bl_label = "中式建筑" 
    bl_category = "China Arch"

    bl_region_type = 'UI'
    bl_space_type = 'VIEW_3D'    
    bl_context = "objectmode"

    # 声明自定义property，与panel中的UI控件绑定，
    # 储存在data中，用于插件计算
    bpy.types.Scene.room_x = bpy.props.IntProperty(name="面阔间数", default=4)
    bpy.types.Scene.room_y = bpy.props.IntProperty(name="进深间数", default=3)
    bpy.types.Scene.base_z = bpy.props.FloatProperty(name="台基高度",default=1.0)

    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        # Label
        row = layout.row()
        row.label(text="中式建筑参数化", icon='MOD_BUILD')

        # 输入整体尺寸，绑定data中的自定义property
        row = layout.row()
        row.prop(context.scene, "room_x")
        row = layout.row()
        row.prop(context.scene, "room_y")
        row = layout.row()
        row.prop(context.scene, "base_z")


        # 按钮：添加建筑，传入data中的自定义property
        row = layout.row()
        room = row.operator("chinarch.build",icon='HOME')
        
        # 分割线
        layout.separator()
        layout.separator()