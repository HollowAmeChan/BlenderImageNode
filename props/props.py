import bpy


class FloatCollectionProps(bpy.types.PropertyGroup):
    float: bpy.props.FloatProperty()


def register():
    bpy.utils.register_class(FloatCollectionProps)


def unregister():
    bpy.utils.unregister_class(FloatCollectionProps)
