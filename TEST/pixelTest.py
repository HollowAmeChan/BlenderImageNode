import bpy
import random
from mathutils import Vector
'''
一个简单的改变图像像素为xy轴的脚本
'''
img = bpy.data.images[-1]
pix = img.pixels
Vp = Vector(pix)
# 这一步其实是copy了一份数据创建了一个vector类
sizeX, sizeY = img.size[0], img.size[1]

rr = random.random
for i in range(sizeX):
    for j in range(sizeY):
        index = 4*(sizeX*j+i)
        pix[index:index+4] = (i/sizeX, j/sizeY, 0, 1)
# 使用vp中转操作会更快
