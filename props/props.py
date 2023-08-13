import bpy


class ImagePoolItem(bpy.types.PropertyGroup):
    image_id: bpy.props.StringProperty()
    pixels_bytes: bpy.props.StringProperty(subtype="BYTE_STRING")
    pixels_bytes_len: bpy.props.IntProperty()
    pixels_size: bpy.props.IntVectorProperty(size=2)


def register():
    bpy.utils.register_class(ImagePoolItem)
    bpy.types.NodeTree.imagePool = bpy.props.CollectionProperty(
        type=ImagePoolItem)


def unregister():
    bpy.utils.unregister_class(ImagePoolItem)


if __name__ == "__main__":
    register()
