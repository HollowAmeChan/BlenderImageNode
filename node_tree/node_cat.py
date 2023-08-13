from nodeitems_utils import NodeCategory, NodeItem
import bpy
import nodeitems_utils

from .node_base import TREE_TYPE, TREE_NAME
from .nodes import nodeCat1


class ImageNodeCategory(NodeCategory):  # 定义一个节点集合类
    @classmethod
    def poll(cls, context):
        return bpy.context.space_data.node_tree.bl_idname == TREE_TYPE


# 注册一个集合

node_categories = [
    ImageNodeCategory('IMAGE', "Image", items=[
                      NodeItem(i.bl_idname) for i in nodeCat1])
]


def register():
    try:
        for i in nodeCat1:
            bpy.utils.register_class(i)
    except Exception:
        print("Nodes load failed!!!")

    try:
        nodeitems_utils.register_node_categories(
            TREE_NAME, node_categories)
    except Exception:
        print("NodeCat load failed!!!")


def unregister():
    for i in nodeCat1:
        bpy.utils.unregister_class(i)

    nodeitems_utils.unregister_node_categories(
        TREE_NAME)
