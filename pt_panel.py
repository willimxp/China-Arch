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

    # 临时存储的变量，后续传入到operator中
    bpy.types.Scene.room_x = bpy.props.IntProperty(default=4)
    bpy.types.Scene.room_y = bpy.props.IntProperty(default=3)
    bpy.types.Scene.base_z = bpy.props.FloatProperty(default=1.0)

    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        # Label
        row = layout.row()
        row.label(text="中式建筑参数化", icon='MOD_BUILD')

        # 输入整体尺寸
        row = layout.row()
        row.prop(context.scene, "room_x", text="面阔间数")
        row = layout.row()
        row.prop(context.scene, "room_y", text="进深间数")
        row = layout.row()
        row.prop(context.scene, "base_z", text="台基高度")


        # 按钮：添加建筑
        row = layout.row()
        room = row.operator("chinarch.build",text="生成建筑框架",icon='HOME')
        room.room_X = context.scene.room_x
        room.room_Y = context.scene.room_y
        room.base_Z = context.scene.base_z
        
        # 分割线
        layout.separator()

        

        