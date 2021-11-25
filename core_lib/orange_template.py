from core_lib.pronto_conf import *
from core_lib.template_component import *

class OrangeCTA(TemplateComponent):
    
    def __init__(self, font_sizes_path='cta_fonts.pkl', wrap_width=30,
                 font=LOCAL_FONTS_PATH+'template_fonts/GothicA1-Bold.ttf',
                 vw=960, vh=540, temp_color=(255,165,0), x=None, y=15, align='center',
                 color='white', stroke_width=0, stroke_fill='blue', bg=None,
                 **kwargs):
        super().__init__(**locals_to_params(locals()))
    
    def get_temp(self, w=960, h=150, temp_color=(255,165,0), text='', **kwargs):
        
        temp = solid_color_img(shape=(h,w,3), color=temp_color)
        return temp
    
    def adjust_temp(self, tm, text, fnt, text_x, text_y, vw=960, vh=540):
        #print(f'text_y: {text_y}')
        tw, th = fnt.getsize_multiline(text)
        tmh, tmw = tm.shape[:2]
        final_height = th+text_y*2+8
        if ((text_x*2 + tw) > int(vw/0.85)):
            text='Text Too Long'
        elif ((text_y + th) > vh/2):
            text='Too Much Text'
        elif ((text_x + tw) > tmw) or ((text_x + tw) < tmw-(text_x*2)):
            print(text)
            #tm = cv2.resize(tm, (tw+(text_x*3),th+x+10))
            tm = cv2.resize(tm, (tmw, final_height))
        else:
            tm = tm[:final_height]
        return tm
    
    def template_gen(self, text, vw=960, vh=540, temp_color=(255,165,0), x=None, y=15, align='center',
                     font=LOCAL_FONTS_PATH+'template_fonts/GothicA1-Bold.ttf', font_size=None,
                     color='white', stroke_width=0, stroke_fill='blue', bg=None, wrap_width=45,
                     **kwargs):
        if len(text) == 0:
            return None
        tm = self.get_temp(w=vw, h=vh//2, temp_color=temp_color, text=text)
        text, fnt, text_x, text_y = self.wrap_text_temp(tm, text, x=x, y=y, font_size=font_size, font=font,
                                                        wrap_width=wrap_width)
        tm = self.adjust_temp(tm=tm, text=text, fnt=fnt, text_x=text_x, text_y=text_y, vw=vw, vh=vh)
        tm = self.display_text_temp(img=tm, text=text, fnt=fnt, text_x=text_x, text_y=text_y, color=color,
                       stroke_width=stroke_width, stroke_fill=stroke_fill, align=align, bg=bg)
        return tm
    
    def temp_on_bg(self, bg, tm=None, corner_logo=None, y_factor=0.85,
                   corner_logo_x=0, corner_logo_y=0, **kwargs):
        
        if tm is None:
            return np.array(bg)

        background = to_pil(bg)
        bgw, bgh = background.size
        tmh, tmw = tm.shape[:2]
        
        x = 0
        y = int((bgh - tmh) * y_factor)
        index = (x,y)
        if corner_logo is not None:
            background = Image.fromarray(img_on_bg(background, corner_logo,
                                                   x_factor=corner_logo_x, y_factor=corner_logo_y))
        try:
            background.paste(Image.fromarray(tm), index, Image.fromarray(tm))
        except:
            background.paste(Image.fromarray(tm), index)
        img = np.array(background)
        return img
    
    def template_gen_fonts(self, text, vw=960, vh=540, temp_color=(255,165,0), x=15, y=15, align='center',
                     font=LOCAL_FONTS_PATH+'template_fonts/GothicA1-Bold.ttf', font_size=None,
                     color='white', stroke_width=0, stroke_fill='blue', bg=None, wrap_width=45, **kwargs):

        tm = self.get_temp(w=vw, h=vh//2, temp_color=temp_color, text=text)
        text, fnt, text_x, text_y = self.wrap_text_temp(tm, text, x=x, y=y, font_size=font_size, font=font,
                                                        wrap_width=wrap_width)
        tw, th = fnt.getsize_multiline(text)
        tmh, tmw = tm.shape[:2]
        return (((text_x + tw) < (tmw*5/6)) and ((text_y + th) < tmh))

    def animate_template(self, tm, frames, temp_fn, num_animate=30, **kwargs):
        num_animate -= 1
        if tm is None:
            return frames[:num_animate]
        tmh,tmw = tm.shape[:2]
        out_frames = [frames[0]]
        tm_chunks = list(reversed(chunkify(range(tmw), (tmw+1)//num_animate)))
        idx = 0
        for f,frame in enumerate(frames[1:num_animate]):
            chunk = tm_chunks[idx]
            left = chunk[0]
            tm2 = tm[:,left:]
            out_frames += [temp_fn(frame, tm=tm2)]
            if chunk[1] >= tmw:
                break
            idx = min(len(tm_chunks), idx+1)
        return out_frames

class OrangeCI(TemplateComponent):    
    
    def __init__(self, font_sizes_path='ci_fonts.pkl', wrap_width=30,
                 font=LOCAL_FONTS_PATH+'template_fonts/GothicA1-Bold.ttf',
                 vw=960, vh=540, temp_color=(255,165,0), x=None, y=15, align='center',
                 color='white', stroke_width=0, stroke_fill='blue', bg=None,
                 **kwargs):
        super().__init__(**locals_to_params(locals()))
    
    def get_temp(self, w=300, h=150, alpha=0, temp_color=(255,165,0), cta=False, text='', **kwargs):
        
        tm = Image.fromarray(solid_color_img(shape=(h,w,3), color=temp_color))
        tm.putalpha(alpha)
        tm = np.array(tm)
        return tm
    
    def adjust_temp(self, tm, text, fnt, text_x, text_y, vw=960, vh=540):
        
        tw, th = fnt.getsize_multiline(text)
        tmh, tmw = tm.shape[:2]
        print(tmh, tmw, th, tw)
        final_height = th+text_y*2+8
        if ((text_x*2 + tw) > int(vw/1.3)):
            text='Text Too Long'
        elif ((text_y + th) > vh/2):
            text='Too Much Text'
        elif (((text_x + tw) > tmw) or ((text_x + tw) < tmw-(text_x*2))):
            print(text)
            tm = cv2.resize(tm, (tw+(text_x*2),final_height))
            tmh, tmw = tm.shape[:2]
            print(tmh, tmw, th, tw)
        else:
            print('lalalalalala')
            tm = tm[:final_height]
        return tm
    
    def template_gen(self, text='', vw=960, vh=540, temp_color=(255,165,0), x=15, y=15, align='center',
                     font=LOCAL_FONTS_PATH+'template_fonts/GothicA1-Bold.ttf', font_size=None,
                     color='white', stroke_width=0, stroke_fill='blue', bg=None, wrap_width=30,
                     **kwargs):
        if len(text) == 0:
            return None
        tm = self.get_temp(w=int(vw/2.5), h=vh//2, temp_color=temp_color, text=text)
        text, fnt, text_x, text_y = self.wrap_text_temp(tm, text, x=x, y=y, font_size=font_size,
                                                        font=font, wrap_width=wrap_width)
        tm = self.adjust_temp(tm=tm, text=text, fnt=fnt, text_x=text_x, text_y=text_y, vw=vw, vh=vh)
        tm = self.display_text_temp(img=tm, text=text, fnt=fnt, text_x=text_x, text_y=text_y, color=color,
                       stroke_width=stroke_width, stroke_fill=stroke_fill, align=align, bg=bg)
        return tm
    
    def temp_on_bg(self, bg, tm=None, corner_logo=None, y_factor=0.85, x_factor=0.2, logo=None,
                   corner_logo_x=0, corner_logo_y=0, temp_color=(255,165,0), **kwargs):
        
        x_factor = 0.5
        y_factor = 0.5
        background = to_pil(bg)
        bgw, bgh = background.size
        if tm is not None:
            tmh, tmw = tm.shape[:2]
        else:
            tmh, tmw = 0,0
        
        ci_bg = Image.fromarray(solid_color_img(shape=(bgh,bgw,3), color=temp_color))
        ci_bg.putalpha(150)
        background.paste(ci_bg, (0,0), ci_bg)
        
        if corner_logo is not None:
            background = Image.fromarray(img_on_bg(background, corner_logo,
                                                   x_factor=corner_logo_x, y_factor=corner_logo_y))
        if logo is not None:
            logo = np.array(logo)
            logo = imutils.resize(logo, height=bgh//3)
            lh, lw = logo.shape[:2]
            total_h = lh+tmh+10

            lx = int((bgw - lw) * x_factor)
            tmx = int((bgw - tmw) * x_factor)
            y = int((bgh - total_h) * y_factor)
            tmy = y+lh+10

            offset_l = (lx, y)
            offset_tm = (tmx, tmy)
            
            background.paste(Image.fromarray(logo), offset_l)
            #try:
            #    background.paste(Image.fromarray(tm), offset_tm, Image.fromarray(tm))
            #except:
            #    background.paste(Image.fromarray(tm), offset_tm)
        else:
            tmx = int((bgw - tmw) * x_factor)
            tmy = int((bgh - tmh) * y_factor)
            offset_tm = (tmx, tmy)

        if tm is not None:
            try:
                background.paste(Image.fromarray(tm), offset_tm, Image.fromarray(tm))
            except:
                background.paste(Image.fromarray(tm), offset_tm)
        img = np.array(background)
        return img
    
    def template_gen_fonts(self, text, vw=960, vh=540, temp_color=(255,165,0), x=15, y=15, align='center',
                     font=LOCAL_FONTS_PATH+'template_fonts/GothicA1-Bold.ttf', font_size=None,
                     color='white', stroke_width=0, stroke_fill='blue', bg=None, wrap_width=30, **kwargs):

        tm = self.get_temp(w=int(vw/2.5), h=vh//2, temp_color=temp_color, text=text)
        text, fnt, text_x, text_y = self.wrap_text_temp(tm, text, x=x, y=y, wrap_width=wrap_width,
                                                        font_size=font_size,font=font)
        tw, th = fnt.getsize_multiline(text)
        tmh, tmw = tm.shape[:2]
        return (((text_x + tw) < tmw) and ((text_y + th) < tmh))

    def animate_template(self, tm, frames, temp_fn, num_animate=30, **kwargs):
        num_animate -= 1
        if tm is None:
            return frames[:num_animate]
        tmh,tmw = tm.shape[:2]
        out_frames = [frames[0]]
        tm_chunks = list(reversed(chunkify(range(tmw), (tmw+1)//num_animate)))
        idx = 0
        for f,frame in enumerate(frames[1:num_animate]):
            chunk = tm_chunks[idx]
            left = chunk[0]
            tm2 = tm[:,left:]
            out_frames += [temp_fn(frame, tm=tm2)]
            if chunk[1] >= tmw:
                break
            idx = min(len(tm_chunks), idx+1)
        return out_frames
    
    def template_on_vid(self, vid, tm, x_factor=0, y_factor=0.85, logo=None,
                        fps=30, corner_logo=None, corner_logo_x=0, corner_logo_y=0,
                        **kwargs):
        
        logo = copy_img(logo)
        corner_logo = copy_img(corner_logo)
        if is_list(vid):
            frames = vid
            fps=fps
        else:
            frames = list(vid.iter_frames())
            fps = vid.fps
        l = locals_to_params(locals(), omit=['vid','frames'])
        # frames_out = parallel_map(frames, self.temp_on_bg, **l)

        par_func = partial(self.temp_on_bg, **l)
        frames_out = parallel_map(frames, par_func)

        clip = mp.ImageSequenceClip(frames_out, fps=fps)
        return clip

class OrangeTemplate():
    def __init__(self, intro='', trans='', outro='', cta='', ci=[], logo=None,
                 font=LOCAL_FONTS_PATH+'template_fonts/GothicA1-Bold.ttf',
                 vw=960, vh=540, temp_color=(255,165,0), animation_dur=0.5,
                 temp_font_sizes_path='org_temp_fonts.pkl',
                 intro_font_sizes_path='org_intro_fonts.pkl',
                 cta_font_sizes_path='org_cta_fonts.pkl',
                 ci_font_sizes_path='org_ci_fonts.pkl',
                 logger=None,
                 **kwargs):
        
        l = locals_to_params(locals())
        self.intro = OrangeCI(font_sizes_path=intro_font_sizes_path, **l)
        self.cta = OrangeCTA(font_sizes_path=cta_font_sizes_path, **l)
        self.ci = OrangeCI(font_sizes_path=ci_font_sizes_path, **l)
        self.temp_component = TemplateComponent(font_sizes_path=temp_font_sizes_path, **l)
        
        self.intro_temp = self.intro.temp()
        self.cta_temp = self.cta.temp(text=cta)
        self.ci_temp = self.ci.temp(text=ci)
        self.trans_temp = self.temp_component.temp(text=trans)
        self.outro_temp = self.temp_component.temp(text=outro)
        
        self.intro_on_vid = partial(self.intro.template_on_vid, tm=self.intro_temp,
                                    animation_dur=animation_dur, logo=logo)
        self.cta_on_vid = partial(self.cta.template_on_vid, tm=self.cta_temp,
                                  animation_dur=animation_dur, temp_dur=5)
        self.trans_on_vid = partial(self.temp_component.template_on_vid, tm=self.trans_temp,
                                    animation_dur=animation_dur, temp_dur=5)
        self.outro_on_vid = partial(self.temp_component.template_on_vid, tm=self.outro_temp,
                                    animation_dur=animation_dur)
        self.ci_on_vid = partial(self.ci.template_on_vid, tm=self.ci_temp, logo=logo,
                                 animation_dur=animation_dur)
