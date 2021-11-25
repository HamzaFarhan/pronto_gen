import re
import cv2
import copy
import random
import inspect
import imutils
import textwrap
import traceback
import numpy as np
import pandas as pd
from pathlib import Path
import moviepy.audio as mpa
import moviepy.editor as mp
from ast import literal_eval
from functools import partial
from matplotlib import colors
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from simpleeval import simple_eval
import moviepy.video.fx.all as vfx
from core_lib.CustomVideoClip import *
from core_lib.pronto_conf import IMAGE_SIZE_THRESH
from PIL import Image, ImageDraw, ImageFont, ImageColor
#from numba import jit, njit
from core_lib.pronto_conf import LOCAL_FONTS_PATH

PRONTO_MIN_IMAGE_RES = 500

fonts_folder = LOCAL_FONTS_PATH

image_extensions = {'.art','.bmp','.cdr','.cdt','.cpt','.cr2','.crw','.djv','.djvu','.erf','.gif','.ico',
                    '.ief','.jng','.jp2','.jpe','.jpeg','.jpf','.jpg','.jpg2','.jpm','.jpx','.nef','.orf',
                    '.pat','.pbm','.pcx','.pgm','.png','.pnm','.ppm','.psd','.ras','.rgb','.svg','.svgz',
                    '.tif','.tiff','.wbmp','.xbm','.xpm','.xwd','.webp'}

def fn_param_defined(fn, param='x'):
    '''Find out if a param's value is defined in a function.

    Args:
        fn (function): The function.
        param (str, optional): The name of the param. Defaults to 'x'.
    '''
    spec = inspect.signature(fn)
    fn_params = dict_values(spec.parameters)
    for p in fn_params:
        p = str(p)
        if '=' in p and p.split('=')[0] == param:
            return True
    return False

def text_case(text, fn='upper'):
    try:
        return getattr(text, fn)()
    except:
        for i,t in enumerate(text):
            text[i] = text_case(t, fn)
        return text

def text_join(text, joiner=' '):
    if is_list(text):
        return joiner.join(text)
    return text

def seq_start_durs(n=4, chunks=5, start=0, dur=1, fps=30):
    starts = [(chunks*i)/fps+start for i in range(n)]
    if dur is None:
        durs = [chunks/fps]*n
    else:
        end = start+dur
        durs = [end-s for s in starts]
    return starts, durs

def seq_start_ends(n=4, chunks=5, start=0, fps=30):
    dur = (chunks/fps)
    starts = [start+dur*i for i in range(n)]
    ends = [s+dur for s in starts]
    return starts, ends

def draw_ellipse(image, bounds, width=1, outline='white', antialias=4):
    """Improved ellipse drawing function, based on PIL.ImageDraw."""

    # Use a single channel image (mode='L') as mask.
    # The size of the mask can be increased relative to the imput image
    # to get smoother looking results. 
    mask = Image.new(
        size=[int(dim * antialias) for dim in image.size],
        mode='L', color='black')
    draw = ImageDraw.Draw(mask)

    # draw outer shape in white (color) and inner shape in black (transparent)
    for offset, fill in (width/-2.0, 'white'), (width/2.0, 'black'):
        left, top = [(value + offset) * antialias for value in bounds[:2]]
        right, bottom = [(value - offset) * antialias for value in bounds[2:]]
        draw.ellipse([left, top, right, bottom], fill=fill)

    # downsample the mask using PIL.Image.LANCZOS 
    # (a high-quality downsampling filter).
    mask = mask.resize(image.size, Image.LANCZOS)
    # paste outline color to input image through the mask
    image.paste(outline, mask=mask)

def get_circle_bg(logo):
    
    shade_color = (255,255,255,60)
    lh,lw = get_hw(logo)
    diff = 20
    sh,sw = lh+diff,lw+diff
    r1,r2 = diff,sh-diff
    c1,c2 = diff,sw-diff
    circle_bg = to_pil(solid_color_img((sh,sw,3), alpha=0))
    draw_ellipse(circle_bg, (20,20,sw-20,sh-20), width=20, outline=shade_color, antialias=15)
    circle_bg = np.array(circle_bg)
    return circle_bg

def first_frame(v):
    if type(v).__name__ == 'ProntoClip':
        return v.first_frame
    return v.get_frame(0)

def add_vo(promo, music_file):
    if len(str(music_file)) > 0:
        bgm = mp.AudioFileClip(str(music_file))
        pa = promo.audio
        if pa is not None:
            print('COMPOSSIIITTEEEEE')
            bgm = mp.CompositeAudioClip([bgm,pa.volumex(0.25)]).set_fps(promo.fps)
        if bgm.duration > promo.duration:
            bgm = bgm.subclip(0,promo.duration)
        promo = promo.set_audio(bgm)#.audio_fadeout(3.5))
    return promo
    
def vo_on_clips(v_clips, vo_data=None, vo_file=None, duration=30):
    if vo_file is not None and len(str(vo_file)) > 0:
        vo_file = str(vo_file)
        video = mp.concatenate_videoclips(v_clips).subclip(0, duration)
        return add_vo(video, vo_file)
    elif vo_data is not None and len(vo_data) > 0:
        vo_clips = []
        prev_j = 0
        for vo_d in vo_data:
            i,j = vo_d['clips_covered'][0], vo_d['clips_covered'][-1]+1
            if i > prev_j:
                print(i, prev_j)
                a = prev_j
                b = i
                vo_clips.append(mp.concatenate_videoclips(v_clips[a:b]))
            vo_clip = mp.concatenate_videoclips(v_clips[i:j])
            vo_clip = add_vo(vo_clip, vo_d['vo_file'])
            vo_clips.append(vo_clip)
            prev_j = j
        if prev_j < len(v_clips):
            vo_clips += v_clips[prev_j:]
        v_clips = vo_clips
    video = mp.concatenate_videoclips(v_clips).subclip(0, duration)
    return video

def add_vo_files(v, vo_files):
    va = v.audio
    if len(vo_files) > 0:
        if va is None:
            va = mp.AudioFileClip(vo_files[0][0]).set_duration(v.duration).volumex(0)
        audio_list = []
        va_start = 0
        for vt in vo_files:
            vo, times = vt
            # print(times)
            vo = mp.AudioFileClip(str(vo))#.subclip(2)
            if not list_or_tuple(times):
                times = [times]
            if len(times) == 1:
                vo_start = times[0]
                vo_end = vo_start + vo.duration
                times = [vo_start,vo_end]
            vo_start, vo_end = times
            vo_end = min(vo_end, va.duration)
            va_end = vo_start
            vo_dur = vo_end - vo_start
            if vo_dur > vo.duration:
                vo_dur = vo.duration
                vo_end = vo_start + vo_dur
            # print(va.duration, va_start, va_end, vo.duration, vo_dur)
            audio_list += [va.subclip(va_start, va_end).set_start(va_start).set_end(va_end), va.subclip(vo_start, vo_end).volumex(0.2).set_start(vo_start).set_end(vo_end), vo.subclip(0, vo_dur).set_start(vo_start).set_end(vo_end)]
            va_start = vo_end
        audio_list.append(va.subclip(va_start).set_start(va_start))
        v.audio = mp.CompositeAudioClip(audio_list).set_duration(v.duration)
    return v

def hex_to_rgb(hex_color):
    return ImageColor.getcolor(hex_color,"RGB")
    
def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format( rgb[0],rgb[1],rgb[2])

def verify_logo(fpath,logger,img_side_min=100,img_side_max=400):
    try:
        img = rgb_read(fpath)
    except Exception as e:
        raise Exception('image not readable')
        
    width = img.shape[0]
    height = img.shape[1]     
    if width >= img_side_min and height >= img_side_min:
        if width <= img_side_max and height <= img_side_max:
            return 'verified'
    width = img.shape[0]
    height = img.shape[1]     
    raise Exception(f'logo dimensions out of limits. Each side shoud be greater than or equal to {img_side_min} and less than or equal to {img_side_max}, Your supplied image Width = {width}, height = {height}')    
    
def verify_image(fpath,logger,img_side_thresh=IMAGE_SIZE_THRESH):
    try:
        img = rgb_read(fpath)
    except Exception as e:
        raise Exception('image not readable')
    width = img.shape[0]
    height = img.shape[1]
    logger.debug(f'IMAGE WIDTH = {width}, IMAGE HEIGHT = {height}, img_side_thresh = {img_side_thresh}')    
    if width >= img_side_thresh and height >= img_side_thresh:
        return 'verified'
    
    raise Exception(f'image dimensions must be : width greater than or equal to {img_side_thresh}, height greater than or equal to {img_side_thresh}. Your image is {width}x{height}')    

def verify_clip(fpath,logger):
    try:
        clip = read_and_resize(fpath)
        return 'verified'
    except Exception as e:
        raise Exception('unsupported clip')
        
def vid_thumbnail(vid, h=150, w=int(150*(16/9)), t=1):
    fr = vid.get_frame(t)
    return cv2.resize(fr, (w, h),interpolation=cv2.INTER_CUBIC)

def create_thumb_path(fpath):
    ext = fpath[fpath.rfind('.'):]
    thumb_path = fpath[:fpath.rfind('.')]
    thumb_path = thumb_path+'_thumb'
    thumb_path = thumb_path+'.jpg'
    if 'clips' in thumb_path:
        thumb_path = thumb_path.replace('clips','images')
    elif 'videos' in thumb_path:
        thumb_path = thumb_path.replace('videos','images')
    return thumb_path

def get_thumb_path(fpath):
    if 'thumb' in fpath:
        return fpath
    ext = fpath[fpath.rfind('.'):]
    thumb_path = fpath[:fpath.rfind('.')]
    thumb_path = thumb_path+'_thumb'
    thumb_path = thumb_path+'.jpg'
    if 'clips' in thumb_path:
        thumb_path = thumb_path.replace('clips','images')
    elif 'videos' in thumb_path:
        thumb_path = thumb_path.replace('videos','images')
    return thumb_path

def vid_file_to_thumbnail(fpath,out_path=None):
    try:
        vid = mp.VideoFileClip(str(fpath))
    except UnicodeDecodeError:
        fpath = str(fpath)
        fname = fpath[:fpath.rfind('.')+1]
        f = fname+'avi'
        os.system(f'ffmpeg -i {fpath} -vcodec h264 -acodec aac  {fname}avi')
        vid = mp.VideoFileClip(str(f))
        fpath = f
    except Exception as e:
        raise Exception(f'Unable to read file: {e}')
    thumb = vid_thumbnail(vid)
    if out_path is not None:
        thumb_path = out_path
    else:
        thumb_path = create_thumb_path(fpath)
    plt.imsave(thumb_path,thumb)
    return thumb_path

def img_file_to_thumbnail(fpath,out_path=None):
    img = rgb_read(fpath)
    thumb = cv2.resize(img,(max(int(img.shape[1]*0.3),60),max(int(img.shape[0]*0.3),60)) ,interpolation=cv2.INTER_CUBIC)
    if out_path is not None:
        thumb_path = out_path
    else:
        thumb_path = create_thumb_path(fpath)
    plt.imsave(thumb_path,thumb)
    return thumb_path

def play_video(v, maxduration=100):
    path = 'play_video.mp4'
    if os.path.exists(path):
        os.remove(path)
    save_video(v, path)
    v = mp.VideoFileClip(path)
    return v.ipython_display(maxduration=maxduration)

def save_video(v, path='video.mp4', audio=True,codec='libx264',ffmpeg_path='/usr/bin/ffmpeg'):
    if type(v).__name__ == 'ProntoClip':
        v = v.v
    try:
        if not audio:
            v = v.set_audio(None)
        v.save(bitrate='10000000', output_file=path,ffmpeg_path=ffmpeg_path,codec=codec)
    except:
        v.write_videofile(path,audio=audio,fps=30,
                        audio_codec='aac',bitrate=str(np.power(10, 6)),
                        preset='ultrafast',
                        verbose=False,
                        threads=6,
                        logger=None)

def plt_show(im, cmap=None, title='', figsize=(7,7)):
    if path_or_str(im):
        im = rgb_read(im)
    fig=plt.figure(figsize=figsize)
    plt.imshow(im, cmap=cmap)
    plt.title(title)
    plt.show()

def p_list(path):
    return list(Path(path).iterdir())

def is_float(x):
    return isinstance(x, float)

def noop(x=None, *args, **kwargs):
    "Do nothing"
    return x

def path_list(path, suffix=None, make_str=False, map_fn=noop):
    # if sort:
    #     if suffix is None:
    #         l = sorted(list(Path(path).iterdir()))
    #         # return sorted(list(Path(path).iterdir()))
    #     else:
    #         l = sorted([p for p in list(Path(path).iterdir()) if p.suffix==suffix])
    #     # return sorted([p for p in list(Path(path).iterdir()) if p.suffix==suffix])
    # else:
    if suffix is None:
        l = p_list(path)
        # return list(Path(path).iterdir())
    else:
        l = [p for p in list(Path(path).iterdir()) if p.suffix==suffix]
    l = list_map(l, map_fn) 
    if make_str:
        l = list_map(l, str)
    return l

def last_modified(x):
    return x.stat().st_ctime

def path_stem(x):
    return Path(x).stem

def sorted_paths(path, key=None, suffix=None, make_str=False, map_fn=None,
                 reverse=False, only_dirs=False, full_path=True):

    if suffix is None:
        l = p_list(path)
    else:
        if isinstance(suffix, str):
            suffix = (suffix)
        l = [p for p in p_list(path) if p.suffix in suffix]
    if only_dirs:
        l = [x for x in l if x.is_dir()]
    if key is None:
        l = sorted(l, key=last_modified, reverse=True)
    else:
        l = sorted(l, key=key, reverse=reverse)
    if map_fn is not None:
        l = list_map(l, map_fn)
    if not full_path:
        l = list_map(l, lambda x:x.name)
    if make_str:
        l = list_map(l, str)
    return l

def dict_values(d):
    return list(d.values())

def dict_keys(d):
    return list(d.keys())

def dict_items(d):
    return list(d.items())

def locals_to_params(l, omit=[], expand=['kwargs']):
    if 'kwargs' not in expand:
        expand.append('kwargs')
    try:
        l = copy.deepcopy(l)
    except:
        pass
    if 'self' in l.keys():
        del l['self']
    if '__class__' in l.keys():
        del l['__class__']
    keys = dict_keys(l)
    for k in keys:
        if k in expand:
            for k2 in l[k]:
                if k2 not in l.keys():
                    l[k2] = l[k][k2]
            del l[k]
        if k in omit:
            del l[k]
    return l

def flatten_list(l):
    if not is_iterable(l):
        return l
    try:
        return sum(l, [])
    except:
        return sum(l, ())

def is_img(x):
    return Path(x).suffix in image_extensions

def list_map(l, m):
    return list(np.array(list(map(m,l))))
    #return list(pd.Series(l).apply(m))

def chunkify(l, chunk_size):
    if chunk_size is None:
        chunk_size = len(l)
    if list_or_tuple(chunk_size):
        l2 = []
        l2.append(l[:chunk_size[0]])
        for i in range(1, len(chunk_size)):
            c1 = sum(chunk_size[:i])
            c2 = chunk_size[i]+c1
            l2.append(l[c1:c2])
        return l2

    return [l[i:i+chunk_size] for i in range(0,len(l), chunk_size)]

def color_to_rgb(color):
    if type(color) == str:
        return list_map(np.ceil(colors.to_rgb(color)).astype(int)*255, int)
    return list_map(color, int)

def solid_color_img(shape=(300,300,3), color='black', alpha=None):
    image = np.zeros(shape, np.uint8)
    color = color_to_rgb(color)
    image[:] = color
    if alpha is not None:
        image = Image.fromarray(image)
        image.putalpha(alpha)
        image = np.array(image)
    return image

def display_img_actual_size(im_data, title=''):
    dpi = 80
    height, width, depth = im_data.shape
    figsize = width / float(dpi), height / float(dpi)
    fig = plt.figure(figsize=figsize)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    ax.imshow(im_data, cmap='gray')
    plt.title(title,fontdict={'fontsize':25})
    plt.show()

def solid_color_img_like(img, color='black', alpha=None):
    h,w = np.array(img).shape[:2]
    shape = (h,w,3)
    return solid_color_img(shape=shape, color=color, alpha=alpha)

def text_size(txt, font='dejavu serif', font_size=10):

    # fnt = ImageFont.truetype(get_font(font), font_size)
    fnt = ImageFont.truetype(font, font_size)
    s = np.array((0,0))
    if not list_or_tuple(txt):
        txt = [txt]
    for t in txt:
        s += fnt.getsize(t)
    return s

def is_list(x):
    return isinstance(x, list)

def is_tuple(x):
    return isinstance(x, tuple)

def list_or_tuple(x):
    return (is_list(x) or is_tuple(x))

def is_iterable(x):
    return list_or_tuple(x) or is_array(x)

def is_dict(x):
    return isinstance(x, dict)

def is_df(x):
    return isinstance(x, pd.core.frame.DataFrame)

def is_str(x):
    return isinstance(x, str)

def is_int(x):
    return isinstance(x, int)    

def is_array(x):
    return isinstance(x, np.ndarray)

def is_pilimage(x):
    return 'PIL' in str(type(x))

def to_pil(x):
    if is_array(x):
        try:
            return Image.fromarray(x)
        except:
            x = (x*255).astype(np.uint8)
            return Image.fromarray(x)
    return x

def is_set(x):
    return isinstance(x, set)

def is_path(x):
    return isinstance(x, Path)

def path_or_str(x):
    return is_str(x) or is_path(x)

def bgr2rgb(img):
    return cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

def rgb2bgr(img):
    return cv2.cvtColor(img,cv2.COLOR_RGB2BGR)

def gray2rgb(img):
    return cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)

def rgb2gray(img):
    return cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)

def rgb2rgba(img):
    return cv2.cvtColor(img,cv2.COLOR_RGB2RGBA)

def bgra2rgb(img):
    if len(img.shape) > 2 and img.shape[2] == 4:
        return cv2.cvtColor(img,cv2.COLOR_BGRA2RGB)

def rgba2rgb(img):
    if len(img.shape) > 2 and img.shape[2] == 4:
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

def img_float_to_int(img):
    return np.clip((np.array(img)*255).astype(np.uint8),0,255)

def img_int_to_float(img):
    return np.clip((np.array(img)/255).astype(np.float),0.,1.)

def rgb_read(img, shape=None):
    if not path_or_str(img):
        return img
    img = str(img)
    if '.png' in img:
        img = (mpimg.imread(img)*255).astype(np.uint8)
    else:
        img = bgr2rgb(cv2.imread(img))
    if shape is not None:
        img = cv2.resize(img, (shape[1], shape[0]),interpolation=cv2.INTER_CUBIC)
    return img

def c1_read(img):
    return cv2.imread(str(img), 0)

def resize_pic(img, target_shape=(720, 1280, 3)):
    
    if (img.shape[0] == target_shape[0]) and (img.shape[1] == target_shape[1]):
        return img
    
    if img.shape[0] > target_shape[0]:
        # print('1')
        img = imutils.resize(img, height=target_shape[0])

    if img.shape[1] > target_shape[1]:
        # print('2')
        img = imutils.resize(img, width=target_shape[1])
    
    if (img.shape[0] == target_shape[0]) and (img.shape[1] == target_shape[1]):
        return img
    
    s = img.shape[:2]
    max_side = np.argmin(s)
    dims = ['height', 'width']
    if (target_shape[max_side] - s[max_side]) < (s[max_side]*2):
        # print('3')
        args = {'image':img, dims[max_side]: target_shape[max_side]}
        img = imutils.resize(**args)
    
    if (img.shape[0] == target_shape[0]) and (img.shape[1] == target_shape[1]):
        return img
    
    if img.shape[0] > target_shape[0]:
        # print('1')
        img = imutils.resize(img, height=target_shape[0])

    if img.shape[1] > target_shape[1]:
        # print('2')
        img = imutils.resize(img, width=target_shape[1])
    
    if (img.shape[0] == target_shape[0]) and (img.shape[1] == target_shape[1]):
        return img
    
    # print(img.shape)
    bg = solid_color_img(shape=target_shape)
    img = paste_img(img, bg)
    return img

# def read_and_resize(x, dur=11, fps=30, promo_w=960, promo_h=540):
#     if dur is None:
#         dur = 120
#     x = str(x)
#     if len(x) == 0: return None
#     if is_img(x):
#         # p = resize_pic(rgb_read(x), target_shape=(promo_h, promo_w, 3))
#         p = cv2.resize(rgb_read(x), (promo_w, promo_h))
#         v = mp.ImageSequenceClip([p]*(dur*fps), fps=fps)
#     else:
#         try:
#             v = mp.VideoFileClip(x)
#             max_dur = v.duration
#             t2 = min(max_dur, dur)
#             v = v.subclip(0,t2)
#         except Exception as e:
#             return None
#     return v.resize((promo_w, promo_h))

def read_and_resize(x, dur=11, fps=30, h=540, w=960):
    if dur is None:
        dur = 120
    x = str(x)
    if len(x) == 0: return None
    if is_img(x):
        # p = resize_pic(rgb_read(x), target_shape=(promo_h, promo_w, 3))
        try:
            p = cv2.resize(rgb_read(x), (w, h),interpolation=cv2.INTER_CUBIC)
            v = mp.ImageSequenceClip([p]*(dur*fps), fps=fps)
            v = v.resize((w, h))
            return v.set_resolution(width=w, height=h)
        except Exception as e:
            print(f'Exception {e}')
            print(traceback.format_exc())
            return None
    else:
        try:
            v = mp.VideoFileClip(x)
            max_dur = v.duration
            t2 = min(max_dur, dur)
            v = v.subclip(0,t2)
            v = v.resize((w, h))
            return v.set_resolution(width=w, height=h)
        except Exception as e:
            print('444')
            return None

def select_vids(vids, num_vids=None, reading_fn=read_and_resize):
    if num_vids is None:
        num_vids = len(vids)
    final_vids = []
    final_paths = []
    wrong = 0
    for v in vids:
        if len(final_paths) == num_vids:
            break
        if is_img(str(v)) and not correct_img(v):
            continue
        try:
            vid = reading_fn(str(v))
            final_vids.append(vid)
            final_paths.append(v)
        except:
            continue
    return final_vids, final_paths

def correct_img(p, img_side_thresh=500):
    if not is_array(p):
        p = rgb_read(str(p))
    return (p.shape[0]>=img_side_thresh) and (p.shape[1]>=img_side_thresh)

# function to merge 2 dicts
def merge_dicts(dict1, dict2):
    for k in set(dict1.keys()).union(dict2.keys()):
        if k in dict1 and k in dict2:
            if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                yield (k, dict(merge_dicts(dict1[k], dict2[k])))
            else:
                yield (k, dict2[k])
        elif k in dict1:
            yield (k, dict1[k])
        else:
            yield (k, dict2[k])

def remove_nones(clips, clip_paths):
    for i,c in enumerate(zip(clips, clip_paths)):
        cl, cp = c
        if cl is None:
            if i == 0:
                clips[i] = clips[i+1].copy()
                clip_paths[i] = copy.deepcopy(clip_paths[i+1])
            else:
                clips[i] = clips[i-1].copy()
                clip_paths[i] = copy.deepcopy(clip_paths[i-1])
    return clips, clip_paths

def get_pos_factors(pos):
    pos_dict = {'center':0.5, 'left':0.15, 'right':0.85, 'top':0.15, 'bottom':0.85}
    x_factor, y_factor = [pos_dict.get(p,p) for p in pos]
    return x_factor, y_factor

def get_pos(img, bg, pos=('center', 'center'), relative=True):
    p0,p1 = copy.deepcopy(pos)
    if is_int(p0) and is_int(p1):
        relative = False
    if not relative:
        return pos
    x_factor, y_factor = get_pos_factors(pos)
    bg = np.array(bg)
    img = np.array(img)
    bh,bw = bg.shape[:2]
    try:
        h,w = img.shape[:2]
    except:
        h,w = img[:2]
    x,y = get_pos_(bh, bw, h, w, x_factor, y_factor)
    if is_int(p0):
        x = p0
    if is_int(p1):
        y = p1
        # print(x, y)
    return x,y

def get_pos_(bh, bw, h, w, x_factor, y_factor):
    x = int((bw - w) * x_factor)
    y = int((bh - h) * y_factor)
    return x,y

# def paste_img(img, bg, pos=('center', 'center'), relative=True):
#     bg = copy.deepcopy(bg)
#     index = get_pos(img, bg, pos, relative=relative)
#     bg = to_pil(bg)
#     img = to_pil(img)
#     try:
#         bg.paste(img, index, img)
#     except:
#         bg.paste(img, index)
#     bg = np.array(bg)
#     print(np.array(img).shape, bg.shape)
#     return bg

# def paste_img(img, bg, pos=('center', 'center'), relative=True):
    
#     bg = np.array(copy.deepcopy(bg))
#     img = np.array(copy.deepcopy(img))
#     if bg.shape[-1] != 4:
#         bg = add_alpha(bg)
#     if img.shape[-1] != 4:
#         img = add_alpha(img)
#     h,w = img.shape[:2]
#     bgh, bgw = bg.shape[:2]
#     x,y = get_pos(img, bg, pos, relative=relative)
#     r1,r2 = y,y+h
#     c1,c2 = x,x+w
#     if h>bgh and w>bgw:
#         # print('lala1')
#         hf = (h-bgh)//2
#         wf = (w-bgw)//2
#         img = img[hf:hf+bgh, wf:wf+bgw]
#         r1,r2 = 0,bgh
#         c1,c2 = 0,bgw
#     elif h>bgh:
#         # print('lala2')
#         hf = (h-bgh)//2
#         img = img[hf:hf+bgh]
#         r1,r2 = 0,bgh
#     elif w>bgw:
#         # print('lala3')
#         wf = (w-bgw)//2
#         img = img[:,wf:wf+bgw]
#         c1,c2 = 0,bgw
        
#     bg2 = copy.deepcopy(bg[r1:r2, c1:c2])
#     # print(bg.shape, bg2.shape, img.shape, r1, r2, x, y)
#     bgh, bgw = bg2.shape[:2]
#     bg_rgb = bg2[...,:3]
#     img_rgb = img[...,:3]
#     bg_alpha = bg2[...,3]/255.0
#     img_alpha = img[...,3]/255.0
#     # print(img_alpha.shape)
#     if (bg_alpha == 1).all():
#         bg_alpha = 1-img_alpha
#     i_len = len(img_alpha)
#     for i in range(i_len):
#         j_len = len(img_alpha[i])
#         for j in range(j_len):
#             if img_alpha[i][j] == 1:
#                 bg_alpha[i][j] = 0
#     out_alpha = bg_alpha + img_alpha*(1-bg_alpha)
#     out_rgb = (bg_rgb*bg_alpha[...,np.newaxis] + img_rgb*img_alpha[...,np.newaxis]*(1-bg_alpha[...,np.newaxis])) / out_alpha[...,np.newaxis]
#     out_rgba = np.dstack((out_rgb,out_alpha*255)).astype(np.uint8)
#     bg[r1:r2,c1:c2] = out_rgba
#     return bg
    
#@jit(forceobj=True)
def paste_img(img, bg, pos=('center', 'center'), relative=True):
    
    bg = np.array(copy.deepcopy(bg))
    img = np.array(copy.deepcopy(img))
    if bg.shape[-1] != 4:
        bg = add_alpha(bg)
    if img.shape[-1] != 4:
        img = add_alpha(img)
    h,w = img.shape[:2]
    bgh, bgw = bg.shape[:2]
    x,y = get_pos(img, bg, pos, relative=relative)
    
    r1,r2 = y,y+h
    c1,c2 = x,x+w
   
    if x < 0 or y < 0 or x >= bgw or y >= bgh:
        # print(x,y,h,w,bgh,bgw)
        bgh2 = max(bgh,h)
        bgw = max(bgw,w)
        px, py = 0.,0.
        if x < 0:
            bgw2 = bgw + abs(x)
            x = 0
            px = 1.
        elif x >= bgw:
            bgw2 = x+w
        else:
            bgw2 = bgw
        if y < 0:
            bgh2 = bgh + abs(y)
            y = 0
            py = 1.
        elif y >= bgh:
            bgh2 = y+h
        else:
            bgh2 = bgh
        new_bg = solid_color_img((bgh2, bgw2, 3), alpha=0)
        bg = paste_img(bg, new_bg, pos=(px,py))
        bgh, bgw = bg.shape[:2]
        r1,r2 = y,y+h
        c1,c2 = x,x+w
    
    elif h>bgh and w>bgw:
        hf = (h-bgh)//2
        wf = (w-bgw)//2
        img = img[hf:hf+bgh, wf:wf+bgw]
        r1,r2 = 0,bgh
        c1,c2 = 0,bgw
    elif h>bgh:
        hf = (h-bgh)//2
        img = img[hf:hf+bgh]
        r1,r2 = 0,bgh
    elif w>bgw:
        wf = (w-bgw)//2
        img = img[:,wf:wf+bgw]
        c1,c2 = 0,bgw

    bg2 = copy.deepcopy(bg[r1:r2, c1:c2])
    bg2h, bg2w = get_hw(bg2)
    img = img[:bg2h, :bg2w]
    # print(bg.shape, bg2.shape, img.shape, r2-r1, c2-c1)
    bgh, bgw = bg2.shape[:2]
    bg_rgb = bg2[...,:3]
    img_rgb = img[...,:3]
    bg_alpha = bg2[...,3]/255.0
    img_alpha = img[...,3]/255.0
    # print(img_alpha.shape)
    if (bg_alpha == 1).all():
        bg_alpha = 1-img_alpha
    i_len = len(img_alpha)
    for i in range(i_len):
        j_len = len(img_alpha[i])
        for j in range(j_len):
            if img_alpha[i][j] == 1:
                # try:
                bg_alpha[i][j] = 0
                # except:
                    # pass
    out_alpha = bg_alpha + img_alpha*(1-bg_alpha)
    out_rgb = (bg_rgb*bg_alpha[...,np.newaxis] + img_rgb*img_alpha[...,np.newaxis]*(1-bg_alpha[...,np.newaxis])) / out_alpha[...,np.newaxis]
    out_rgba = np.dstack((out_rgb,out_alpha*255)).astype(np.uint8)
    bg[r1:r2,c1:c2] = out_rgba
    return bg

def add_alpha(img, alpha=None):
    if alpha is None:
        alpha = 255
    img = to_pil(img)
    img.putalpha(alpha)
    return np.array(img)

def has_alpha(img):
    return np.array(img).shape[-1] == 4

def draw_ellipse(image, bounds, width=1, outline='white', antialias=4):
    """Improved ellipse drawing function, based on PIL.ImageDraw."""

    # Use a single channel image (mode='L') as mask.
    # The size of the mask can be increased relative to the imput image
    # to get smoother looking results. 
    mask = Image.new(
        size=[int(dim * antialias) for dim in image.size],
        mode='L', color='black')
    draw = ImageDraw.Draw(mask)

    # draw outer shape in white (color) and inner shape in black (transparent)
    for offset, fill in (width/-2.0, 'white'), (width/2.0, 'black'):
        left, top = [(value + offset) * antialias for value in bounds[:2]]
        right, bottom = [(value - offset) * antialias for value in bounds[2:]]
        draw.ellipse([left, top, right, bottom], fill=fill)

    # downsample the mask using PIL.Image.LANCZOS 
    # (a high-quality downsampling filter).
    mask = mask.resize(image.size, Image.LANCZOS)
    # paste outline color to input image through the mask
    image.paste(outline, mask=mask)

def split_img_zoom(img, direction='right', num_chunks=None, animation_dur=1, fps=30):
    
    if num_chunks is None:
        num_chunks = int(fps*animation_dur)
    h,w = img.shape[:2]
    if h==1 and w==1:
        return [img]
    
    if direction.lower() in ['right', 'left']:
        splits = np.array_split(range(w), num_chunks)
        chunks = [img[:,x[0]:x[-1]+1] for x in splits]
        
    elif direction.lower() in ['down','up']:
        splits = np.array_split(range(h), num_chunks)
        chunks = [img[x[0]:x[-1]+1,:] for x in splits]
    return chunks

#@jit(forceobj=True)
def split_img(img, direction='right', num_chunks=None, animation_dur=1, fps=30):
    
    if num_chunks is None:
        num_chunks = int(fps*animation_dur)
    h,w = img.shape[:2]
    if h==1 and w==1:
        return [img]
    
    # if direction.lower() in ['lr', 'rl']:
    #     splits = np.array_split(range(w), num_chunks)
    #     chunks = [img[:,x[0]:x[-1]+1] for x in splits]
        
    # elif direction.lower() in ['ud','du']:
    #     splits = np.array_split(range(h), num_chunks)
    #     chunks = [img[x[0]:x[-1]+1,:] for x in splits]
        
    if direction.lower() in ['mv']:
        num_chunks*=2
        splits = np.array_split(range(h), num_chunks)
        splits = [[x[0],x[-1]+1] for x in splits]

        i = num_chunks//2
        j = max(i,num_chunks-i-1)
        chunks = []
        while i >= 0:
            top = splits[i][0]
            bottom = splits[j][1]
            chunks.append(img[top:bottom,:])
            i-=1
            j = max(i,num_chunks-i-1)

    elif direction.lower() in ['mh']:
        num_chunks*=2
        splits = np.array_split(range(w), num_chunks)
        splits = [[x[0],x[-1]+1] for x in splits]

        i = num_chunks//2
        j = max(i,num_chunks-i-1)
        chunks = []
        while i >= 0:
            left = splits[i][0]
            right = splits[j][1]
            chunks.append(img[:,left:right])
            i-=1
            j = max(i,num_chunks-i-1)

    elif direction.lower() in ['up']:
        splits = np.array_split(range(h), num_chunks)
        tops = [x[0] for x in splits][::-1]

        chunks = []
        for top in tops:
            chunks.append(img[top:,:])

    elif direction.lower() in ['down']:
        splits = np.array_split(range(h), num_chunks)
        bottoms = [x[-1] for x in splits]

        chunks = []
        for b in bottoms:
            chunks.append(img[:b,:])

    elif direction.lower() in ['left']:
        splits = np.array_split(range(w), num_chunks)
        starts = [x[0] for x in splits][::-1]

        chunks = []
        for s in starts:
            chunks.append(img[:,s:])

    elif direction.lower() in ['right']:
        splits = np.array_split(range(w), num_chunks)
        ends = [x[-1] for x in splits]

        chunks = []
        for s in ends:
            chunks.append(img[:,:s])
    return chunks

def split_img_slide(img, direction='right', num_chunks=None, animation_dur=1, fps=30):
    
    if num_chunks is None:
        num_chunks = int(fps*animation_dur)
    h,w = img.shape[:2]
    if h==1 and w==1:
        return [img]

    if direction.lower() in ['down']:
        splits = np.array_split(range(h), num_chunks)
        tops = [x[0] for x in splits][::-1]

        chunks = []
        for top in tops:
            chunks.append(img[top:,:])

    elif direction.lower() in ['up']:
        splits = np.array_split(range(h), num_chunks)
        bottoms = [x[-1] for x in splits]

        chunks = []
        for b in bottoms:
            chunks.append(img[:b,:])

    elif direction.lower() in ['right']:
        splits = np.array_split(range(w), num_chunks)
        starts = [x[0] for x in splits][::-1]

        chunks = []
        for start in starts:
            chunks.append(img[:,start:])
    
    elif direction.lower() in ['left']:
        splits = np.array_split(range(w), num_chunks)
        stops = [x[-1] for x in splits]

        chunks = []
        for stop in stops:
            chunks.append(img[:,:stop])

    return chunks

def concat_img_appear(chunks, bg=solid_color_img((540, 960, 3), 'black'), axis=1, reverse=False,
                keep_every=None, first_kept=None, pos=(0.5,0.5)):
    if keep_every is None:
        keep_every = 1
    if first_kept is None:
        first_kept = keep_every-1
    keep_idx = list(range(first_kept, len(chunks), keep_every))
    if reverse: chunks = chunks[::-1]
    img = chunks[0]
    an = [paste_img(img, bg, pos=pos)]
    kept = None
    for i,c in enumerate(chunks[1:], start=0):
        if i in keep_idx:
            kept_chunks = [chunks[i] for i in keep_idx[:keep_idx.index(i)+1]]
            kept = np.concatenate(kept_chunks, axis=axis)
        if kept is not None:
            kh,kw = kept.shape[:2]
            ch,cw = c.shape[:2]
            if axis == 1:
                bg2h, bg2w = ch, kw
            else:
                bg2h, bg2w = kh, cw
            bg2 = solid_color_img((bg2h, bg2w, 3), alpha=0)
            k2 = paste_img(kept, bg2)
            if not has_alpha(k2):
                k2 = add_alpha(k2)
            if not has_alpha(c):
                c = add_alpha(c)
            if reverse:
                c = np.concatenate([c, k2], axis=axis)
            else:
                c = np.concatenate([k2, c], axis=axis)
        an.append(paste_img(c, bg, pos=pos))
    return an

def appear_img(chunks, direction='right', bg=solid_color_img((540, 960, 3), 'black'),
               keep_every=None, first_kept=None, pos=(0.5,0.5)):
    
    if direction.lower() == 'right':
        axis = 1
        reverse = False
    elif direction.lower() == 'left':
        axis = 1
        reverse = True
    
    elif direction.lower() == 'down':
        axis = 0
        reverse = False
    elif direction.lower() == 'up':
        axis = 0
        reverse = True
    an = concat_img_appear(chunks, bg=bg, axis=axis, reverse=reverse, keep_every=keep_every,
                           first_kept=first_kept, pos=pos)
        
    return an

def animate_appear(img, direction='right', num_chunks=None, animation_dur=1, fps=30,
                   bg=solid_color_img((540, 960, 3), 'black', alpha=0), keep_every=None, first_kept=None,
                   pos=(0.5,0.5)):
    chunks = split_img(img, direction=direction, num_chunks=num_chunks, animation_dur=animation_dur, fps=fps)
    an = appear_img(chunks, direction=direction, bg=bg, keep_every=keep_every,
                    first_kept=first_kept, pos=pos)
    return an

def animate_open(img, bg=None, direction='mv', num_chunks=None, animation_dur=1, fps=30, reverse=False, **kwargs):
    if num_chunks is None:
        num_chunks = int(fps*animation_dur)
    num_chunks-=1
    h,w = np.array(img).shape[:2]
    if h==1 and w == 1:
        return [img]
    chunks = split_img(img, direction=direction, num_chunks=num_chunks, animation_dur=animation_dur, fps=fps)
    if bg is None:
        bg = solid_color_img_like(img, alpha=0)
    chunks = [paste_img(c, bg) for c in chunks]
    if reverse:
        chunks = chunks[::-1]+[bg]
    else:
        chunks = [bg]+chunks
    return chunks

def animate_vertical_appear(img, direction='up', num_chunks=None,
                            animation_dur=1, fps=30, reverse=False, **kwargs):
    bg = solid_color_img_like(img, alpha=0)
    pos_d = {'up':(0.,1.), 'down':(0.,0.)}
    pos = pos_d[direction]
    h,w = np.array(img).shape[:2]
    if h==1 and w == 1:
        return [img]
    chunks = split_img(img, direction=direction, num_chunks=num_chunks, animation_dur=animation_dur, fps=fps)
    chunks = [paste_img(c, bg, pos=pos) for c in chunks]
    if reverse:
        chunks = chunks[::-1]
    return chunks

def animate_horizontal_appear(img, direction='right', num_chunks=None,
                            animation_dur=1, fps=30, reverse=False, **kwargs):
    bg = solid_color_img_like(img, alpha=0)
    pos_d = {'right':(0.,0.), 'left':(1.,0.)}
    pos = pos_d[direction]
    h,w = np.array(img).shape[:2]
    if h==1 and w == 1:
        return [img]
    chunks = split_img(img, direction=direction, num_chunks=num_chunks, animation_dur=animation_dur, fps=fps)
    chunks = [paste_img(c, bg, pos=pos) for c in chunks]
    if reverse:
        chunks = chunks[::-1]
    return chunks

def animate_horizontal_slide(img, bg=None, direction='right', num_chunks=None, animation_dur=1, fps=30, reverse=False, **kwargs):
    if bg is None:
        bg = solid_color_img_like(img, alpha=0)
    pos_d = {'right':(0.,0.), 'left':(1.,0.)}
    pos = pos_d[direction]
    h,w = np.array(img).shape[:2]
    if h==1 and w == 1:
        return [img]
    chunks = split_img_slide(img, direction=direction, num_chunks=num_chunks-1, animation_dur=animation_dur, fps=fps)
    chunks = [bg]+[paste_img(c, bg, pos=pos) for c in chunks]
    if reverse:
        chunks = chunks[::-1]
    # [plt_show(x) for x in chunks]
    return chunks

def animate_vertical_slide(img, bg=None, direction='down', num_chunks=None, animation_dur=1, fps=30, reverse=False, **kwargs):
    if bg is None:
        bg = solid_color_img_like(img, alpha=0)
    pos_d = {'down':(0.,0.), 'up':(0.,1.)}
    pos = pos_d[direction]
    h,w = np.array(img).shape[:2]
    if h==1 and w == 1:
        return [img]
    chunks = split_img_slide(img, direction=direction, num_chunks=num_chunks-1, animation_dur=animation_dur, fps=fps)
    chunks = [bg]+[paste_img(c, bg, pos=pos) for c in chunks]
    if reverse:
        chunks = chunks[::-1]
    return chunks

def get_hw(img):
    return np.array(img).shape[:2]

def split_img_move(img, bg, direction='right', num_chunks=None, animation_dur=1, fps=30):
    
    if num_chunks is None:
        num_chunks = int(fps*animation_dur)
    h,w = get_hw(img)
    bgh,bgw = get_hw(bg)
    if h==1 and w==1:
        return [img]
    
    start_d = {'right':0, 'left':bgw-w, 'down':0, 'up':bgh-h}
    w_splits = np.array_split(range(bgw-w), num_chunks)
    h_splits = np.array_split(range(bgh-h), num_chunks)
    
    if direction.lower() in ['up']:
        starts = [x[0] for x in h_splits][::-1]
        start = start_d[direction]
        chunks = []
        for s in starts:
            bg2 = copy.deepcopy(bg)
            # bg2[s:s+h,:] = img
            bg2[s:s+h,:] = paste_img(img, bg2[s:s+h,:])
            chunks.append(bg2)

    elif direction.lower() in ['down']:
        starts = [x[0] for x in h_splits]
        start = start_d[direction]
        chunks = []
        for s in starts:
            bg2 = copy.deepcopy(bg)
            bg2[s:s+h,:] = img
            chunks.append(bg2)

    elif direction.lower() in ['right']:
        starts = [x[0] for x in w_splits]
        start = start_d[direction]
        chunks = []
        for s in starts:
            bg2 = copy.deepcopy(bg)
            bg2[:,s:s+w] = img
            chunks.append(bg2)
        
        # bg2 = copy.deepcopy(bg)
        # bg2[:,bgw-w:] = img
        # chunks.append(bg2)
    
    elif direction.lower() in ['left']:
        starts = [x[0] for x in w_splits][::-1]
        chunks = []
        for s in starts:
            bg2 = copy.deepcopy(bg)
            bg2[:,s:s+w] = img
            chunks.append(bg2)
        # bg2 = copy.deepcopy(bg)
        # bg2[:,0:0+w] = img
        # chunks.append(bg2)

    return chunks

def animate_horizontal_move(img, bg=None, direction='right', num_chunks=None, animation_dur=1, fps=30):
    h,w = get_hw(img)
    if bg is None:
        bg = solid_color_img((h,int(w*3),3), alpha=0)
    bgh, bgw = get_hw(bg)
    start_d = {'right':0, 'left':bgw-w}
    start = start_d[direction]
    if h==1 and w == 1:
        return [img]
    bg2 = copy.deepcopy(bg)
    bg2[:,start:start+w] = img
    chunks = [bg2] + split_img_move(img, bg, direction=direction, num_chunks=num_chunks-1,
                                    animation_dur=animation_dur, fps=fps)
    return chunks

def animate_vertical_move(img, bg=None, direction='up', num_chunks=None, animation_dur=1, fps=30):
    h,w = get_hw(img)
    if bg is None:
        bg = solid_color_img((h,int(w*3),3), alpha=0)
    bgh, bgw = get_hw(bg)
    start_d = {'down':0, 'up':bgh-h}
    start = start_d[direction]
    if h==1 and w == 1:
        return [img]
    bg2 = copy.deepcopy(bg)
    # bg2[start:start+h,:] = img
    bg2[start:start+h,:] = paste_img(img, bg2[start:start+h,:])
    chunks = [bg2] + split_img_move(img, bg, direction=direction, num_chunks=num_chunks-1,
                                    animation_dur=animation_dur, fps=fps)
    return chunks

def progressive_zoom(img, scales=[3,2,1], num_chunks=None):
    if not is_iterable(scales):        
        scales = [scales, 1]
    if len(scales) < 2:
        scales = [scales[0], 1]
    if num_chunks is not None and len(scales)==2:
        s1,s2 = scales[0], scales[-1]
        step = (s2-s1)/num_chunks
        scales = np.arange(s1, s2+step, step)    
    imgs = [cv2.resize(img, None, fx=s, fy=s,interpolation=cv2.INTER_CUBIC) for s in scales]
    return imgs
        
def animate_zoom_appear(img, direction='right', num_chunks=None, animation_dur=1, fps=30,
                        zoom_scales=[3,2,1], zoom_chunks=3, bg=solid_color_img((540, 960, 3), 'black'),
                        pos=(0.5,0.5), **kwargs):
    if bg is None:
        bg = solid_color_img_like(img, alpha=0)
        pos = (0., 0.)
    if img.shape[-1] == 3 and bg.shape[-1] == 4:
        img = add_alpha(img)
    elif img.shape[-1] == 4 and bg.shape[-1] == 3:
        bg = add_alpha(bg)
    if num_chunks is None:
        num_chunks = int(fps*animation_dur)
    num_chunks = max(1, num_chunks)
    if not is_list(zoom_scales):
        zoom_scales = [zoom_scales, 1]
    if len(zoom_scales) < 2:
        zoom_scales = [zoom_scales[0], 1]
    if zoom_chunks is not None and len(zoom_scales)==2:
        s1,s2 = zoom_scales[0], zoom_scales[-1]
        step = (s2-s1)/zoom_chunks
        zoom_scales = np.arange(s1, s2+step, step)
        zoom_chunks = len(zoom_scales)
    zoom_chunks = max(len(zoom_scales), zoom_chunks)
    # num_chunks = max(1, num_chunks//zoom_chunks)
    # num_chunks = 1
    # print(zoom_scales, num_chunks)
    chunks = split_img_zoom(img, direction=direction, num_chunks=num_chunks, animation_dur=animation_dur, fps=fps)
    chunks = flatten_list([progressive_zoom(c, scales=zoom_scales) for c in chunks])
    bgh, bgw = get_hw(bg)
    an = appear_img(chunks, direction=direction, bg=bg, keep_every=zoom_chunks, pos=pos)
    an = [a[:bgh, :bgw] for a in an]
    return an

def resize_logo(logo, height=None, width=None):
    logo = rgb_read(str(logo))
    h,w = get_hw(logo)
    if height is not None and h > height:
        return imutils.resize(logo, height=height)
    if width is not None and w > width:
        return imutils.resize(logo, width=width)
    return logo

def blank_clip(duration=1):
    return mp.ImageClip(solid_color_img((1,1,3), alpha=0), duration=duration, fromalpha=True)

def handle_str_hw(hw, height=540, width=960):
    if is_iterable(hw):
        return [handle_str_hw(x, height=height, width=width) for x in hw]
    if not is_str(hw):
        return hw
    if 'height' in hw:
        hw = hw.replace('height', str(height))
    elif 'width' in hw:
        hw = hw.replace('width', str(width))
    else:
        return hw
    try:
        return simple_eval(hw)
    except:
        return hw

def convert_wh(args, height=540, width=960):
    for k,v in args.items():
        # if is_str(v) and ('height' in v or 'width' in v):
        args[k] = handle_str_hw(v, height, width)

def read_clips(clips=[], dims=[]):
    for i,c in enumerate(clips):
        w,h = dims[i]
        if path_or_str(c):
            clips[i] = read_and_resize(c, dur=None, h=h, w=w)
        else:
            c = c.resize((w, h))
            clips[i] = c.set_resolution(width=w, height=h)
    return clips 

def box_pos(wh, bg_h=540, bg_w=960, align='center', gap=5):
    box_h = [x[1] for x in wh]
    h_fun = lambda i: sum(box_h[:i])
    if align == 'center':
        xy = [(int((bg_w-j[0])*0.5),(h_fun(i)+gap*i)) for i,j in enumerate(wh)]
    elif align == 'left':
        xy = [(0,(h_fun(i)+gap*i)) for i,j in enumerate(wh)]
    elif align == 'right':
        xy = [(bg_w-j[0],(h_fun(i)+gap*i)) for i,j in enumerate(wh)]
    return xy

def split_array(start, stop, steps):
    if start == stop:
        return [start]*steps
    step = 1
    if stop < start:
        step = -1
    chunks = np.array_split(range(start,stop,step), steps)
    return [list(x)[-1] for x in chunks]

def pto_noop(img, t, **kwargs):
    return img

def pto_resize(img, t, factor=0.2, **kwargs):
    h,w = get_hw(img)
    h2,w2 = int(h+factor*t), int(w+factor*t)
    return cv2.resize(img, (w2,h2),interpolation=cv2.INTER_CUBIC)

def move_img(img, bg=solid_color_img((540,960,3)), x1=0., y1=0., x2=0.5, y2=0.5, steps=15, fn=pto_noop, h2=None, w2=None,
             vh=540, vw=960, **kwargs):

    if bg is None:
        bg = solid_color_img((vh,vw,3), alpha=0)
    bh,bw = get_hw(bg)
    h,w = get_hw(img)
    if h2 is None:
        h2 = h
    if w2 is None:
        w2 = w
    if is_float(h2):
        h2 = h*h2
    if is_float(w2):
        w2 = w*w2
    final_img = cv2.resize(img, (w2,h2),interpolation=cv2.INTER_CUBIC)
    
    x1,y1 = get_pos(img, bg, (x1,y1))
    x2,y2 = get_pos(final_img, bg, (x2,y2))
    x_chunks = split_array(x1, x2, steps)
    y_chunks = split_array(y1, y2, steps)
    h_chunks = split_array(h, h2, steps)
    w_chunks = split_array(w, w2, steps)
    # print(x_chunks, y_chunks, h_chunks, w_chunks)
    # print(h,h2, w,w2)
    an = [paste_img(img, bg, (x1,y1), relative=False)]
    for i,chunks in enumerate(zip(x_chunks, y_chunks, h_chunks, w_chunks), start=1):
        x,y = chunks[:2]
        h,w = chunks[2:]
        an.append(paste_img(fn(cv2.resize(img,(w,h),interpolation=cv2.INTER_CUBIC), i), bg, (x,y), relative=False))
        
    # [plt_show(x) for x in an]
    return an

def full_text_pos(txt_w, bg_w=960, align='center', gap=5, top=0):
    # top = gap/4-2
    # top = min(-7,top)
    # top = 0
    if align == 'center':
        xy = (int((bg_w-txt_w)*0.5), top)
    elif align == 'left':
        xy = (gap, top)
    elif align == 'right':
        xy = (bg_w-txt_w-gap, top)
    return xy

def text_template_components(text='Luxury interior design has a few simple rules.', wrap_width=35,
                             font='/usr/local/share/fonts/energized/Poppins-ExtraBold.ttf', font_size=50,
                             gap=30, align='left', color='white', stroke_width=0, stroke_fill=None, text_bg_color=[0,191,255],
                             text_bg_alpha=220, temp_color='black', temp_alpha=0,
                             full_text_bg=False, **kwargs):
    if not is_list(text):
        text = [text]
    if len(text) == 0:
        text = ['']
    if len(text[0]) == 0:
        return ([solid_color_img((1,1,3), alpha=0)], [solid_color_img((1,1,3), alpha=0)],
                solid_color_img((1,1,3), alpha=0))
    font = str(Path(fonts_folder)/Path(font).name)
    font = str(font)
    fnt = ImageFont.truetype(font, font_size)
    gap_2 = min(5,int(gap/3))
    # if gap == 0:
        # gap_3 = 2
    text = flatten_list([textwrap.wrap(t, wrap_width) for t in text])
    wh = [fnt.getsize(t) for t in text]
    # bg_h = sum([h for _,h in wh])+(gap*(len(wh)-1)+(gap_2*2))
    bg_w = max([w for w,_ in wh])+gap_2*2
    # temp_bg = solid_color_img((bg_h, bg_w, 3), alpha=temp_alpha, color=temp_color)
    if full_text_bg:
        text_bg_fn = lambda x: (x[1]+gap_2*2, bg_w, 3)
    else:
        text_bg_fn = lambda x: (x[1]+gap_2*2, x[0]+gap_2*2, 3)
    blank_bgs = [to_pil(solid_color_img(text_bg_fn(x), alpha=text_bg_alpha,
                                        color=text_bg_color)) for x in wh]
    text_bgs = [to_pil(solid_color_img(text_bg_fn(x), alpha=0)) for x in wh]
    top = gap_2/4-2
    top = min(-7,top)
    if 'FranklinGothic-Light' in font:
        top = gap_2-2     
    elif 'NotoSansTC-Medium.otf' in font:
        top = gap_2/4-2
    if full_text_bg:
        txt_xy = [full_text_pos(twh[0], x.size[0], align=align, gap=gap_2,top=top) for twh,x in zip(wh,text_bgs)]
    else:
        txt_xy = [(gap_2, top)]*len(wh)
        # txt_xy = [(gap_2, gap_2/4-2)]*len(wh)
    bg_h = sum([x.size[1] for x in blank_bgs])+(gap_2*(len(wh)-1))
    # print(bg_h, [x.size[1] for x in blank_bgs])
    temp_bg = solid_color_img((bg_h, bg_w, 3), alpha=temp_alpha, color=temp_color)
    box_xy = box_pos([tbg.size for tbg in text_bgs], bg_h, bg_w, align=align, gap=gap_2)
    # if gap == 0:
        # print(text, wh)
        # print(temp_bg.shape, [np.array(b).shape for b in blank_bgs])
        # print(box_xy)
    temp = copy.deepcopy(temp_bg)
    for i,tbg in enumerate(text_bgs):
        t = text[i]
        bbg = blank_bgs[i]
        d = ImageDraw.Draw(tbg)
        d.text(txt_xy[i], text=t, fill=color, font=fnt, stroke_width=stroke_width, stroke_fill=stroke_fill)
        # print(wh, gap_2, temp_bg.shape, tbg.size, bbg.size, xy[i])
        blank_bgs[i] = paste_img(bbg, temp_bg, pos=box_xy[i], relative=False)
        text_bgs[i] = paste_img(tbg, temp_bg, pos=box_xy[i], relative=False)
        d = ImageDraw.Draw(bbg)
        d.text(txt_xy[i], text=t, fill=color, font=fnt, stroke_width=stroke_width, stroke_fill=stroke_fill)
        temp = paste_img(bbg, temp, pos=box_xy[i], relative=False)
        # temp = paste_img(tbg, temp, pos=xy[i], relative=False)

    return blank_bgs, text_bgs, temp

def text_template(text='Luxury interior design has a few simple rules.', wrap_width=35,
                             font='/usr/local/share/fonts/energized/Poppins-ExtraBold.ttf', font_size=50,
                             gap=30, align='left', color='white', stroke_width=0, stroke_fill=None, text_bg_color=[0,191,255],
                             text_bg_alpha=220, temp_color='black', temp_alpha=0,
                             full_text_bg=False, **kwargs):
    return text_template_components(**locals_to_params(locals()))[-1]

def text_template_blanks(text='Luxury interior design has a few simple rules.', wrap_width=35,
                             font='/usr/local/share/fonts/energized/Poppins-ExtraBold.ttf', font_size=50,
                             gap=30, align='left', color='white', stroke_width=0, stroke_fill=None, text_bg_color=[0,191,255],
                             text_bg_alpha=220, temp_color='black', temp_alpha=0,
                             full_text_bg=False, **kwargs):
    return text_template_components(**locals_to_params(locals()))[0]

def text_template_texts(text='Luxury interior design has a few simple rules.', wrap_width=35,
                             font='/usr/local/share/fonts/energized/Poppins-ExtraBold.ttf', font_size=50,
                             gap=30, align='left', color='white', stroke_width=0, stroke_fill=None, text_bg_color=[0,191,255],
                             text_bg_alpha=220, temp_color='black', temp_alpha=0,
                             full_text_bg=False, **kwargs):
    return text_template_components(**locals_to_params(locals()))[1]

# def text_template(img=solid_color_img(), pos=('center', 'center'),
#                   text='Luxury interior design has a few simple rules.', wrap_width=35,
#                   font='/usr/local/share/fonts/energized/Poppins-ExtraBold.ttf', font_size=50,
#                   gap=30, align='left', color='white', text_bg_color=[0,191,255],
#                   text_bg_alpha=220, temp_color='black', temp_alpha=0):
    
#     blank_bgs, text_bgs, temp = text_template_components(**locals_to_params(locals()))
#     img = paste_img(temp, img, pos=pos)
#     return img

def put_alphas(imgs, alpha_scales=[]):
    
    if len(alpha_scales)>0:
        scales = np.array_split(range(alpha_scales[0], alpha_scales[-1]+1), len(imgs))
        alphas = [x[-1] for x in scales]
        for i,img in enumerate(imgs):
            imgs[i] = Image.fromarray(img)
            imgs[i].putalpha(alphas[i])
            imgs[i] = np.array(imgs[i])        
    return imgs
        
def zoom_template(tm, vh=540, vw=960, direction='right', num_chunks=3, zoom_scales=[5,1], zoom_chunks=3,
                  num_chunks_2=2, zoom_scales_2=[1,10], zoom_chunks_2=2, pos=(0.2,0.5), temp_dur=4, fps=30,
                  vid_bg_color=(128,128,255), vid_bg_alpha=64, position=(0.,0.), start=0,
                  bg = solid_color_img((540, 960, 3), alpha=0), text_alpha_scales=[]):
    zt1 = animate_zoom_appear(tm, direction=direction, num_chunks=num_chunks, zoom_scales=zoom_scales,
                              zoom_chunks=zoom_chunks, pos=pos, bg=bg, fps=fps)
    if zoom_scales_2 is None or len(zoom_scales_2) == 0:
        s = zoom_scales[-1]
        zt2 = [paste_img(cv2.resize(tm, None, fx=s, fy=s), bg, pos=pos,interpolation=cv2.INTER_CUBIC)]
    else:
        zt2 = animate_zoom_appear(tm, direction=direction, num_chunks=num_chunks_2, fps=fps,
                                  zoom_scales=zoom_scales_2, zoom_chunks=zoom_chunks_2, pos=pos, bg=bg)
    z_clips = []
    zt2_len = len(zt2)/fps
    if temp_dur == None:
        temp_dur = (len(zt1)+len(zt2))/fps
    zv1 = mp.ImageSequenceClip(zt1, fps=fps).subclip(0, temp_dur-zt2_len)
    zv2 = mp.ImageSequenceClip(zt2, fps=fps)
    vid_bg = solid_color_img((vh, vw, 3))
    if vid_bg_color is not None:
        vid_bg = solid_color_img((vh,vw,3), color=vid_bg_color, alpha=vid_bg_alpha)
        zbg = mp.ImageClip(vid_bg).set_duration(zv1.duration).set_position(position).set_start(start)
        z_clips.append(zbg)
    position = get_pos(zt1[0], vid_bg, pos=position)
    z_clips += [zv1.set_position(position).set_start(start),
                zv2.set_position(position).set_start(zv1.duration+start)]
    return z_clips

def open_template(temp, direction='mv', vh=540, vw=960, num_chunks=5, num_chunks_2=3,
                  pos=('left', 'center'), temp_start=0, temp_dur=4, fps=30):
    th,tw = temp.shape[:2]
    temp_bg_shape = (th, tw, 3)
    temp_bg = solid_color_img(temp_bg_shape, alpha=0)
    bg_shape = (vh, vw, 3)
    bg = solid_color_img(bg_shape, alpha=0)
    pos = get_pos(temp, bg, pos)
    o1 = animate_open(temp, direction=direction, bg=temp_bg, num_chunks=num_chunks, fps=fps)
    if num_chunks_2 > 0 and num_chunks is not None:
        o2 = animate_open(temp, direction=direction, bg=temp_bg, num_chunks=num_chunks_2, fps=fps)
        o2 = o2[::-1]
    else:
        o2 = [copy.deepcopy(temp)]
    
    o2_len = len(o2)/fps
    if temp_dur == None:
        temp_dur = (len(o1)+len(o2))/fps
    ov1 = mp.ImageSequenceClip(o1, fps=fps).set_duration(temp_dur-o2_len).set_position(pos).set_start(temp_start)
    ov2 = mp.ImageSequenceClip(o2, fps=fps).set_position(pos).set_start(temp_start+ov1.duration)
    clips = [ov1,ov2]
    return clips

def slide_template(temp, direction='right', vh=540, vw=960, num_chunks=5, num_chunks_2=3,
                   pos=('left', 'center'), temp_start=0, temp_dur=4, fps=30, reverse=False,
                   bg=None):

    an_func_d = {'right': animate_horizontal_slide, 'left': animate_horizontal_slide,
                 'up': animate_vertical_slide, 'down':animate_vertical_slide}
    an_func = an_func_d[direction]
    th,tw = temp.shape[:2]
    if bg is None:
        bg_shape = (vh, vw, 3)
        bg = solid_color_img(bg_shape, alpha=0)
    pos = get_pos(temp, bg, pos)
    o1 = an_func(temp, direction=direction, num_chunks=num_chunks, fps=fps)
    if temp_dur is None:
        temp_dur = (len(o1)+1)/fps
    if num_chunks_2 > 0 and num_chunks_2 is not None:
        o2 = an_func(temp, direction=direction, num_chunks=num_chunks_2, fps=fps)
        o2 = o2[::-1]
        # o2 = copy.deepcopy(o1)[::-1]
    else:
        o2 = [copy.deepcopy(temp)]
    
    o2_len = len(o2)/fps
    if reverse:
        o1 = o1[::-1]
        if num_chunks_2 == 0 or num_chunks_2 is None:
            o2 = [copy.deepcopy(o1[-1])]
    # vbg_shape = (vh, vw, 3)
    # vbg = solid_color_img(vbg_shape, alpha=0)
    # pos = get_pos(bg, vbg, position)
    ov1 = mp.ImageSequenceClip(o1, fps=fps).set_duration(temp_dur-o2_len).set_position(pos).set_start(temp_start)
    ov2 = mp.ImageSequenceClip(o2, fps=fps).set_position(pos).set_start(temp_start+ov1.duration).set_duration(o2_len)
    # ov2 = ov2.fx(vfx.time_mirror)
    clips = [ov1,ov2]
    return clips

def get_clip_lens(num_clips=6, duration=30):
    clips = [1]*(num_clips)
    idx = 0
    while sum(clips) < duration:
        if idx > len(clips)-1:
            idx = 0
        clips[idx]+=1
        idx+=1
    return clips

def process_clips(all_clips=[], pronto_paths=[], extra_paths=[], user_paths=[],
                  meta_data={'num_vids':6, 'num_extra':1},
                  reading_fn=read_and_resize):

    if len(all_clips) > 0:
        print('GOT ALL CLIPS')
        print(f'num paths: {len(all_clips)}')
        clips = [reading_fn(c) for c in all_clips]
        clip_paths = all_clips.copy()

    elif len(pronto_paths) > 0 or len(user_paths) > 0:

        print('GOT SEPARATE CLIPS')

        # EXTRACT CLIPS
        num_vids = meta_data['num_vids']
        pronto_clips = []
        extra_clips = []
        clips, clip_paths = select_vids(user_paths, num_vids, reading_fn)
        # print()
        num_user = len(clips)
        if len(pronto_paths) > 0:
            num_pronto = num_vids-num_user
            pronto_clips, pronto_paths = select_vids(pronto_paths, num_pronto, reading_fn)
            num_pronto = len(pronto_clips)
        num_extra = 0
        if len(extra_paths) > 0:
            num_extra = meta_data['num_extra']
            extra_clips, extra_paths = select_vids(extra_paths, num_extra, reading_fn)
            num_extra = len(extra_clips)
            
        clips+=pronto_clips
        clip_paths+=pronto_paths
        # print(clips)
        # print()
        if num_extra > 0:
            clips = clips[:-num_extra]
            clip_paths = clip_paths[:-num_extra]
        # print(clips)
        # print()
        
        cl = list(zip(clips, clip_paths))
        random.shuffle(cl)
        clips, clip_paths = [list(x) for x in zip(*cl)]
        
        clips+=extra_clips
        clip_paths+=extra_paths
        # print(clips)
        # print()

    # if len(all_clips) > 0:
    #     print('GOT ALL CLIPS')
    #     print(f'paths: {len(all_clips)}')
    #     clips = [reading_fn(c) for c in all_clips]
    #     clip_paths = all_clips.copy()

    return remove_nones(clips, clip_paths)

def clean_subclip(v):
    return v.subclip(t_end=(v.duration - 1.0/v.fps))

def handle_oem_dur(oem_clips, clip_lens, reading_fn, duration=30):
    oem_clip = ''
    if len(oem_clips) > 0:
        oem_clip = reading_fn(oem_clips[0])
        oem_clip = oem_clip.subclip(0, int(oem_clip.duration))
    print(f'clip_lens: {clip_lens}')
    if not is_str(oem_clip):
        oem_dur = oem_clip.duration
        i = 1
        while sum(clip_lens)+oem_dur > duration:
            clip_lens[i]-=1
            i+=1
            if i == len(clip_lens):
                i = 1
        print(f'clip_lens: {clip_lens}')
    return clip_lens, oem_clip

def add_oem(v, oem_clip, duration, music_file, add_music):
    if not is_str(oem_clip):
        oem_dur = oem_clip.duration
        v_dur = duration - oem_dur
        v = v.subclip(0, v_dur)
        if len(music_file) > 0:
            v = add_music(v, music_file)
        v = mp.concatenate_videoclips([v, oem_clip])
    else:
        v = v.subclip(0, duration)
        if len(music_file) > 0:
            v = add_music(v, music_file)
    return v

def add_wm(v, watermark):
    if len(watermark) > 0:
        wm = cv2.resize(rgb_read(watermark), v.size,interpolation=cv2.INTER_CUBIC)
        wm = add_alpha(wm, alpha=45)
        wm = mp.ImageClip(wm).set_duration(v.duration)
        v = mp.CompositeVideoClip([v,wm])
    return v