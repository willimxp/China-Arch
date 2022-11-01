# Create by willimxp
# Blender插件，用以创建中式建筑

import bpy

# 创建一个Operator
class CHINAARCH_OT_hello(bpy.types.Operator):
   bl_idname="ppaddon.hello"
   bl_label = "hello"

   def execute(self, context):
     # 显示状态栏提示
     # s = "Hello, PP~"

     # 访问data
     currentlist = list(bpy.data.meshes)
     # s = ' '.join(map(str, currentlist))
     
     # 访问对象属性
     s = currentlist[0].name
     
     self.report({"INFO"} , s)

     # 设置对象位置
     bpy.context.scene.objects[0].location.x += 1.0

     return {'FINISHED'}