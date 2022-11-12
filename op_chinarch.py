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

    def execute(self, context): 
        # 从data中读取用户通过Panel输入的值
        dataset : chinarch_data.ChinarchData = \
            context.scene.chinarch_data
        
        x_rooms = dataset.x_rooms   # 面阔几间
        y_rooms = dataset.y_rooms   # 进深几间
        z_base = dataset.z_base    # 台基多高
        piller_source = dataset.piller_source # 关联的柱子对象
        room_space = 3.0    # 间广几何
        piller_Z = 4.0      # 柱子多高
        base_border = 2.0   # 地基边框

        # 1、创建china_arch collection集合
        # 所有对象建立在china_arch目录下，以免误删用户自建的模型
        coll_name = 'china_arch'  # 在大纲中的目录名称
        coll = bpy.data.collections.get(coll_name)
        if coll is None:    
            # 新建collection，不与其他用户自建的模型打架
            print("PP: Add new collection " + coll_name)
            coll = bpy.data.collections.new(coll_name)
            context.scene.collection.children.link(coll)
            context.view_layer.active_layer_collection = \
                context.view_layer.layer_collection.children[-1]
        else:               
            # 清空collection，每次重绘
            print("PP: Clear collection " + coll_name)
            for obj in coll.objects: 
                bpy.data.objects.remove(obj)
            # 强制关闭目录隐藏属性，防止失焦
            coll.hide_viewport = False
            context.view_layer.layer_collection.children[coll_name].hide_viewport = False
            # 选中目录，防止用户手工选择其他目录而导致的失焦
            layer_collection = bpy.context.view_layer.layer_collection
            layerColl = recurLayerCollection(layer_collection, coll_name)
            bpy.context.view_layer.active_layer_collection = layerColl
            
        # 2、创建根对象（empty）
        print("PP: Build root")
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        root_obj = context.object
        root_obj.name = "中式建筑"

        # 3、创建地基
        print("PP: Build base")
        base_width = x_rooms * room_space + base_border
        base_length = y_rooms * room_space + base_border
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, 
            calc_uvs=True, 
            enter_editmode=False, 
            align='WORLD', 
            location=(0.0, 0.0, z_base/-2), 
            rotation=(0.0, 0.0, 0.0), 
            scale=(base_width, base_length, z_base))
        context.object.name = "台基"
        context.object.parent = root_obj

        # 4、创建柱网
        print("PP: Build pillers")
        # 是否用户有自定义柱子？
        print("PP: Piller_source=" + piller_source)
        basic_piller_name = "基本立柱"
        if piller_source == '':
            # 默认创建简单柱子
            bpy.ops.mesh.primitive_cylinder_add(
                        vertices = 8, 
                        radius = 0.25, 
                        depth = piller_Z ,
                        end_fill_type='NGON', 
                        calc_uvs=True, 
                        enter_editmode=False, 
                        align='WORLD', 
                        location=(0, 0, piller_Z/2), 
                        rotation=(0.0, 0.0, 0.0), 
                        scale=(1,1,1)
                    )
            piller_mesh = context.object
            piller_mesh.name = basic_piller_name
            piller_mesh.parent = root_obj
        else:
            # 关联用户自定义柱子
            piller_mesh = bpy.data.objects.get(piller_source)
        
        # 按柱网坐标系分布柱子
        offset_x = x_rooms * room_space / 2
        offset_y = y_rooms * room_space / 2
        for y in range(y_rooms + 1):
            for x in range(x_rooms + 1):
                # 统一命名为“柱.x/y”，以免更换不同柱时，柱网中的名称无法匹配
                piller_copy_name = "柱" + \
                    '.' + str(x) + '/' + str(y)
                
                # 验证是否已被用户手工减柱
                piller_list_str = dataset.piller_net
                if piller_copy_name not in dataset.piller_net \
                        and piller_list_str != "" :
                    print("PP: piller skiped " + piller_copy_name)
                    continue

                # 复制柱子，仅instance，包含modifier
                piller_copy = chinarchCopy(
                    sourceObj = piller_mesh,
                    name = piller_copy_name,
                    locX = x * room_space - offset_x,
                    locY = y * room_space - offset_y,
                    locZ = piller_mesh.location.z,
                    parentObj = root_obj,
                    linkCollection = coll_name
                )

                # 复制柱础 ## 柱础选择暂时在UI上已隐藏，此逻辑暂时无用
                # 但仍未想好柱子和柱础是否要分开
                piller_base_source = dataset.piller_base_source
                if piller_base_source != '' :
                    piller_base_obj = bpy.data.objects.get(piller_base_source)
                    piller_base_copy = chinarchCopy(
                        sourceObj = piller_base_obj,
                        name = "柱础",
                        locX = x * room_space - offset_x,
                        locY = y * room_space - offset_y,
                        locZ = piller_base_obj.location.z,
                        parentObj = root_obj,
                        linkCollection = coll_name
                    )

        print("PP: finish")
        
        # 选择聚焦到根结点
        piller_mesh.select_set(False)
        root_obj.select_set(True)

        # 删除自动生成的基本立柱范本（默认在（0，0，0）坐标）
        if piller_mesh.name == basic_piller_name:
            bpy.data.objects.remove(piller_mesh)

        return {'FINISHED'}

# 复制对象（仅复制instance，包括modifier）
def chinarchCopy(sourceObj, name, locX, locY, locZ, parentObj, linkCollection):
    # 复制基本信息
    newObj = sourceObj.copy()
    newObj.name = name
    newObj.location.x = locX
    newObj.location.y = locY
    newObj.location.z = locZ
    newObj.parent = parentObj            
    bpy.data.collections[linkCollection].objects.link(newObj)

    # 复制modifier
    bpy.ops.object.select_all(action='DESELECT')
    sourceObj.select_set(True)
    bpy.context.view_layer.objects.active = sourceObj
    newObj.select_set(True)
    bpy.ops.object.make_links_data(type='MODIFIERS') 
    
    return newObj

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

# 保存柱网
# 用户可以手工减柱，然后在panel上点击“保存柱网”
# 下次重绘时，将根据保存的柱网列表重绘
class CHINARCH_OT_piller_net_save(bpy.types.Operator):
    bl_idname="chinarch.piller_net_save"
    bl_label = "保存柱网"
    bl_description: str = "保存已手工删除的柱子，避免重绘时覆盖"

    def execute(self, context): 
        dataset : chinarch_data.ChinarchData = \
            context.scene.chinarch_data
        piller_name = "柱"
        piller_net = ""     # 柱网清单
        for obj in bpy.data.objects:
            if piller_name in obj.name:
                piller_net += obj.name + ','

        print("PP: Save piller net:" + piller_net)
        dataset.piller_net = piller_net
        return {'FINISHED'}

# 重设柱网
# 丢弃手工减柱，全部重新生成
class CHINARCH_OT_piller_net_reset(bpy.types.Operator):
    bl_idname="chinarch.piller_net_reset"
    bl_label = "重设柱网"
    bl_description: str = "丢弃手工减柱，全部重新生成"

    def execute(self, context): 
        dataset : chinarch_data.ChinarchData = \
            context.scene.chinarch_data
        print("PP: Reset piller net")
        dataset.piller_net = ""
        
        # 调用重绘
        bpy.ops.chinarch.build()
        return {'FINISHED'}

# 类模板
class CHINARCH_OT_func_temp(bpy.types.Operator):
    bl_idname="chinarch.somefunc"
    bl_label = "类模板"

    def execute(self, context): 

        return {'FINISHED'}