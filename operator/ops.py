import bpy
import sys
import os
import subprocess


class RaiseInfo(bpy.types.Operator):
    """
    抛出提示
    """
    bl_idname = "ho.raiseinfo"  # 注册到bpy.ops下,必须xx.开头,必须全部小写
    bl_label = "引发信息提示"
    info = "没有参数"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        self.report({'INFO'}, self.info)
        self.report({'INFO'},  bpy.context.space_data.tree_type)
        return {'FINISHED'}


class RestartBlender(bpy.types.Operator):
    bl_idname = "ho.restart_blender"
    bl_label = "快速重启"
    bl_description = "不保存重启"
    bl_options = {'REGISTER'}

    def execute(self, context):
        py = os.path.join(os.path.dirname(__file__), "console_toggle.py")
        filepath = bpy.data.filepath
        if (filepath != ""):
            subprocess.Popen([sys.argv[0], filepath, '-P', py])
        else:
            subprocess.Popen([sys.argv[0], '-P', py])
        bpy.ops.wm.quit_blender()
        return {'FINISHED'}


class NodeRootProcess(bpy.types.Operator):
    """用在节点里面的一个操作,绘制在节点基类上的小工具中"""
    bl_idname = "ho.noderootprocess"  # 注册到bpy.ops下
    bl_label = "作为根运行节点"

    node_name: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            node = bpy.context.space_data.node_tree.nodes[self.node_name]
            node.root_process(is_force_ops=True, is_linkError_check=True)
            return {'FINISHED'}
        except:
            return {'FINISHED'}


class NodeSetDefaultSize(bpy.types.Operator):
    bl_idname = "ho.nodesetdefaultsize"  # 注册到bpy.ops下
    bl_label = "恢复node默认大小"

    node_name: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            node = bpy.context.space_data.node_tree.nodes[self.node_name]
            node.size2default()
            node.preview_scale = node.preview_scale_default

            return {'FINISHED'}
        except:
            return {'FINISHED'}


class NodeSetBiggerSize(bpy.types.Operator):
    bl_idname = "ho.nodesetbiggersize"  # 注册到bpy.ops下
    bl_label = "加宽node/加宽预览图像"

    node_name: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            node = bpy.context.space_data.node_tree.nodes[self.node_name]
            node.width *= 2

            return {'FINISHED'}
        except:
            return {'FINISHED'}


clss = [RaiseInfo, RestartBlender, NodeRootProcess,
        NodeSetDefaultSize, NodeSetBiggerSize]


def register():
    try:
        for i in clss:
            bpy.utils.register_class(i)
    except Exception:
        print("ops load failed!!!")


def unregister():
    for i in clss:
        bpy.utils.unregister_class(i)
