# Create by willimxp
# 中式建筑插件 for blender
# 构建逻辑类
# 根据输入的数据参数，按照《营造法式》，完成建筑体的自动建模

import math
import bpy
from bpy_extras.object_utils import AddObjectHelper
from mathutils import Vector
from . import data

# 柱网坐标，在全局共用
net_x=[]
net_y=[]

# 隐藏对象，包括viewport和render渲染
def hideObj(object:bpy.types.Object) : 
    object.hide_set(True)          # 隐藏“眼睛”，暂时隐藏
    object.hide_viewport = True    # 隐藏“屏幕”，不含在viewport中
    object.hide_render = True      # 隐藏“相机”，不渲染

# 复制对象（仅复制instance，包括modifier）
def chinarchCopy(sourceObj:bpy.types.Object, name, 
        locX, locY, locZ, parentObj:bpy.types.Object):
    # 强制原对象不能隐藏
    IsHideViewport = sourceObj.hide_viewport
    sourceObj.hide_viewport = False
    IsHideRender = sourceObj.hide_render
    sourceObj.hide_render = False
    
    # 复制基本信息
    newObj:bpy.types.Object = sourceObj.copy()
    newObj.name = name
    newObj.location.x = locX
    newObj.location.y = locY
    newObj.location.z = locZ
    newObj.parent = parentObj
    bpy.context.collection.objects.link(newObj) 

    # 复制modifier
    bpy.ops.object.select_all(action='DESELECT')
    sourceObj.select_set(True)
    bpy.context.view_layer.objects.active = sourceObj
    newObj.select_set(True)
    bpy.ops.object.make_links_data(type='MODIFIERS') 

    # 恢复原对象的隐藏属性
    sourceObj.hide_viewport = IsHideViewport
    sourceObj.hide_render = IsHideRender
    
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

# 刷新viewport，避免长时间卡死，并可见到建造过程
def redrawViewport():
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

# 新建或找到china_arch目录
# 所有对象建立在china_arch目录下，以免误删用户自建的模型
def getCollection(context:bpy.types.Context, name:str, isRedraw:bool):
    coll_name = name  # 在大纲中的目录名称
    coll_found = False
    coll = bpy.types.Collection
    for coll in context.scene.collection.children:
        # 在有多个scene时，名称可能是“china_arch.001”
        if str.find(coll.name,coll_name) >= 0:
            coll_found = True
            coll_name = coll.name
            break   # 找到第一个匹配的目录

    if not coll_found:    
        # 新建collection，不与其他用户自建的模型打架
        print("PP: Add new collection " + coll_name)
        coll = bpy.data.collections.new(coll_name)
        context.scene.collection.children.link(coll)
        # 聚焦到新目录上
        context.view_layer.active_layer_collection = \
            context.view_layer.layer_collection.children[-1]
    else:
        if isRedraw :
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
    
    # 返回china_arch目录的对象
    return coll

# 计算两个点之间距离
# 使用blender提供的mathutils库中的Vector类
# https://sinestesia.co/blog/tutorials/calculating-distances-in-blender-with-python/
def getVectorDistance(point1: Vector, point2: Vector) -> float:
    """Calculate distance between two points.""" 
    return (point2 - point1).length

# 根据基本参数，构建建筑体
class CHINARCH_OT_build_piller(bpy.types.Operator, AddObjectHelper):
    bl_idname="chinarch.buildpiller"
    bl_label = "生成柱网层"

    def execute(self, context): 
        # 从data中读取用户通过Panel输入的值
        dataset : data.CHINARCH_scene_data = \
            context.scene.chinarch_data
        
        # 1、创建china_arch collection集合
        # 所有对象建立在china_arch目录下，以免误删用户自建的模型
        root_coll = getCollection(context, "ca铺作层" ,True) #清空目录
        root_coll = getCollection(context, "ca屋顶层" ,True) #清空目录
        root_coll = getCollection(context, "ca柱网层" ,True)        

        # 2、创建根对象（empty）===========================================================
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        root_obj = context.object
        root_obj.name = "柱网层"
        root_obj.location = (0,0,0)

        # 3、创建地基===========================================================
        print("PP: Build base")
        x_rooms = dataset.x_rooms   # 面阔几间
        y_rooms = dataset.y_rooms   # 进深几间
        base_border = 3.0   # 地基边框

        # 根据间数，计算台基宽度
        base_width = 0.0
        if x_rooms >=1:
            base_width += dataset.x_1   # 明间
        if x_rooms >=3:
            base_width += dataset.x_2 * 2   # 次间
        if x_rooms >=5:
            base_width += dataset.x_3 * 2   # 梢间
        if x_rooms >=7:
            base_width += dataset.x_4 * 2   # 尽间
        if x_rooms >=9:
            base_width += dataset.x_3 * (x_rooms-7) #更多梢间
        # 边框
        base_width += base_border

        # 根据间数，计算台基宽度
        base_length = 0.0
        if y_rooms >=1:
            base_length += dataset.y_1 * (2 - y_rooms % 2)  # 明间
        if y_rooms >=3:
            base_length += dataset.y_2 * 2   # 次间
        if y_rooms >=5:
            base_length += dataset.y_3 * 2   # 梢间
        
        base_length += base_border  # 边框
        z_base = dataset.z_base     # 台基多高

        # 默认矩形台基
        baseObj = bpy.types.Object
        if dataset.base_source == '':
            bpy.ops.mesh.primitive_cube_add(
                size=1.0, 
                calc_uvs=True, 
                enter_editmode=False, 
                align='WORLD', 
                location=(0.0, 0.0, z_base/-2), 
                rotation=(0.0, 0.0, 0.0), 
                scale=(base_width, base_length, z_base))
            context.object.name = "台基"
            context.object.chinarch_obj = True
            context.object.parent = root_obj
            baseObj = context.object
        # 关联外部台基资产
        else:
            baseObj = context.scene.objects.get(dataset.base_source)
            baseObj.scale.x = base_width / baseObj.dimensions.x * baseObj.scale.x
            baseObj.scale.y = base_length / baseObj.dimensions.y * baseObj.scale.y
            # apply scale
            baseObj.select_set(True)
            bpy.ops.object.transform_apply(scale=True)

        # 关联外部踏道资产
        if dataset.step_source != '' :
            stepObj:bpy.types.Object = context.scene.objects.get(dataset.step_source)
            stepObj.location.x = 0
            stepObj.location.y = -(base_length / 2 + stepObj.dimensions.y / 2)
            stepObj.location.z = baseObj.location.z - stepObj.dimensions.z / 2
            stepObj.dimensions.z = baseObj.dimensions.z
        
        redrawViewport()

        # 4、创建柱网===========================================================
        print("PP: Build pillers")
        basic_piller_name = "基本立柱"
        piller_Z = 4.0      # 柱子多高
        piller_source = dataset.piller_source # 关联的柱子对象
        # 是否用户有自定义柱子？
        print("PP: Piller_source=" + piller_source)

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
        
        # 构造柱网X坐标序列，罗列了1，3，5，7，9，11间的情况，未能抽象成通用公式
        global net_x
        net_x = []  # 重新计算
        if x_rooms >=1:     # 明间
            offset = dataset.x_1 / 2
            net_x.append(offset)
            net_x.insert(0, -offset)
        if x_rooms >=3:     # 次间
            offset = dataset.x_1 / 2 + dataset.x_2
            net_x.append(offset)
            net_x.insert(0, -offset)  
        if x_rooms >=5:     # 梢间
            offset = dataset.x_1 / 2 + dataset.x_2 \
                    + dataset.x_3
            net_x.append(offset)
            net_x.insert(0, -offset)  
        if x_rooms >=7:     # 尽间
            offset = dataset.x_1 / 2 + dataset.x_2 \
                + dataset.x_3 + dataset.x_4
            net_x.append(offset)
            net_x.insert(0, -offset)  
        if x_rooms >=9:     #更多梢间
            offset = dataset.x_1 / 2 + dataset.x_2 \
                + dataset.x_3 * 2
            net_x[-1] = offset
            net_x[0]= -offset  
            offset = dataset.x_1 / 2 + dataset.x_2 \
                + dataset.x_3 *2 + dataset.x_4
            net_x.append(offset)
            net_x.insert(0, -offset) 
        if x_rooms >=11:     #更多梢间
            offset = dataset.x_1 / 2 + dataset.x_2 \
                + dataset.x_3 * 3
            net_x[-1] = offset
            net_x[0]= -offset  
            offset = dataset.x_1 / 2 + dataset.x_2 \
                + dataset.x_3 *3 + dataset.x_4
            net_x.append(offset)
            net_x.insert(0, -offset) 

        # 构造柱网Y坐标序列，罗列了1-5间的情况，未能抽象成通用公式
        global net_y
        net_y=[]    # 重新计算
        if y_rooms%2 == 1: # 奇数间
            if y_rooms >= 1:     # 明间
                offset = dataset.y_1 / 2
                net_y.append(offset)
                net_y.insert(0, -offset)
            if y_rooms >= 3:     # 次间
                offset = dataset.y_1 / 2 + dataset.y_2
                net_y.append(offset)
                net_y.insert(0, -offset)  
            if y_rooms >= 5:     # 梢间
                offset = dataset.y_1 / 2 + dataset.y_2 \
                        + dataset.y_3
                net_y.append(offset)
                net_y.insert(0, -offset) 
        else:   #偶数间
            if y_rooms >= 2:
                net_y.append(0)
                offset = dataset.y_1
                net_y.append(offset)
                net_y.insert(0,-offset)
            if y_rooms >= 4:
                offset = dataset.y_1 + dataset.y_2
                net_y.append(offset)
                net_y.insert(0,-offset)

        for y in range(y_rooms + 1):
            for x in range(x_rooms + 1):
                # 统一命名为“柱.x/y”，以免更换不同柱时，柱网中的名称无法匹配
                piller_copy_name = "柱" + \
                    '.' + str(x) + '/' + str(y)
                
                # 验证是否已被用户手工减柱
                piller_list_str = dataset.piller_net
                if piller_copy_name not in dataset.piller_net \
                        and piller_list_str != "" :
                    # print("PP: piller skiped " + piller_copy_name)
                    continue

                # 复制柱子，仅instance，包含modifier
                piller_copy = chinarchCopy(
                    sourceObj = piller_mesh,
                    name = piller_copy_name,
                    locX = net_x[x],
                    locY = net_y[y],
                    locZ = piller_mesh.location.z,
                    parentObj = root_obj
                )
                
                # # 复制柱础 ## 柱础选择暂时在UI上已隐藏，此逻辑暂时无用
                # # 但仍未想好柱子和柱础是否要分开
                # piller_base_source = dataset.piller_base_source
                # if piller_base_source != '' :
                #     piller_base_obj = bpy.data.objects.get(piller_base_source)
                #     piller_base_copy = chinarchCopy(
                #         sourceObj = piller_base_obj,
                #         name = "柱础",
                #         locX = x * room_space - offset_x,
                #         locY = y * room_space - offset_y,
                #         locZ = piller_base_obj.location.z,
                #         parentObj = root_obj
                #     )

                redrawViewport()

        # 柱高，为后续阑额定位使用
        pill_top = piller_mesh.dimensions.z

        # 删除自动生成的基本立柱范本（默认在（0，0，0）坐标）
        if piller_mesh.name == basic_piller_name:
            bpy.data.objects.remove(piller_mesh)
        else: # 隐藏参考柱
            piller_mesh.hide_set(True)          # 隐藏“眼睛”，暂时隐藏
            piller_mesh.hide_viewport = True    # 隐藏“屏幕”，不含在viewplayer中
            piller_mesh.hide_render = True      # 隐藏“相机”，不渲染

        # 5、生成阑额，基于柱网坐标 ===========================================================
        lane_length = 0    # 阑额长度
        lane_height = 0.45     # 默认阑额高度
        lane_thicken = 0.3     # 默认阑额厚度
        lane_gap = 0.3         # 阑额间距（约为一柱宽）
        
        # 生成X轴向阑额
        ny = 0
        n = 0 # 标志重新开始循环
        x_pre = 0       # 上一个柱点
        x_next = 0      # 下一个柱点
        x_now = 0       # 阑额中点
        for y in net_y :
            # 只生成外圈阑额，内部阑额需要根据地盘确定
            if ny not in [0,1,len(net_y)-2,len(net_y)-1]:  
                pass
            else : 
                for x in net_x :
                    if n == 0 :
                        x_pre = x
                        n += 1
                    else:
                        x_next = x
                        
                        # 创建阑额
                        lane_length = x_next - x_pre - lane_gap
                        x_now = x_next - (x_next - x_pre) / 2
                        x_zcord = pill_top - lane_height / 2
                        
                        if dataset.lane_source == '' :
                            bpy.ops.mesh.primitive_cube_add(
                                size=1.0, 
                                calc_uvs=True, 
                                enter_editmode=False, 
                                align='WORLD', 
                                location=(x_now, net_y[ny], x_zcord), 
                                rotation=(0.0, 0.0, 0.0), 
                                scale=(lane_length, lane_thicken, lane_height))
                            context.object.name = "阑额"
                            context.object.chinarch_obj = True
                            context.object.parent = root_obj
                        else :
                            lane_obj = bpy.data.objects.get(dataset.lane_source)
                            lane_copy = chinarchCopy(
                                sourceObj = lane_obj,
                                name = "阑额",
                                locX = x_now,
                                locY = net_y[ny],
                                locZ = x_zcord,
                                parentObj = root_obj
                                )
                            lane_copy.scale.x = lane_length / lane_copy.dimensions.x
                        # 向上传递旧坐标
                        x_pre = x

                        redrawViewport()
                    # end if x_pre == 0
                # end for x
            ny += 1
            n = 0
            # end if ny in []
        # end for y

        # 生成Y轴向阑额
        nx = 0
        n = 0 # 标志重新开始循环
        y_pre = 0       # 上一个柱点
        y_next = 0      # 下一个柱点
        y_now = 0       # 阑额中点
        for x in net_x :
            # 只生成外圈阑额，内部阑额需要根据地盘确定
            if nx not in [0,1,len(net_x)-2,len(net_x)-1]:  
                pass
            else : 
                for y in net_y :
                    if n == 0:
                        y_pre = y
                        n += 1
                    else:
                        y_next = y
                        
                        # 创建阑额
                        lane_length = y_next - y_pre - lane_gap
                        # print("PP: x=" + str(x) + " y=" + str(y) + " length=" + str(lane_length))
                        y_now = y_next - (y_next - y_pre) / 2
                        y_zcord = pill_top - lane_height / 2
                        
                        if dataset.lane_source == '' :
                            bpy.ops.mesh.primitive_cube_add(
                                size=1.0, 
                                calc_uvs=True, 
                                enter_editmode=False, 
                                align='WORLD', 
                                location=(net_x[nx],y_now, y_zcord), 
                                rotation=(0.0, 0.0, 0.0), 
                                scale=(lane_thicken, lane_length, lane_height))
                            context.object.name = "阑额"
                            context.object.chinarch_obj = True
                            context.object.parent = root_obj
                        else :
                            lane_obj = bpy.data.objects.get(dataset.lane_source)
                            lane_copy = chinarchCopy(
                                sourceObj = lane_obj,
                                name = "阑额",
                                locX = net_x[nx],
                                locY = y_now,
                                locZ = y_zcord,
                                parentObj = root_obj
                                )
                            lane_copy.scale.x = lane_length / lane_copy.dimensions.x
                            lane_copy.rotation_euler.z = math.radians(90)
                        # 向上传递旧坐标
                        y_pre = y

                        redrawViewport()
                    # end if x_pre == 0
                # end for x
            nx += 1
            n = 0
            # end if ny in []
        # end for y
        
        # 隐藏参考阑额
        if dataset.lane_source != '' :
            hideObj(lane_obj)

        

        # 选择聚焦到根结点
        root_obj.select_set(True)

        return {'FINISHED'}

# 构建铺作层
class CHINARCH_OT_build_puzuo(bpy.types.Operator):
    bl_idname="chinarch.buildpuzuo"
    bl_label = "构建铺作"

    def execute(self, context): 
        # 从data中读取用户通过Panel输入的值
        dataset : data.CHINARCH_scene_data = \
            context.scene.chinarch_data
        global net_x
        global net_y
        if len(net_x) == 0:
            bpy.ops.chinarch.buildpiller()

        # 1、创建china_arch collection集合
        # 所有对象建立在china_arch目录下，以免误删用户自建的模型
        root_coll = getCollection(context,"ca铺作层",True)  

        # 2、创建根对象（empty）===========================================================
        if dataset.piller_source != '' :
            pillerObj:bpy.types.Object = context.scene.objects.get(dataset.piller_source)
        pill_top = pillerObj.dimensions.z

        # 默认无普拍枋时，铺作直接坐于柱头
        puzuo_base = pill_top   
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        root_obj = context.object
        root_obj.name = "铺作层"
        root_obj.location = (0,0,puzuo_base)

        # 3、布置铺作======================================================
        

        if dataset.puzuo_corner_source != '':
            # 转角铺作
            puzuoCornerObj:bpy.types.Object = context.scene.objects.get(dataset.puzuo_corner_source)
            # 四个角柱坐标
            puzuoCornerArray = [
                [net_x[-1], net_y[0]],
                [net_x[-1], net_y[-1]],
                [net_x[0], net_y[-1]],
                [net_x[0], net_y[0]]
            ]
            for n in range(len(puzuoCornerArray)) :
                puzuoCornerCopy:bpy.types.Object = chinarchCopy(
                    sourceObj = puzuoCornerObj,
                    name = "转角铺作",
                    locX = puzuoCornerArray[n][0],
                    locY = puzuoCornerArray[n][1],
                    locZ = 0,
                    parentObj = root_obj
                    )
                puzuoCornerCopy.rotation_euler.z = math.radians(n * 90)
                redrawViewport()
            # 隐藏参考铺作
            hideObj(puzuoCornerObj)
            
        # 四面柱头铺作
        if dataset.puzuo_piller_source != '':
            puzuoPillerObj:bpy.types.Object = context.scene.objects.get(dataset.puzuo_piller_source)
            # 下侧
            for n in range(len(net_x)-2) : 
                puzuoPillerCopy:bpy.types.Object = chinarchCopy(
                    sourceObj = puzuoPillerObj,
                    name = "柱头铺作",
                    locX = net_x[n+1],
                    locY = net_y[0],
                    locZ = 0,
                    parentObj = root_obj
                    )
                redrawViewport()
            # 右侧
            for n in range(len(net_y)-2) : 
                puzuoPillerCopy:bpy.types.Object = chinarchCopy(
                    sourceObj = puzuoPillerObj,
                    name = "柱头铺作",
                    locX = net_x[-1],
                    locY = net_y[n+1],
                    locZ = 0,
                    parentObj = root_obj
                    )
                puzuoPillerCopy.rotation_euler.z = math.radians(90)
                redrawViewport()
            # 上侧
            for n in range(len(net_x)-2) : 
                puzuoPillerCopy:bpy.types.Object = chinarchCopy(
                    sourceObj = puzuoPillerObj,
                    name = "柱头铺作",
                    locX = net_x[-n-2],
                    locY = net_y[-1],
                    locZ = 0,
                    parentObj = root_obj
                    )
                puzuoPillerCopy.rotation_euler.z = math.radians(180)
                redrawViewport()
            # 左侧
            for n in range(len(net_y)-2) : 
                puzuoPillerCopy:bpy.types.Object = chinarchCopy(
                    sourceObj = puzuoPillerObj,
                    name = "柱头铺作",
                    locX = net_x[0],
                    locY = net_y[-n-2],
                    locZ = 0,
                    parentObj = root_obj
                    )
                puzuoPillerCopy.rotation_euler.z = math.radians(270)
                redrawViewport()            
            # 隐藏参考铺作
            hideObj(puzuoPillerObj)
        
        # 四面补间铺作
        if dataset.puzuo_fillgap_source != '' :
            puzuoFillObj:bpy.types.Object = context.scene.objects.get(dataset.puzuo_fillgap_source)
            # 下侧
            for n in range(len(net_x)-1) : 
                puzuoFillCopy:bpy.types.Object = chinarchCopy(
                    sourceObj = puzuoFillObj,
                    name = "补间铺作",
                    locX = (net_x[n] + net_x[n+1])/2,
                    locY = net_y[0],
                    locZ = 0,
                    parentObj = root_obj
                    )
                redrawViewport()
            # 右侧
            for n in range(len(net_y)-1) : 
                puzuoFillCopy:bpy.types.Object = chinarchCopy(
                    sourceObj = puzuoFillObj,
                    name = "补间铺作",
                    locX = net_x[-1],
                    locY = (net_y[n] + net_y[n+1])/2,
                    locZ = 0,
                    parentObj = root_obj
                    )
                puzuoFillCopy.rotation_euler.z = math.radians(90)
                redrawViewport()
            # 上侧
            for n in range(len(net_x)-1) : 
                puzuoFillCopy:bpy.types.Object = chinarchCopy(
                    sourceObj = puzuoFillObj,
                    name = "补间铺作",
                    locX = (net_x[-1-n] + net_x[-2-n])/2,
                    locY = net_y[-1],
                    locZ = 0,
                    parentObj = root_obj
                    )
                puzuoFillCopy.rotation_euler.z = math.radians(180)
                redrawViewport()    
            # 左侧
            for n in range(len(net_y)-1) : 
                puzuoFillCopy:bpy.types.Object = chinarchCopy(
                    sourceObj = puzuoFillObj,
                    name = "补间铺作",
                    locX = net_x[0],
                    locY = (net_y[-1-n] + net_y[-2-n])/2,
                    locZ = 0,
                    parentObj = root_obj
                    )
                puzuoFillCopy.rotation_euler.z = math.radians(270)
                redrawViewport()             
            # 隐藏参考铺作
            hideObj(puzuoFillObj)

        return {'FINISHED'}

# 构建屋顶层
class CHINARCH_OT_build_roof(bpy.types.Operator):
    bl_idname="chinarch.buildroof"
    bl_label = "构建屋顶"

    def execute(self, context): 
        # 从data中读取用户通过Panel输入的值
        dataset : data.CHINARCH_scene_data = \
            context.scene.chinarch_data

        # 1、创建china_arch collection集合
        # 所有对象建立在china_arch目录下，以免误删用户自建的模型
        getCollection(context,"ca屋顶层",True)  

        # 获取全局参数，柱网坐标
        global net_x
        global net_y
        if len(net_x) == 0:
            bpy.ops.chinarch.buildpiller()
            bpy.ops.chinarch.buildpuzuo()
            # 将焦点重新聚到屋顶层
            root_coll = getCollection(context,"ca屋顶层",True)          

        # 2、创建根对象（empty）===========================================================
        roof_base = dataset.roof_base   # 屋顶起始高度，撩风槫中点
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        root_obj = context.object
        root_obj.name = "屋顶层"
        root_obj.location = (0,0,roof_base)

        # 3、计算槫子的坐标列表============================================================
        # 用户自定义屋顶参数
        roof_height = dataset.roof_height   # 举高            
        roof_extend = dataset.roof_extend   # 斗栱出跳
        #rafter_count = dataset.rafter_count # 椽架数
        rafter_count = int(dataset.rafter_count_select)
        hill_extend = 1.5   # 两厦出际，殿堂为1椽，厅堂为3～5尺，这里简化为固定值

        # 根据柱网，计算屋的总宽，总深
        room_width = net_x[-1] - net_x[0]  # 屋宽
        room_length = net_y[-1] - net_y[0] # 屋深
        # 前后撩风槫距离=屋深+斗栱出跳x2
        eave_length = room_length + roof_extend*2
        eave_width = room_width + roof_extend*2
        # 椽架宽度=屋深/椽架数
        rafter_space = room_length / rafter_count
        rafter_extend = 0.6     # 槫子相交出头(两头一共) 

        # 槫子位置列表(x,y,z,length,rotation)
        purlin_pos = []
        # 椽子定位点，基于槫子的举折，便于后续布椽子(x,y,z)
        rafter_pos = []
        
        # 脊槫
        if rafter_count >= 6 :
            # 6架椽以上，山宽=屋宽-内转两侧各2椽+向外出际
            hill_width = room_width - rafter_space*4 + hill_extend 
        elif rafter_count >= 4 :
            # 4架椽以下，只转1椽
            hill_width = room_width - rafter_space*2 + hill_extend
        else : 
            # 2架椽一下，无歇山，有出际
            hill_width = room_width + hill_extend
        purlin_pos.append((0,0,roof_height,hill_width,0))
        rafter_pos.append((0,0,roof_height))

        # 平槫举折计算(4椽以上才有举折，2椽无举折)
        rafter_z = roof_height
        rafter_z_pre = roof_height # 迭代高度
        if rafter_count >= 4 :
            shift_var  = roof_height / 10   # 营造法式的举折量，可以调整该参数，改变曲率
            shift_time  = 2               # 举折公比，可以调整该参数，改变曲率
            for n in range(1,int(rafter_count/2)):
                # 椽架水平位置
                rafter_y = n * rafter_space
                # 举折高度，迭代
                rafter_z = rafter_z_pre \
                        - rafter_z_pre * 1/(rafter_count/2-(n-1)) \
                        - shift_var/(shift_time**(n-1))
                # 2椽以上的槫子为歇山宽度
                if n == rafter_count/2-1 and rafter_count >= 6 :
                    # 大于6椽，歇山转2椽，下平槫长度减1椽
                    rafter_length = room_width - rafter_space*2 + rafter_extend
                else: 
                    rafter_length = hill_width
                purlin_pos.append((0, rafter_y, rafter_z,rafter_length,0))
                purlin_pos.append((0, -rafter_y, rafter_z,rafter_length,0))
                rafter_pos.append((0, rafter_y, rafter_z))

                #山面平槫
                if (rafter_count/2 - n <= 2 and rafter_count >= 6) or \
                    (rafter_count/2 - n <= 1 and rafter_count >= 4):
                    # 6椽架以上，山面下平槫，下平槫减1椽
                    # 4椽架以下，平槫减1椽
                    rafter_x = room_width/2 - rafter_space*(rafter_count/2-n)
                    rafter_length = room_length - rafter_space*2*(rafter_count/2-n) + rafter_extend
                    purlin_pos.append((rafter_x, 0, rafter_z,rafter_length,90))
                    purlin_pos.append((-rafter_x, 0, rafter_z,rafter_length,90))                

                # 为下一次迭代保存当前高度
                rafter_z_pre = rafter_z
        
        # 牛脊槫，位于柱头上方，在撩檐枋和平槫的连接线上
        piller_tuan_y = room_length/2
        piller_tuan_z = rafter_z*roof_extend / (roof_extend+rafter_space)
        # 牛脊槫长=屋宽+斗栱出跳x2+槫子出头
        rafter_length = room_width + rafter_extend
        purlin_pos.append((0,piller_tuan_y,piller_tuan_z,rafter_length,0))
        purlin_pos.append((0,-piller_tuan_y,piller_tuan_z,rafter_length,0))
        # 山面牛脊槫
        piller_tuan_x = room_width/2
        rafter_length = room_length + rafter_extend
        purlin_pos.append((piller_tuan_x,0,piller_tuan_z,rafter_length,90))
        purlin_pos.append((-piller_tuan_x,0,piller_tuan_z,rafter_length,90))

        # 撩风槫
        rafter_length = eave_width + rafter_extend
        purlin_pos.append((0,eave_length/2,0,rafter_length,0))
        purlin_pos.append((0,-eave_length/2,0,rafter_length,0))
        rafter_pos.append((0,eave_length/2,0))
        # 山面撩风槫
        rafter_length = eave_length + rafter_extend
        purlin_pos.append((eave_width/2,0,0,rafter_length,90))
        purlin_pos.append((-eave_width/2,0,0,rafter_length,90))

        # 布置所有槫子
        if dataset.tuan_source != '' :
            tuanObj:bpy.types.Object = context.scene.objects.get(dataset.tuan_source)
            for pos in purlin_pos :
                tuanCopyObj = chinarchCopy(
                    sourceObj= tuanObj,
                    name="槫子",
                    locX=pos[0],
                    locY=pos[1],
                    locZ=pos[2],
                    parentObj=root_obj
                )
                tuanCopyObj.dimensions.x = pos[3]
                tuanCopyObj.rotation_euler.z = math.radians(pos[4])

            hideObj(tuanObj)

        # 布置椽子
        if dataset.rafter_source != '' :
            rafterObj:bpy.types.Object = context.scene.objects.get(dataset.rafter_source)
            point_pre = (0,0,0)
            for n in range(len(rafter_pos)) :
                if n == 0 :
                    point_pre = rafter_pos[0]
                else :
                    point = rafter_pos[n]
                    pX = (point_pre[0] + point[0]) /2
                    pY = (point_pre[1] + point[1]) /2
                    pZ = (point_pre[2] + point[2]) /2
                    rafterCopyObj = chinarchCopy(
                        sourceObj= rafterObj,
                        name="椽子",
                        locX = pX, locY = pY, locZ = pZ,
                        parentObj=root_obj
                    ) 
                    rafterCopyObj.dimensions.x = getVectorDistance(Vector(point),Vector(point_pre))
                    
                    # 根据起止点计算旋转角度
                    # https://blender.stackexchange.com/questions/194549/find-angles-between-list-of-sorted-vertices-using-vertex-co-angle
                    y_axis = Vector((0,1,0))
                    vec = Vector(point_pre) - Vector(point)
                    rotaion = math.degrees(y_axis.angle(vec))
                    rafterCopyObj.rotation_euler.y = math.radians(180-rotaion)
                    # 添加Array modifier
                    mod = rafterCopyObj.modifiers.new(name='array', type='ARRAY')
                    mod.count = 40
                    mod.relative_offset_displace[0] = 0
                    mod.relative_offset_displace[1] = 2
                    # 添加Mirror modifier
                    mod = rafterCopyObj.modifiers.new(name='mirror', type='MIRROR')
                    mod.use_axis[0] = True
                    mod.use_axis[1] = True
                    mod.mirror_object = root_obj
                    # 迭代到下一个循环
                    point_pre = point

            hideObj(rafterObj)

        return {'FINISHED'}

# 保存柱网
# 用户可以手工减柱，然后在panel上点击“保存柱网”
# 下次重绘时，将根据保存的柱网列表重绘
class CHINARCH_OT_piller_net_save(bpy.types.Operator):
    bl_idname="chinarch.piller_net_save"
    bl_label = "保存柱网"
    bl_description: str = "保存已手工删除的柱子，避免重绘时覆盖"

    def execute(self, context): 
        dataset : data.ChinarchData = \
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
        dataset : data.ChinarchData = \
            context.scene.chinarch_data
        print("PP: Reset piller net")
        dataset.piller_net = ""
        
        # 调用重绘
        bpy.ops.chinarch.buildpiller()
        return {'FINISHED'}

# 缩放构件材等
class CHINARCH_OT_level_scale(bpy.types.Operator):
    bl_idname="chinarch.level_scale"
    bl_label = "缩放构件材等"

    def execute(self, context): 
        # 根据《营造法式》定义的各材等尺寸
        dict_level = {
            '1':9,
            '2':8.25,
            '3':7.5,
            '4':7.2,
            '5':6.6,
            '6':6,
            '7':5.25,
            '8':4.5
        }
        scale_before = dict_level[str(context.object.chinarch_level)]
        scale_after = dict_level[context.object.chinarch_scale]
        scale_rate = scale_after/scale_before
        print("PP: 缩放材等 from " + str(context.object.chinarch_level) + "等（" \
            + str(scale_before) + "寸）" \
            + " to " + context.object.chinarch_scale + "等（" \
            + str(scale_after) + "寸）" \
            + str(scale_rate)
        )

        context.object.scale = (scale_rate,scale_rate,scale_rate)
        
        
        return {'FINISHED'}

# 类模板
class CHINARCH_OT_func_temp(bpy.types.Operator):
    bl_idname="chinarch.somefunc"
    bl_label = "类模板"

    def execute(self, context): 

        return {'FINISHED'}