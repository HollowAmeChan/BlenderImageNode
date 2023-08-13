import typing
import bpy
from bpy.types import Context, Operator
from bpy.types import Panel
#
#
#
# 这是一个备份
#
#
#
bl_info = {
    "name": "_Hollow_addon",
    "author": "Hollow_ame",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "Hollow",
    "description": "test",
    "warning": "",
    "wiki_url": "",
    "category": "Hollow",
}


class HollowOperator(Operator):
    bl_idname = "hollowoperator.operator"
    # 注意这里是小写，命名是操作实例名.operator
    bl_label = "这是一个随机抖动的操作"
    bl_description = "这是操作的描述"
    # 悬停的描述

    # def execute(self, context: Context) -> Set[str] | Set[int]:
    #     return super().execute(context)
    #     # 这是当操作被执行时调用的函数，所有的操作都是写在这里面的
    #     # 默认的补全是这样的，其实只需要传入self，context是上下文，默认返回也是上下文

    def execute(self, context):
        obj = bpy.context.object
        if not obj:
            return {"CANCELLED"}
        from random import random
        location = (random(), random(), random())
        obj.location = location
        return {"FINISHED"}
        # 自己写最简单的就这种形式
        # 要注意操作结束必须返回固定的内容之一，这里的两个就是其中之二
        # 可以看到bpy.context.object可以获得活动物体，以及他有location属性，这个属性是一个元组


class HollowPanel(Panel):
    bl_idname = "CATEGORY_PT_HollowPanel"  # 面板内部标识符,categrory可以自己改，不能动的是_PT_
    bl_label = "我的面板"  # 面板的标签（显示）
    bl_space_type = "VIEW_3D"  # 指定面板显示的窗口类型
    bl_region_type = "UI"  # 指定面板显示在指定类型下的区域
    bl_category = "HollowAddon"  # 在区域内的归类（VIEW_3D-UI下就是T面板的类）

    def draw(self, context):
        layout = self.layout
        layout.operator(HollowOperator.bl_idname)
        layout.operator("object.select_all", text="测试")


clss = [HollowOperator, HollowPanel]


def register():
    for i in clss:
        bpy.utils.register_class(i)


def unregister():
    for i in clss:
        bpy.utils.unregister_class(i)
# 卸载同样需要每个都卸载
