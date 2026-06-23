from PIL import Image, ImageDraw

# 首页图标 - 房子形状
img = Image.new('RGBA', (48, 48), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
draw.polygon([(24, 4), (4, 20), (44, 20)], fill=(0, 87, 191, 255))
draw.rectangle([10, 20, 38, 44], fill=(0, 87, 191, 255))
draw.rectangle([18, 30, 30, 44], fill=(255, 255, 255, 255))
img.save('uniapp/static/tab/home.png')

img2 = Image.new('RGBA', (48, 48), (0, 0, 0, 0))
draw2 = ImageDraw.Draw(img2)
draw2.polygon([(24, 4), (4, 20), (44, 20)], fill=(0, 87, 191, 255))
draw2.rectangle([10, 20, 38, 44], fill=(0, 87, 191, 255))
draw2.rectangle([18, 30, 30, 44], fill=(255, 255, 255, 255))
img2.save('uniapp/static/tab/home-active.png')

# 控制图标 - 火焰形状
img3 = Image.new('RGBA', (48, 48), (0, 0, 0, 0))
draw3 = ImageDraw.Draw(img3)
draw3.ellipse([14, 4, 34, 24], fill=(0, 87, 191, 255))
draw3.polygon([(24, 44), (14, 24), (34, 24)], fill=(0, 87, 191, 255))
img3.save('uniapp/static/tab/control.png')

img4 = Image.new('RGBA', (48, 48), (0, 0, 0, 0))
draw4 = ImageDraw.Draw(img4)
draw4.ellipse([14, 4, 34, 24], fill=(0, 87, 191, 255))
draw4.polygon([(24, 44), (14, 24), (34, 24)], fill=(0, 87, 191, 255))
img4.save('uniapp/static/tab/control-active.png')

import os
for f in ['home.png', 'home-active.png', 'control.png', 'control-active.png']:
    path = 'uniapp/static/tab/' + f
    print(f + ': ' + str(os.path.getsize(path)) + ' bytes')
print('Done')
