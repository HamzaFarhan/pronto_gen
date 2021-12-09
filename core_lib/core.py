from core_lib.video_utils import *
from core_lib.template_config import *

def store_attr(self, nms):
    "Store params named in comma-separated `nms` from calling context into attrs in `self`"
    mod = inspect.currentframe().f_back.f_locals
    for n in re.split(', *', nms):
        try:
            setattr(self,n,mod[n])
        except:
            setattr(self,n,mod['kwargs'][n])
            
class Structure:
    def __init__(self, h=540, w=960, shapes=[[50,150],[25,200], [25,200]],
                 pos=[[0.5, 0.15], [0.5,'fwd_posy0+10'], ['fwd_posx0*2','fwd_posy1+10']],
                 times=[[0,2], [2,4], [4,6]], **kwargs):
        
        # temps = [solid_color_img(s[:2]+[3]) for s in shapes]
        self.bg = solid_color_img((h,w,3), alpha=0)
        self.handle_pos(shapes=shapes, pos=pos)
        self.times = times
    
    def handle_pos(self, shapes, pos):
        pos_dict = {}
        self.pos = []
        for i,shape in enumerate(shapes):
            th, tw = shape[:2]
            pos_ = self.set_fwd_args({'pos':pos[i]}, pos_dict)['pos']
            pos_ = get_pos(shape, self.bg, pos_)
            pos_x, pos_y = pos_
            pos_dict[f'th{i}'] = th
            pos_dict[f'tw{i}'] = tw
            pos_dict[f'posx{i}'] = pos_x
            pos_dict[f'posy{i}'] = pos_y
            pos_dict['posx'] = pos_x
            pos_dict['posy'] = pos_y
            pos_dict['th'] = th
            pos_dict['tw'] = tw
            self.pos.append(pos_)
                
    def set_fwd_args(self, args, pos_dict={}, **kwargs):
        for key,arg_v in args.items():
            not_list = False
            if not is_iterable(arg_v):
                not_list = True
                arg_v = [arg_v]
            for v_id,v in enumerate(arg_v):
                if is_str(v) and 'fwd_' in v:
                    v2 = copy.deepcopy(v)
                    v = v.replace('fwd_','')
                    ops = ['+','-','*','/',"//"]
                    v = v.replace('//','/')
                    used_ops = []
                    for op in ops:
                        if op in v:
                            used_ops.append(op)
                            v = v.replace(op, ' ', 1)
                    v = v.split()
                    v = [str(pos_dict.get(x,x)) for x in v]
                    v = ''.join([x+op for op,x in zip(used_ops, v[:-1])]+[v[-1]])
                    print(v)
                    v = int(simple_eval(v))
                    arg_v[v_id] = v
                    print(f'FWD POS: {v2} to {v}')
            if not_list:
                arg_v = arg_v[0]
            args[key] = arg_v
        return args

class ProntoClass:
    def __init__(self, vh=540, vw=960, fps=30, **kwargs):
        self.vbg = solid_color_img((vh,vw,3), alpha=0)
        store_attr(self, ','.join(dict_keys(locals_to_params(locals()))))

class Animation(ProntoClass):
    def __init__(self, temp, vh=540, vw=960, an_fn=noop, animation_dur=1, fps=30, **kwargs):
        super().__init__(**locals_to_params(locals()))
        self.an_fn = partial(an_fn, **locals_to_params(locals()))
        self.animate()
        self.durs = [x.duration for x in self.clips]
                
    def animate(self):
        x = self.an_fn(self.temp)
        if not is_list(x):
            x = [x]
        # if self.reverse:
        #     x = x[::-1]
        self.an_chunks = x
        self.v = mp.ImageSequenceClip(x, fps=self.fps)
        self.clips = [self.v]

class MoveAnimation(Animation):
    def __init__(self, temp, bg=solid_color_img((540,960,3)), x1=0., y1=0., x2=0.5, y2=0.5, steps=15, fn=pto_noop, h2=None, w2=None,
                 vh=540, vw=960, **kwargs):
        an_fn = move_img
        super().__init__(**locals_to_params(locals()))

class VerticalAppearAnimation(Animation):
    def __init__(self, temp, direction='up', num_chunks=5, animation_dur=1, fps=30, num_chunks_2=5, animation_dur_2=1, **kwargs):
        an_fn = animate_vertical_appear
        self.fwd = Animation(**locals_to_params(locals())).v
        self.v = self.fwd
        an_fn = partial(an_fn, reverse=True)
        num_chunks = num_chunks_2
        animation_dur = animation_dur_2
        self.bwd = Animation(**locals_to_params(locals())).v
        self.clips = [self.fwd, self.bwd]
        self.durs = [num_chunks/fps, num_chunks_2/fps]

class HorizontalAppearAnimation(Animation):
    def __init__(self, temp, direction='right', num_chunks=5, animation_dur=1, fps=30, num_chunks_2=5, animation_dur_2=1, **kwargs):
        an_fn = animate_horizontal_appear
        self.fwd = Animation(**locals_to_params(locals())).v
        self.v = self.fwd
        an_fn = partial(an_fn, reverse=True)
        num_chunks = num_chunks_2
        animation_dur = animation_dur_2
        self.bwd = Animation(**locals_to_params(locals())).v
        self.clips = [self.fwd, self.bwd]
        self.durs = [num_chunks/fps, num_chunks_2/fps]

class VerticalSlideAnimation:
    def __init__(self, temp, direction='down', num_chunks=5, bg=None, animation_dur=1, fps=30,
                 num_chunks_2=5, animation_dur_2=1, **kwargs):
        an_fn = animate_vertical_slide
        self.fwd = Animation(**locals_to_params(locals())).v
        self.v = self.fwd
        an_fn = partial(an_fn, reverse=True)
        num_chunks = num_chunks_2
        animation_dur = animation_dur_2
        self.bwd = Animation(**locals_to_params(locals())).v
        self.clips = [self.fwd, self.bwd]
        self.durs = [num_chunks/fps, num_chunks_2/fps]
        
class HorizontalSlideAnimation:
    def __init__(self, temp, direction='right', num_chunks=5, bg=None, animation_dur=1, fps=30,
                 num_chunks_2=5, animation_dur_2=1, **kwargs):
        an_fn = animate_horizontal_slide
        self.fwd = Animation(**locals_to_params(locals())).v
        self.v = self.fwd
        an_fn = partial(an_fn, reverse=True)
        num_chunks = num_chunks_2
        animation_dur = animation_dur_2
        self.bwd = Animation(**locals_to_params(locals())).v
        self.clips = [self.fwd, self.bwd]
        self.durs = [num_chunks/fps, num_chunks_2/fps]
    
class ZoomAnimation(Animation):
    def __init__(self, temp, direction='right', bg=None, pos=(0.,0.), num_chunks=3,
                 zoom_scales=[5,1], zoom_chunks=3, **kwargs):
        an_fn = animate_zoom_appear
        super().__init__(**locals_to_params(locals()))

class OpenAnimation(Animation):
    def __init__(self, temp, direction='mv', num_chunks=5, bg=None, animation_dur=1, fps=30, **kwargs):
        an_fn = animate_open
        super().__init__(**locals_to_params(locals()))
        
class CloseAnimation(Animation):
    def __init__(self, temp, direction='mv', num_chunks=5, bg=None, animation_dur=1, fps=30, **kwargs):
        reverse = True
        an_fn = partial(animate_open, reverse=reverse)
        super().__init__(**locals_to_params(locals()))
        
class OpenCloseAnimation:
    def __init__(self, temp, direction='mv', bg=None, num_chunks=5, num_chunks_2=5,
                 animation_dur=1, animation_dur_2=1, fps=30, **kwargs):
        self.open = OpenAnimation(**locals_to_params(locals())).v
        num_chunks = num_chunks_2
        animation_dur = animation_dur_2
        self.close = CloseAnimation(**locals_to_params(locals())).v
        self.clips = [self.open, self.close]
        self.durs = [num_chunks/fps, num_chunks_2/fps]

def no_effect(text='', font_size=40, font='/usr/local/share/fonts/relaxed/NotoSansTC-Medium.otf',
              color='white', align='center', wrap_width=25, start=0, end=5, fps=30, img=None, **kwargs):
    
    '''
    No special effect, just the text or image on the screen.

    Parameters:
        text (str): The text to display.
        font_size (int): The font size.
        font (str): The font to use.
        color (str or [r,g,b] list): The color of the text.
        align (str): The alignment of the text. Can be one of 'left', 'center', 'right'.
        wrap_width (int): The nuber of text characters per line.
        start (int): The starting timestamp(second) of the clip.
        end (int): The ending timestamp(second) of the clip.
        fps (int): The frames per second of the clip.
        img (str): If text is an emtpy string, this image will be used instead.
    '''
    
    duration = end-start
    clips = []
    pos = []
    times = []
    
    if len(text) > 0:
        img = text_template(text=text, wrap_width=wrap_width, font=font, font_size=font_size,
                             gap=0, align=align, color=color, full_text_bg=True, text_bg_alpha=0)
    elif img is None:
        return blank_clip(duration)
    clips.append(mp.ImageClip(img, duration=duration))
    pos.append([0.5,0.5])
    times.append([0,duration])
    h,w = get_hw(img)
    return ProntoClip(clips=clips, times=times, pos=pos, start=start, end=end, fps=fps, vh=w, vw=w)

def art_effect(text='', font_size=40, color='white', font='/usr/local/share/fonts/relaxed/NotoSansTC-Medium.otf', theme=[16,184,254],
               align='center', start=0, end=5, fps=30, img=None, **kwargs):
    
    '''
    Effect adapted from the Art template.
    The text/image will be split into 3 and slide down onto the screen with a colorful bar on the left.

    Parameters:
        text (str): The text to display.
        font_size (int): The font size.
        font (str): The font to use.
        theme (str or [r,g,b] list): The color of the bar on the left.
        color (str or [r,g,b] list): The color of the text.
        align (str): The alignment of the text. Can be one of 'left', 'center', 'right'.
        wrap_width (int): The nuber of text characters per line.
        start (int): The starting timestamp(second) of the clip.
        end (int): The ending timestamp(second) of the clip.
        fps (int): The frames per second of the clip.
        img (str): If text is an emtpy string, this image will be used instead.
    '''
        
    duration = end-start
    clips = []
    pos = []
    times = []
    
    if len(text) > 0:
        img = text_template(text=text, wrap_width=55, font=font, font_size=font_size, text_bg_color=theme,
                            gap=0, align=align, color=color, full_text_bg=True, text_bg_alpha=0)
    elif img is None:
        return blank_clip(duration)
    
    img_clip = mp.ImageClip(img, duration=duration)
    th,tw = get_hw(img)
    num_splits = 3
    splits = np.array_split(range(tw), num_splits)
    t1,t2,t3 = [img[:,x[0]:x[-1]+1] for x in splits]
    tws = [get_hw(t)[1] for t in [t1,t2,t3]]
    num_chunks = 5
    an_dur = num_chunks/fps
    t1_an1 = VerticalSlideAnimation(t1, direction='down', num_chunks=num_chunks).fwd
    t2_an1 = VerticalSlideAnimation(t2, direction='down', num_chunks=num_chunks).fwd
    t3_an1 = VerticalSlideAnimation(t3, direction='down', num_chunks=num_chunks).fwd
    img_clip2 = VerticalAppearAnimation(img, direction='up', num_chunks_2=num_chunks).bwd
    gap = 20
    barw = 5
    barh = th-5
    bar = solid_color_img((barh, barw, 3), color=theme)
    bar_an1 = VerticalSlideAnimation(bar, direction='down', num_chunks=num_chunks).fwd
    bar_an2 = VerticalAppearAnimation(bar, direction='up', num_chunks_2=num_chunks).bwd
    img_pos = [gap//2+barw, 0]
    clips += [t1_an1, t2_an1, t3_an1, bar_an1, bar_an2, img_clip, img_clip2]
    pos += [img_pos, [f'fwd_pos_x+{tws[0]}', 'fwd_pos_y'], [f'fwd_pos_x+{tws[1]}', 'fwd_pos_y']]
    pos += [[0, f'fwd_pos_y+7']]*2
    pos += [img_pos]*2
    times += [[an_dur,an_dur*4], [an_dur*2,an_dur*4], [an_dur*3,an_dur*4]]
    times += [[an_dur,duration-an_dur-an_dur], duration-an_dur-an_dur]
    times += [[an_dur*4, duration-an_dur-an_dur], duration-an_dur-an_dur]
    w = barw+tws[0]+tws[1]+tws[2]+gap
    h = max(max([get_hw(t1)[0], get_hw(t2)[0], get_hw(t3)[0]]),barh)
    return ProntoClip(clips=clips, times=times, pos=pos, start=start, end=end, fps=fps, vh=h, vw=w)

def slide_effect(text='', direction='right', font_size=40, font='/usr/local/share/fonts/relaxed/NotoSansTC-Medium.otf',
                 color='white', align='center', wrap_width=25, start=0, end=5, fps=30, slide_out=True,
                 img=None, **kwargs):
    
    '''
    The text/image will slide onto the screen.

    Parameters:
        text (str): The text to display.
        direction (str): The direction of the slide. Can be one of 'left', 'right', 'up', 'down'.
        font_size (int): The font size.
        font (str): The font to use.
        color (str or [r,g,b] list): The color of the text.
        align (str): The alignment of the text. Can be one of 'left', 'center', 'right'.
        wrap_width (int): The nuber of text characters per line.
        start (int): The starting timestamp(second) of the clip.
        end (int): The ending timestamp(second) of the clip.
        fps (int): The frames per second of the clip.
        img (str): If text is an emtpy string, this image will be used instead.
        slide_out (bool): If True, the text will also slide out of the screen.
    '''
    
    ans = {'down':VerticalSlideAnimation, 'up':VerticalSlideAnimation, 'right':HorizontalSlideAnimation, 'left':HorizontalSlideAnimation}
    duration = end-start
    clips = []
    pos = []
    times = []
    
    if len(text) > 0:
        img = text_template(text=text, wrap_width=wrap_width, font=font, font_size=font_size,
                            gap=0, align=align, color=color, full_text_bg=True, text_bg_alpha=0)
    elif img is None:
        return blank_clip(duration)
    an = ans[direction]
    img_an = an(temp=img, direction=direction, num_chunks=5, num_chunks_2=5, fps=fps)
    clips = img_an.clips
    pos += [[0.5,0.5]]*len(clips)
    dur0, dur1 = img_an.durs
    times += [[0, duration-dur1], duration-dur1]
    h,w = get_hw(img)
    if not slide_out:
        clips = clips[:1]
        times = times[:1]
        pos = pos[:1]
    return ProntoClip(clips=clips, times=times, pos=pos, start=start, end=end, fps=fps, vh=w, vw=w)

def move_effect(text='', bg=None, x1=0., y1=0., x2=0.5, y2=0.5, steps=15, fn=pto_noop, h2=None, w2=None,
                font_size=40, font='/usr/local/share/fonts/relaxed/NotoSansTC-Medium.otf', color='white', align='center',
                wrap_width=25, start=0, end=5, fps=30, img=None, vh=540, vw=960, **kwargs):
    
    '''
    The text/image will move from position (x1,y1) to position (x2,y2).

    Parameters:
        text (str): The text to display.
        bg (image): The background on which the text/image can move around.
                    If None, the background will be the entire screen based on vh and vw.
        x1 (float or int): The starting x position of the text/image.
        y1 (float or int): The starting y position of the text/image.
        x2 (float or int): The ending x position of the text/image.
        y2 (float or int): The ending y position of the text/image.
        steps (int): The number of steps/frames to move the text/image. 15 means the text/image moves for half a second if fps is 30.
        h2 (int): The final height of the text/image. If None, the text/image is not resized.
        w2 (int): The final width of the text/image. If None, the text/image is not resized.
        font_size (int): The font size.
        font (str): The font to use.
        color (str or [r,g,b] list): The color of the text.
        align (str): The alignment of the text. Can be one of 'left', 'center', 'right'.
        wrap_width (int): The nuber of text characters per line.
        start (int): The starting timestamp(second) of the clip.
        end (int): The ending timestamp(second) of the clip.
        fps (int): The frames per second of the clip.
        img (str): If text is an emtpy string, this image will be used instead.
        vh (int): The height of the overall video the text/image will be displayed on.
        vw (int): The width of the overall video the text/image will be displayed on.
    '''    
    
    duration = end-start
    clips = []
    pos = []
    times = []
    
    if len(text) > 0:
        img = text_template(text=text, wrap_width=wrap_width, font=font, font_size=font_size,
                             gap=0, align=align, color=color, full_text_bg=True, text_bg_alpha=0)
    elif img is None:
        return blank_clip(duration)
    if bg is None:
        bg = solid_color_img((vh,vw,3), alpha=0)
    clips.append(MoveAnimation(img, bg=bg, x1=x1, y1=y1, x2=x2, y2=y2, steps=steps, fn=fn, h2=h2, w2=w2, fps=fps).v)
    pos.append([0.5,0.5])
    times.append([0,-1])
    h,w = get_hw(bg)
    return ProntoClip(clips=clips, times=times, pos=pos, start=start, end=end, fps=fps, vh=h, vw=w)

def slide_move_effect(text='', direction='right', font_size=40, font='/usr/local/share/fonts/relaxed/NotoSansTC-Medium.otf',
                      color='white', align='center', wrap_width=25, start=0, end=5, fps=30,
                      bg=None, x1=0.5, y1=0.5, x2=0.75, y2=0.5, steps=5, fn=pto_noop, h2=None, w2=None, vh=540, vw=960,
                      img=None, **kwargs):
    
    '''
    The text/image will slide in a direction and then move from position (x1,y1) to position (x2,y2).

    Parameters:
        text (str): The text to display.
        direction (str): The direction of the slide. Can be one of 'down', 'up', 'right', 'left'.
        font_size (int): The font size.
        font (str): The font to use.
        color (str or [r,g,b] list): The color of the text.
        align (str): The alignment of the text. Can be one of 'left', 'center', 'right'.
        wrap_width (int): The nuber of text characters per line.
        start (int): The starting timestamp(second) of the clip.
        end (int): The ending timestamp(second) of the clip.
        fps (int): The frames per second of the clip.
        bg (image): The background on which the text/image can move around.
                    If None, the background will be the entire screen based on vh and vw.
        x1 (float or int): The starting x position of the text/image.
        y1 (float or int): The starting y position of the text/image.
        x2 (float or int): The ending x position of the text/image.
        y2 (float or int): The ending y position of the text/image.
        steps (int): The number of steps/frames to move the text/image. 15 means the text/image moves for half a second if fps is 30.
        h2 (int): The final height of the text/image. If None, the text/image is not resized.
        w2 (int): The final width of the text/image. If None, the text/image is not resized.
        vh (int): The height of the overall video the text/image will be displayed on.
        vw (int): The width of the overall video the text/image will be displayed on.
        img (str): If text is an emtpy string, this image will be used instead.
    '''        
    
    duration = end-start
    clips = []
    pos = []
    times = []
    
    if len(text) == 0 and img is None:
        return blank_clip(duration)
    
    if bg is None:
        bg = solid_color_img((vh,vw,3), alpha=0)
    # bg_clip = mp.ImageClip(bg, duration=duration)
    
    slide_start = 0
    slide_end = 1.5
    clips.append(slide_effect(text=text, direction=direction, font_size=font_size, font=font, color=color, align=align, wrap_width=wrap_width,
                              start=slide_start, end=slide_end, fps=fps, slide_out=False, img=img, **kwargs))
    pos.append([x1, y1])
    times.append([slide_start, slide_end])

    move_start = slide_end-steps/fps
    clips.append(move_effect(text=text, font_size=font_size, font=font, color=color, align=align, wrap_width=wrap_width, img=img,
                             bg=bg, x1=x1, y1=y1, x2=x2, y2=y2, steps=steps, fn=fn, h2=h2, w2=w2, fps=fps, start=move_start, end=end))
    pos.append([0.,0.])
    times.append(move_start)
    print(pos)
    return ProntoClip(bg_clip='', clips=clips, times=times, pos=pos, start=start, end=end, fps=fps, vh=vh, vw=vw)

def candid_effect(text='', font_size=30, font='/usr/local/share/fonts/relaxed/NotoSansTC-Medium.otf',
                  color='white', align='center', wrap_width=55, start=0, end=5, fps=30, theme='blue',
                  img=None, **kwargs):
    
    '''
    Effect adapted from the Candid template. A textbox opens and closes witha grey background and bars on each side.

    Parameters:
        text (str): The text to display.
        font_size (int): The font size.
        font (str): The font to use.
        color (str or [r,g,b] list): The color of the text.
        align (str): The alignment of the text. Can be one of 'left', 'center', 'right'.
        wrap_width (int): The nuber of text characters per line.
        start (int): The starting timestamp(second) of the clip.
        end (int): The ending timestamp(second) of the clip.
        fps (int): The frames per second of the clip.
        theme (str or [r,g,b] list): The color of the bars on each side.
        img (str): If text is an emtpy string, this image will be used instead.
    '''    
    
    duration = end-start
    pos = [[0,0]]*2
    close_dur = 3/fps
    open_end = duration-close_dur*2
    times = [[0,open_end], open_end]

    if len(text) > 0:
        text = text_case(text, 'capitalize')
        img = text_template(text=text, wrap_width=wrap_width, font=font, font_size=font_size,
                            gap=10, align=align, color=color, full_text_bg=True, text_bg_alpha=170,
                            text_bg_color=(40,40,40))
    elif img is None:
        return blank_clip(duration)
    
    th,tw = get_hw(img)
    line = solid_color_img((th,5,3), color=theme, alpha=225)
    img = np.concatenate([line, img, line], axis=1)
    th,tw = get_hw(img)
    
    text_an = OpenCloseAnimation(temp=img, direction='mh', num_chunks=5, num_chunks_2=3, fps=fps)
    clips = [text_an.open, text_an.close]            
    
    return ProntoClip(vh=th, vw=tw, clips=clips, pos=pos, times=times, end=duration)

def bold_effect(text='', font_size=95, font='/usr/local/share/fonts/energized/Poppins-ExtraBold.ttf', theme='blue',
                color='white', align='left', wrap_width=15, start=0, end=5, fps=30, img=None, vh=540, vw=960,
                pos=['left', 'center'], **kwargs):
     
    '''
    Effect adapted from the Bold template.
    The text splits into 3 and zooms in/out with a slightly transparent background on the whole video.

    Parameters:
        text (str): The text to display.
        font_size (int): The font size.
        font (str): The font to use.
        theme (str or [r,g,b] list): The color of the slightly transparent background.
        color (str or [r,g,b] list): The color of the text.
        align (str): The alignment of the text. Can be one of 'left', 'center', 'right'.
        wrap_width (int): The nuber of text characters per line.
        start (int): The starting timestamp(second) of the clip.
        end (int): The ending timestamp(second) of the clip.
        fps (int): The frames per second of the clip.
        img (str): If text is an emtpy string, this image will be used instead.
        vh (int): The height of the overall video the text/image will be displayed on.
        vw (int): The width of the overall video the text/image will be displayed on.
        pos (list): The [x,y] position of the text on the video.
    '''         
        
    duration = end-start
    zoom_start = 0
    zoom_dur = min(4, duration-1)
    zoom_end = zoom_start+zoom_dur
    zoom_out_dur = 2/fps
    if len(text) > 0:
        text = text_case(text, 'upper')
        img = text_template(text=text, temp_alpha=0, align=align, temp_bg_color=theme, text_bg_alpha=0, font_size=font_size, font=font,
                            wrap_width=wrap_width, gap=0, color=color)
    elif img is None:
        return blank_clip(duration)
    vbg = solid_color_img((vh,vw,3), alpha=0)
    zoom_in = ZoomAnimation(img, direction='right', bg=vbg, pos=pos, num_chunks=3, zoom_chunks=3, zoom_scales=[5,1]).v
    zoom_out = ZoomAnimation(img, direction='right', bg=vbg, pos=pos, num_chunks=1, zoom_chunks=2, zoom_scales=[1,5]).v
    zoom_bg = mp.ImageClip(solid_color_img_like(vbg, color=theme, alpha=45), duration=zoom_dur-zoom_out_dur)
    times = [zoom_start, [zoom_start, zoom_end-zoom_out_dur],zoom_end-zoom_out_dur]
    return ProntoClip(clips=[zoom_bg, zoom_in, zoom_out], vh=vh, w=vw, times=times, end=duration)

def zoom_effect(text='', font_size=95, font='/usr/local/share/fonts/energized/Poppins-ExtraBold.ttf',
                color='white', align='left', wrap_width=15, start=0, end=5, fps=30, img=None, vh=540, vw=960,
                pos=['left', 'center'], **kwargs):
 
    '''
    The text zooms in/out with a slightly transparent background on the whole video.

    Parameters:
        text (str): The text to display.
        font_size (int): The font size.
        font (str): The font to use.
        color (str or [r,g,b] list): The color of the text.
        align (str): The alignment of the text. Can be one of 'left', 'center', 'right'.
        wrap_width (int): The nuber of text characters per line.
        start (int): The starting timestamp(second) of the clip.
        end (int): The ending timestamp(second) of the clip.
        fps (int): The frames per second of the clip.
        img (str): If text is an emtpy string, this image will be used instead.
        vh (int): The height of the overall video the text/image will be displayed on.
        vw (int): The width of the overall video the text/image will be displayed on.
        pos (list): The [x,y] position of the text on the video.
    '''         
        
    duration = end-start
    zoom_start = 0
    zoom_dur = min(4, duration-1)
    zoom_end = zoom_start+zoom_dur
    zoom_out_dur = 2/fps
    if len(text) > 0:
        text = text_case(text, 'upper')
        img = text_template(text=text, temp_alpha=0, align=align, text_bg_alpha=0, font_size=font_size, font=font,
                            wrap_width=wrap_width, gap=0, color=color)
    elif img is None:
        return blank_clip(duration)
    vbg = solid_color_img((vh,vw,3), alpha=0)
    zoom_in = ZoomAnimation(img, direction='right', bg=vbg, pos=pos, num_chunks=1, zoom_chunks=3, zoom_scales=[5,1]).v
    zoom_out = ZoomAnimation(img, direction='right', bg=vbg, pos=pos, num_chunks=1, zoom_chunks=2, zoom_scales=[1,5]).v
    # zoom_bg = mp.ImageClip(solid_color_img_like(vbg, color=theme, alpha=45), duration=zoom_dur-zoom_out_dur)
    times = [[zoom_start, zoom_end-zoom_out_dur],zoom_end-zoom_out_dur]
    return ProntoClip(clips=[zoom_in, zoom_out], vh=vh, w=vw, times=times, end=duration)

def fresh_effect(text='', font_size=40, font='/usr/local/share/fonts/relaxed/NotoSansTC-Medium.otf', theme=[16,184,254],
                 color='white', wrap_width=35, start=0, end=5, fps=30, img=None, **kwargs):
    
    '''
    Effect adapted from the Fresh template.
    The text background and the text slide in and out one after another.

    Parameters:
        text (str): The text to display.
        font_size (int): The font size.
        font (str): The font to use.
        theme (str or [r,g,b] list): The color of the bar on the left.
        color (str or [r,g,b] list): The color of the text.
        wrap_width (int): The nuber of text characters per line.
        start (int): The starting timestamp(second) of the clip.
        end (int): The ending timestamp(second) of the clip.
        fps (int): The frames per second of the clip.
        img (str): If text is an emtpy string, this image will be used instead.
    '''    
    
    duration = end-start
    # all_pos = [['left', 'top'], ['left', 'bottom'], ['center', 'center'], ['right', 'bottom'], ['right', 'top']]
    directions = ['down', 'right']
    alignement = ['left', 'right']
    ans = {'down':VerticalAppearAnimation, 'right':HorizontalAppearAnimation}
    clips = []
    pos = []
    times = []
    
    if len(text) == 0 and img is None:
        return blank_clip(duration)
    if len(text) > 0:
        # temp_pos = random.choice(all_pos)
        temp_pos = [0,0]
        bb_direction = random.choice(directions)
        temp_direction = random.choice(directions)
        trans_direction = random.choice(directions)
        bb_an = ans[bb_direction]
        temp_an = ans[temp_direction]
        trans_direction = ans[trans_direction]
        align = random.choice(alignement)
        blank_bgs, text_bgs, temp = text_template_components(text=text, temp_alpha=0, align=align,
                                                             temp_bg_color=theme, color=color,
                                                             text_bg_alpha=210, font_size=font_size,
                                                             font=font, wrap_width=wrap_width)
        chunks = 10
        slide_dur = chunks/fps
        bbg_dur = duration-slide_dur
        bbgs = [bb_an(bbg, direction=bb_direction, num_chunks=chunks, fps=fps).v for bbg in blank_bgs]
        clips += bbgs
        times += [[0, bbg_dur]]*len(bbgs)
        pos += [temp_pos]*len(bbgs)
        tbg_start = 0.1
        tbgs = [mp.ImageClip(tbg, duration=bbg_dur-tbg_start).set_fadein(slide_dur) for tbg in text_bgs]
        clips += tbgs
        times += [tbg_start]*len(tbgs)
        pos += [temp_pos]*len(tbgs)
        temp_v = temp_an(temp, direction=temp_direction, num_chunks=chunks, fps=fps, reverse=True).v
        clips.append(temp_v)
        times.append(bbg_dur)
        pos.append(temp_pos)
        vh,vw = get_hw(temp)
        return ProntoClip(clips=clips, pos=pos, times=times, vh=vh, vw=vw, end=duration)

def fresh_first_effect(text='', font_size=40, font='/usr/local/share/fonts/relaxed/NotoSansTC-Medium.otf',
                       color='white', wrap_width=35, start=0, end=5, fps=30, align='center', img=None, **kwargs):
    duration = end-start
    clips = []
    pos = []
    times = []
    
    if len(text) > 0:
        temp = text_template(text=text, temp_alpha=0, align=align, text_bg_alpha=0, font_size=font_size,
                             font=font, gap=0, full_text_bg=True, color=color, wrap_width=wrap_width)
        th,tw = get_hw(temp)
        underline = solid_color_img((10, 75, 3), color='white')
        bg = solid_color_img((th+10+10, tw,3), alpha=0)
        img = paste_img(temp, bg, pos=[0.5, 0.])
        img = paste_img(underline, img, pos=[0.5,th+10])
        text_clip = mp.ImageClip(img, duration=duration).set_fadein(0.5)
        clips.append(text_clip)
        pos.append([0,0])
        times.append(0)
        vh,vw = get_hw(img)
        return ProntoClip(clips=clips, pos=pos, times=times, vh=vh, vw=vw, end=duration, fps=fps)
    return blank_clip(duration)

effects_dict = {'no_effect':no_effect, 'art_effect':art_effect, 'slide_effect':slide_effect, 'move_effect':move_effect,
                'slide_move_effect': slide_move_effect, 'candid_effect':candid_effect, 'bold_effect':bold_effect,
                'zoom_effect': zoom_effect, 'fresh_first_effect': fresh_first_effect
                }

def slide_transition(v, direction='left', num_chunks=5, fps=30, vh=540, vw=960, clip_dur=5):
    if path_or_str(v):
        v = read_and_resize(v, dur=clip_dur, fps=fps, h=vh, w=vw)
    temp = first_frame(v)
    ans = {'down':VerticalSlideAnimation, 'up':VerticalSlideAnimation, 'right':HorizontalSlideAnimation, 'left':HorizontalSlideAnimation}
    an = ans[direction]
    trans_v = an(temp, direction=direction, num_chunks=num_chunks, fps=fps)
    return trans_v

def zoom_transition(v, zoom_chunks=5, zoom_scales=[0.2,1], pos=(0.5,0.5), bg=None, fps=30, vh=540, vw=960, clip_dur=5):
    if path_or_str(v):
        v = read_and_resize(v, dur=clip_dur, fps=fps, h=vh, w=vw)
    temp = first_frame(v)
    trans_v = ZoomAnimation(num_chunks=1, **locals_to_params(locals()))
    return trans_v

def fresh_transition(v, theme=[16,184,254], fps=30):
    vw,vh = v.size
    trans_direction = random.choice(['down', 'right'])
    ans = {'down':VerticalAppearAnimation, 'right':HorizontalAppearAnimation}
    trans_an = ans[trans_direction]
    return trans_an(solid_color_img((vh, vw, 3), color=theme, alpha=255),
                    direction=trans_direction, num_chunks=15, fps=fps, reverse=True)

def add_transition(v, trans, start=0, end=5, fps=30):
    if trans is None:
        return v
    duration = end-start
    # print(trans['trans_name'], trans['trans_args'])
    trans, trans_args = trans_dict[trans['trans_name']], trans['trans_args']
    trans = trans(v, **trans_args, fps=fps)
    trans_v = trans.v
    trans_dur = trans.durs[0]
    vw,vh = trans_v.size
    v = ProntoClip(clips=[trans_v,v], times=[0,[trans_dur, -1]], vh=vh, vw=vw, start=0, end=duration)
    # save_video(v, 'trans.mp4')
    return v

def add_clip_effect(v, effect, fps=30):
    if effect is None:
        return v
    effect, effect_args = clip_effects_dict[effect['effect_name']], effect['effect_args']
    v = effect(v, **effect_args, fps=fps)
    return v

trans_dict = {'slide_transition': slide_transition, 'zoom_transition':zoom_transition}

def fresh_end_effect(v, start=0, end=5, theme=[16,184,254], **kwargs):
    duration = end-start
    vw,vh = v.size
    bg = solid_color_img((vh,vw,3), color=theme, alpha=255)
    bg_clip = mp.ImageClip(bg, duration=duration)
    duration = max(duration, v.duration)
    return ProntoClip(clips=[v, bg_clip], pos=[[0,0], [0,0]], times=[[0,-1], [start, end]], vh=vh, vw=vw, end=duration)

clip_effects_dict = {}

class ProntoClip(ProntoClass):
    def __init__(self, bg_clip='', clips=[], vh=540, vw=960, start=0, end=5, pos=[], times=[], music_files=[], music_file='',
                 vo_files=[], vo_file='', logger=None,**kwargs):
        super().__init__(**locals_to_params(locals()))
        self.logger=logger
        self.duration = end-start
        self.first_frames = []
        for i,c in enumerate(self.clips):
            self.first_frames.append(first_frame(c))
            if type(c).__name__ == 'ProntoClip':
                self.clips[i] = c.v
        if path_or_str(bg_clip):
            bg_clip = str(bg_clip)
            if self.logger:
                self.logger.debug(f'**************** BG CLIP = {bg_clip}')
            if len(bg_clip) > 0:
                bg_clip = read_and_resize(bg_clip, dur=self.duration, h=vh, w=vw)
                self.first_frames.insert(0, first_frame(bg_clip))
                if self.logger:
                    self.logger.debug(f'**************** AFTER READ AND RESIZE: BG CLIP = {bg_clip}')
            else:
                bg_clip = mp.ImageClip(self.vbg, duration=self.duration).set_fps(self.fps)
                if self.logger:
                    self.logger.debug(f'**************** BG CLIP = {bg_clip}')
        else:
            bg_clip = bg_clip.set_duration(self.duration).subclip(0, self.duration)
            self.first_frames.insert(0, first_frame(bg_clip))
        if pos is None or len(pos) == 0:
            self.pos = [[0.5,0.5]]*len(self.clips)
        if times is None or len(times) == 0:
            self.times = []
            start = 0
            for c in self.clips:
                end = start+c.duration
                self.times.append([start, end])
                start = end
        self.bg_clip = bg_clip.set_fps(self.fps)
        self.get_shapes()
        self.create_structure()
        self.create_v()
    
    def create_structure(self, **kwargs):
        self.structure = Structure(h=self.vh, w=self.vw, shapes=self.shapes, pos=self.pos, times=self.times)
    
    def get_shapes(self, **kwargs):
        self.shapes = [[c.h, c.w] for c in self.clips]
                    
    def add_music(self, clips=[], music_files=[]):
        if not is_list(music_files):
            music_files = [music_files]
        if not is_list(clips):
            clips = [clips]
        for i, cm in enumerate(zip(clips, music_files)):
            clip, music_file = cm
            music_file = str(music_file)
            if len(music_file) > 0:
                clip_start = clip.start
                clip_end = clip.end
                audio_duration = clip_end-clip_start
                background_music = mp.AudioFileClip(music_file)
                bg_duration = background_music.duration
                while bg_duration <= 120:
                    background_music = mpa.AudioClip.concatenate_audioclips([background_music,
                                                                    background_music.subclip(bg_duration//2)])
                    bg_duration = background_music.duration
                bgm = background_music.subclip(0,audio_duration)#.audio_fadeout(3.5)
                pa = clip.audio
                if pa is not None:
                    print('COMPOSSIIITTEEEEE')
                    bgm = mp.CompositeAudioClip([pa.volumex(0.2),bgm]).set_fps(clip.fps)
                if clip.duration >= 10:
                    bgm = bgm.audio_fadeout(3.5)
                clip = clip.set_audio(bgm.subclip(0, audio_duration).set_start(clip.start).set_end(clip.end))
                clips[i] = clip
        if len(clips) == 1: clips = clips[0]
        return clips
    
    def add_vo(self, clips=[], music_files=[]):
        if not is_list(music_files):
            music_files = [music_files]
        if not is_list(clips):
            clips = [clips]
        for i, cm in enumerate(zip(clips, music_files)):
            clip, music_file = cm
            music_file = str(music_file)
            if len(music_file) > 0:
                bgm = mp.AudioFileClip(music_file)#.subclip(0,10)
                if bgm.duration >= clip.duration:
                    bgm = bgm.subclip(0,clip.duration)
                pa = clip.audio
                if pa is not None:
                    print('COMPOSSIIITTEEEEE')
                    bgm = mp.CompositeAudioClip([pa.volumex(0.2),bgm]).set_fps(clip.fps)
                clip = clip.set_audio(bgm.set_start(clip.start).set_end(clip.end))
                clips[i] = clip
        if len(clips) == 1: clips = clips[0]
        return clips
    
    def create_v(self):
        first_frame_clips = []
        # print(self.structure.pos)
        for i,group in enumerate(zip(self.clips, self.structure.pos, self.structure.times)):
            c,p,t = group
            if not is_list(t): t = [t]
            if len(t) == 1:
                t.append(t[0]+c.duration)
            if t[-1] == -1:
                t[-1] = self.duration
            self.clips[i] = c.set_position(p).set_start(t[0]).set_end(t[1]).set_audio(None)
            if t[0] == 0:
                first_frame_clips.append(mp.ImageClip(self.first_frames[i], duration=0.1))
        if len(self.clips) == 0:
            self.v = self.bg_clip
        else:
            self.v = CustomCompositeVideoClip([self.bg_clip,*self.clips])
        if len(first_frame_clips) > 0:
            self.first_frame = mp.CompositeVideoClip(first_frame_clips).get_frame(0)
        else:
            self.first_frame = self.vbg
        self.v.set_start(self.start).set_end(self.end)
        self.v = self.add_music(self.v, self.music_file)
        self.v = self.add_vo(self.v, self.vo_file)
        self.v = add_vo_files(self.v, self.vo_files)

def get_block_args(temp_blocks, clip_paths=[], texts=[], logo='', vh=540, vw=960, **kwargs):
    
    block_args_list = []
    texts_used = 0
    clips_used = 0
    bg_clip = mp.ImageClip(solid_color_img((vh, vw, 3), alpha=None), duration=1)
    extra_effect = {'effect_name': 'no_effect', 'effect_args': {}}
    if len(clip_paths) > 0:
        # block_clip_idx = []
        # block_text_idx = []
        for b in temp_blocks:
            block_name = b['block_name']
            block_args = block_config[block_name]
            convert_wh(block_args, height=vh, width=vw)
            block_duration = block_args.get('duration', 5)
            num_clips = block_args.get('num_clips', 1)
            clip_dims = block_args.get('clip_dims', [[vw,vh]]*num_clips)
            clip_pos = block_args.get('clip_pos', [[0,0]]*num_clips)
            clip_times = block_args.get('clip_times', [[0,block_duration]]*num_clips)
            clip_trans = block_args.get('clip_trans', [None]*num_clips)
            clip_trans += [None]*(num_clips-len(clip_trans))
            clip_effects = block_args.get('clip_effects', [None]*num_clips)
            clip_effects += [None]*(num_clips-len(clip_effects))
            num_texts = block_args.get('num_texts', 1)
            text_effects = b.get('effects', [extra_effect]*num_texts)
            text_effects += [extra_effect]*(num_texts-len(text_effects))
            text_pos = block_args.get('text_pos', [[0.5,0.5]]*num_texts)
            text_times = block_args.get('text_times', [[0,block_duration]]*num_texts)
            fps = block_args.get('fps', 30)
            
            clips_end_id = clips_used+num_clips
            texts_end_id = texts_used+num_texts
            
            if texts_end_id > len(texts):
                texts += ['']*(texts_end_id-len(texts))
            if clips_end_id > len(clip_paths):
                clip_paths += [bg_clip]*(clips_end_id-len(clip_paths))    
                
            clip_idx = b.get('clip_idx', list(range(clips_used, clips_end_id)))[:num_clips]
            clip_idx += [clip_idx[-1]]*(num_clips-len(clip_idx))
            b['clip_idx'] = clip_idx
            block_clips = list(np.array(clip_paths)[clip_idx])
            for i,zipped in enumerate(zip(read_clips(block_clips, dims=clip_dims), clip_trans, clip_effects, clip_times)):
                v,trans,effect,ct = zipped
                if ct[-1] == -1:
                    clip_times[i][-1] = block_duration
                block_clips[i] = add_transition(add_clip_effect(v, effect, fps=fps), trans, start=ct[0], end=ct[1], fps=fps)
                
            # block_clips = [add_transition(add_clip_effect(v, effect, fps=fps), trans, start=ct[0], end=ct[1], fps=fps) \
            #                for v,trans,effect,ct in zip(read_clips(block_clips, dims=clip_dims), clip_trans, clip_effects, clip_times)]
            
            text_idx = b.get('text_idx', list(range(texts_used, texts_end_id)))[:num_texts]
            text_idx += [text_idx[-1]]*(num_texts-len(text_idx))
            b['text_idx'] = text_idx
            block_texts = list(np.array(texts)[text_idx])
            
            for i,text_args in enumerate(zip(text_times, text_effects, block_texts)):
                tt,e,txt = text_args
                effect_args = e.get('effect_args', {})
                text_pos[i] = effect_args.get('pos', text_pos[i])
                if tt[-1] == -1:
                    text_times[i][-1] = block_duration
                convert_wh(effect_args, height=vh, width=vw)
                effect_name = e.get('effect_name', 'no_effect')
                block_clips.append(effects_dict[effect_name](text=txt, **dict(merge_dicts(effect_args, {'start':tt[0], 'end':tt[1]}))))
                
            block_pos = clip_pos + text_pos
            block_times = clip_times + text_times
            
            block_args_keys = dict_keys(block_args)
            if any(k.lower().find('logo')>=0 for k in block_args_keys) and len(logo)>0:
                wh = block_args.get('logo_dims', [200,200])
                if is_list(wh) and is_list(wh[0]):
                    wh = wh[0]
                w,h = wh
                logo_pos = block_args.get('logo_pos', [0.5,0.5])
                if is_list(logo_pos) and is_list(logo_pos[0]):
                    logo_pos = logo_pos[0]
                logo = resize_logo(logo, height=h, width=w)
                logo_clip = mp.ImageClip(logo, duration=1)
                logo_effect = block_args.get('logo_effect', None)
                logo_clip = add_clip_effect(logo_clip, logo_effect, fps=fps)
                logo_times = block_args.get('logo_times', [[0,block_duration]])
                if is_list(logo_times) and is_list(logo_times[0]):
                    logo_times = logo_times[0]
                block_clips.append(logo_clip)
                block_pos.append(logo_pos)
                block_times.append(logo_times)
            
            args_dict = {'block_clips':block_clips, 'block_pos': block_pos,'block_times':block_times,
                         'duration': block_args['duration'], 'fps':block_args['fps']}
            
            texts_used += num_texts
            clips_used += num_clips
            block_args_list.append(args_dict)
            
    return block_args_list
    
def create_block(block_clips=[], block_pos=[], block_times=[], duration=15, fps=30, **kwargs):
    start = 0
    end = duration
    return ProntoClip(clips=block_clips, pos=block_pos, times=block_times, start=start, end=end, fps=fps)

# def create_blocks(temp_blocks, clip_paths=[], texts=[], logo='', vh=540, vw=960, **kwargs):
#     block_args_list = get_block_args(temp_blocks=temp_blocks, clip_paths=clip_paths, texts=texts, logo=logo, vh=vh, vw=vw)
#     paths = []
#     for i,args in enumerate(block_args_list):
#         block = create_block(**args)
#         path = f'block_{i}.mp4'
#         paths.append(path)
#         save_video(block, path)
#     return paths

def create_blocks(temp_blocks, clip_paths=[], texts=[], logo='', vh=540, vw=960, **kwargs):
    block_args_list = get_block_args(temp_blocks=temp_blocks, clip_paths=clip_paths, texts=texts, logo=logo, vh=vh, vw=vw)
    return [create_block(**args) for args in block_args_list]

def get_num_block_clips_texts(block_name):
    num_clips = block_config[block_name]['num_clips']
    num_texts = block_config[block_name]['num_texts']
    return num_clips, num_texts

def create_video(template='Bold1', vh=540, vw=960, duration=60, clip_paths=[], logo='', vo_file='', vo_files=[],
                 music_file='', music_files=[], texts=[], logger=None, temp_blocks=[], **kwargs):
    
    if len(temp_blocks) == 0:
        temp_blocks = template_config[template][duration]['blocks']
    block_args_list = get_block_args(temp_blocks, clip_paths=clip_paths, texts=texts, vh=vh, vw=vw, logo=logo)
    # for i,ct in enumerate(zip(block_clip_idx, block_text_idx)):
    #     c,t = ct
    #     temp_blocks[i]['clip_idx'] = c
    #     temp_blocks[i]['text_idx'] = t
    blocks = [create_block(**block_args) for block_args in block_args_list]
    promo = ProntoClip(clips=blocks, vh=vh, vw=vw, start=0, end=duration,
                       music_file=music_file, music_files=music_files,
                       vo_file=vo_file, vo_files=vo_files, logger=logger)
    return promo.v, temp_blocks
