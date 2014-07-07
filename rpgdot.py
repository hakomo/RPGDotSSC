from glob import *
import json
import os
import re
import shutil
from zipfile import *
from PIL import Image
import wget

def image(fn):
    f = Image.open(fn)
    img = Image.new('RGB', f.size)
    img.paste(f, (0, 0))
    return img

for i in range(1, 27):
    zn = wget.download(
        'http://www.geocities.co.jp/Milano-Cat/3319/muz/mon{}.zip'.format(i))
    with ZipFile(zn) as z:
        z.extractall()
    os.remove(zn)
    for fp in (os.path.join(zn[:-4], fn) for fn in os.listdir(zn[:-4])
            if re.search('^mon_\d{3}r?.bmp$', fn)):
        if fp[-5] == 'r':
            shutil.copyfile(fp, 'm{:0>3}.bmp'.format(int(fp[-8:-5]) * 2 + 1))
        else:
            shutil.copyfile(fp, 'm{:0>3}.bmp'.format(int(fp[-7:-4]) * 2))
    shutil.rmtree(zn[:-4])

smw, mxh, mxn = 0, 0, 0
bcs, fcs = set(), set()
for fn in iglob('m*.bmp'):
    img = image(fn)

    smw += img.size[0]
    mxh = max(mxh, img.size[1])
    mxn = max(mxn, int(fn[1:4]))

    bc = img.getpixel((0, 0))
    bcs.add(bc)
    fcs |= {c[1] for c in img.getcolors() if c[1] != bc}

for c in bcs:
    if c in fcs: continue
    bc = c
    break
else:
    print('not fount back color')
    exit()

a = [None] * (mxn + 1)
dst = Image.new('RGBA', (smw, mxh))
l = 0
for fn in iglob('m*.bmp'):
    img = image(fn).convert('RGBA')
    p = img.load()
    c = p[0, 0]
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if p[x, y] == c:
                p[x, y] = (0, 0, 0, 0)
    dst.paste(img, (l, 0))

    a[int(fn[1:4])] = l, img.size[0], img.size[1]

    l += img.size[0]

with open('rpgdot.json', 'w') as f:
    json.dump(a, f)

dst.save('rpgdot.png', 'png')
