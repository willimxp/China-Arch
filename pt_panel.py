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
        
        #box 一
        box = layout.box()

        # Label        
        row = box.row()
        row.label(text="一、基本参数")

        # 输入整体尺寸，绑定data中的自定义property
        row = box.row()
        row.prop(context.scene.chinarch_data, "x_rooms")
        row = box.row()
        row.prop(context.scene.chinarch_data, "y_rooms")
        row = box.row()
        row.prop(context.scene.chinarch_data, "z_base")


        # box 二
        box = layout.box()
        # 标题：
        row = box.row()
        row.label(text="二、设置柱网")
        # 选择柱子对象
        row = box.row()
        row.prop_search(
                context.scene.chinarch_data,
                "piller_source",
                bpy.data,
                "objects"
        )
        row = box.row()
        row.prop_search(
                context.scene.chinarch_data,
                "piller_base_source",
                bpy.data,
                "objects"
        )
        row = box.row(align=True)
        # 按钮：保存柱网
        row.operator("chinarch.piller_net_save",icon='PARTICLES')
        # 按钮：重设柱网
        row.operator("chinarch.piller_net_reset",icon='MOD_PARTICLE_INSTANCE')

        # box 三
        box = layout.box()
        # 标题：
        row = box.row()
        row.label(text="三、生成外形")
        # 选择框：是否自动重绘
        row = box.row()
        row.prop(context.scene.chinarch_data, "is_auto_redraw")
        # 按钮：生成建筑外形，绑定build operator
        row = box.row()
        row.operator("chinarch.build",icon='HOME')