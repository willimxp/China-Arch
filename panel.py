# Create by willimxp
# Blender插件，用以创建中式建筑
# 定义插件面板

import bpy
import data

# 地盘设置面板
class CHINAARCH_PT_panel_base(bpy.types.Panel):
    bl_idname = "CHINAARCH_PT_panel_base"
    bl_label = "柱网层" 
    bl_category = "China Arch"
    bl_region_type = 'UI'
    bl_space_type = 'VIEW_3D'    
    bl_context = "objectmode"

    def draw(self, context):
        dataset : data.CHINARCH_scene_data = context.scene.chinarch_data
        layout = self.layout
        # row = layout.row()
        # row.label(text="地盘设置")
        
        # 选择框：是否自动重绘
        row = layout.row()
        row.prop(context.scene.chinarch_data, "is_auto_redraw")

        #box 一
        box = layout.box()   
        # 输入整体尺寸，绑定data中的自定义property
        row = box.column(align=True)
        row.prop(dataset, "x_rooms")    # 面阔间数
        row.prop(dataset, "x_1")        # 明间宽度
        if dataset.x_rooms >= 3:
            row.prop(dataset, "x_2")    # 次间宽度
        if dataset.x_rooms >= 5:
            row.prop(dataset, "x_3")    # 梢间宽度
        if dataset.x_rooms >= 7:
            row.prop(dataset, "x_4")    # 尽间宽度

        row = box.column(align=True)
        row.prop(context.scene.chinarch_data, "y_rooms")    # 进深间数
        row.prop(dataset, "y_1")        # 明间深度
        if dataset.y_rooms >= 3:
            row.prop(dataset, "y_2")    # 次间深度
        if dataset.y_rooms >= 5:
            row.prop(dataset, "y_3")    # 梢间深度

        # 地基设置：高度，外部对象
        box = layout.box()  
        row = box.row()
        row.prop(dataset, "z_base")     # 台基高度
        row = box.row()
        row.prop_search(dataset, "base_source",bpy.data,"objects")  # 台基对象
        row = box.row()
        row.prop_search(dataset, "step_source",bpy.data,"objects")  # 踏道对象

        # 选择柱子对象
        box = layout.box() 
        row = box.row()
        row.prop_search(dataset,"piller_source",bpy.data,"objects")
        # 选择柱础对象 ## 暂时隐藏，还没想好到底柱子和柱础是否要分开
        # row = box.row()
        # row.prop_search(dataset,"piller_base_source",bpy.data,"objects")
        row = box.row(align=True)
        # 按钮：保存柱网
        row.operator("chinarch.piller_net_save",icon='PARTICLES')
        # 按钮：重设柱网
        row.operator("chinarch.piller_net_reset",icon='MOD_PARTICLE_INSTANCE')

        # 选择阑额对象
        box = layout.box() 
        row = box.row()
        row.prop_search(dataset,"lane_source",bpy.data,"objects")

        # 按钮：生成建筑外形，绑定build operator
        row = layout.row()
        row.operator("chinarch.buildpiller",icon='HOME')

# 铺作属性面板
class CHINAARCH_PT_panel_puzuo(bpy.types.Panel):
    bl_idname = "CHINAARCH_PT_panel_puzuo"
    bl_label = "铺作层" 
    bl_category = "China Arch"
    bl_region_type = 'UI'
    bl_space_type = 'VIEW_3D'    
    bl_context = "objectmode"

    def draw(self, context):
        dataset : data.CHINARCH_scene_data = context.scene.chinarch_data
        layout = self.layout

        # 选择铺作对象
        box = layout.box() 
        row = box.row()
        row.prop_search(dataset,"puzuo_piller_source",bpy.data,"objects")
        row = box.row()
        row.prop_search(dataset,"puzuo_fillgap_source",bpy.data,"objects")
        row = box.row()
        row.prop_search(dataset,"puzuo_corner_source",bpy.data,"objects")

        # 按钮：生成建筑外形，绑定build operator
        row = layout.row()
        row.operator("chinarch.buildpuzuo",icon='HOME')

# 屋顶属性面板
class CHINAARCH_PT_panel_roof(bpy.types.Panel):
    bl_idname = "CHINAARCH_PT_panel_roof"
    bl_label = "屋顶层" 
    bl_category = "China Arch"
    bl_region_type = 'UI'
    bl_space_type = 'VIEW_3D'    
    bl_context = "objectmode"

    def draw(self, context):
        dataset : data.CHINARCH_scene_data = context.scene.chinarch_data
        layout = self.layout
        
        # 选择铺作对象
        box = layout.box() 
        col = box.column(align=True)
        col.prop(dataset,"rafter_count_select")   # 椽架数量
        col.prop(dataset,"roof_base")   # 檐槫高
        col.prop(dataset,"roof_height") # 举高
        col.prop(dataset,"roof_extend") # 斗栱出跳
        col.prop(dataset,"eave_extend") # 檐椽出跳
        col.prop(dataset,"feizi_extend") # 飞子出跳

        row = box.row()
        row.prop_search(dataset,"tuan_source",bpy.data,"objects")   #槫子对象
        row = box.row()
        row.prop_search(dataset,"rafter_source",bpy.data,"objects")   #椽子对象
        # row = box.row()
        # row.prop_search(dataset,"fu_source",bpy.data,"objects")     #梁栿对象

        # 按钮：生成建筑外形，绑定build operator
        row = layout.row()
        row.operator("chinarch.buildroof",icon='HOME')

# 构件属性面板
class CHINAARCH_PT_panel_property(bpy.types.Panel):
    bl_idname = "CHINAARCH_PT_panel_property"
    bl_label = "构件属性" 
    bl_category = "China Arch"
    bl_region_type = 'UI'
    bl_space_type = 'VIEW_3D'    
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout

        # 仅在选中构件时显示
        if bpy.context.object and \
                "chinarch_obj" in context.object:
            box = layout.box()
            
            # 名称
            # if "chinarch_name" in context.object:
            row = box.row()
            row.prop(
                data = context.object,
                property = "name",
                text = "名称"
            )
            # 说明
            if "chinarch_desc" in context.object:
                row = box.row()
                row.prop(
                    data = context.object,
                    property = "chinarch_desc",
                    text = "说明"
                )            

            # 尺寸
            row = box.column(align=True)
            row.label(text="尺寸:")
            if "chinarch_scale" in context.object:
                row.prop(
                    data = context.object,
                    property = "chinarch_scale",
                    text = "材份等级"
                ) 
            row.prop(context.object,"dimensions",text="")

            # 位置
            row = box.column()
            row.prop(context.object,"location",text="位置")