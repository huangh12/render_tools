# coding=utf-8
"Render video with detection boxes"
"""anchors: he.huang"""

from easydict import EasyDict as edict

font_dict = {
    0: './font/STFANGSO.TTF',   # 仿宋
    1: './font/STKAITI.TTF',    # 楷体
    2: './font/STLITI.TTF',     # 简体
    3: './font/STXINGKA.TTF'    # 行楷
}

config = edict()

config.orig_video_path = 'orig_video/hangjing_demo_head.mp4'
config.cache_data_path = './cache_data'
config.score_thresh = 0.7
config.crowd_thresh_num = 4
config.rendered_video_path = 'render_video/hangjing_demo_head_rendered.mp4'
config.boxes_path = './pred_data'
config.valid_region = [(325,0), (280,719), (735,0), (900,719)]
config.box_color = (0,255,255)
config.text_position = (950, 70)
config.font_size = 50
config.font_type = 1
config.font_path = font_dict[config.font_type]