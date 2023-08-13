from typing import Any
from bpy.types import Node
from .node_base import ImageNode, TREE_TYPE
import bpy
import struct
import datetime
import random

PREV_DICT = bpy.utils.previews.new()


def updateNodeProp(self, context):  # 必须传context
    '''
    节点内部prop的更新逻辑
    根节点prop更新作为根运行
    运输节点prop更新以自己为根运行

    这个东西有很大一部分程度是给纯输出节点用的
    他们需要prop中转,防止无限回调

    在这里写判断是不是linktype是因为做不到提取合并这个操作
    '''
    if self.link_type in ["root", "trans"]:
        self.root_process(is_linkError_check=False)


def addSocket(
    self,
    location: str in ["in", "out"] = "out",
    type='HO_SocketFloat',
    name="Float",
    hide=False,
    hide_value=False,
):
    '''
    一个简化的添加接口的函数
    专门用来添加HO节点的HO_socket,默认方形接口
    location        :   ["in","out"]            规定加接口的位置
    type            :   [HO_SocketType]         规定socket类,需要的是注册的类的bl_idname/原生socket类也行
    name            :   "Float"                 规定socket的索引名,获取socket可以node.input.get("name")
    hide            :   False
    '''

    if location == "out":
        s = self.outputs.new(type=type, name=name)
    if location == "in":
        s = self.inputs.new(type=type, name=name)
    s.display_shape = "SQUARE"
    s.hide = hide
    s.hide_value = hide_value
    return s


def check_ho_type(node, location: str in ["in", "out"], socket_name: str, need_ho_type: str):
    '''
    基本的检查ho_type,注意这是检查单socket,node依然要定义自己的完全检查check_node_ho_type
    '''
    if location == "in":
        socket = node.inputs.get(socket_name)  # 填入抓取socket
    else:
        socket = node.outputs.get(socket_name)

    for link in socket.links:
        if not hasattr(link.from_socket, "ho_type"):  # 没东西
            print("no ho_type")
            raise Exception
        if link.from_socket.ho_type != need_ho_type:  # 判错 填入对比的
            print("wrong type")
            raise Exception


def ListBytesPack(input):
    '''
    使用二进制打包解包加速传递,不然太慢了
    返回[bytes,len]
    input           :   打包对象|list/tuple    
    bytes           :   bytes结果
    len             :   打包长度
    '''
    length = len(input)
    bytes = struct.pack(f'{length}f', *input)
    return [bytes, length]


def ListBytesUnpack(bytes, length):
    '''
    二进制打包对应的解包
    bytes           :   解包对象
    len             :   解包长度
    返回解包内容
    '''
    return struct.unpack(f'{length}f', bytes)


def img_preview_HQupdate(img):
    '''强制将图像的icon替换为高清版本,preview的会自动生成'''
    img = img
    img.preview_ensure()
    prev = img.preview
    prev.image_size = img.size
    col = img.pixels[:]
    img.preview.image_pixels_float = col


class BaseNode(ImageNode, Node):
    bl_label = "基础节点"
    bl_idname = "HO_BaseNode"  # 注册名

    def init(self, context):
        '''定义新建节点时的操作,blender原生'''
        super().init()
        # 只能在这里新建(实例化)完了改socket的参数
        addSocket(self, "in", 'HO_SocketFloat', "Float")
        addSocket(self, "out", 'HO_SocketFloat', "Float")

    def draw_buttons(self, context, layout):  #
        '''定义如何绘制节点,blender原生'''
        # 绘制在进出socket中间
        # 一定要注意绘制的都是参与process的参数，这些参数一般我是要公开的所以也没有绘制的必要
        super().draw_buttons(context, layout)

    def check_node_ho_type(self):
        '''
        遍历link判定linkerror
        目前每个节点规则不一，也许可以写进基类直接调用
        同时单独写出来是为了让监听到cut时用
        '''
        check_ho_type(self,
                      socket_name='Float',
                      location="in",
                      need_ho_type='VALUE')

    def process(self):
        super().process()

        # 拿到socket
        input = self.inputs.get('Float')
        output = self.outputs.get('Float')

        # 拿到输入data
        data_in: Any
        if self.link_type in ["root", "alone"]:  # 没上游
            data_in = input.socket_value
        if self.link_type in ["trans", "crown"]:  # 有上游
            data_in = input.links[-1].from_socket.socket_value

        # 运算并输出data
        output.socket_value = data_in


class ValueTest(ImageNode, Node):
    bl_label = "ValueTest"
    bl_idname = TREE_TYPE + '_' + bl_label

    n_float: bpy.props.FloatProperty(
        name="n_float", precision=4, soft_max=1, soft_min=-1, update=updateNodeProp)
    n_vector: bpy.props.FloatVectorProperty(
        update=updateNodeProp)
    n_color: bpy.props.FloatVectorProperty(
        size=3, subtype="COLOR", update=updateNodeProp, soft_max=1, soft_min=0)
    n_bool: bpy.props.BoolProperty(
        update=updateNodeProp)
    n_int: bpy.props.IntProperty(
        update=updateNodeProp)
    n_str: bpy.props.StringProperty(
        update=updateNodeProp)

    n_tex: bpy.props.PointerProperty(
        type=bpy.types.Image, update=updateNodeProp)
    n_collection: bpy.props.PointerProperty(
        type=bpy.types.Collection, update=updateNodeProp)
    n_material: bpy.props.PointerProperty(
        type=bpy.types.Material, update=updateNodeProp)
    n_object: bpy.props.PointerProperty(
        type=bpy.types.Object, update=updateNodeProp)
    # n_shader : bpy.props.PointerProperty(type=bpy.types.ShaderNodeMix)
    n_floatangel: bpy.props.FloatProperty(
        subtype="FACTOR", update=updateNodeProp)

    def init(self, context):
        self.outsct_float = self.outputs.new(
            'NodeSocketFloat', name='Float')
        self.outsct_vector = self.outputs.new(
            'NodeSocketVector', name='Vector')
        self.outsct_color = self.outputs.new(
            'NodeSocketColor',  name='Color')
        self.outsct_bool = self.outputs.new(
            'NodeSocketBool', name='Bool')
        self.outsct_int = self.outputs.new(
            'NodeSocketInt',  name='Int')
        self.outsct_string = self.outputs.new(
            'NodeSocketString', name='String')

        self.outsct_texture = self.outputs.new(
            'NodeSocketTexture', name='Texture')
        self.outsct_collection = self.outputs.new(
            'NodeSocketCollection', name='Collection')
        self.outsct_material = self.outputs.new(
            'NodeSocketMaterial', name='Material')
        self.outsct_object = self.outputs.new(
            'NodeSocketObject', name='Object')
        self.outsct_shader = self.outputs.new(
            'NodeSocketShader',  name='Shader')

        self.outsct_floatangle = self.outputs.new(
            'NodeSocketFloatAngle', name='FloatAngle')
        self.outsct_floatfactor = self.outputs.new(
            'NodeSocketFloatFactor', name='FloatFactor')
        self.outsct_virtual = self.outputs.new(
            'NodeSocketVirtual', name='Virtual')

        addSocket(self, "in", "HO_SocketImage", "Image")
        addSocket(self, "out", "HO_SocketImage", "Image")

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)
        layout.label(text="这是一个测试节点")
        layout.label(text="测试socket类型,成员变量类型,输出,节点刷新")
        layout.prop(self, "n_float")
        layout.prop(self, "n_vector")
        layout.prop(self, "n_color")
        layout.prop(self, "n_bool")
        layout.prop(self, "n_int")
        layout.prop(self, "n_str")
        layout.separator()
        layout.prop(self, "n_tex")
        layout.prop(self, "n_collection")
        layout.prop(self, "n_material")
        layout.prop(self, "n_object")
        # layout.prop(self,"n_shader")
        layout.prop(self, "n_floatangel")

    def process(self):
        super().process()
        # 拿到socket

        outputFloat = self.outputs.get('Float')

        # 拿到输入data
        data_in: Any
        if self.link_type in ["root", "alone"]:  # 没上游
            data_in = input.socket_value
        if self.link_type in ["trans", "crown"]:  # 有上游
            data_in = input.links[-1].from_socket.socket_value

        # 运算并输出data
        outputFloat.socket_value = data_in


class ImageInputNode(ImageNode, Node):
    bl_label = "输入图像"
    bl_idname = "HO_ImageInputNode"  # 注册名

    default_width: bpy.props.FloatProperty(default=180)  # 修改默认大小

    def UPDATE_NODE_PROP(self, context):
        '''输入图像node的特殊更新机制'''
        self.root_process(is_linkError_check=False)

    input_image: bpy.props.PointerProperty(
        type=bpy.types.Image, update=UPDATE_NODE_PROP)

    def init(self, context):
        super().init()
        self.is_preview = True
        addSocket(self, "out", 'HO_SocketImage',
                  "Image", hide_value=True)

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)
        layout.template_ID(self, "input_image",
                           new='image.new', open='image.open')

    def check_node_ho_type(self):
        return

    def process(self):
        super().process()
        # 拿到socket
        output = self.outputs.get("Image")

        # 拿到输入data，得到pixels与size
        img = self.input_image
        if self.link_type == "root":  # 不是根不读像素
            pixels_out = img.pixels[:]
            size_out = img.size[:]
            name = img.name

            # 在当前node_group下的imgPool创建一个图像副本，存入bytes颜色、bytes长度、size、name
            node_group = bpy.context.space_data.node_tree.name

            pool = bpy.data.node_groups[node_group].imagePool
            pool_img = pool.get(name)
            if pool_img is None:  # 池无旧图则新建，否则覆盖
                pool_img = pool.add()

            pool_img.name = name
            pool_img.image_id = name
            pack = ListBytesPack(pixels_out)
            pool_img.pixels_bytes = pack[0]
            pool_img.pixels_bytes_len = pack[1]
            pool_img.pixels_size = size_out

            # 传出图像索引名
            output.socket_value = name

        # 输出到自身预览图
        self.prev_img = img
        img_preview_HQupdate(self.prev_img)

        # 调整节点大小
        if self.input_image is None:
            self.size2default()
        if not self.is_preview:
            return
        scale = self.prev_img.preview.image_size[0]
        self.width = scale * 2


class ImageOutputNode(ImageNode, Node):
    bl_label = "输出图像"
    bl_idname = "HO_ImageOutputNode"  # 注册名

    default_width: bpy.props.FloatProperty(default=180)

    output_image: bpy.props.PointerProperty(
        type=bpy.types.Image)

    def init(self, context):
        super().init()
        self.is_preview = True
        addSocket(self, "in", 'HO_SocketImage',
                  "Image", hide_value=True,)

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)

    def check_node_ho_type(self):
        check_ho_type(self,
                      socket_name="Image",
                      location="in",
                      need_ho_type='IMAGE')

    def process(self):
        super().process()
        # 拿到socket与数据
        dataBase = self.inputs.get("Image").links[0].from_socket

        # 从imagPool拿到数据,解包bytes
        node_group = bpy.context.space_data.node_tree.name
        name = dataBase.socket_value
        pool = bpy.data.node_groups[node_group].imagePool
        pool_img = pool.get(name)
        pixels = [0]
        size = [0, 0]
        if pool_img is not None:
            pixels_bytes = pool_img.pixels_bytes
            pixels_bytes_len = pool_img.pixels_bytes_len
            pixels = list(ListBytesUnpack(
                bytes=pixels_bytes, length=pixels_bytes_len))
            size = pool_img.pixels_size

        # 检测预览图并输出到预览/调整节点大小
        viewer = bpy.data.images.get("HO_imgViewer")
        if viewer is not None:
            bpy.data.images.remove(bpy.data.images['HO_imgViewer'])
        viewer = bpy.data.images.new(
            "HO_imgViewer", width=size[0], height=size[1])
        viewer.pixels = pixels[:]
        self.prev_img = viewer
        img_preview_HQupdate(self.prev_img)

        if self.is_preview:
            prev_size = self.prev_img.preview.image_size
            scale = max(prev_size[0], prev_size[1])
            self.width = scale * 2


class TransNode(ImageNode, Node):
    bl_label = "运算与传输"
    bl_idname = "HO_TransNode"  # 注册名

    def init(self, context):
        super().init()
        # 只能在这里新建(实例化)完了改socket的参数
        addSocket(self, "in", 'HO_SocketImage',
                  "Image", hide_value=True,)
        addSocket(self, "out", 'HO_SocketImage',
                  "Image", hide_value=True,)

    def draw_buttons(self, context, layout):  #
        super().draw_buttons(context, layout)

    def check_node_ho_type(self):
        check_ho_type(self,
                      socket_name="Image",
                      location="in",
                      need_ho_type='IMAGE')

    def process(self):
        super().process()

        # 拿到socket
        input = self.inputs.get("Image")
        output = self.outputs.get("Image")

        # 拿到输入data
        dataBase: Any
        if self.link_type in ["root", "alone"]:  # 没上游
            dataBase = input
        if self.link_type in ["trans", "crown"]:  # 有上游
            dataBase = input.links[-1].from_socket

        output.socket_value = dataBase.socket_value


nodeCat1 = [BaseNode, ImageInputNode, ImageOutputNode, TransNode]
