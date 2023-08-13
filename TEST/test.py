import bpy


def reg_icon_by_pixel(prev, name):
    PREV_DICT = bpy.utils.previews.new()
    p = PREV_DICT.new(name)
    p.icon_size = (32, 32)
    p.image_size = (prev.size[0], prev.size[1])
    p.image_pixels_float[:] = prev.pixels[:]


reg_icon_by_pixel(icon_id, scale=max(
    self.prev.size[0], self.prev.size[1]) // 20)
