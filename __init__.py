import typing
import bpy
from bpy.types import Context, Operator
from bpy.types import Panel

from .node_tree import node_base, node_cat, nodes
from .operator import ops
from .panel import panels
from .props import props

bl_info = {
    "name": "_Hollow_addon",
    "author": "Hollow_ame",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "Hollow",
    "description": "image nodes",
    "warning": "",
    "wiki_url": "",
    "category": "Hollow",
}


def register():
    props.register()
    ops.register()
    panels.register()
    node_base.register()
    node_cat.register()
    # bpy.types.NodeGroup.imagePool = bpy.props.CollectionProperty(
    #     type=props.ImagePoolItem)


def unregister():
    ops.unregister()
    panels.unregister()
    node_base.unregister()
    node_cat.unregister()
