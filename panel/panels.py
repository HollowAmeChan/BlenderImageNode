import bpy
from bpy.types import Panel
from ..operator import ops


class HollowPanel(Panel):
    bl_idname = "VIEW_PT_HollowPanel"  # 面板内部标识符,categrory可以自己改，不能动的是_PT_
    bl_label = "我的面板"  # 面板的标签（显示）
    bl_space_type = "NODE_EDITOR"  # 指定面板显示的窗口类型
    bl_region_type = "UI"  # 指定面板显示在指定类型下的区域
    bl_category = "HollowAddon"  # 在区域内的归类（VIEW_3D-UI下就是T面板的类）

    def draw(self, context):
        layout = self.layout
        layout.operator(ops.RestartBlender.bl_idname)
        layout.operator(ops.RaiseInfo.bl_idname)
        layout.separator()
        layout.operator(ops.NodeRootProcess.bl_idname)


clss = [
    HollowPanel
]


def register():
    for i in clss:
        bpy.utils.register_class(i)


def unregister():
    for i in clss:
        bpy.utils.unregister_class(i)
