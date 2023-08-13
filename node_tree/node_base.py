from typing import Any
import bpy
from bpy.types import NodeTree, NodeSocket
from bpy.app.handlers import persistent
from ..operator import ops
from ..props import props
import datetime
import random


'''
这个文件定义了
NodeTree树类 Node基类 Socket接口类 
每个类前面还有自己要用的函数/类

基类是新增的节点的基类
socket接口是对原生socket的补充
树类本质就是窗口，也可以是一个巨大节点的内部
树类与socket类需要注册 node不要注册会报错 socket没写好也不要注册

我这个节点系统因为使用了输出socket的默认值作为中转
因此是不能做输出socket的prop绘制的
遇到纯输出节点需要使用内部变量来中转到输出socket
'''

TREE_NAME = 'IMGTREE_SYS'  # 节点树系统注册进去的代号
TREE_TYPE = 'ImgNodeTree'  # 节点树系统的标识符idname


class ImageNodeTree(NodeTree):  #
    '''Tree类型,新建到editor type'''
    bl_idname = TREE_TYPE
    bl_label = "图像节点 Image Nodes"  # 界面显示名
    bl_icon = 'TEXTURE'

    @classmethod
    def poll(self, context):  # 什么时候能进去编辑器
        return True


class ImageNode:  # 新建节点基类
    '''定义一些基本功能,续写先super'''
    stat: bpy.props.FloatProperty(
        name="stat", precision=4, soft_max=1, soft_min=-1)

    link_type: bpy.props.StringProperty(name="拓补", default="alone")
    debug: bpy.props.BoolProperty(name="调试", default=False)
    auto_process: bpy.props.BoolProperty(
        name="自动", default=True)

    base_color: bpy.props.FloatVectorProperty(
        name="默认类型", size=3, subtype="COLOR", default=(0.191, 0.061, 0.012))  # 可以在子类修改
    bug_color: bpy.props.FloatVectorProperty(
        name="link连接bug", size=3, subtype="COLOR", default=(1, 0, 0))
    bug_text: bpy.props.StringProperty(name="Bug详情", default="No bug")
    is_bug: bpy.props.BoolProperty(name="是否bug", default=False)

    is_preview: bpy.props.BoolProperty(name="是否预览图片", default=False)
    preview_type: bpy.props.BoolProperty(name="是否正在预览", default=True)
    prev_img: bpy.props.PointerProperty(type=bpy.types.Image)
    preview_scale: bpy.props.FloatProperty(
        name="预览缩放/动态", default=40)
    preview_scale_default: bpy.props.FloatProperty(
        name="预览默认缩放", default=40)

    default_width: bpy.props.FloatProperty(default=140)
    default_heigh: bpy.props.FloatProperty(default=100)

    def size2default(self):
        self.width = self.default_width
        self.height = self.default_heigh

    def init(self):
        self.use_custom_color = True  # 开启自定义颜色
        self.color = self.base_color  # 设置颜色为自己的默认
        self.size2default()  # 设置大小为自己的默认

    def draw_label(self):
        '''定义如何动态标签,blender原生'''
        return f"{self.name}"

    def draw_buttons(self, context, layout):
        '''定义如何绘制节点按钮,blender原生'''
        # 绘制小工具栏
        # ----------------------------------------------------------------------------
        main_row = layout.row(align=False)  # 常用按钮显示

        # 左侧按钮
        row_L = main_row.row(align=True)
        row_L.alignment = 'LEFT'
        if self.is_bug:
            row_L.label(icon="ERROR",)
        row_L.prop(self, "debug", text="", toggle=True, icon="FILE_SCRIPT")
        if self.is_preview:
            if self.preview_type:
                row_L.prop(self, "preview_type", text="",
                           toggle=True, icon="HIDE_OFF")
            else:
                row_L.prop(self, "preview_type", text="",
                           toggle=True, icon="HIDE_ON")

        # 中心按钮
        row_C = main_row.row(align=True)
        SetDefaultSize = row_C.operator(
            ops.NodeSetDefaultSize.bl_idname, text="", icon="REMOVE")
        SetDefaultSize.node_name = self.name
        SetBiggerSize = row_C.operator(
            ops.NodeSetBiggerSize.bl_idname, text="", icon="ADD")
        SetBiggerSize.node_name = self.name

        # 右侧按钮
        row_R = main_row.row(align=True)
        row_R.alignment = 'RIGHT'
        row_R.prop(self, "auto_process", text="", toggle=True, icon="LINKED")
        refresh = row_R.operator(
            ops.NodeRootProcess.bl_idname, text="", icon="FILE_REFRESH")
        refresh.node_name = self.name

        if self.debug:  # debug显示

            # stat与拓补
            row = layout.row()
            row.label(text=f"状态 : {self.stat*10000:.0f}")
            row.label(text=f"拓补 : {self.link_type}")

            # bug描述
            layout.label(text=f"bug类型:{self.bug_text}")

            # 全部socket的默认值
            try:
                for out_socket in self.outputs:
                    if out_socket.ho_type in [""]:
                        continue
                    row = layout.row(align=False)
                    row.alignment = 'RIGHT'
                    row.label(
                        text=f"{out_socket.name} : {out_socket.socket_value}")
                    row.label(icon="FORWARD")
                for in_socket in self.inputs:
                    if out_socket.ho_type in [""]:
                        continue
                    row = layout.row(align=False)
                    row.alignment = 'LEFT'
                    row.label(icon="BACK")  # 输入socket自身值显示
                    row.label(
                        text=f"{in_socket.name} : {in_socket.socket_value}")
            except Exception:
                layout.label(text="socket不能预览")

        # ----------------------------------------------------------------------------
        # 绘制预览图
        if self.preview_type and self.prev_img is not None:
            img = self.prev_img
            draw_img = layout.column()
            draw_img.template_icon(img.preview.icon_id,
                                   scale=self.preview_scale)
        # ----------------------------------------------------------------------------

    def process(self):
        '''需要续写'''
        if self.debug:
            self.stat = random.random()

    def root_process(self, is_force_ops=False, is_linkError_check=False):
        '''
        若自动更新则
        root运行
        传递下游process
        '''
        self.bug_text = "No bug"  # 清空bug记录
        if not self.auto_process:  # 没开自动更新，也不是强制就跳过
            if not is_force_ops:
                return
        if is_linkError_check:  # 刷新时会开这个
            nodes_linkError_check([self])

        try:
            self.process()  # 尝试运行，报错切换，终止传递
        except Exception:
            self.bug_text = "process失败"
            return

        for output in self.outputs:  # 遍历所有的输出接口的所有link传递root_process
            try:
                for link in output.links:
                    tn = link.to_node
                    tn.root_process()
            except:
                continue

    @classmethod
    def poll(cls, context):
        '''规定是否在节点集合中显示，无用'''
        return True


def socket_prop_update(self, context):
    '''接口prop更新'''
    if self.is_output:  # 输出接口总不触发process
        return
    # 开了预览的节点总运算
    if self.node.is_preview or self.node.link_type in ["trans", "root"]:
        self.node.root_process(is_linkError_check=False)
        return


class SocketFloat(NodeSocket):
    '''
    socket_value    :   区别于bl的default_value的属性,运算唯一调用的接口
    ho_type         :   区别于bl的type的属性,运算前linkerror检查的调用接口
    不能定义有值的成员变量，注册不通过，并且创建时会被替换为默认
    新建socket的name参数传进来的位置是text
    default_value不要动,type也不要动,实例化后type修改直接改变socket类
    '''
    bl_idname = 'HO_SocketFloat'
    bl_label = "Hollow Socket Float"
    socket_value: bpy.props.FloatProperty(
        default=0.0, update=socket_prop_update)
    ho_type: bpy.props.StringProperty(
        default="VALUE")

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return (0.6, 0.6, 0.6, 1)  # 灰色


class SocketImageColor(NodeSocket):
    '''socket类中,如果socket_value是一个指针变量,我们在这里访问会始终得到None'''
    bl_idname = 'HO_SocketImage'
    bl_label = "Hollow Socket Image/point node_group.imagePool[name]"

    socket_value: bpy.props.StringProperty(
        update=socket_prop_update)  # 传递imgPool中的name/img_id两者相同

    ho_type: bpy.props.StringProperty(
        default="IMAGE")

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked or self.hide_value:
            layout.label(text=text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return (0.13, 0.06, 1, 1)  # 蓝色

# -------------------------------------------------------------
# 检查相关


def nodes_topo_check(nodes):
    '''遍历检查节点列表的拓补结构,修改节点link_type'''
    for node in nodes:
        if len(node.inputs) != 0 and len(node.outputs) != 0:  # 首尾都有socket
            is_inputs_anyLinked = any(s.is_linked for s in node.inputs)
            is_outputs_anyLinked = any(s.is_linked for s in node.outputs)
            if is_inputs_anyLinked and is_outputs_anyLinked:
                node.link_type = "trans"  # 运输
                continue
            if (not is_inputs_anyLinked) and (not is_outputs_anyLinked):
                node.link_type = "alone"  # 孤立
                continue
            if (not is_inputs_anyLinked) and is_outputs_anyLinked:
                node.link_type = "root"  # 根
                continue
            else:
                node.link_type = "crown"  # 冠
                continue
        if len(node.inputs) == 0 and len(node.outputs) != 0:  # 无首socket
            is_outputs_anyLinked = any(s.is_linked for s in node.outputs)
            if is_outputs_anyLinked:
                node.link_type = "root"  # 根
                continue
            else:
                node.link_type = "alone"  # 孤立
                continue
        if len(node.inputs) != 0 and len(node.outputs) == 0:  # 无尾socket
            is_inputs_anyLinked = any(s.is_linked for s in node.inputs)
            if is_inputs_anyLinked:
                node.link_type = "crown"  # 冠
                continue
            else:
                node.link_type = "alone"  # 孤立
                continue
        node.link_type = "alone"  # 无首无尾 孤立


def node_bug_switch(node):
    '''切换node到bug状态'''
    node.color = node.bug_color
    node.is_bug = True


def node_nobug_switch(node):
    '''切换node到正常状态'''
    node.color = node.base_color
    node.is_bug = False


def nodes_linkError_check(nodes, bug_only=False):
    '''遍历检查所有节点是否有linkerror'''
    for node in nodes:
        try:
            if bug_only and not node.is_bug:
                # bug_only跳过正常node
                continue
            '''检查linkError'''
            node.check_node_ho_type()
            node_nobug_switch(node)
        except Exception:
            node.bug_text = "LinkError"
            node_bug_switch(node)
            continue


def node_topu_link(bug_only=False):
    '''若有新建link则
    拓补检查,linkError检查(全员检查)
    运行根节点
    '''
    nodes = bpy.context.space_data.node_tree.nodes
    nodes_topo_check(nodes)
    nodes_linkError_check(nodes, bug_only=bug_only)

    for node in nodes:
        if node.link_type == "root":
            node.root_process(is_linkError_check=True)


def node_topu_cut(bug_only=True):
    '''若有切断link则
    拓补检查,linkError检查(只检查bug)
    '''
    nodes = bpy.context.space_data.node_tree.nodes
    nodes_topo_check(nodes)
    nodes_linkError_check(nodes, bug_only=bug_only)


def node_topu_delete():
    '''若删除node则
    拓补检查
    '''
    nodes = bpy.context.space_data.node_tree.nodes
    nodes_topo_check(nodes)


def node_topu_select():
    '''若选择node则'''
    pass


@persistent
def update_on_links(context):
    '''拓补关系变化监听,装饰器是为了常开,见bpy.app.handlers文档'''
    try:  # 防止拿不到名字
        ops_name = bpy.context.active_operator.name
        tree_type = bpy.context.space_data.node_tree.bl_idname
        if tree_type == TREE_TYPE:  # 不在我的tree不运行
            print(ops_name)
            if ops_name == 'Cut Links':
                node_topu_cut()
                return
            if ops_name == 'Link Nodes':
                node_topu_link()
                return
            if ops_name == 'Select':
                node_topu_select()
                return
            if ops_name == 'Delete':
                node_topu_delete()
                return
    except:
        pass


clss = [ImageNodeTree, SocketFloat, SocketImageColor
        ]


def register():
    try:
        for i in clss:
            bpy.utils.register_class(i)
        bpy.app.handlers.depsgraph_update_post.append(
            update_on_links)  # 挂载ops监听到界面深度图
    except Exception:
        print("node_base load failed!!!")


def unregister():
    for i in clss:
        bpy.utils.unregister_class(i)
    bpy.app.handlers.depsgraph_update_post.clear()  # 卸载ops监听从界面深度图
