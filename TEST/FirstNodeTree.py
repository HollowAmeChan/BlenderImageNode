from nodeitems_utils import NodeCategory, NodeItem
import nodeitems_utils
import bpy
from bpy.types import NodeTree, Node, NodeSocket


class HollowTree(NodeTree):  # 新建到editor type
    bl_idname = 'CustomTreeType'  # 不要动他
    bl_label = "Hollow节点"
    bl_icon = 'NODETREE'


class HollowNode:  # 新建节点大类
    @classmethod
    def poll(cls, ntree):
        # bl_idname不要随便动(这个可能是标记在哪个editor type中使用)
        return ntree.bl_idname == 'CustomTreeType'


class BaseNode(HollowNode, Node):  # 新建节点
    # bl_idname = 'CustomNodeType'
    # bl_idname最好不要乱改，关乎到节点类能不能弄进去，要么就不写，要么就不动他
    bl_label = "A"  # 显示的名称
    float: bpy.props.FloatProperty()  # 直接定义不会显示在节点上
    image: bpy.props.PointerProperty(name="Image", type=bpy.types.Image)

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "out")
        self.inputs.new('NodeSocketFloat', "in")
        # 不写名字不会添加

    def draw_buttons(self, context, layout):
        layout.label(text="显示标题")
        layout.prop(self, "float")  # 传入内部定义的参数需要使用字符串
        layout.template_ID(bpy.data.images, "image")


class HollowNodeCategory(NodeCategory):  # 定义一个节点类
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CustomTreeType'


# 填充节点类
node_categories = [
    HollowNodeCategory('TYPE1', "类型1", items=[
        NodeItem("BaseNode"),
    ])
    # NodeItem传入的是bl_idname，这个名字如果节点里没写就是传入节点类名（最好都不写），bl_idname在很多地方有有命名规范
]

classes = (
    HollowTree,
    BaseNode,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    nodeitems_utils.register_node_categories('ImageNodes', node_categories)


def unregister():
    nodeitems_utils.unregister_node_categories('ImageNodes')

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    def update():
        from bpy.utils import register_class
        for cls in classes:
            register_class(cls)

    # register()
    update()
