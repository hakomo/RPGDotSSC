from bisect import *
from glob import *
from itertools import *
import json
from math import *
import os
import re
import shutil
from zipfile import *
from PIL import Image
import wget

class Accumulate:

    def __init__(self, a):
        self.a = [0] + list(accumulate(a))

    def end(self, bg, sm):
        return bisect_right(self.a, self.a[bg] + sm, bg + 1) - 1

    def sum(self, bg, ed):
        return self.a[ed] - self.a[bg]

    def __len__(self):
        return len(self.a) - 1

class SegmentTree:

    def __init__(self, a):
        ln = 2 ** ceil(log2(len(a)))
        self.a = [0] * (ln - 1) + a + [-1 << 30] * (ln - len(a))
        for i in range(ln - 2, -1, -1):
            self.a[i] = max(self.a[i * 2 + 1], self.a[i * 2 + 2])

    def max(self, bg, ed):
        return self.rmax(bg, ed, 0, 0, len(self.a) // 2 + 1)

    def rmax(self, bg, ed, ix, l, r):
        if r <= bg or ed <= l:
            return -1 << 30
        if bg <= l and r <= ed:
            return self.a[ix]
        return max(self.rmax(bg, ed, ix * 2 + 1, l, (l + r) // 2),
            self.rmax(bg, ed, ix * 2 + 2, (l + r) // 2, r))

def transparentImage(fn):
    f = Image.open(fn)
    img = Image.new('RGBA', f.size)
    img.paste(f, (0, 0))
    p = img.load()
    c = p[0, 0] if p[0, 0] == p[5, 0] else p[9, 0]
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if p[x, y] == c:
                p[x, y] = (0, 0, 0, 0)
    return img

def height(ac, st, w):
    h, bg = 0, 0
    while bg < len(ac):
        ed = ac.end(bg, w)
        h += st.max(bg, ed)
        bg = ed
    return h

def diff(ac, st, w):
    return abs(w / height(ac, st, w) - 2)

def size(ac, st, w):
    l, r = w, ac.sum(0, -1)
    while r - l > 2:
        if diff(ac, st, l + (r - l) // 3) < diff(ac, st, l // 3 + r * 2 // 3):
            r = l // 3 + r * 2 // 3
        else:
            l += (r - l) // 3
    return min(((w, height(ac, st, w)) for w in range(l, r + 1)),
        key=lambda s: abs(s[0] / s[1] - 2))

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

imgs = [(int(fn[1:4]), transparentImage(fn)) for fn in iglob('m*.bmp')]
imgs.sort(key=lambda v: v[1].size[1])

ws, hs, mxw, mxn = [], [], 0, 0
for ix, img in imgs:
    ws.append(img.size[0])
    hs.append(img.size[1])
    mxw = max(mxw, img.size[0])
    mxn = max(mxn, ix + 1)

bs = [None] * mxn
dstimg = Image.new('RGBA', size(Accumulate(ws), SegmentTree(hs), mxw))
x = y = h = 0
for ix, img in imgs:
    if x + img.size[0] > dstimg.size[0]:
        y += h
        x = h = 0
    bs[ix] = x, y, img.size[0], img.size[1]
    dstimg.paste(img, (x, y))
    x += img.size[0]
    h = max(h, img.size[1])

with open('rpgdot.json', 'w') as f:
    json.dump(bs, f)
dstimg.save('rpgdot.png', 'png')
