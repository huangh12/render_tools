# coding=utf-8
"Render video with detection boxes"
"""anchors: he.huang"""

import os
import logging
logging.getLogger().setLevel(logging.INFO)
from config import config as cfg
import cv2
import glob
from random import random as rand
from PIL import Image, ImageDraw, ImageFont
import numpy as np


# import cPickle
# with open('result.pkl', 'r') as f:
#     roidbs = cPickle.load(f)
# for r in roidbs:
#     name = os.path.splitext(os.path.basename(r['image']))[0] 
#     boxes = r['boxes'][1]
#     write_str = []
#     for box in boxes:
#         box_str = ' '.join([str(_) for _ in box])
#         write_str.append(box_str)
#     with open('%s/%s.txt' %(cfg.boxes_path,name), 'w') as f:
#         f.write('\n'.join(write_str))
 
def empty_dir(dir):
    if os.path.exists(dir):
        os.system('rm -r %s' % dir)
    os.system('mkdir %s' % dir)


# extract the video frames
empty_dir(cfg.cache_data_path)
orig_frames_path = os.path.join(cfg.cache_data_path, 'orig_frames')
empty_dir(orig_frames_path)

cmd = 'time ffmpeg -i {} -q:v 2 -r 25 {}/%08d.jpg'.\
        format(cfg.orig_video_path, orig_frames_path)
os.system(cmd)


# render the frames
rendered_frames_path = os.path.join(cfg.cache_data_path, 'rendered_frames')
empty_dir(rendered_frames_path)

x = float(sum([_[0] for _ in cfg.valid_region])) / len(cfg.valid_region)
y = float(sum([_[1] for _ in cfg.valid_region])) / len(cfg.valid_region)
ref_point = (x,y)

# judge whether (xc,yc)->(xr,yr) is crossed with (x1,y1)->(x2,y2)
def is_cross((xc,yc), (xr,yr), (x1,y1),(x2,y2)):
    if x1 == x2:
        if (xc-x1) * (xr-x1) < 0:
            return True
        else:
            return False
    return ((y2-y1)/(x2-x1)*(xc-x1)+y1-yc) * \
           ((y2-y1)/(x2-x1)*(xr-x1)+y1-yr) < 0


def draw_box(im, box, box_color=None):
    color = (rand() * 255, rand() * 255, rand() * 255) if box_color is None else box_color
    cv2.rectangle(im, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), color=color, thickness=2)
    return im


def cv2ImgAddText(img, text, (left, top), font_path='', textColor=(0, 255, 0), textSize=20):
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fontText = ImageFont.truetype(
        font_path, textSize)
    draw.text((left, top), text, textColor, font=fontText)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


orig_frames_files = glob.glob(orig_frames_path + '/*.jpg')
for im_f in orig_frames_files:
    im = cv2.imread(im_f, cv2.IMREAD_COLOR)
    cv2.line(im, cfg.valid_region[0], cfg.valid_region[1], color=(0,0,225), thickness=2)
    cv2.line(im, cfg.valid_region[2], cfg.valid_region[3], color=(0,0,225), thickness=2)
    txt_path = os.path.join(cfg.boxes_path, os.path.splitext(os.path.basename(im_f))[0]+'.txt')
    assert os.path.isfile(txt_path)
    boxes = []
    with open(txt_path, 'r') as f:
        lines = [_.strip() for _ in f.readlines()]
        for line in lines:
            box = [float(_) for _ in line.split(' ')]
            # drop box lower than cfg.score_thresh
            if len(box) > 4:
                if box[4] < cfg.score_thresh:
                    continue
            xc = (box[0] + box[2]) / 2
            yc = (box[1] + box[3]) / 2
            # drop box beyond valid region
            if is_cross((xc,yc),(x,y),cfg.valid_region[0], cfg.valid_region[1]) or \
               is_cross((xc,yc),(x,y),cfg.valid_region[2], cfg.valid_region[2]):
               continue
            boxes.append(box)
        
        num_boxes = len(boxes)
        is_crowd = True if num_boxes > cfg.crowd_thresh_num else False
        textColor = (0, 0, 255) if is_crowd else (0, 255, 0)
        text = '%d 人: %s' %(num_boxes, '密集' if is_crowd else '正常')
        text = unicode(text, 'utf-8')
        im = cv2ImgAddText(im, text, tuple(cfg.text_position), font_path=cfg.font_path,\
                             textColor=textColor, textSize=cfg.font_size)
        for box in boxes:
            im = draw_box(im, box, cfg.box_color)

    save_path = os.path.join(rendered_frames_path, os.path.basename(im_f))
    cv2.imwrite(save_path, im)


# synthesize the video from frames
save_dir = os.path.dirname(cfg.rendered_video_path)
empty_dir(save_dir)

cmd = 'ffmpeg -f image2 -i {}/%08d.jpg -vcodec libx264 -r 25 {}'.\
        format(rendered_frames_path, cfg.rendered_video_path)
os.system(cmd)

