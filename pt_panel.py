# Create by willimxp
# Blender插件，用以创建中式建筑
# 定义插件面板

import bpy

#   创建插件面板
class CHINAARCH_PT_panel(bpy.types.Panel):
    bl_idname = "CHINAARCH_PT_panel"
    bl_label = "中式建筑" 
    bl_category = "China Arch"
    bl_region_type = 'UI'
    bl_space_type = 'VIEW_3D'    
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        
        # Label
        row = layout.row()
        row.label(text="中式建筑参数化", icon='MOD_BUILD')

        # 输入整体尺寸，绑定data中的自定义property
        row = layout.row()
        row.prop(context.scene.chinarch_data, "x_rooms")
        row = layout.row()
        row.prop(context.scene.chinarch_data, "y_rooms")
        row = layout.row()
        row.prop(context.scene.chinarch_data, "z_base")


        # 按钮：添加建筑，绑定build operator
        row = layout.row()
        room = row.operator("chinarch.build",icon='HOME')
        
        # 分割线
        layout.separator()
        row = layout.row()
        row.prop_search(
                context.scene.chinarch_data,
                "piller_source",
                bpy.data,
                "objects",
                text="柱子"
        )