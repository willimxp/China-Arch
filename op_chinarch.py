# Create by willimxp
# 中式建筑插件 for blender
# 构建逻辑类
# 根据输入的数据参数，按照《营造法式》，完成建筑体的自动建模

import bpy
from bpy_extras.object_utils import AddObjectHelper
from . import chinarch_data

# 根据基本参数，构建建筑体
class CHINARCH_OT_build(bpy.types.Operator, AddObjectHelper):
    bl_idname="chinarch.build"
    bl_label = "生成建筑外形"
   
    room_X = 4          # 面阔几间
    room_Y = 3          # 进深几间
    room_space = 3.0    # 间广几何
    base_Z = 0.5        # 台基多高
    piller_Z = 4.0      # 柱子多高
    piller_source = ""  # 关联的柱子对象

    dir_name = 'china_arch' # 在大纲中的目录名称

    def execute(self, context): 
        # 从data中读取用户通过Panel输入的值
        dataset : chinarch_data.ChinarchData = context.scene.chinarch_data
        self.room_X = dataset.x_rooms
        self.room_Y = dataset.y_rooms
        self.base_Z = dataset.z_base
        self.piller_source = dataset.piller_source

        # 所有对象建立在china_arch目录下，以免误删用户自建的模型
        coll_name = self.dir_name
        coll = bpy.data.collections.get(coll_name)
        if coll is None:    
            # 新建collection，不与其他用户自建的模型打架
            print("PP: Add new collection")
            coll = bpy.data.collections.new(coll_name)
            context.scene.collection.children.link(coll)
            context.view_layer.active_layer_collection = \
                context.view_layer.layer_collection.children[-1]
        else:               
            # 清空collection，每次重绘
            print("PP: Clear collection")
            for obj in coll.objects: 
                bpy.data.objects.remove(obj)
            
            # 关闭目录隐藏属性
            coll.hide_viewport = False
            context.view_layer.layer_collection.children[coll_name].hide_viewport = False
            # 选中目录，防止用户手工选择其他目录而导致的失焦
            layer_collection = bpy.context.view_layer.layer_collection
            layerColl = recurLayerCollection(layer_collection, coll_name)
            bpy.context.view_layer.active_layer_collection = layerColl
            
        # 一、创建根对象（empty）
        print("PP: Build root")
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        root_obj = bpy.context.object
        bpy.context.object.name = "中式建筑"
        # print("PP: " + bpy.context.object.name)

        # 二、创建地基
        print("PP: Build base")
        base_border = 2
        base_width = self.room_X * self.room_space + base_border
        base_length = self.room_Y * self.room_space + base_border
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, 
            calc_uvs=True, 
            enter_editmode=False, 
            align='WORLD', 
            location=(0.0, 0.0, self.base_Z/-2), 
            rotation=(0.0, 0.0, 0.0), 
            scale=(base_width, base_length, self.base_Z))
        context.object.name = "台基"
        context.object.parent = root_obj

        # 三、创建柱网
        print("PP: Build pillers")
        # 是否用户有自定义柱子？
        print("PP: Piller_source=" + self.piller_source)
        if self.piller_source == '':
            # 默认创建简单柱子
            piller_mesh = bpy.ops.mesh.primitive_cylinder_add(
                        vertices = 8, 
                        radius = 0.25, 
                        depth = self.piller_Z ,
                        end_fill_type='NGON', 
                        calc_uvs=True, 
                        enter_editmode=False, 
                        align='WORLD', 
                        location=(0, 0, self.piller_Z/2), 
                        rotation=(0.0, 0.0, 0.0), 
                        scale=(1,1,1)
                    )
            context.object.name = "立柱"
            context.object.parent = root_obj
        else:
            # 关联用户自定义柱子
            piller_mesh = bpy.data.objects.get(self.piller_source)

        # 按柱网坐标系分布柱子
        offset_x = self.room_X * self.room_space / 2
        offset_y = self.room_Y * self.room_space / 2

        for x in range(self.room_X+1):
            for y in range(self.room_Y+1):
                # 复制链接
                piller_copy = bpy.data.objects.new(
                    piller_mesh.name, piller_mesh.data)
                piller_copy.location.x = x * self.room_space - offset_x
                piller_copy.location.y = y * self.room_space - offset_y
                piller_copy.location.z = piller_mesh.location.z
                piller_copy.parent = root_obj            
                bpy.data.collections[coll_name].objects.link(piller_copy)

                # 复制modifier
                bpy.ops.object.select_all(action='DESELECT')
                piller_mesh.select_set(True)
                bpy.context.view_layer.objects.active = piller_mesh
                piller_copy.select_set(True)
                bpy.ops.object.make_links_data(type='MODIFIERS')         
        print("PP: finish")
        piller_mesh.select_set(False)
        root_obj.select_set(True)

        return {'FINISHED'}

# 递归查询，并选择collection，似乎没有找到更好的办法
# Recursivly transverse layer_collection for a particular name
# https://blender.stackexchange.com/questions/127403/change-active-collection
def recurLayerCollection(layerColl, collName):
    found = None
    if (layerColl.name == collName):
        return layerColl
    for layer in layerColl.children:
        found = recurLayerCollection(layer, collName)
        if found:
            return found
