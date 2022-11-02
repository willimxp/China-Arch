# Create by willimxp
# 中式建筑插件 for blender


from email.mime import base
import bpy
from bpy_extras.object_utils import AddObjectHelper, object_data_add

# 根据基本参数，构建建筑体
class CHINARCH_OT_build(bpy.types.Operator, AddObjectHelper):
    bl_idname="chinarch.build"
    bl_label = "生成建筑外形"
   
    room_X = 4          # 面阔几间
    room_Y = 3          # 进深几间
    room_space = 3.0    # 间广几何
    base_Z = 0.5        # 台基多高
    piller_Z = 4.0      # 柱子多高

    def execute(self, context): 
        # 删除全部
        print("PP: delete all")
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)

        # 从data中读取用户通过Panel输入的值
        self.room_X = context.scene.room_x
        self.room_Y = context.scene.room_y
        self.base_Z = context.scene.base_z

        # 创建根对象（empty）
        print("PP: Build root")
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        root_obj = bpy.context.object
        bpy.context.object.name = "中式建筑"
        # print("PP: " + bpy.context.object.name)

        # 创建地基
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
        bpy.context.object.name = "台基"
        bpy.context.object.parent = root_obj

        # 创建柱网
        print("PP: Build pillers")
        offset_x = self.room_X * self.room_space / 2
        offset_y = self.room_Y * self.room_space / 2
        for x in range(self.room_X+1):
            for y in range(self.room_Y+1):
                loc_x = x * self.room_space - offset_x
                loc_y = y * self.room_space - offset_y
                bpy.ops.mesh.primitive_cylinder_add(
                        vertices = 8, 
                        radius = 0.25, 
                        depth = self.piller_Z , 
                        end_fill_type='NGON', 
                        calc_uvs=True, 
                        enter_editmode=False, 
                        align='WORLD', 
                        location=(loc_x, loc_y, self.piller_Z/2), 
                        rotation=(0.0, 0.0, 0.0), 
                        scale=(1,1,1)
                    )
                bpy.context.object.name = "立柱"
                bpy.context.object.parent = root_obj

        print("PP: finish")

        return {'FINISHED'}
