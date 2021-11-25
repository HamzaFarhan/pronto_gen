from numpy.core.numeric import full
from core_lib.core import *
# from video_utils import *

class TemplateA():
    def __init__(self, texts=[], logo='',
                 font='/usr/local/share/fonts/energized/Poppins-ExtraBold.ttf',
                 duration=30, vh=540, vw=960, temp_color=[16,184,254], font_size=40, fps=30,
                 all_paths=[], pronto_paths=[], extra_paths=[], user_paths=[], music_file='',
                 oem_paths=[], watermark='', vo_data=[], vo_file='', logger=None,**kwargs):
        
        meta_dict = {
                     15: {'num_vids':4, 'num_extra':1},
                     30: {'num_vids':6, 'num_extra':1},
                     60: {'num_vids':8, 'num_extra':1}
                    }
        self.logger = logger
        
        reading_fn = partial(read_and_resize, fps=fps, promo_w=vw, promo_h=vh)
        clips, self.clip_paths = process_clips(all_clips=all_paths, pronto_paths=pronto_paths,
                                          extra_paths=extra_paths, user_paths=user_paths,
                                          meta_data=meta_dict[duration], reading_fn=reading_fn)
        
        texts = self.process_texts(texts)
        texts = texts[:len(clips)-1]
        self.num_components = len(texts)
        clip_lens = get_clip_lens(len(clips), duration)
        oem_reader = partial(read_and_resize, dur=None, fps=fps, promo_w=vw, promo_h=vh)
        clip_lens, self.oem_clip = handle_oem_dur(oem_clips=oem_paths, clip_lens=clip_lens,
                                                  reading_fn=oem_reader, duration=duration)
        self.vid_starts, self.vid_idx = self.get_vid_starts(clip_lens, self.num_components)
        print(self.vid_starts, self.vid_starts[:len(texts)])

        v_clips = [v.subclip(0,l) for v,l in zip(clips, clip_lens)]
        self.video = vo_on_clips(v_clips, vo_data=vo_data, vo_file=vo_file, duration=duration)
        logo = str(logo)
        #print(self.vid_starts, self.vid_idx)
        self.watermark = watermark
        self.clips = []
        self.intro_dur = self.vid_starts[1]
        self.fps = fps
        self.font = font
        self.font_size = font_size
        self.v_dur = duration
        self.vh, self.vw = vh, vw
        self.temp_color = temp_color
        self.music_file = music_file
        self.create_intro(texts[0], logo=logo)
        self.create_components(texts[1:])
        self.create_temp_clips()
        self.create_outro(logo)
    
    def process_texts(self, texts):
        if not is_list(texts):
            texts = [texts]
        texts = [list_map(t, str.capitalize) for t in texts]
        texts[0] = list_map(texts[0], str.upper)
        for i,t in enumerate(texts[-1]):
            if t[:3].lower() == 'www':
                texts[-1][i] = t.lower()
        self.texts = texts
        return texts
    
    def create_thumbnail(self, thumbnail_path=''):
         if len(thumbnail_path) > 0:
            plt.imsave(thumbnail_path, self.v.get_frame(1))
    
    def get_text_clips(self):
        paths_dict = {cp:'' for cp in self.clip_paths}
        for idx, text in zip(self.vid_idx, self.texts):
            paths_dict[self.clip_paths[idx]] = text_join(text)
        return paths_dict
    
    def get_vid_starts(self, clip_lens, num_components=5):
        num_components+=1
        cumsum = list(np.cumsum(clip_lens))
        vid_starts = [0]+cumsum[:-1]
        starts = []
        i = 0
        j = len(vid_starts)-1
        while 1:
            if len(starts)>=num_components:
                if starts[-1] < len(vid_starts)-1:
                    while (starts[-1] - starts[-2]) >= 3:
                        starts[-1]-=1
                break
            else:
                starts.append(i)
                i+=1
            if len(starts)<num_components:
                starts.append(j)
                j-=1
        starts = sorted(starts)
        vid_starts2 = list(np.array(vid_starts)[starts])
        vid_idx = [vid_starts.index(x) for x in vid_starts2[:-1]]
        return vid_starts2, vid_idx
    
    def create_intro(self, text, logo=''):
        
        gap = 15
        gap_2 = min(5,int(gap/3))
        bg = solid_color_img((self.vh, self.vw, 3), alpha=170, color=self.temp_color)
        blank_bgs, text_bgs, temp = text_template_components(text=text, temp_alpha=0, align='center',
                                                             text_bg_alpha=0, font_size=self.font_size,
                                                             font=self.font, gap=gap)
        
        th,tw = temp.shape[:2]
        pos = get_pos(temp, bg, (0.5, 0.15))
        underline = solid_color_img((10, 75, 3), color='white')
        pos_u = get_pos(underline, bg, (0.5, 0.5))
        pos_u = (pos_u[0],pos[1]+th-gap_2*2+10)
        
        self.clips = [
            mp.ImageClip(bg, duration=self.intro_dur)
        ]
        if len(text) > 0:
            self.clips += [
              mp.ImageClip(temp, duration=self.intro_dur-0.2).set_start(0.2).set_position(pos).fadein(0.5),
              mp.ImageClip(underline, duration=self.intro_dur-0.1).set_position(pos_u).set_start(0.1).fadein(0.5)]
        
        if len(logo) > 0:
            logo = imutils.resize(rgb_read(logo), width=int(self.vw/6))
            pos2 = get_pos(logo, bg, pos=('center', 0.8))
            pos2 = (pos2[0], pos_u[1]+50)
            self.clips += [mp.ImageClip(logo).set_duration(self.intro_dur).set_position(pos2)]
            
        cbg = to_pil(solid_color_img((500,500,3), alpha=0))
        d = ImageDraw.Draw(cbg)
        d.ellipse((0,0,490,490), fill=tuple(self.temp_color))
        self.clips += zoom_template(np.array(cbg), self.vh, self.vw, num_chunks=1, zoom_scales=[0.2, 3.],
                                    zoom_chunks=15, num_chunks_2=1, zoom_scales_2=[],
                                    pos=(0.5,0.5), temp_dur=0.5, fps=self.fps, start=self.intro_dur-0.2,
                                    vid_bg_color=self.temp_color, vid_bg_alpha=0, bg=bg)
        
        self.vid_starts = self.vid_starts[1:]
    
    def create_outro(self, logo=''):
        self.outro = []
        if len(logo) > 0:
            outro_start = self.vid_starts[-1]
            outro_dur = self.v_dur - outro_start
            bg = solid_color_img((self.vh, self.vw, 3), alpha=0)
            logo = imutils.resize(rgb_read(logo), height=int(self.vh/2))
            self.outro = zoom_template(logo, self.vh, self.vw, num_chunks=1, zoom_scales=[3, 1.],
                                 zoom_chunks=5, zoom_scales_2=None, temp_dur=outro_dur,
                                 fps=self.fps, vid_bg_color=self.temp_color, vid_bg_alpha=255,
                                 bg=bg, pos=(0.5, 0.5), start=outro_start)
        self.clips += self.outro
    
    def create_components(self, texts, font_size=30):
        
        self.bb_chunks = 10
        self.components = []
        directions = ['down', 'right']
        alignement = ['left', 'right']#, 'center']
        for idx,text in enumerate(texts):
            bb_direction = random.choice(directions)
            temp_direction = random.choice(directions)
            trans_direction = random.choice(directions)
            align = random.choice(alignement)
            blank_bgs, text_bgs, temp = text_template_components(text=text, temp_alpha=0, align=align,
                                                                 temp_bg_color=self.temp_color,
                                                                 text_bg_alpha=210, font_size=self.font_size,
                                                                 font=self.font
                                                                )
            pos = (0.,0.)
            shape = blank_bgs[0].shape[:2]+tuple([3])

            bbgs = [animate_appear(bbg, direction=bb_direction, num_chunks=self.bb_chunks, pos=pos,
                                   bg=solid_color_img(shape, 'black', alpha=0),
                                   fps=self.fps) for bbg in blank_bgs]

            tbgs = [paste_img(tbg, bg=solid_color_img(shape, 'black', alpha=0),
                              pos=pos) for tbg in text_bgs]
            temps = animate_appear(direction=temp_direction, img=temp,
                                   bg=solid_color_img(shape, alpha=0),
                                   pos=pos, num_chunks=10, fps=self.fps)[::-1]
            if idx == 0:
                trans = []
            else:
                trans = animate_appear(solid_color_img((self.vh, self.vw, 3), color=self.temp_color,
                                       alpha=255), direction=trans_direction, pos=pos, num_chunks=15,
                                       fps=self.fps)[::-1]
            
            self.components.append({'bbgs':bbgs, 'tbgs':tbgs, 'temps':temps, 'trans':trans})
            
    def create_temp_clips(self):
        
        fps = self.fps
        all_pos = [('left', 'top'), ('left', 'bottom'), ('center', 'center'),
                   ('right', 'bottom'), ('right', 'top')]
        clips = []
        for idx,component in enumerate(self.components):
            
            bbgs = component['bbgs']
            tbgs = component['tbgs']
            temps = component['temps']
            trans = component['trans']
            pos = get_pos(tbgs[0], solid_color_img((self.vh, self.vw, 3)), pos=random.choice(all_pos))
            
            trans_start = self.vid_starts[idx]
            bb_start = trans_start+0.5
            temp_dur = min(4, self.vid_starts[idx+1]-trans_start-1)
            bb_starts = [bb_start+self.bb_chunks/fps*i for i in range(len(bbgs))]
            bb_durs = [temp_dur-self.bb_chunks/fps*i for i in range(len(bbgs))]
            if idx > 0:                
                clips += [mp.ImageSequenceClip(trans, fps=fps).set_start(trans_start).set_position((0,0))]
            
            clips += [mp.ImageSequenceClip(bbg, fps=fps).set_duration(bb_durs[i])\
                     .set_start(bb_starts[i]).set_position(pos) for i,bbg in enumerate(bbgs)]

            clips += [mp.ImageClip(tbg).set_duration(bb_durs[i]-0.1).set_start(bb_starts[i]+0.1)\
                      .fadein(self.bb_chunks/fps).set_position(pos) for i,tbg in enumerate(tbgs)]
            #print(f'temp start: {bb_starts[-1]+bb_durs[-1]}')
            #print(f'trans start: {self.vid_starts[idx+1]}')
            clips += [mp.ImageSequenceClip(temps, fps=fps).set_start(bb_starts[-1]+bb_durs[-1]).set_position(pos)]
            
        self.clips += clips
        
    def add_music(self, promo, music_file):
        
        background_music = mp.AudioFileClip(music_file)
        bg_duration = background_music.duration
        while bg_duration <= 120:
            background_music = mpa.AudioClip.concatenate_audioclips([background_music,
                                                                     background_music.subclip(bg_duration//2)])
            bg_duration = background_music.duration
        bgm = background_music.subclip(0,promo.duration).audio_fadeout(3.5)
        pa = promo.audio
        if pa is not None:
            print('COMPOSSIIITTEEEEE')
            bgm = mp.CompositeAudioClip([bgm.volumex(0.2),pa]).set_fps(promo.fps)
        promo = promo.set_audio(bgm.subclip(0, promo.duration).audio_fadeout(3.5))
        return promo

    # def add_vo(self, promo, music_file):
        
    #     background_music = mp.AudioFileClip(music_file)
    #     bgm = background_music.subclip(0,promo.duration)#.audio_fadeout(3.5)
    #     pa = promo.audio
    #     if pa is not None:
    #         print('COMPOSSIIITTEEEEE')
    #         bgm = mp.CompositeAudioClip([bgm,pa.volumex(0.5)]).set_fps(promo.fps)
    #     promo = promo.set_audio(bgm.subclip(0, promo.duration))#.audio_fadeout(3.5))
    #     return promo
    
    def create_video(self):
        v = mp.CompositeVideoClip([self.video]+self.clips)
        v = add_oem(v, self.oem_clip, self.v_dur, self.music_file, self.add_music)
        v = add_wm(v, self.watermark)
        self.v = v
        return v

class TemplateB(TemplateA):
    def __init__(self, texts=[], logo='',
                 font='/usr/local/share/fonts/energized/Poppins-ExtraBold.ttf',
                 duration=30, vh=540, vw=960, temp_color='blue', font_size=95, wrap_width=15, fps=30,
                 all_paths=[], pronto_paths=[], extra_paths=[], user_paths=[], music_file='',
                 oem_paths=[], watermark='', vo_data=[], vo_file='', logger=None,**kwargs):
        self.logger = logger
        texts = copy.deepcopy(texts)
        meta_dict = {
                     15: {'num_vids':4, 'num_extra':1},
                     30: {'num_vids':6, 'num_extra':1},
                     60: {'num_vids':8, 'num_extra':1}
                    }
        reading_fn = partial(read_and_resize, fps=fps, promo_w=vw, promo_h=vh)
        clips, self.clip_paths = process_clips(all_clips=all_paths, pronto_paths=pronto_paths,
                                          extra_paths=extra_paths, user_paths=user_paths,
                                          meta_data=meta_dict[duration], reading_fn=reading_fn)
        texts = self.process_texts(texts)
        self.num_components = len(texts)
        clip_lens = get_clip_lens(len(clips), duration)
        oem_reader = partial(read_and_resize, dur=None, fps=fps, promo_w=vw, promo_h=vh)
        clip_lens, self.oem_clip = handle_oem_dur(oem_clips=oem_paths, clip_lens=clip_lens,
                                                  reading_fn=oem_reader, duration=duration)
        self.vid_starts, self.vid_idx = self.get_vid_starts(clip_lens, self.num_components)

        v_clips = [v.subclip(0,l) for v,l in zip(clips, clip_lens)]
        self.video = vo_on_clips(v_clips, vo_data=vo_data, vo_file=vo_file, duration=duration)

        # self.video = mp.concatenate_videoclips([v.subclip(0,l) for v,
                                                # l in zip(clips, clip_lens)]).subclip(0, duration)
        #print(self.vid_starts, self.vid_idx)
        # print(texts)
        # print(self.vid_starts, self.vid_starts[:len(texts)])
        self.watermark = watermark
        logo = str(logo)
        self.clips = []
        self.intro_dur = self.vid_starts[1]
        self.fps = fps
        self.font = font
        self.font_size = font_size
        self.wrap_width = wrap_width
        self.v_dur = duration
        self.vh, self.vw = vh, vw
        self.temp_color = temp_color
        self.music_file = music_file
        self.create_components(texts[:-1])
        self.create_temp_clips()
        self.create_outro(texts[-1],logo)
    
    def process_texts(self, texts):
        if not is_list(texts):
            texts = [texts]
        texts = [list_map(t, str.upper) for t in texts]
        texts[-1] = list_map(texts[-1], str.capitalize)
        for i,t in enumerate(texts[-1]):
            if t[:3].lower() == 'www':
                texts[-1][i] = t.lower()
        self.texts = texts
        return texts
    
    def get_vid_starts(self, clip_lens, num_components=5):
        num_components+=1
        cumsum = list(np.cumsum(clip_lens))
        vid_starts = [0]+cumsum
        # print(num_components)
        # print(f'clip_lens: {clip_lens}')
        # print(f'cumsum: {cumsum}')
        # print(f'vid_starts: {vid_starts}')
        starts = []
        i = 0
        j = len(vid_starts)-1
        while 1:
            if len(starts)>=num_components:
                if starts[-1] < len(vid_starts)-1:
                    while (starts[-1] - starts[-2]) >= 3:
                        starts[-1]-=1
                # print(f'starts: {starts}')
                break
            else:
                starts.append(i)
                i+=1
            if len(starts)<num_components:
                starts.append(j)
                j-=1
        starts = sorted(starts)
        vid_starts2 = list(np.array(vid_starts)[starts])
        # print(f'vs2: {vid_starts2}')
        vid_idx = [vid_starts.index(x) for x in vid_starts2[:-1]]
        return vid_starts2, vid_idx
    
    def create_outro(self, text='', logo=''):
        if len(text) > 0 or len(logo) > 0:
            self.outro = []
            gap = 0
            temp_start = self.vid_starts[-2]
            temp_dur = self.vid_starts[-1] - temp_start
            th,tw,lh,lw = 0,0,0,0
            logo_xy = (0,0)
            if len(text) > 0:
                text = text_template_components(text, font=self.font, font_size=25, gap=0, align='center',
                                                text_bg_alpha=0, full_text_bg=True)[-1]
                th,tw = text.shape[:2]
            if len(logo) > 0:
                gap = 7
                logo = imutils.resize(rgb_read(logo), height=int(self.vh/3))
                lh,lw = logo.shape[:2]
            total_h = lh+gap+th
            total_w = max(lw, tw)
            temp_bg = solid_color_img((total_h,total_w,3), alpha=0)
            if len(logo) > 0:
                logo_xy = get_pos(logo, temp_bg, (0.5, 0.))
                temp_bg = paste_img(logo, temp_bg, logo_xy, relative=False)
            if len(text) > 0:
                text_xy = (get_pos(text, temp_bg, (0.5, 0.5))[0], logo_xy[1]+lh+gap)
                temp_bg = paste_img(text, temp_bg, text_xy, relative=False)
            bg = solid_color_img((self.vh, self.vw, 3), alpha=0)
            self.outro = zoom_template(temp_bg, self.vh, self.vw, num_chunks=1, zoom_scales=[3, 1.],
                                    zoom_chunks=5, zoom_scales_2=None, temp_dur=temp_dur,
                                    fps=self.fps, vid_bg_color=self.temp_color, vid_bg_alpha=45,
                                    bg=bg, pos=(0.5, 0.5), start=temp_start)
            self.clips += self.outro

    # def create_outro(self, text='', logo=''):
    #     self.outro = []
    #     if len(logo) > 0:
    #         outro_start = self.vid_starts[-2]
    #         outro_dur = self.vid_starts[-1] - outro_start
    #         logo = imutils.resize(rgb_read(logo), height=int(self.vh/3))
    #         lh,lw = logo.shape[:2]
    #         h,w = logo.shape[:2]
    #         if len(text) > 0:
    #             text = text_template_components(text, font=self.font, font_size=25, gap=0, align='center',
    #                                            text_bg_alpha=0)[-1]
    #             th,tw = text.shape[:2]
    #             h = lh+5+th
    #             w = max(lw,tw)
    #         logo_bg = solid_color_img((h,w,3), alpha=0)
    #         logo_xy = get_pos(logo, logo_bg, (0.5, 0.))
    #         logo_img = paste_img(logo, logo_bg, logo_xy, relative=False)
    #         if len(text) > 0:
    #             text_xy = (get_pos(text, logo_bg, (0.5, 0.5))[0], logo_xy[1]+lh+5)
    #             logo_img = paste_img(text, logo_img, text_xy, relative=False)
    #         bg = solid_color_img((self.vh, self.vw, 3), alpha=0)
    #         self.outro = zoom_template(logo_img, self.vh, self.vw, num_chunks=1, zoom_scales=[3, 1.],
    #                              zoom_chunks=5, zoom_scales_2=None, temp_dur=outro_dur,
    #                              fps=self.fps, vid_bg_color=self.temp_color, vid_bg_alpha=45,
    #                              bg=bg, pos=(0.5, 0.5), start=outro_start)
    #     self.clips += self.outro
    
    def create_components(self, texts):
        
        self.components = []
        alignement = ['left', 'right']#, 'center']
        for idx,text in enumerate(texts):
            align = random.choice(alignement)
            align = 'left'
            blank_bgs, text_bgs, temp = text_template_components(text=text, temp_alpha=0, align=align,
                                                                 temp_bg_color=self.temp_color,
                                                                 text_bg_alpha=0, font_size=self.font_size,
                                                                 font=self.font, wrap_width=self.wrap_width
                                                                )
            
            self.components.append({'temp':temp})
            
    def create_temp_clips(self):
        
        fps = self.fps
        all_pos = [('left', 'top'), ('left', 'bottom'), ('center', 'center'),
                   ('right', 'bottom'), ('right', 'top')]
        clips = []
        for idx,component in enumerate(self.components):
            
            temp = component['temp']
            bg_shape = (self.vh, self.vw, 3)
            bg = solid_color_img(bg_shape, alpha=0)
            pos = pos=('left', 'center')
            temp_start = self.vid_starts[idx]
            temp_dur = min(4, self.vid_starts[idx+1]-temp_start-1)
            #print(temp.shape, bg.shape)
            clips += zoom_template(temp, self.vh, self.vw, num_chunks=3, zoom_scales=[5, 1.],
                                   zoom_chunks=3, num_chunks_2=1, zoom_scales_2=[1,5], zoom_chunks_2=2,
                                   temp_dur=temp_dur, fps=self.fps, vid_bg_color=self.temp_color,
                                   vid_bg_alpha=45, bg=bg, pos=pos, start=temp_start)
            
        self.clips += clips

class TemplateC(TemplateA):
    def __init__(self, texts=[], logo='',
                 font='/usr/local/share/fonts/relaxed/NotoSansTC-Medium.otf',
                 duration=30, vh=540, vw=960, temp_color='blue', font_size=30, wrap_width=55, fps=30,
                 all_paths=[], pronto_paths=[], extra_paths=[], user_paths=[], music_file='',
                 oem_paths=[], watermark='', vo_data=[], vo_file='', logger=None,**kwargs):
        self.logger = logger
        meta_dict = {
                     15: {'num_vids':4, 'num_extra':1, 'cta_id':1},
                     30: {'num_vids':6, 'num_extra':1, 'cta_id':2},
                     60: {'num_vids':8, 'num_extra':1, 'cta_id':2}
                    }
        
        reading_fn = partial(read_and_resize, fps=fps, promo_w=vw, promo_h=vh)
        clips, self.clip_paths = process_clips(all_clips=all_paths, pronto_paths=pronto_paths,
                                          extra_paths=extra_paths, user_paths=user_paths,
                                          meta_data=meta_dict[duration], reading_fn=reading_fn)
        self.cta_id = meta_dict[duration]['cta_id']
        texts = self.process_texts(texts)
        self.num_components = len(texts)
        clip_lens = get_clip_lens(len(clips), duration)
        oem_reader = partial(read_and_resize, dur=None, fps=fps, promo_w=vw, promo_h=vh)
        clip_lens, self.oem_clip = handle_oem_dur(oem_clips=oem_paths, clip_lens=clip_lens,
                                                  reading_fn=oem_reader, duration=duration)
        self.vid_starts, self.vid_idx = self.get_vid_starts(clip_lens, self.num_components)

        v_clips = [v.subclip(0,l) for v,l in zip(clips, clip_lens)]
        self.video = vo_on_clips(v_clips, vo_data=vo_data, vo_file=vo_file, duration=duration)

        # self.video = mp.concatenate_videoclips([v.subclip(0,l) for v,
                                                # l in zip(clips, clip_lens)]).subclip(0, duration)
        # print(self.vid_starts, self.vid_idx)
        print(self.vid_starts, self.vid_starts[:len(texts)])
        self.watermark = watermark
        logo = str(logo)
        self.clips = []
        self.intro_dur = self.vid_starts[1]
        self.fps = fps
        self.font = font
        self.font_size = font_size
        self.wrap_width = wrap_width
        self.v_dur = duration
        self.vh, self.vw = vh, vw
        self.temp_color = temp_color
        self.music_file = music_file
        self.create_components(texts)
        self.create_intro(logo=logo)
        self.create_temp_clips()
        self.create_outro(logo=logo)
    
    def process_texts(self, texts):
        if not is_list(texts):
            texts = [texts]
        texts = [list_map(t, str.upper) for t in texts]
        texts[1] = list_map(texts[1], str.capitalize)
        texts[self.cta_id] = list_map(texts[self.cta_id], str.upper)
        texts[-2] = list_map(texts[-2], str.capitalize)
        self.texts = texts
        return texts
    
    def get_vid_starts(self, clip_lens, num_components=5):
        num_components+=1
        cumsum = list(np.cumsum(clip_lens))
        vid_starts = [0]+cumsum
        starts = []
        i = 0
        j = len(vid_starts)-1
        while 1:
            if len(starts)>=num_components:
                if starts[-1] < len(vid_starts)-1:
                    while (starts[-1] - starts[-2]) >= 3:
                        starts[-1]-=1
                break
            else:
                starts.append(i)
                i+=1
            if len(starts)<num_components:
                starts.append(j)
                j-=1
        starts = sorted(starts)
        vid_starts2 = list(np.array(vid_starts)[starts])
        vid_idx = [vid_starts.index(x) for x in vid_starts2[:-1]]
        return vid_starts2, vid_idx
    
    def create_intro(self, logo=''):
        
        gap = 15
        temp = self.components[0]['temp']
        th,tw = temp.shape[:2]
        temp_start = self.vid_starts[0]
        temp_dur = min(4, self.vid_starts[1]-temp_start-1)
        bg = solid_color_img((self.vh, self.vw, 3), alpha=0)
        temp_pos = (0.5, 0.5)
        temp_xy = get_pos(temp, bg, temp_pos)
        clips = []
        if len(logo) > 0:
            logo = imutils.resize(rgb_read(logo), height=int(self.vh/4))
            lh,lw = logo.shape[:2]
            total_h = lh+gap+th
            
            logo_bg = solid_color_img((total_h,lw,3), alpha=3)
            logo_pos = get_pos(logo_bg, bg, pos=temp_pos)
            logo_pos = (int(logo_pos[0]), int(logo_pos[1]))
            clips += [mp.ImageSequenceClip([logo], fps=self.fps)\
                      .set_duration(temp_dur).set_position(logo_pos)]
            
            temp_pos = (int(temp_xy[0]), logo_pos[1]+lh+gap)
            
        
        clips += open_template(temp, vh=self.vh, vw=self.vw, num_chunks=5, num_chunks_2=3, pos=temp_pos,
                               temp_start=temp_start, temp_dur=temp_dur, fps=self.fps)
        self.clips += clips
    
    def create_outro(self, logo=''):
        
        gap = 15
        th,tw,lh,lw = 0,0,0,0
        temp = self.components[-1]['temp']
        th,tw = temp.shape[:2]
        if len(logo) > 0 or (th>1 and th>1):
            # temp = paste_img(temp, solid_color_img((th, tw-10, 3),
                                #  color=(40,40,40), alpha=170))
            temp_start = self.vid_starts[-2]
            temp_dur = self.vid_starts[-1]-temp_start
            bg = solid_color_img((self.vh, self.vw, 3), alpha=0)
            temp_pos = (0.5, 0.5)
            temp_xy = get_pos(temp, bg, temp_pos)
            clips = []
            if len(logo) > 0:
                logo = imutils.resize(rgb_read(logo), height=int(self.vh/4))
                lh,lw = logo.shape[:2]
                total_h = lh+gap+th
                logo_bg = solid_color_img((total_h,lw,3), alpha=30)
                logo_pos = get_pos(logo_bg, bg, pos=temp_pos)
                logo_pos = (int(logo_pos[0]), int(logo_pos[1]))
                clips += [mp.ImageSequenceClip([logo], fps=self.fps)\
                        .set_duration(temp_dur).set_position(logo_pos).set_start(temp_start)]
                
                temp_pos = (int(temp_xy[0]), logo_pos[1]+lh+gap)
            
            clips += open_template(temp, self.vh, self.vw, num_chunks=5, num_chunks_2=0, pos=temp_pos,
                                temp_start=temp_start, temp_dur=temp_dur, fps=self.fps)
            self.clips += clips
    
    def create_components(self, texts):
        
        self.components = []
        for idx,text in enumerate(texts):
            align = 'center'
            full_text_bg = True
            text_bg_color = (40,40,40)
            text_bg_alpha = 170
            if idx == self.cta_id:
                text_bg_color = self.temp_color
                text_bg_alpha = 140
            blank_bgs, text_bgs, temp = text_template_components(text=text, align=align,
                                                                 temp_alpha=0, full_text_bg=full_text_bg,
                                                                 temp_color=self.temp_color, gap=10,
                                                                 text_bg_alpha=text_bg_alpha,
                                                                 text_bg_color=text_bg_color,
                                                                 font_size=self.font_size,
                                                                 font=self.font, wrap_width=self.wrap_width
                                                                )
            th,tw = temp.shape[:2]
            if len(text) > 0 and idx != self.cta_id:
                th,tw = temp.shape[:2]
                line = solid_color_img((th,5,3), color=self.temp_color, alpha=225)
                temp = np.concatenate([line, temp, line], axis=1)
            self.components.append({'temp':temp})
            
    def create_temp_clips(self):
        
        clips = []
        for idx,component in enumerate(self.components[1:-1], start=1):
            
            temp = component['temp']
            #th,tw = temp.shape[:2]
            #temp_bg_shape = (th, tw, 3)
            #temp_bg = solid_color_img(temp_bg_shape, alpha=0)
            #bg_shape = (self.vh, self.vw, 3)
            #bg = solid_color_img(bg_shape, alpha=0)
            pos = (0.5, 0.85)
            temp_start = self.vid_starts[idx]
            temp_dur = min(4, self.vid_starts[idx+1]-temp_start-1)
            clips += open_template(temp, self.vh, self.vw, num_chunks=5, num_chunks_2=3, pos=pos,
                                   temp_start=temp_start, temp_dur=temp_dur, fps=self.fps)
            #clips += [mp.ImageSequenceClip(animate_open(temp, bg=temp_bg, num_chunks=5, fps=self.fps),
            #         fps=self.fps).set_duration(temp_dur).set_start(temp_start).set_position(pos)]
            
        self.clips += clips

class CandidTemplate(ProntoClass):
    def __init__(self, vh=540, vw=960, duration=30, fps=30, font_size=30,
                 font='/usr/local/share/fonts/relaxed/NotoSansTC-Medium.otf',
                 temp_color='blue', texts=[], logo='', clip_paths=[],
                 music_file='', music_files=[], vo_file='', vo_files=[], logger=None, **kwargs):
        super().__init__(**locals_to_params(locals()))
        self.texts = text_case(texts, 'capitalize')
        self.logo = str(logo)
        getattr(self, f'create_{duration}')()
        self.create_v()
    
    def create_clip(self, clip, text='', start=0, end=5):
        
        duration = end-start
        pos = [[0.5,0.85]]*2
        close_dur = 3/self.fps
        open_end = duration-close_dur*2
        times = [[0,open_end], open_end]

        if len(text) > 0:
            text = text_template(text=text, wrap_width=55, font=self.font, font_size=self.font_size,
                                 gap=10, align='center', color='white', full_text_bg=True, text_bg_alpha=170,
                                 text_bg_color=(40,40,40))
            th,tw = get_hw(text)
            line = solid_color_img((th,5,3), color=self.temp_color, alpha=225)
            text = np.concatenate([line, text, line], axis=1)
            
            text_an = OpenCloseAnimation(temp=text, direction='mh', vh=self.vh, vw=self.vw, num_chunks=5, num_chunks_2=3, fps=self.fps)
            clips = [text_an.open, text_an.close]            
            
            clip = ProntoClip(clip, vh=self.vh, vw=self.vw, clips=clips, pos=pos,
                              times=times, end=duration).v
        else:
            clip = read_and_resize(clip, dur=duration, h=self.vh, w=self.vw)
        return clip
    
    def create_clips(self, durs=[5,5,5,5,5], start=5, start_id=1, end_id=5):
        
        n = 0
        for i in range(start_id, end_id):
            dur = durs[n]
            txt = self.texts[i]
            end = start+dur
            self.times += [[start, end]]
            clip = self.clip_paths[i]
            fn = partial(self.create_clip, clip=clip, start=start, end=end)
            self.clips_fn.append(fn)
            self.clips.append(fn(text=txt))
            n+=1
            start=end
    
    def create_first(self, clip, text='', start=0, end=5):
        duration = end-start
        clips = []
        pos = []
        times = []

        text = text_template(text=text, wrap_width=55, font=self.font, font_size=self.font_size,
                                gap=10, align='center', color='white', full_text_bg=True, text_bg_alpha=170,
                                text_bg_color=(40,40,40))
        th,tw = get_hw(text)
        if th > 1:
            line = solid_color_img((th,5,3), color=self.temp_color, alpha=225)
            text = np.concatenate([line, text, line], axis=1)
        
        text_an = OpenCloseAnimation(temp=text, direction='mh', vh=self.vh, vw=self.vw, num_chunks=5, num_chunks_2=3, fps=self.fps)
        clips += [text_an.open, text_an.close]            
        pos += [[0.5,0.5]]*2
        close_dur = 3/self.fps
        open_end = duration-close_dur*2
        times += [[0,open_end], open_end]
            
        if len(self.logo) > 0:
            logo = resize_logo(self.logo, height=int(self.vh/4))
            lh,lw = get_hw(logo)
            clips.append(mp.ImageClip(logo, duration=open_end))
            pos.append([0.5,f'fwd_pos_y-{15+lh}'])
            times.append(0)
        clip = ProntoClip(clip, clips=clips, vh=self.vh, vw=self.vw, end=duration, pos=pos, times=times).v     
        return clip
    
    def get_text_clips(self):
        paths_dict = {cp:text_join(txt) for cp,txt in zip(self.clip_paths, self.texts)}
        return paths_dict
    
    def create_15(self):
        self.clips = []
        self.clips_fn = []
        self.times = []
        dur = 4
        fn = partial(self.create_first, start=0, end=dur)
        self.clips_fn.append(fn)
        self.clips.append(fn(clip=self.clip_paths[0], text=self.texts[0]))
        self.times.append([0,dur])
        self.create_clips(durs=[4,4,3], start=dur, start_id=1, end_id=4)
    
    def create_30(self):
        self.clips = []
        self.clips_fn = []
        self.times = []
        dur = 5
        fn = partial(self.create_first, start=0, end=dur)
        self.clips_fn.append(fn)
        self.clips.append(fn(clip=self.clip_paths[0], text=self.texts[0]))
        self.times.append([0,dur])
        self.create_clips(durs=[dur]*5, start=dur, start_id=1, end_id=6)
    
    def create_60(self):
        self.clips = []
        self.clips_fn = []
        self.times = []
        dur = 8
        fn = partial(self.create_first, start=0, end=dur)
        self.clips_fn.append(fn)
        self.clips.append(fn(clip=self.clip_paths[0], text=self.texts[0]))
        self.times.append([0,dur])
        self.create_clips(durs=[8, 8, 8, 7, 7, 7, 7], start=dur, start_id=1, end_id=8)
    
    def create_v(self):
        for i,c in enumerate(self.clips):
            if hasattr(c, 'save_clip') and c.save_clip:
                save_video(c, f'bold_{i}.mp4')
        self.v = ProntoClip(clips=self.clips, times=self.times, start=0, end=self.duration, vh=self.vh, vw=self.vw, music_file=self.music_file, music_files=self.music_files, vo_file=self.vo_file, vo_files=self.vo_files).v

class SAPTemplate(ProntoClass):
    def __init__(self, vh=540, vw=960, duration=30, fps=30, font_size1=35, font_size2=25,
                 font1='/usr/local/share/fonts/FranklinGothic_Bold.ttf',
                 font2='/usr/local/share/fonts/FranklinGothic-Light.ttf',
                 temp_color=[255,215,0], texts=[], logo='', clip_paths=[],
                 music_file='', music_files=[], vo_file='', vo_files=[], **kwargs):
        super().__init__(**locals_to_params(locals()))
        self.texts = text_case(texts, 'upper')
        self.logo = str(logo)
        self.clip_paths = [x for x in self.clip_paths if 'newtemplate_boundry' not in x]
        getattr(self, f'create_{duration}')()
        self.create_v()
    
    def create_clip(self, clip, text='', start=0, end=5):
        
        duration = end-start
        clips = []
        times = []
        pos = []
        if len(text) > 0:
            if not is_list(text):
                text = [text]
            t1 = text[0]
            text1 = text_template(text=t1, wrap_width=25, font=self.font1, font_size=self.font_size1,
                                  gap=0, align='left', color='white', full_text_bg=True, text_bg_alpha=0)
            if len(text) > 1:
                t2 = text[1]
            else:
                t2 = ''
            text2 = text_template(text=t2, wrap_width=40, font=self.font2, font_size=self.font_size2,
                                  gap=0, align='left', color='white', full_text_bg=True, text_bg_alpha=0)
            
            chunks = 10
            an_dur = chunks/self.fps
            
            text1_an = HorizontalSlideAnimation(text1, direction='right', num_chunks=chunks,
                                                vh=self.vh, vw=self.vw).fwd
            text2_an = VerticalSlideAnimation(text2, direction='down', num_chunks=chunks,
                                              vh=self.vh, vw=self.vw).fwd
            
            h1,w1 = get_hw(text1)
            h2,w2 = get_hw(text2)
            slider1 = solid_color_img((h1+h2+10,self.vw//8,3), color=self.temp_color)
            sh,sw = get_hw(slider1)
            barw = 10
            bar = solid_color_img((sh, barw, 3), color=self.temp_color)
            sh2, sw2 = sh,self.vw-sw+barw
            slider2 = solid_color_img((sh2,sw2,3), color=self.temp_color)
            
            slider1_an1 = HorizontalSlideAnimation(slider1, direction='right', num_chunks=chunks,
                                                   vh=self.vh, vw=self.vw).fwd
            slider1_an2 = HorizontalSlideAnimation(slider1, direction='left', num_chunks=chunks,
                                                   vh=self.vh, vw=self.vw).bwd
            
            slider2_an1 = HorizontalSlideAnimation(slider2, direction='right', num_chunks=chunks,
                                                   vh=self.vh, vw=self.vw).fwd
            slider2_an2 = HorizontalSlideAnimation(slider2, direction='left', num_chunks=chunks,
                                                   vh=self.vh, vw=self.vw).bwd
            bar_clip = mp.ImageClip(bar, duration=an_dur)
            ans_dur = min(duration, 4)
            clips = [slider1_an1, slider1_an2, bar_clip, text1_an, text2_an, slider2_an1, slider2_an2]
            times = [0, an_dur, [an_dur, ans_dur-an_dur], [an_dur, ans_dur-an_dur],
                     [an_dur*2, ans_dur-an_dur], ans_dur-an_dur*2, ans_dur-an_dur]
            pos = [[0.,0.8], [0.,0.8], [sw-barw, 0.8], [f'fwd_pos_x+{5+barw}', 'fwd_pos_y+5'],
                   ['fwd_pos_x', f'fwd_pos_y+{h1}'], ['fwd_pos_x2', 'fwd_pos_y2'],
                   ['fwd_pos_x2', 'fwd_pos_y2']]
            
            clip = ProntoClip(clip, vh=self.vh, vw=self.vw, clips=clips, pos=pos,
                              times=times, end=duration).v
            
        else:
            clip = read_and_resize(clip, dur=duration, h=self.vh, w=self.vw)
        return clip
    
    def create_last(self, text='', start=0, end=5, **kwargs):
        
        duration = end - start
        text = text_template(text, wrap_width=25, font_size=self.font_size1, font=self.font1,
                             text_bg_alpha=255, text_bg_color='black', gap=0)
        text_clip = HorizontalSlideAnimation(text, direction='right', vh=self.vh, vw=self.vw,
                                             num_chunks=10).fwd
        th,tw = get_hw(text)
        clips = [text_clip]
        times = [[0,-1]]
        pos = [[0.5,0.5]]
        logo = self.logo
        if len(logo) > 0:
            logo = resize_logo(self.logo, height=35)
            logo_clip = mp.ImageClip(logo, duration=duration).fadein(0.5)
            clips.append(logo_clip)
            times.append([1,-1])
            pos.append([0.5, f'fwd_pos_y+{th+50}'])
        
        return ProntoClip(clips=clips, vh=self.vh, w=self.vw, times=times, pos=pos, end=duration).v
    
    def create_clips(self, durs=[5,5,5,5,5], start=5, start_id=1, end_id=5):
        
        n = 0
        for i in range(start_id, end_id):
            dur = durs[n]
            txt = self.texts[i]
            end = start+dur
            self.times += [[start, end]]
            clip = self.clip_paths[i-1]
            fn = partial(self.create_clip, clip=clip, start=start, end=end)
            self.clips_fn.append(fn)
            self.clips.append(fn(text=txt))
            n+=1
            start=end
        dur = durs[n]
        idx = end_id
        end = self.duration
        self.times += [[start, -1]]
        fn = partial(self.create_last, text=self.texts[idx], start=start, end=end)
        self.clips_fn.append(fn)
        self.clips.append(fn())
    
    def create_first(self, text='', start=0, end=5):
        duration = end-start
        clips = []
        times = []
        pos = []
        wrap_width = 35
        if not is_list(text):
            text = [text]
        t1 = text[0]
        t2 = ''
        if len(text) > 1:
            t2 = text[1]
        if len(t1) > 0:
            
            intro_list = textwrap.wrap(t1, wrap_width)
            intro_list = [text_template(text=t.upper(),text_bg_alpha=255, gap=0,
                          text_bg_color='black', temp_alpha=0, wrap_width=wrap_width,
                          font_size=self.font_size1, font=self.font1, align='left', color='white',
                          full_text_bg=True) for t in intro_list]
            
            intro_clips = [VerticalSlideAnimation(t, direction='up', num_chunks=10,
                                                  vh=self.vh, vw=self.vw).fwd for t in intro_list]
            th_list = [get_hw(x)[0] for x in intro_list]
            th = sum(th_list)
            lh,lw = self.vh-th-200, 3
            line = solid_color_img((lh,lw, 3), color='white')
            line_clip = VerticalSlideAnimation(line, direction='down', num_chunks=30,
                                               vh=self.vh, vw=self.vw).fwd
            an_dur = 10/self.fps
            clips = [line_clip]+intro_clips
            pos+=[[50,50], [40, f'fwd_pos_y+{20+lh}']]
            times+=[[0,-1], [1,-1]]
            
            th = get_hw(intro_list[0])[0]
            for i,c in enumerate(intro_clips[1:]):
                pos.append([40,f'fwd_pos_y+{th}'])
                times.append([1+(an_dur*(i+1)), -1])
        if len(t2) > 0:
            t2 = text_template(text=t2.upper(),text_bg_alpha=255, gap=0,
                          text_bg_color='black', temp_alpha=0, wrap_width=wrap_width,
                          font_size=self.font_size1, font=self.font1, align='left', color='white',
                          full_text_bg=True)
            t2_clip = mp.ImageClip(t2, duration=duration)
            clips.append(t2_clip)
            pos.append([0.95,20])
            times.append([0,-1])
            
            logo = self.logo
            if len(logo) > 0:
                logo = resize_logo(self.logo, height=35)
                logo_clip = mp.ImageClip(logo, duration=duration)
                clips.append(logo_clip)
                pos.append([0.95,0.95])
                times.append([0,-1])
        return ProntoClip(clips=clips, pos=pos, times=times, start=0, end=duration).v
    
    def get_text_clips(self):
        boundry_clip = mp.ImageClip(solid_color_img_like(self.vbg), duration=2)
        boundry_path_start = 'newtemplate_boundry_start.mp4'
        boundry_path_end = 'newtemplate_boundry_end.mp4'
        save_video(boundry_clip, path=boundry_path_start)
        save_video(boundry_clip, path=boundry_path_end)
        text_clips = [boundry_path_start] + self.clip_paths + [boundry_path_end]
        paths_dict = {str(cp):text_join(txt) for cp,txt in zip(text_clips, self.texts)}
        return paths_dict
    
    def create_15(self):
        self.clips = []
        self.clips_fn = []
        self.times = []
        dur = 4
        fn = partial(self.create_first, start=0, end=dur)
        self.clips_fn.append(fn)
        self.clips.append(fn(text=self.texts[0]))
        self.times.append([0,dur])
        self.create_clips(durs=[4,4,3], start=dur, start_id=1, end_id=3)
    
    def create_30(self):
        self.clips = []
        self.clips_fn = []
        self.times = []
        dur = 5
        fn = partial(self.create_first, start=0, end=dur)
        self.clips_fn.append(fn)
        self.clips.append(fn(text=self.texts[0]))
        self.times.append([0,dur])
        self.create_clips(durs=[dur]*5, start=dur, start_id=1, end_id=5)
    
    def create_60(self):
        self.clips = []
        self.clips_fn = []
        self.times = []
        dur = 8
        fn = partial(self.create_first, start=0, end=dur)
        self.clips_fn.append(fn)
        self.clips.append(fn(text=self.texts[0]))
        self.times.append([0,dur])
        self.create_clips(durs=[8, 8, 8, 7, 7, 7, 7], start=dur, start_id=1, end_id=7)
    
    def create_v(self):
        for i,c in enumerate(self.clips):
            if hasattr(c, 'save_clip') and c.save_clip:
                save_video(c, f'bold_{i}.mp4')
        self.v = ProntoClip(clips=self.clips, times=self.times, start=0, end=self.duration, vh=self.vh, vw=self.vw, music_file=self.music_file, music_files=self.music_files, vo_file=self.vo_file, vo_files=self.vo_files).v

class FreshTemplate(ProntoClass):
    def __init__(self, vh=540, vw=960, duration=30, fps=30, font_size=40,
                 font='/usr/local/share/fonts/energized/Poppins-ExtraBold.ttf',
                 temp_color=[16,184,254], texts=[], logo='', clip_paths=[],
                 music_file='', music_files=[], vo_file='', vo_files=[], logger=None,**kwargs):
        super().__init__(**locals_to_params(locals()))
        self.logger = logger
        self.texts = text_case(texts, 'capitalize')
        self.logo = str(logo)
        getattr(self, f'create_{duration}')()
        self.create_v()
    
    def create_clip(self, clip, text='', start=0, end=5):
        
        duration = end-start
        all_pos = [['left', 'top'], ['left', 'bottom'], ['center', 'center'],
                   ['right', 'bottom'], ['right', 'top']]
        directions = ['down', 'right']
        alignement = ['left', 'right']
        ans = {'down':VerticalAppearAnimation, 'right':HorizontalAppearAnimation}
        clips = []
        times = []
        pos = []
        if len(text) > 0:
            temp_pos = random.choice(all_pos)
            bb_direction = random.choice(directions)
            temp_direction = random.choice(directions)
            trans_direction = random.choice(directions)
            bb_an = ans[bb_direction]
            temp_an = ans[temp_direction]
            trans_direction = ans[trans_direction]
            align = random.choice(alignement)
            blank_bgs, text_bgs, temp = text_template_components(text=text, temp_alpha=0, align=align,
                                                                 temp_bg_color=self.temp_color,
                                                                 text_bg_alpha=210, font_size=self.font_size,
                                                                 font=self.font)
            chunks = 10
            slide_dur = chunks/self.fps
            bbg_dur = duration-slide_dur
            bbgs = [bb_an(bbg, direction=bb_direction, num_chunks=chunks, fps=self.fps).v\
                    for bbg in blank_bgs]
            clips += bbgs
            times += [[0, bbg_dur]]*len(bbgs)
            pos += [temp_pos]*len(bbgs)
            tbg_start = 0.1
            tbgs = [mp.ImageClip(tbg, duration=bbg_dur-tbg_start).set_fadein(slide_dur) for tbg in text_bgs]
            clips += tbgs
            times += [tbg_start]*len(tbgs)
            pos += [temp_pos]*len(tbgs)
            temp_v = temp_an(temp, direction=temp_direction, num_chunks=chunks, fps=self.fps, reverse=True).v
            clips.append(temp_v)
            times.append(bbg_dur)
            pos.append(temp_pos)
            clip = ProntoClip(clip, vh=self.vh, vw=self.vw, clips=clips, pos=pos, times=times, end=duration).v
            clip.save_clip = True
        else:
            clip = read_and_resize(clip, dur=duration, h=self.vh, w=self.vw)
        return clip
    
    def create_last(self, start=0, end=5, **kwargs):
        
        duration = end - start
        bg = solid_color_img_like(self.vbg, color=self.temp_color, alpha=255)
        zoom_bg = mp.ImageClip(bg, duration=duration)
        logo = self.logo
        if len(logo) == 0:
            return zoom_bg
        
        logo = resize_logo(logo, height=int(self.vh/2))
        zoom_in = ZoomAnimation(logo, bg=bg, pos=('center','center'), num_chunks=1,
                                zoom_chunks=5, zoom_scales=[3,1]).v
        
        return ProntoClip(clips=[zoom_bg, zoom_in], vh=self.vh, w=self.vw,
                          times=[[0,-1], [0,-1]], end=duration, pos=[]).v
    
    def create_trans(self):
        trans_direction = random.choice(['down', 'right'])
        ans = {'down':VerticalAppearAnimation, 'right':HorizontalAppearAnimation}
        trans_an = ans[trans_direction]
        return trans_an(solid_color_img((self.vh, self.vw, 3), color=self.temp_color, alpha=255),
                        direction=trans_direction, num_chunks=15, fps=self.fps, reverse=True).v
    
    def create_clips(self, durs=[5,5,5,5,5], start=5, start_id=1, end_id=5):
        
        n = 0
        for i in range(start_id, end_id):
            dur = durs[n]
            txt = self.texts[i]
            end = start+dur
            self.times += [[start, end]]
            clip = self.clip_paths[i]
            fn = partial(self.create_clip, clip=clip, start=start, end=end)
            self.clips_fn.append(fn)
            self.clips.append(fn(text=txt))
            if n > 0:
                self.times += [start]
                fn = partial(self.create_trans)
                self.clips_fn.append(fn)
                self.clips.append(fn())
            n+=1
            start=end
        dur = durs[n]
        idx = end_id
        # start = dur*idx
        end = self.duration
        self.times += [[start, -1]]
        fn = partial(self.create_last, start=start, end=end)
        self.clips_fn.append(fn)
        self.clips.append(fn())
    
    def create_first(self, clip, text='', start=0, end=5):
        dur = end-start
        clips = []
        times = []
        pos = []
        bg = solid_color_img((self.vh, self.vw, 3), alpha=170, color=self.temp_color)
        clips.append(mp.ImageClip(bg, duration=dur))
        times.append([0,-1])
        pos.append([0,0])
        
        if len(text) > 0:
            temp = text_template(text=text, temp_alpha=0, align='center',
                                 text_bg_alpha=0, font_size=self.font_size,
                                 font=self.font, gap=0, full_text_bg=True)
            th,tw = get_hw(temp)
            text_clip = mp.ImageClip(temp, duration=dur-0.2).set_fadein(0.5)
            clips.append(text_clip)
            times.append(0.2)
            pos.append([0.5,0.15])
            underline_clip = mp.ImageClip(solid_color_img((10, 75, 3), color='white'),
                                          duration=dur-0.1).set_fadein(0.5)
            clips.append(underline_clip)
            times.append(0.1)
            pos.append([0.5,f'fwd_pos_y+{th+10}'])
            
        if len(self.logo) > 0:
            logo = resize_logo(self.logo, width=int(self.vw/6))
            logo_clip = mp.ImageClip(logo, duration=dur)
            clips.append(logo_clip)
            times.append(0)
            pos.append([0.5,f'fwd_pos_y+{th+40}'])
        
        cbg = to_pil(solid_color_img((500,500,3), alpha=0))
        d = ImageDraw.Draw(cbg)
        d.ellipse((0,0,490,490), fill=tuple(self.temp_color))
        clips.append(ZoomAnimation(np.array(cbg), bg=self.vbg, num_chunks=1, zoom_scales=[0.2, 3.],
                                   zoom_chunks=15, fps=self.fps, pos=[0.5,0.5]).v)
        times.append(end-0.2)
        pos.append([0.,0.])
        
        return ProntoClip(clip, clips=clips, pos=pos, times=times, start=0, end=dur).v
    
    def get_text_clips(self):
        paths_dict = {cp:text_join(txt) for cp,txt in zip(self.clip_paths, self.texts)}
        return paths_dict
    
    def create_15(self):
        self.texts.append('')
        self.clips = []
        self.clips_fn = []
        self.times = []
        dur = 4
        fn = partial(self.create_first, start=0, end=dur)
        self.clips_fn.append(fn)
        self.clips.append(fn(text=self.texts[0], clip=self.clip_paths[0]))
        self.times.append([0,dur])
        self.create_clips(durs=[4,4,3], start=dur, start_id=1, end_id=3)
    
    def create_30(self):
        self.texts.append('')
        self.clips = []
        self.clips_fn = []
        self.times = []
        dur = 5
        fn = partial(self.create_first, start=0, end=dur)
        self.clips_fn.append(fn)
        self.clips.append(fn(text=self.texts[0], clip=self.clip_paths[0]))
        self.times.append([0,dur])
        self.create_clips(durs=[dur]*5, start=dur, start_id=1, end_id=5)
    
    def create_60(self):
        self.texts.append('')
        self.clips = []
        self.clips_fn = []
        self.times = []
        dur = 8
        fn = partial(self.create_first, start=0, end=dur)
        self.clips_fn.append(fn)
        self.clips.append(fn(text=self.texts[0], clip=self.clip_paths[0]))
        self.times.append([0,dur])
        self.create_clips(durs=[8, 8, 8, 7, 7, 7, 7], start=dur, start_id=1, end_id=7)
    
    def create_v(self):
        #for i,c in enumerate(self.clips):
        #    if hasattr(c, 'save_clip') and c.save_clip:
        #        save_video(c, f'bold_{i}.mp4')
        self.v = ProntoClip(clips=self.clips, times=self.times, start=0, end=self.duration, vh=self.vh, vw=self.vw, music_file=self.music_file, music_files=self.music_files, vo_file=self.vo_file, vo_files=self.vo_files).v

class BoldTemplate(ProntoClass):
    def __init__(self, vh=540, vw=960, duration=30, fps=30, font_size=95, temp_color='blue',
                 font='/usr/local/share/fonts/energized/Poppins-ExtraBold.ttf',
                 texts=[], logo='', clip_paths=[], music_file='', music_files=[], vo_file='', vo_files=[], logger=None,**kwargs):
        super().__init__(**locals_to_params(locals()))
        self.logger = logger
        self.texts = text_case(texts, 'upper')
        self.logo = str(logo)
        getattr(self, f'create_{duration}')()
        self.create_v()
    
    def get_text_clips(self):
        paths_dict = {cp:text_join(txt) for cp,txt in zip(self.clip_paths, self.texts)}
        return paths_dict
    
    def create_clip(self, clip, text='', start=0, end=5):
        
        duration = end-start
        if len(text) > 0:
            zoom_start = 0
            zoom_dur = min(4, duration-1)
            zoom_end = zoom_start+zoom_dur
            zoom_out_dur = 2/self.fps
            temp = text_template(text=text, temp_alpha=0, align='left', temp_bg_color=self.temp_color,
                                 text_bg_alpha=0, font_size=self.font_size, font=self.font,
                                 wrap_width=15, gap=0)
            zoom_in = ZoomAnimation(temp, direction='right', bg=self.vbg, pos=('left','center'), num_chunks=3,
                                    zoom_chunks=3, zoom_scales=[5,1]).v
            zoom_out = ZoomAnimation(temp, direction='right', bg=self.vbg, pos=('left','center'), num_chunks=1,
                                     zoom_chunks=2, zoom_scales=[1,5]).v
            zoom_bg = mp.ImageClip(solid_color_img_like(self.vbg, color=self.temp_color, alpha=45),
                                   duration=zoom_dur-zoom_out_dur)
            clip = ProntoClip(clip, clips=[zoom_bg, zoom_in, zoom_out], vh=self.vh, w=self.vw,
                              times=[zoom_start, [zoom_start, zoom_end-zoom_out_dur],
                                     zoom_end-zoom_out_dur], end=duration, pos=[],logger=self.logger).v
        else:
            clip = read_and_resize(clip, dur=duration, h=self.vh, w=self.vw)
        return clip
    
    def create_last(self, clip, text='', start=0, end=5):
        
        logo = self.logo
        duration = end - start
        if len(logo) == 0 and len(text) == 0:
            return read_and_resize(clip, dur=duration, h=self.vh, w=self.vw)
        if len(logo) > 0:
            logo = resize_logo(logo, height=int(self.vh/3))
        else:
            logo = solid_color_img((1,1,3), alpha=0)
        if len(text) > 0:
            text = text_case(text, fn='capitalize')
            text = text_template(text, font=self.font, font_size=25, gap=0, align='center',
                                 text_bg_alpha=0, full_text_bg=True)
        else:
            text = solid_color_img((1,1,3), alpha=0)
        lh,lw = get_hw(logo)
        temp = paste_img(text, logo, pos=(0.5, lh+7))
        zoom_in = ZoomAnimation(temp, direction='right', bg=self.vbg, pos=('center','center'), num_chunks=1,
                                zoom_chunks=5, zoom_scales=[3,1]).v
        zoom_bg = mp.ImageClip(solid_color_img_like(self.vbg, color=self.temp_color, alpha=45),
                               duration=duration)
        
        return ProntoClip(clip, clips=[zoom_bg, zoom_in], vh=self.vh, w=self.vw,
                          times=[[0,-1], [0,-1]], end=duration, pos=[]).v
    
    def create_clips(self, dur=6, start_id=0, end_id=2):
        
        for i in range(start_id, end_id):
            txt = self.texts[i]
            start = dur*i
            end = start+dur
            self.times += [[start, end]]
            clip = self.clip_paths[i]
            fn = partial(self.create_clip, clip=clip, start=start, end=end)
            self.clips_fn.append(fn)
            self.clips.append(fn(text=txt))
        idx = end_id
        start = dur*idx
        end = self.duration
        txt = self.texts[idx]
        self.times += [[start, end]]
        fn = partial(self.create_last, clip=self.clip_paths[idx], start=0, end=dur)
        self.clips_fn.append(fn)
        self.clips.append(fn(text=txt))
    
    def create_15(self):
        self.clips = []
        self.clips_fn = []
        self.times = []
        dur = 4
        self.create_clips(dur=dur, start_id=0, end_id=2)
    
    def create_30(self):
        self.clips = []
        self.clips_fn = []
        self.times = []
        dur = 6
        self.create_clips(dur=dur, start_id=0, end_id=4)
    
    def create_60(self):
        self.clips = []
        self.clips_fn = []
        self.times = []
        dur = 8
        self.create_clips(dur=dur, start_id=0, end_id=7)
    
    def create_v(self):
        self.v = ProntoClip(clips=self.clips, times=self.times, start=0, end=self.duration, vh=self.vh, vw=self.vw, music_file=self.music_file, music_files=self.music_files, vo_file=self.vo_file, vo_files=self.vo_files).v

class ArtTemplate(ProntoClass):
    def __init__(self, vh=540, vw=960, duration=30, fps=30, font_size=40,
                 font='/usr/local/share/fonts/relaxed/NotoSansTC-Medium.otf',
                 temp_color=[16,184,254], texts=[], logo='', clip_paths=[],
                 music_file='', music_files=[], vo_file='', vo_files=[], logger=None, **kwargs):
        super().__init__(**locals_to_params(locals()))
        self.texts = text_case(texts, 'upper')
        self.logo = str(logo)
        getattr(self, f'create_{duration}')()
        self.create_v()
    
    def create_first(self, clip, text='', start=0, end=5, **kwargs):
        
        duration = end-start
        clips = []
        pos = []
        times = []
        text_start = 0
        
        if len(self.logo) > 0:
            logo_dur = 0.7
            zoom_chunks = 5
            zoom_dur = zoom_chunks/self.fps
            logo = resize_logo(self.logo, height=int(self.vh/2))
            logo_bg = solid_color_img_like(self.vbg, color='white')
            logo = paste_img(logo, logo_bg)
            logo_an = ZoomAnimation(logo, num_chunks=1, zoom_scales=[1,5], zoom_chunks=zoom_chunks).v
            
            logo_clip = mp.ImageClip(logo, duration=logo_dur)
            text_start = logo_dur+zoom_dur*2
            
            clips += [logo_clip, logo_an]
            pos += [[0,0]]*2
            times += [0, logo_dur]

        if len(text) > 0:
            text = text_template(text=text, wrap_width=55, font=self.font, font_size=self.font_size,
                                 gap=0, align='center', color='white', full_text_bg=True, text_bg_alpha=0)
            th,tw = get_hw(text)
            text_pos = get_pos(text, self.vbg)
            num_splits = 2
            splits = np.array_split(range(tw), num_splits)
            t1,t2 = [text[:,x[0]:x[-1]+1] for x in splits]
            tws = [get_hw(t)[1] for t in [t1,t2]]
            num_chunks = 5
            bwd_dur = num_chunks/self.fps
            t1_clip = HorizontalSlideAnimation(t1, direction='right', num_chunks=num_chunks)
            t2_clip = HorizontalSlideAnimation(t2, direction='left', num_chunks=num_chunks)
            
            clips += [t1_clip.fwd, t2_clip.fwd, t1_clip.bwd, t2_clip.bwd]
            pos += [[text_pos[0], text_pos[1]], [f'fwd_pos_x+{tws[0]-1}', 'fwd_pos_y']]*2
            times += [[text_start, duration-bwd_dur-bwd_dur]]*2 + [[duration-bwd_dur-bwd_dur]]*2
        clip = ProntoClip(clip, clips=clips, pos=pos, times=times, end=duration, vh=self.vh, vw=self.vw).v
        # else:
            # clip = read_and_resize(clip, dur=duration, h=self.vh, w=self.vw)
        return clip
    
    def create_second(self, clip, text='', start=0, end=5, **kwargs):
        
        duration = end-start
        clips = []
        pos = []
        times = []
        
        if len(text) > 0:
            text = text_template(text=text, wrap_width=55, font=self.font, font_size=self.font_size,
                                 gap=0, align='center', color='white', full_text_bg=True, text_bg_alpha=0)
            th,tw = get_hw(text)
            num_chunks = 5
            text_an1 = HorizontalAppearAnimation(text, direction='right', num_chunks=num_chunks).v
            text_an2 = VerticalAppearAnimation(text, direction='up', num_chunks_2=num_chunks).bwd
            save_video(text_an2)
            gap = 30
            text_bg = solid_color_img((th+gap, tw+gap, 3), color=self.temp_color, alpha=None)
            bg_an1 = HorizontalAppearAnimation(text_bg, direction='right', num_chunks=num_chunks).fwd
            bg_an2 = HorizontalAppearAnimation(text_bg, direction='left', num_chunks_2=num_chunks).bwd
            bgh, bgw = get_hw(text_bg)
            bwd_dur = num_chunks/self.fps
            
            clips += [bg_an1, text_an1, text_an2, bg_an2]
            pos += [[self.vw-bgw, 0.8]] + [[f'fwd_pos_x+{gap//2}', f'fwd_pos_y+{gap//2-5}']]*2 + [[self.vw-bgw, 0.8]]
            times += [[bwd_dur,duration-bwd_dur-bwd_dur]]*2 + [[duration-bwd_dur-bwd_dur]]*2
        return ProntoClip(clip, clips=clips, pos=pos, times=times, end=duration, vh=self.vh, vw=self.vw).v
    
    def create_last(self, clip='', start=0, end=5, **kwargs):
        
        duration = end-start
        clips = []
        pos = []
        times = []
        clip = read_and_resize(clip, dur=duration)
        if len(self.logo) > 0:
            logo = resize_logo(self.logo, height=int(self.vh/2))
            logo_bg = solid_color_img_like(self.vbg, color='black', alpha=0)
            logo = paste_img(logo, logo_bg)
            num_chunks = 5
            logo_clip = ZoomAnimation(logo, num_chunks=1, zoom_scales=[5,1],
                                      zoom_chunks=num_chunks).v
            clips.append(logo_clip)
            pos.append([0.,0.])
            times.append([5/self.fps, duration])
        return ProntoClip(clip, clips=clips, pos=pos, times=times, end=duration, vh=self.vh, vw=self.vw).v
    
    def create_clip(self, clip, text='', start=0, end=5, **kwargs):
        
        duration = end-start
        clips = []
        pos = []
        times = []
        
        if len(text) > 0:
            text = text_template(text=text, wrap_width=55, font=self.font, font_size=self.font_size,
                                 gap=0, align='center', color='white', full_text_bg=True, text_bg_alpha=0)
            text_clip = mp.ImageClip(text, duration=duration)
            th,tw = get_hw(text)
            num_splits = 3
            splits = np.array_split(range(tw), num_splits)
            t1,t2,t3 = [text[:,x[0]:x[-1]+1] for x in splits]
            tws = [get_hw(t)[1] for t in [t1,t2,t3]]
            text_pos = list(get_pos(text, self.vbg))
            num_chunks = 5
            an_dur = num_chunks/self.fps
            t1_an1 = VerticalSlideAnimation(t1, direction='down', num_chunks=num_chunks).fwd
            t2_an1 = VerticalSlideAnimation(t2, direction='down', num_chunks=num_chunks).fwd
            t3_an1 = VerticalSlideAnimation(t3, direction='down', num_chunks=num_chunks).fwd
            text_clip2 = VerticalAppearAnimation(text, direction='up', num_chunks_2=num_chunks).bwd
            gap = 20
            barw = 5
            barh = 50
            bar = solid_color_img((barh, barw, 3), color=self.temp_color)
            bar_an1 = VerticalSlideAnimation(bar, direction='down', num_chunks=num_chunks).fwd
            bar_an2 = VerticalAppearAnimation(bar, direction='up', num_chunks_2=num_chunks).bwd
            
            clips += [t1_an1, t2_an1, t3_an1, bar_an1, bar_an2, text_clip, text_clip2]
            pos += [text_pos, [f'fwd_pos_x+{tws[0]}', 'fwd_pos_y'], [f'fwd_pos_x+{tws[1]}', 'fwd_pos_y']]
            pos += [[f'fwd_pos_x0-{gap//2+barw}', f'fwd_pos_y+7']]*2
            pos += [[0.5,0.5]]*2
            times += [[an_dur,an_dur*4], [an_dur*2,an_dur*4], [an_dur*3,an_dur*4]]
            times += [[an_dur,duration-an_dur-an_dur], duration-an_dur-an_dur]
            times += [[an_dur*4, duration-an_dur-an_dur], duration-an_dur-an_dur]
        return ProntoClip(clip, clips=clips, pos=pos, times=times, end=duration, vh=self.vh, vw=self.vw).v
    
    def create_clips(self, durs=[5,5,5,5,5], start=5, texts=[], clips=[]):
        for i,tcd in enumerate(zip(texts, clips, durs)):
            txt,clip,dur = tcd
            end = start+dur
            self.add_clip(fn=self.create_clip, start=start, end=end, clip_path=clip, text=txt)
            start = end
    
    def get_text_clips(self):
        clips_txt = list(zip(self.clip_paths, self.texts))
        clips_txt += [(self.clip_paths[len(clips_txt)], '')]
        paths_dict = {cp:text_join(txt) for cp,txt in clips_txt}
        return paths_dict
    
    def add_clip(self, fn, start=0, end=5, clip_path='', text='', **kwargs):
        fn = partial(fn, start=start, end=end)
        self.clips_fn.append(fn)
        self.clips.append(fn(clip=clip_path, text=text))
        self.times.append([start,end])
    
    def add_trans(self, start=0, clip='', clip_dur=5, **kwargs):
        trans = slide_transition(clip, t=0, num_chunks=5, clip_dur=clip_dur, vh=self.vh, vw=self.vw)
        self.clips.append(trans)
        self.times.append(start)
    
    def create_15(self):
        self.texts += ['']*(3-(len(self.texts)))
        self.texts = self.texts[:3]
        self.clips = []
        self.clips_fn = []
        self.times = []
        dur = 4
        self.add_clip(fn=self.create_first, start=0, end=dur, clip_path=self.clip_paths[0], text=self.texts[0])
        #self.add_clip(fn=self.create_second, start=dur, end=dur*2, clip_path=self.clip_paths[1], text=self.texts[1])
        self.create_clips(durs=[dur]*2, start=dur, texts=self.texts[1:], clips=self.clip_paths[1:])
        self.add_clip(fn=self.create_last, start=self.duration-3, end=self.duration, clip_path=self.clip_paths[3])
    
    def create_30(self):
        self.texts += ['']*(5-(len(self.texts)))
        self.texts = self.texts[:5]
        self.clips = []
        self.clips_fn = []
        self.times = []
        dur = 5
        self.add_clip(fn=self.create_first, start=0, end=dur, clip_path=self.clip_paths[0], text=self.texts[0])
        #self.add_trans(start=dur-(5/self.fps), clip=self.clip_paths[1], clip_dur=dur)
        self.add_clip(fn=self.create_second, start=dur, end=dur*2, clip_path=self.clip_paths[1], text=self.texts[1])
        #self.add_trans(start=(dur*2)-(5/self.fps), clip=self.clip_paths[2], clip_dur=dur)
        self.create_clips(durs=[dur]*3, start=dur*2, texts=self.texts[2:], clips=self.clip_paths[2:])
        self.add_clip(fn=self.create_last, start=self.duration-5, end=self.duration, clip_path=self.clip_paths[5])
    
    def create_60(self):
        self.texts += ['']*(7-(len(self.texts)))
        self.texts = self.texts[:7]
        self.clips = []
        self.clips_fn = []
        self.times = []
        dur = 8
        self.add_clip(fn=self.create_first, start=0, end=dur, clip_path=self.clip_paths[0], text=self.texts[0])
        #self.add_trans(start=dur-5/self.fps, clip=self.clip_paths[0], clip_dur=dur)
        self.add_clip(fn=self.create_second, start=dur, end=dur*2, clip_path=self.clip_paths[1], text=self.texts[1])
        #self.add_trans(start=(dur*2)-(5/self.fps), clip=self.clip_paths[1], clip_dur=dur)
        self.create_clips(durs=[8, 7, 7, 7, 7], start=dur*2, texts=self.texts[2:], clips=self.clip_paths[2:])
        self.add_clip(fn=self.create_last, start=self.duration-8, end=self.duration, clip_path=self.clip_paths[7])
        
    def create_v(self):
        for i,c in enumerate(self.clips):
            if hasattr(c, 'save_clip') and c.save_clip:
                save_video(c, f'bold_{i}.mp4')
        self.v = ProntoClip(clips=self.clips, times=self.times, start=0, end=self.duration, vh=self.vh, vw=self.vw, music_file=self.music_file, music_files=self.music_files, vo_file=self.vo_file, vo_files=self.vo_files).v

def lined_block(h=100, w=177, color=(195, 49, 212), width=5):

    line_bg = solid_color_img((h, w, 3), alpha=0)
    line = to_pil(line_bg)
    d = ImageDraw.Draw(line)
    d.rectangle(((0,0), (w, h)), fill=None, outline=color, width=5)
    line = np.array(line)
    line_bg = solid_color_img_like(line, alpha=0)
    line_side = line[:,:5]
    line_top = line[:5,:]
    line1 = paste_img(line_side, line_bg, (w-5,0))
    line2 = paste_img(line_top, line_bg, (0,h-5))
    line3 = paste_img(line_side, line_bg, (0,0))
    line4 = paste_img(line_top, line_bg, (0,0))
    
    line_bg = paste_img(line_side, line_bg, (w-5,0))
    line_bg = paste_img(line_top, line_bg, (0,h-5))
    line_bg = paste_img(line_side, line_bg, (0,0))
    line_bg = paste_img(line_top, line_bg, (0,0))
    return [line1, line2, line3, line4], line_bg

class SolaTemplate(ProntoClass):
    def __init__(self, vh=540, vw=960, fps=30, font_size=30, temp_color='blue',
                 font='/usr/lcoal/share/fonts/template_fonts/Baskerville.ttc',
                 texts=[], logo='', clip_paths=[], small_clips=[], music_file='',
                 music_files=[], vo_file='', vo_files=[], duration=15, **kwargs):
        super().__init__(**locals_to_params(locals()))
        intro_texts, bar_texts, outro_texts, ci_texts = texts
        self.intro_texts = intro_texts
        self.bar_texts = bar_texts
        self.outro_texts = outro_texts
        self.ci_texts = ci_texts
        getattr(self, f'create_{duration}')()
        self.create_v()
    
    def sola_bar(self, bar_txt, font_size=45, align='center', width=160):
        bar_txt_temp = text_template(bar_txt, wrap_width=10, font=self.font, gap=0, full_text_bg=True,
                                     color='white', text_bg_alpha=0, temp_alpha=0, align=align,
                                     font_size=font_size)
        bar_txt_h, bar_txt_w = get_hw(bar_txt_temp)
        bar_bg = solid_color_img((self.vh, width, 3))
        bar = paste_img(bar_txt_temp, bar_bg)
        return bar
    
    def get_text_clips(self):
        paths_dict = {}
        if self.duration == 60:
            paths_dict[self.clip_paths[0]] = text_join(self.intro_texts)
            paths_dict[self.clip_paths[1]] = text_join(self.bar_texts)
            paths_dict[self.clip_paths[5]] = text_join(self.outro_texts)
        elif self.duration == 30:
            paths_dict[self.clip_paths[0]] = text_join(self.intro_texts)
            paths_dict[self.clip_paths[1]] = text_join(self.outro_texts)
        elif self.duration == 15:
            paths_dict[self.clip_paths[0]] = text_join(self.intro_texts)
            paths_dict[self.clip_paths[2]] = text_join(self.outro_texts)
        elif self.duration == 6:
            paths_dict[self.clip_paths[0]] = text_join(self.intro_texts)
            paths_dict[self.clip_paths[1]] = text_join(self.outro_texts)
        return paths_dict

    def create_6(self):
        
        self.clips = []
        self.times = []
        
        start = 0
        end = 1.5
        clip_dur = end-start
        line_start = 0
        line_end = end-5/self.fps
        block_start = 0
        block_end = end
        
        clip_list = []
        clip0 = read_and_resize(self.clip_paths[0], dur=clip_dur, h=self.vh, w=self.vw)
                
        if len(self.intro_texts[1]) > 0:
        
            # block
            block_color = (51,147,255)
            block = solid_color_img((int(self.vh/1.7), int(self.vw/1.3), 3), color=block_color, alpha=220)
            block_clips = [mp.ImageClip(block, duration=clip_dur)]
            block_times = [[block_start, block_end]]

            block_h, block_w = get_hw(block)

            # lines
            line_diff = 60
            line_color = (195, 49, 212)
            line_width = 5
            line_h = block_h-line_diff
            line_w = block_w-line_diff
            lines, line_bg = lined_block(h=line_h, w=line_w, color=line_color, width=line_width)
            line_starts, line_ends = seq_start_ends(len(lines), chunks=5, start=line_start)
            line_an = [VerticalSlideAnimation(lines[0], direction='down'),
                       HorizontalSlideAnimation(lines[1], direction='left'),
                       VerticalSlideAnimation(lines[2], direction='up'),
                       HorizontalSlideAnimation(lines[3], direction='right')]
            line_clips = [mp.ImageClip(line_bg, duration=line_end-line_start)]
            line_clips += [x.bwd for x in line_an]
            line_times = [line_start]
            line_times += [[line_end-(5/self.fps), line_end]] * len(line_an)

            # text

            text1 = self.intro_texts[1][0].title()
            txt1_start = start
            txt1_end = line_end
            txt1_temp = text_template(text1, font_size=70, font=self.font, wrap_width=25, gap=10,
                                      full_text_bg=True, color='white', text_bg_alpha=0, temp_alpha=0,
                                      align='center')
            txt1_h, txt1_w = get_hw(txt1_temp)

            text2 = self.intro_texts[1][1].lower()
            txt2_temp = text_template(text2, font_size=45, font=self.font, wrap_width=35, gap=10,
                                            full_text_bg=True, color='white', text_bg_alpha=0, temp_alpha=0,
                                            align='center')
            txt1_temp = paste_img(txt2_temp, txt1_temp, pos=(0.5, txt1_h))
            txt1_clips = [mp.ImageClip(txt1_temp, duration=txt1_end-txt1_start)]
            txt1_times = [[txt1_start, txt1_end]]

            clips = block_clips + line_clips + txt1_clips
            times = block_times + line_times + txt1_times
        
            clip = ProntoClip(bg_clip=clip0, clips=clips, start=start, end=end, pos=[[0.5,0.5]]*len(clips),
                              times=times).v
        else:
            clip = clip0
            
        self.clips.append(clip)
        self.times.append([start, end])
        
        starts = [1.5,3]
        ends = [3,5]
        clips = self.clip_paths[1:3]
        start = starts[0]
        end = ends[-1]
        clip_dur = end-start
        dur0 = ends[0] - starts[0]
        dur1 = ends[1] - starts[1]
        
        clip_list = []
        clip0 = read_and_resize(clips[0], dur=dur0-5/self.fps, h=self.vh, w=self.vw)
        clip1 = read_and_resize(clips[1], dur=dur1, h=self.vh, w=self.vw)
        trans = slide_transition(clip0, direction='left').set_start(0)
        clip = CustomCompositeVideoClip([trans, clip0.set_start(5/self.fps),
                                         clip1.set_start(dur0)]).subclip(0, clip_dur)
        # block
        block_color = (51,147,255)
        block = solid_color_img((int(self.vh/1.7), int(self.vw/1.3), 3), color=block_color, alpha=220)
        block_clip = ZoomAnimation(block, num_chunks=1, zoom_chunks=3, zoom_scales=[1,1.7], bg=self.vbg,
                                   pos=(0.5,0.5)).v
        block_times = [0, clip_dur]
        block_h, block_w = get_hw(block)
        
        # text
        text0 = self.outro_texts[0]
        text0_temp = text_template(text0, font_size=45, font=self.font, wrap_width=25, gap=10,
                                   full_text_bg=True, color='white', text_bg_alpha=0, temp_alpha=0,
                                   align='center')
        
        text0_clip = MoveAnimation(text0_temp, bg=self.vbg, x1=0.5, y1=0.65, x2=0.5, y2=0.5, steps=5).v
        text0_times = [0, 1.5]
        
        text1 = self.outro_texts[1]
        text1_temp = text_template(text1, font_size=45, font=self.font, wrap_width=25, gap=10,
                                   full_text_bg=True, color='white', text_bg_alpha=0, temp_alpha=0,
                                   align='center')
        
        text1_clip = MoveAnimation(text1_temp, bg=self.vbg, x1=0.5, y1=0.65, x2=0.5, y2=0.5, steps=5).v
        text1_times = [1.5, 3]
        
        # ci
        
        clip3_dur = 1
        clip3_blue = (30,119,201)
        clip3_bg = solid_color_img_like(self.vbg, color=clip3_blue)
        clip3 = mp.ImageClip(clip3_bg, duration=clip3_dur)
        font_size = 45
        clip3_txt = self.ci_texts
        clip3_txt_temp = text_template(clip3_txt, wrap_width=35, font=self.font, gap=30, full_text_bg=True,
                                       color='white', text_bg_alpha=0, temp_alpha=0, align='center',
                                       font_size=font_size)
        clip3_clips = [VerticalSlideAnimation(clip3_txt_temp, direction='up', num_chunks=5).fwd]
        clip3_pos = [[0.5,0.5]]
        clip3_times = [[0,-1]]
        if len(self.logo) > 0:
            clip3_txt_h, clip3_txt_w = get_hw(clip3_txt_temp)
            logo = resize_logo(self.logo, height=80)
            clip3_clips.append(mp.ImageClip(logo, duration=clip3_dur))
            clip3_pos.append([0.5, f'fwd_pos_y0+{30+clip3_txt_h}'])
            clip3_times.append([0,-1])

        clip3 = ProntoClip(clip3, clips=clip3_clips, times=clip3_times, pos=clip3_pos, end=clip3_dur).v
        clip3_start = 5
        clip3_times = clip3_start
        
        clips = [block_clip, text0_clip, text1_clip]
        times = [block_times, text0_times, text1_times]
        
        clip = ProntoClip(clip, clips=clips, times=times, start=0, end=clip_dur).v
        self.times.append(start)
        self.clips.append(clip)
        self.times.append(clip3_start)
        self.clips.append(clip3)
        
        if len(self.logo) > 0:
            logo = resize_logo(self.logo, height=80)
            clip4_logo = paste_img(logo, self.vbg, pos=(0.99, 0.99))
            clip4_end = clip3_start
            clip4 = mp.ImageClip(clip4_logo, duration=clip4_end)
            self.times.append([0,clip4_end])
            self.clips.append(clip4)
        
        self.v = ProntoClip(clips=self.clips, times=self.times, start=0, end=self.duration,
                            vh=self.vh, vw=self.vw, music_file=self.music_file,
                            music_files=self.music_files, vo_file=self.vo_file, vo_files=self.vo_files).v
        self.v = self.v.subclip(0,self.duration)
    
    def create_first_15(self, clips=[], starts=[0,5], ends=[5,10]):
        
        start = starts[0]
        end = ends[-1]
        clip_dur = end-start
        line_start = start+0.1
        line_end = end-1
        block_start = line_start+1
        block_end = end
        
        clip_list = []
        clip0 = read_and_resize(clips[0], dur=ends[0]-starts[0], h=self.vh, w=self.vw)
        clip1 = read_and_resize(clips[1], dur=ends[1]-starts[1]-5/self.fps, h=self.vh, w=self.vw)
        trans = slide_transition(clip1, direction='left')
        clip = CustomCompositeVideoClip([clip0, trans.set_start(starts[1]),
                                         clip1.set_start(starts[1]+5/self.fps)]).subclip(start, end)
        
        # block
        block_color = (51,147,255)
        block = solid_color_img((int(self.vh/1.7), int(self.vw/1.3), 3), color=block_color, alpha=220)
        block_open = OpenAnimation(block, direction='mh', num_chunks=10)
        block_clips = [block_open.v]
        block_times = [[block_start, block_end]]

        block_h, block_w = get_hw(block)
        
        # lines
        line_diff = 60
        line_color = (195, 49, 212)
        line_width = 5
        line_h = block_h-line_diff
        line_w = block_w-line_diff
        lines = lined_block(h=line_h, w=line_w, color=line_color, width=line_width)[0]
        line_starts, line_ends = seq_start_ends(len(lines), chunks=5, start=line_start)
        line_an = [VerticalSlideAnimation(lines[0], direction='down'),
                   HorizontalSlideAnimation(lines[1], direction='left'),
                   VerticalSlideAnimation(lines[2], direction='up'),
                   HorizontalSlideAnimation(lines[3], direction='right')]
        line_clips = [x.fwd for x in line_an]
        line_clips += [x.bwd for x in line_an]
        line_times = [[line_start+(5/self.fps)*i, line_end-(5/self.fps)] for i in range(len(lines))]
        line_times += [[line_end-(5/self.fps), line_end]] * len(line_an)
        
        # text
        text0 = self.intro_texts[0].capitalize()
        txt0_start = block_start+0.5
        txt0_end = ends[0]
        txt0_temp = text_template(text0, font_size=67, font=self.font, wrap_width=25, gap=0,
                                  full_text_bg=True, color='white', text_bg_alpha=0, temp_alpha=0,
                                  align='center')
        txt0_clips = [VerticalAppearAnimation(txt0_temp, direction='up', num_chunks=5).v]
        txt0_times = [[txt0_start, txt0_end]]
        
        text1 = self.intro_texts[1][0].title()
        txt1_start = starts[1]
        txt1_end = line_end
        txt1_temp = text_template(text1, font_size=70, font=self.font, wrap_width=25, gap=10,
                                  full_text_bg=True, color='white', text_bg_alpha=0, temp_alpha=0,
                                  align='center')
        txt1_h, txt1_w = get_hw(txt1_temp)
        
        text2 = self.intro_texts[1][1].lower()
        txt2_temp = text_template(text2, font_size=45, font=self.font, wrap_width=35, gap=10,
                                        full_text_bg=True, color='white', text_bg_alpha=0, temp_alpha=0,
                                        align='center')
        txt1_temp = paste_img(txt2_temp, txt1_temp, pos=(0.5, txt1_h))
        txt1_clips = [VerticalAppearAnimation(txt1_temp, direction='up', num_chunks=5).v]
        txt1_times = [[txt1_start, txt1_end]]
        
        clips = block_clips + line_clips + txt0_clips + txt1_clips
        times = block_times + line_times + txt0_times + txt1_times
        
        clip = ProntoClip(bg_clip=clip, clips=clips, start=start, end=end, pos=[[0.5,0.5]]*len(clips),
                          times=times).v
        
        self.clips.append(clip)
        self.times.append([start, end])

    def create_second_15(self, clips=[], starts=[10,12], ends=[12,14]):
        
        start = starts[0]
        end = ends[-1]
        clip_dur = end-start
        dur0 = ends[0] - starts[0]
        dur1 = ends[1] - starts[1]
        
        clip_list = []
        clip0 = read_and_resize(clips[0], dur=dur0-5/self.fps, h=self.vh, w=self.vw)
        clip1 = read_and_resize(clips[1], dur=dur1, h=self.vh, w=self.vw)
        trans = slide_transition(clip0, direction='left').set_start(0)
        clip = CustomCompositeVideoClip([trans, clip0.set_start(5/self.fps),
                                         clip1.set_start(dur0)]).subclip(start, end)
        
        # block
        block_color = (51,147,255)
        block = solid_color_img((int(self.vh/1.7), int(self.vw/1.3), 3), color=block_color, alpha=220)
        block_clip = ZoomAnimation(block, num_chunks=1, zoom_chunks=3, zoom_scales=[1,1.7], bg=self.vbg,
                                   pos=(0.5,0.5)).v
        block_times = [0, clip_dur]
        block_h, block_w = get_hw(block)
        
        # text
        text0 = self.outro_texts[0]
        text0_temp = text_template(text0, font_size=45, font=self.font, wrap_width=25, gap=10,
                                   full_text_bg=True, color='white', text_bg_alpha=0, temp_alpha=0,
                                   align='center')
        
        text0_clip = MoveAnimation(text0_temp, bg=self.vbg, x1=0.5, y1=0.65, x2=0.5, y2=0.5, steps=5).v
        text0_times = [0, 1.5]
        
        text1 = self.outro_texts[1]
        text1_temp = text_template(text1, font_size=45, font=self.font, wrap_width=25, gap=10,
                                   full_text_bg=True, color='white', text_bg_alpha=0, temp_alpha=0,
                                   align='center')
        
        text1_clip = MoveAnimation(text1_temp, bg=self.vbg, x1=0.5, y1=0.65, x2=0.5, y2=0.5, steps=5).v
        text1_times = [1.5, 3]
        
        # ci
        
        clip3_dur = 2
        clip3_blue = (30,119,201)
        clip3_bg = solid_color_img_like(self.vbg, color=clip3_blue)
        clip3 = mp.ImageClip(clip3_bg, duration=clip3_dur)
        font_size = 45
        clip3_txt = self.ci_texts
        clip3_txt_temp = text_template(clip3_txt, wrap_width=35, font=self.font, gap=30, full_text_bg=True,
                                       color='white', text_bg_alpha=0, temp_alpha=0, align='center',
                                       font_size=font_size)
        clip3_clips = [VerticalSlideAnimation(clip3_txt_temp, direction='up', num_chunks=5).fwd]
        clip3_pos = [[0.5,0.5]]
        clip3_times = [[0,-1]]
        if len(self.logo) > 0:
            clip3_txt_h, clip3_txt_w = get_hw(clip3_txt_temp)
            logo = resize_logo(self.logo, height=80)
            clip3_clips.append(mp.ImageClip(logo, duration=clip3_dur))
            clip3_pos.append([0.5, f'fwd_pos_y0+{30+clip3_txt_h}'])
            clip3_times.append([0,-1])

        clip3 = ProntoClip(clip3, clips=clip3_clips, times=clip3_times, pos=clip3_pos, end=clip3_dur).v
        clip3_start = 3
        clip3_times = clip3_start
        
        clips = [block_clip, text0_clip, text1_clip, clip3]
        times = [block_times, text0_times, text1_times, clip3_times]
        
        clip = ProntoClip(clip, clips=clips, times=times, start=0, end=clip_dur).v
        self.times.append(start)
        self.clips.append(clip)
        
        if len(self.logo) > 0:
            logo = resize_logo(self.logo, height=80)
            clip4_logo = paste_img(logo, self.vbg, pos=(0.99, 0.99))
            clip4_end = 12.5
            clip4 = mp.ImageClip(clip4_logo, duration=clip4_end)
            self.times.append([0,clip4_end])
            self.clips.append(clip4)
        
        self.v = ProntoClip(clips=self.clips, times=self.times, start=0, end=self.duration,
                            vh=self.vh, vw=self.vw, music_file=self.music_file,
                            music_files=self.music_files, vo_file=self.vo_file, vo_files=self.vo_files).v
        self.v = self.v.subclip(0,14.9)
        
    def create_v(self):
        pass
        
    def create_15(self):
        self.clips = []
        self.times = []
        self.create_first_15(clips=self.clip_paths[:2], starts=[0,5], ends=[5,10])
        self.create_second_15(clips=self.clip_paths[2:4], starts=[9.9,12], ends=[12,15])
    
    def create_30(self):
        
        self.clips = []
        
        #clip0
        
        clip0_start = 0
        clip0_end = 10
        clip0_line_start = clip0_start+0.1
        clip0_line_end = clip0_end-1.5
        clip0_block_start = clip0_line_start+1
        clip0_block_end = clip0_line_end+0.5
        
        self.times = [[clip0_start,clip0_end]]
        
        # block
        clip0_block_color = (51,147,255)
        clip0_block = solid_color_img((int(self.vh/1.7), int(self.vw/1.3), 3),
                                      color=clip0_block_color, alpha=220)
        clip0_block_open = OpenAnimation(clip0_block, direction='mh', num_chunks=10)
        clip0_block_close = CloseAnimation(clip0_block, direction='mv', num_chunks=10)
        clip0_block_clips = [clip0_block_open.v, clip0_block_close.v]
        clip0_block_times = [[clip0_block_start, clip0_block_end-(10/self.fps)],
                             [clip0_block_end-(10/self.fps)]]

        clip0_block_h, clip0_block_w = get_hw(clip0_block)
        
        # lines
        line_diff = 60
        clip0_line_color = (195, 49, 212)
        clip0_line_width = 5
        clip0_line_h = clip0_block_h-line_diff
        clip0_line_w = clip0_block_w-line_diff
        clip0_lines = lined_block(h=clip0_line_h, w=clip0_line_w,
                                  color=clip0_line_color, width=clip0_line_width)[0]
        clip0_line_starts, clip0_line_ends = seq_start_ends(len(clip0_lines), chunks=5,
                                                            start=clip0_line_start)
        clip0_line_an = [VerticalSlideAnimation(clip0_lines[0], direction='down'),
                         HorizontalSlideAnimation(clip0_lines[1], direction='left'),
                         VerticalSlideAnimation(clip0_lines[2], direction='up'),
                         HorizontalSlideAnimation(clip0_lines[3], direction='right')]
        clip0_line_clips = [x.fwd for x in clip0_line_an]
        clip0_line_clips += [x.bwd for x in clip0_line_an]
        clip0_line_times = [[clip0_line_start+(5/self.fps)*i, clip0_line_end-(5/self.fps)]\
                            for i in range(len(clip0_lines))]
        clip0_line_times += [[clip0_line_end-(5/self.fps), clip0_line_end]] * len(clip0_line_an)
        
        # text
        text0 = self.intro_texts[0].capitalize()
        clip0_txt0_start = clip0_block_start+0.5
        clip0_txt0_end = clip0_txt0_start+4
        clip0_txt0_temp = text_template(text0, font_size=67, font=self.font, wrap_width=25, gap=0,
                                        full_text_bg=True, color='white', text_bg_alpha=0, temp_alpha=0,
                                        align='center')
        clip0_txt0_clips = [VerticalAppearAnimation(clip0_txt0_temp, direction='up', num_chunks=5).v]
        clip0_txt0_times = [[clip0_txt0_start, clip0_txt0_end]]
        
        text1 = self.intro_texts[1][0].title()
        clip0_txt1_start = clip0_txt0_end+1
        clip0_txt1_end = clip0_line_end-0.5
        clip0_txt1_temp = text_template(text1, font_size=70, font=self.font, wrap_width=25, gap=10,
                                        full_text_bg=True, color='white', text_bg_alpha=0, temp_alpha=0,
                                        align='center')
        clip0_txt1_h, clip0_txt1_w = get_hw(clip0_txt1_temp)
        
        text2 = self.intro_texts[1][1].lower()
        clip0_txt2_temp = text_template(text2, font_size=45, font=self.font, wrap_width=35, gap=10,
                                        full_text_bg=True, color='white', text_bg_alpha=0, temp_alpha=0,
                                        align='center')
        clip0_txt1_temp = paste_img(clip0_txt2_temp, clip0_txt1_temp, pos=(0.5, clip0_txt1_h))
        clip0_txt1_clips = [VerticalAppearAnimation(clip0_txt1_temp, direction='up', num_chunks=5).v]
        clip0_txt1_times = [[clip0_txt1_start, clip0_txt1_end]]
        
        clip0_clips = clip0_block_clips + clip0_line_clips + clip0_txt0_clips + clip0_txt1_clips
        clip0_times = clip0_block_times + clip0_line_times + clip0_txt0_times + clip0_txt1_times
        
        clip0 = ProntoClip(bg_clip=self.clip_paths[0], clips=clip0_clips,
                           start=clip0_start, end=clip0_end, pos=[[0.5,0.5]]*len(clip0_clips),
                           times=clip0_times).v.set_fadeout(1)
        
        self.clips.append(clip0)
        
        #trans
        trans_color = (195, 49, 212)
        trans = solid_color_img_like(self.vbg, color=trans_color, alpha=200)
        clip2_trans_clip = mp.ImageClip(trans, duration=2).fadein(1).fadeout(1)
        self.times += [[clip0_end-1, clip0_end+1]]
        self.clips.append(clip2_trans_clip)
        
        #clip2
        
        clip2_dur = 18
        clip2_start = clip0_end
        clip2_end = clip2_start + clip2_dur
        clip2 = self.clip_paths[1]
        self.times += [[clip2_start, clip2_end]]
        
        #trans
        trans_color = (195, 49, 212)
        trans = solid_color_img_like(self.vbg, color=trans_color, alpha=200)
        clip2_trans_clip = mp.ImageClip(trans, duration=2).fadein(1).fadeout(1)
        
        #black
        clip2_black = solid_color_img((self.vh, self.vw//2, 3), alpha=200)
        clip2_black_h, clip2_black_w = get_hw(clip2_black)
        clip2_black_clip = HorizontalSlideAnimation(clip2_black, direction='right', num_chunks=10).fwd

        #texts
        clip2_txt1 = self.outro_texts[0]
        font_size = 47
        clip2_txt1_temp = text_template(clip2_txt1, wrap_width=20, font=self.font, gap=0, full_text_bg=True,
                                        color='white', text_bg_alpha=0, temp_alpha=0, align='left',
                                        font_size=font_size)
        clip2_txt1_clip = VerticalSlideAnimation(clip2_txt1_temp, direction='up', num_chunks=10).fwd
        
        clip2_txt2 = self.outro_texts[1]
        font_size = 47
        clip2_txt2_temp = text_template(clip2_txt2, wrap_width=25, font=self.font, gap=0, full_text_bg=True,
                                        color='white', text_bg_alpha=0, temp_alpha=0, align='center',
                                        font_size=font_size)
        clip2_txt2_clip = VerticalSlideAnimation(clip2_txt2_temp, direction='up', num_chunks=10).fwd
        
        clip2_black_clip = ProntoClip(clip2_black_clip, clips=[clip2_txt1_clip, clip2_txt2_clip],
                                      vh=clip2_black_h, vw=clip2_black_w, pos=[[0.5,0.5], [0.5,0.5]],
                                      times=[[0.5,7.5], [8,-1]], start=2, end=clip2_end).v
        
        clip2_small1 = read_and_resize(self.small_clips[0], h=350, w=300)
        clip2_small1_trans = zoom_transition(clip2_small1, zoom_chunks=5, zoom_scales=[0.2,1])
        clip2_small2 = read_and_resize(self.small_clips[1], h=200, w=200)
        clip2_small2_trans = zoom_transition(clip2_small2, zoom_chunks=5, zoom_scales=[0.2,1])
        
        clip2 = ProntoClip(clip2, clips=[clip2_black_clip, clip2_small1_trans, clip2_small1,
                                         clip2_small2_trans, clip2_small2],
                           times=[[2,-1], [10-5/self.fps], [10,-1], [12-5/self.fps], [12,-1]],
                           pos=[[0,0], [(self.vw//2)+10, 30], [(self.vw//2)+10, 30], [0.95,0.9], [0.95,0.9]],
                           start=clip2_start, end=clip2_end).v
        self.clips.append(clip2)
        
        #clip3
        
        clip3_start = clip2_end
        clip3_end = 30
        clip3_dur = clip3_end - clip3_start
        clip3_blue = (30,119,201)
        clip3_bg = solid_color_img_like(self.vbg, color=clip3_blue)
        clip3 = mp.ImageClip(clip3_bg, duration=clip3_dur)
        self.times += [[clip3_start, clip3_end]]
        
        #texts
        
        font_size = 45
        clip3_txt = self.ci_texts
        clip3_txt_temp = text_template(clip3_txt, wrap_width=35, font=self.font, gap=30, full_text_bg=True,
                                       color='white', text_bg_alpha=0, temp_alpha=0, align='center',
                                       font_size=font_size)
        clip3_clips = [VerticalSlideAnimation(clip3_txt_temp, direction='up', num_chunks=5).fwd]
        clip3_pos = [[0.5,0.5]]
        clip3_times = [[0,-1]]
        if len(self.logo) > 0:
            clip3_txt_h, clip3_txt_w = get_hw(clip3_txt_temp)
            logo = resize_logo(self.logo, height=80)
            clip3_clips.append(mp.ImageClip(logo, duration=clip3_dur))
            clip3_pos.append([0.5, f'fwd_pos_y0+{30+clip3_txt_h}'])
            clip3_times.append([0,-1])

        clip3 = ProntoClip(clip3, clips=clip3_clips, times=clip3_times, pos=clip3_pos, end=clip3_dur).v
        self.clips.append(clip3)
        if len(self.logo) > 0:
            logo = resize_logo(self.logo, height=80)
            clip4_logo = paste_img(logo, self.vbg, pos=(0.99, 0.99))
            clip4_end = clip3_end-4.5
            clip4 = mp.ImageClip(clip4_logo, duration=clip4_end)
            self.times += [[0,clip4_end]]
            self.clips.append(clip4)
        
        self.v = ProntoClip(clips=self.clips, times=self.times, pos=[[0,0]]*len(self.clips),
                            start=0, end=30, music_file=self.music_file, music_files=self.music_files,
                            vo_file=self.vo_file, vo_files=self.vo_files).v

    
    def create_60(self):
        
        self.clips = []
        
        #clip0
        
        clip0_start = 0
        clip0_end = 18
        clip0_line_start = clip0_start+0.1
        clip0_line_end = clip0_end-1
        clip0_block_start = clip0_line_start+1
        clip0_block_end = clip0_line_end
        
        self.times = [[clip0_start,clip0_end]]
        
        # block
        clip0_block_color = (51,147,255)
        clip0_block = solid_color_img((int(self.vh/1.7), int(self.vw/1.3), 3),
                                      color=clip0_block_color, alpha=220)
        clip0_block_open = OpenAnimation(clip0_block, direction='mh', num_chunks=10)
        clip0_block_close = CloseAnimation(clip0_block, direction='mv', num_chunks=10)
        clip0_block_clips = [clip0_block_open.v, clip0_block_close.v]
        clip0_block_times = [[clip0_block_start, clip0_block_end-(10/self.fps)],
                             [clip0_block_end-(10/self.fps)]]

        clip0_block_h, clip0_block_w = get_hw(clip0_block)
        
        # lines
        line_diff = 60
        clip0_line_color = (195, 49, 212)
        clip0_line_width = 5
        clip0_line_h = clip0_block_h-line_diff
        clip0_line_w = clip0_block_w-line_diff
        clip0_lines = lined_block(h=clip0_line_h, w=clip0_line_w,
                                  color=clip0_line_color, width=clip0_line_width)[0]
        clip0_line_starts, clip0_line_ends = seq_start_ends(len(clip0_lines), chunks=5,
                                                            start=clip0_line_start)
        clip0_line_an = [VerticalSlideAnimation(clip0_lines[0], direction='down'),
                         HorizontalSlideAnimation(clip0_lines[1], direction='left'),
                         VerticalSlideAnimation(clip0_lines[2], direction='up'),
                         HorizontalSlideAnimation(clip0_lines[3], direction='right')]
        clip0_line_clips = [x.fwd for x in clip0_line_an]
        clip0_line_clips += [x.bwd for x in clip0_line_an]
        clip0_line_times = [[clip0_line_start+(5/self.fps)*i, clip0_line_end-(5/self.fps)]\
                            for i in range(len(clip0_lines))]
        clip0_line_times += [[clip0_line_end-(5/self.fps), clip0_line_end]] * len(clip0_line_an)
        
        # text
        text0 = self.intro_texts[0].capitalize()
        clip0_txt0_start = clip0_block_start+0.5
        clip0_txt0_end = clip0_txt0_start+6
        clip0_txt0_temp = text_template(text0, font_size=67, font=self.font, wrap_width=25, gap=0,
                                        full_text_bg=True, color='white', text_bg_alpha=0, temp_alpha=0,
                                        align='center')
        clip0_txt0_clips = [VerticalAppearAnimation(clip0_txt0_temp, direction='up', num_chunks=5).v]
        clip0_txt0_times = [[clip0_txt0_start, clip0_txt0_end]]
        
        text1 = self.intro_texts[1][0].title()
        clip0_txt1_start = clip0_txt0_end+1.5
        clip0_txt1_end = clip0_txt1_start+7
        clip0_txt1_temp = text_template(text1, font_size=70, font=self.font, wrap_width=25, gap=10,
                                        full_text_bg=True, color='white', text_bg_alpha=0, temp_alpha=0,
                                        align='center')
        clip0_txt1_h, clip0_txt1_w = get_hw(clip0_txt1_temp)
        
        text2 = self.intro_texts[1][1].lower()
        clip0_txt2_temp = text_template(text2, font_size=45, font=self.font, wrap_width=35, gap=10,
                                        full_text_bg=True, color='white', text_bg_alpha=0, temp_alpha=0,
                                        align='center')
        clip0_txt1_temp = paste_img(clip0_txt2_temp, clip0_txt1_temp, pos=(0.5, clip0_txt1_h))
        clip0_txt1_clips = [VerticalAppearAnimation(clip0_txt1_temp, direction='up', num_chunks=5).v]
        clip0_txt1_times = [[clip0_txt1_start, clip0_txt1_end]]
        
        clip0_clips = clip0_block_clips + clip0_line_clips + clip0_txt0_clips + clip0_txt1_clips
        clip0_times = clip0_block_times + clip0_line_times + clip0_txt0_times + clip0_txt1_times
        
        clip0 = ProntoClip(bg_clip=self.clip_paths[0], clips=clip0_clips,
                           start=clip0_start, end=clip0_end, pos=[[0.5,0.5]]*len(clip0_clips),
                           times=clip0_times).v.set_fadeout(1)
        
        self.clips.append(clip0)
        
        #clip1
        
        clip1_dur = 18
        clip1_start = clip0_end
        clip1_end = clip1_start + clip1_dur
        clip1 = self.clip_paths[1]
        bar_width = self.vw//6
        bar_pos = []
        bar_times = []
        bar_clips = []
        bars = []
        self.times += [[clip1_start, clip1_end]]
        for i in range(3):
            start = 3*(i+1)
            end = start+3
            if i == 2:
                end = clip1_dur
            bar = self.sola_bar(self.bar_texts[i], width=bar_width)
            bar_clip = VerticalSlideAnimation(bar, direction='down', num_chunks=10).fwd
            clip = read_and_resize(self.clip_paths[i+2], dur=15, h=self.vh, w=self.vw)
            trans_v = slide_transition(clip, direction='left')
            bar_clips += [bar_clip, trans_v, clip]
            bar_pos += [[0,0], [bar_width, 0], [bar_width, 0]]
            bar_times += [[start, end], [start-5/self.fps, start], [start, end]]
            
        clip1 = ProntoClip(clip1, clips=bar_clips, times=bar_times, pos=bar_pos,
                           start=clip1_start, end=clip1_end).v
        self.clips.append(clip1)
        
        #trans
        trans_color = (195, 49, 212)
        trans = solid_color_img_like(self.vbg, color=trans_color, alpha=200)
        clip2_trans_clip = mp.ImageClip(trans, duration=2).fadein(1).fadeout(1)
        self.times += [[clip1_end-1, clip1_end+1]]
        self.clips.append(clip2_trans_clip)
        
        #clip2
        
        clip2_dur = 20
        clip2_start = clip1_end
        clip2_end = clip2_start + clip2_dur
        clip2 = self.clip_paths[5]
        self.times += [[clip2_start, clip2_end]]
        
        #trans
        trans_color = (195, 49, 212)
        trans = solid_color_img_like(self.vbg, color=trans_color, alpha=200)
        clip2_trans_clip = mp.ImageClip(trans, duration=2).fadein(1).fadeout(1)
        
        #black
        clip2_black = solid_color_img((self.vh, self.vw//2, 3), alpha=200)
        clip2_black_h, clip2_black_w = get_hw(clip2_black)
        clip2_black_clip = HorizontalSlideAnimation(clip2_black, direction='right', num_chunks=10).fwd

        #texts
        clip2_txt1 = self.outro_texts[0]
        font_size = 47
        clip2_txt1_temp = text_template(clip2_txt1, wrap_width=20, font=self.font, gap=0, full_text_bg=True,
                                        color='white', text_bg_alpha=0, temp_alpha=0, align='left',
                                        font_size=font_size)
        clip2_txt1_clip = VerticalSlideAnimation(clip2_txt1_temp, direction='up', num_chunks=10).fwd
        
        clip2_txt2 = self.outro_texts[1]
        font_size = 47
        clip2_txt2_temp = text_template(clip2_txt2, wrap_width=25, font=self.font, gap=0, full_text_bg=True,
                                        color='white', text_bg_alpha=0, temp_alpha=0, align='center',
                                        font_size=font_size)
        clip2_txt2_clip = VerticalSlideAnimation(clip2_txt2_temp, direction='up', num_chunks=10).fwd
        
        clip2_black_clip = ProntoClip(clip2_black_clip, clips=[clip2_txt1_clip, clip2_txt2_clip],
                                      vh=clip2_black_h, vw=clip2_black_w, pos=[[0.5,0.5], [0.5,0.5]],
                                      times=[[0.5,7.5], [8,-1]], start=2, end=clip2_end).v
        
        clip2_small1 = read_and_resize(self.small_clips[0], h=350, w=300)
        clip2_small1_trans = zoom_transition(clip2_small1, zoom_chunks=5, zoom_scales=[0.2,1])
        clip2_small2 = read_and_resize(self.small_clips[1], h=200, w=200)
        clip2_small2_trans = zoom_transition(clip2_small2, zoom_chunks=5, zoom_scales=[0.2,1])
        
        clip2 = ProntoClip(clip2, clips=[clip2_black_clip, clip2_small1_trans, clip2_small1,
                                         clip2_small2_trans, clip2_small2],
                           times=[[2,-1], [10-5/self.fps], [10,-1], [12-5/self.fps], [12,-1]],
                           pos=[[0,0], [(self.vw//2)+10, 30], [(self.vw//2)+10, 30], [0.95,0.9], [0.95,0.9]],
                           start=clip2_start, end=clip2_end).v
        self.clips.append(clip2)
        
        #clip3
        
        clip3_start = clip2_end
        clip3_end = 60
        clip3_dur = clip3_end - clip3_start
        clip3_blue = (30,119,201)
        clip3_bg = solid_color_img_like(self.vbg, color=clip3_blue)
        clip3 = mp.ImageClip(clip3_bg, duration=clip3_dur)
        self.times += [[clip3_start, clip3_end]]
        
        #texts
        
        font_size = 45
        clip3_txt = self.ci_texts
        clip3_txt_temp = text_template(clip3_txt, wrap_width=35, font=self.font, gap=30, full_text_bg=True,
                                       color='white', text_bg_alpha=0, temp_alpha=0, align='center',
                                       font_size=font_size)
        clip3_clips = [VerticalSlideAnimation(clip3_txt_temp, direction='up', num_chunks=5).fwd]
        clip3_pos = [[0.5,0.5]]
        clip3_times = [[0,-1]]
        if len(self.logo) > 0:
            clip3_txt_h, clip3_txt_w = get_hw(clip3_txt_temp)
            logo = resize_logo(self.logo, height=80)
            clip3_clips.append(mp.ImageClip(logo, duration=clip3_dur))
            clip3_pos.append([0.5, f'fwd_pos_y0+{30+clip3_txt_h}'])
            clip3_times.append([0,-1])

        clip3 = ProntoClip(clip3, clips=clip3_clips, times=clip3_times, pos=clip3_pos, end=clip3_dur).v
        self.clips.append(clip3)
        if len(self.logo) > 0:
            logo = resize_logo(self.logo, height=80)
            clip4_logo = paste_img(logo, self.vbg, pos=(0.99, 0.99))
            clip4_end = clip3_end-4.5
            clip4 = mp.ImageClip(clip4_logo, duration=clip4_end)
            self.times += [[0,clip4_end]]
            self.clips.append(clip4)
        
        self.v = ProntoClip(clips=self.clips, times=self.times, pos=[[0,0]]*len(self.clips), start=0, end=60, music_file=self.music_file, music_files=self.music_files, vo_file=self.vo_file, vo_files=self.vo_files).v

def prev_logo(font_size=20, font='/usr/lcoal/share/fonts/FranklinGothic_Bold.ttf', shape=(80,80,3), bg_alpha=None,
              bg_color='white', color='black'):
    bg = solid_color_img(shape, color=bg_color, alpha=bg_alpha)
    logo_p = paste_img(text_template('LOGO', color=color, text_bg_color='white', font_size=font_size, font=font, text_bg_alpha=255), bg)
    return logo_p


class TemplateDealership():
    
    def __init__(self, texts=['find great deals here!',
                             ['lease a [car name]', '$199/per month', 'for 36 months']],
                            #  ['XX ADDRESS STREET', 'XX CITY, XX STATE, XX ZIP'],
                            #  ['www.dealershipname.com', '1-800-777-7777']],
                 font='/usr/lcoal/share/fonts/template_fonts/Oswald-Medium.ttf', font_size=60, vh=540, vw=960,
                 all_paths=[], user_paths=['/home/hamza/dev/pronto/Dealership/clips/luxurycar-1080_D.mov',
                                           '/home/hamza/dev/pronto/Dealership/clips/closeupofcar1080__D.mp4'],
                 extra_paths=['/home/hamza/dev/pronto/Dealership/clips/businessmansalecardealership_1080_D.mp4'],
                 pronto_paths=['/home/hamza/dev/pronto/Dealership/clips/attractivewomanbuyinganewcar_1080_D.mov',
                               '/home/hamza/dev/pronto/Dealership/clips/keysofcar-dealership_1080_D.mov',
                               '/home/hamza/dev/pronto/Dealership/clips/3dhundredscarsred_1080_D.mp4',
                               '/home/hamza/dev/pronto/Dealership/clips/businessmansalecardealership_1080_D.mp4'
                              ], duration=30, logo='', music_file='', watermark='', vo_data=[], fps=30,
                 vo_file='', ci_dict={'address': ['XX ADDRESS STREET', 'XX CITY, XX STATE, XX ZIP'],
                                      'url':'www.dealershipname.com', 'phone':'1-800-777-7777'}, logger=None,**kwargs):
        duration = 30
        meta_dict = {30: {'num_vids':6, 'num_extra': 1}}
        
        reading_fn = partial(read_and_resize, fps=fps, promo_w=vw, promo_h=vh)
        clips, self.clip_paths = process_clips(all_clips=all_paths, pronto_paths=pronto_paths,
                                          extra_paths=extra_paths, user_paths=user_paths,
                                          meta_data=meta_dict[duration], reading_fn=reading_fn)
        self.clips = [c.subclip(0,s) for c,s in zip(clips, [5.1,5,10,7,5,5])]
        if len(ci_dict) > 0:
            texts = texts[:2]
            texts.append(ci_dict['address'])
            texts.append([ci_dict['url'], ci_dict['phone']])
        for i,t in enumerate(texts):
            if not is_list(t):
                texts[i] = [t]
        self.texts = texts
        if len(logo) == 0:
            logo = prev_logo(font_size=font_size,font=font, shape=(160,160,3))
        self.logo = logo
        self.lh,self.lw = get_hw(self.logo)
        self.vbg = solid_color_img((vh,vw,3), alpha=0)
        self.gray = (90,90,90)
        self.dark_gray = (56,56,56)
        self.light_grey = (169,169,169,100)
        self.shade_color = (255,255,255,60)
        self.fps = fps
        self.vh, self.vw = vh, vw
        self.font = font
        self.font_size = font_size
        self.v_dur = duration
        self.create_intro()
        self.create_temp_clips()
        self.music_file = music_file
        self.watermark = watermark
        self.vo_file = vo_file

    def create_intro(self):
        
        logo, lh, lw, vh, vw, vbg, fps = self.logo, self.lh, self.lw, self.vh, self.vw, self.vbg, self.fps
        intro_clip = self.clips[0]
        circle_bg = get_circle_bg(logo)
        chunks = 7
        starts = [(chunks+chunks*i)/30 for i in range(3)]
        logo_v = zoom_template(logo, vh, vw, num_chunks=1, zoom_scales=[5,1], zoom_chunks=5, num_chunks_2=1,
                               zoom_scales_2=[], pos=(0.5,0.5), bg=vbg, vid_bg_color=None,
                               temp_dur=starts[1], start=0)
        frames = flatten_list([zoom_template(circle_bg, vh, vw, num_chunks=1, zoom_scales=[1,6],
                                             zoom_chunks=chunks, num_chunks_2=1, zoom_scales_2=[],
                                             pos=(0.5,0.5), bg=vbg, vid_bg_color=None, temp_dur=chunks/30,
                                             start=s) for s in starts])
        logo_big = cv2.resize(logo, (lw+30, lh+30))
        logo_v2 = [mp.ImageClip(paste_img(cv2.resize(logo, (lw+f, lh+f)), vbg)).set_duration(d).set_start(s)\
                                for f,d,s in zip([10,20,30],[chunks/30,chunks/30,4],starts)]
        logo_v3 = [mp.ImageSequenceClip(move_img(logo_big, bg=vbg, x1=0.5, y1=0.5, x2=0.95, y2=0.07,
                                                 steps=10, h2=50, w2=50), fps=fps)\
                  .set_start(logo_v2[-1].start+logo_v2[-1].duration)]

        clips = logo_v+frames+logo_v2+logo_v3
        self.v1 = mp.CompositeVideoClip([intro_clip]+clips)

    def create_temp_clips(self):
        
        v1 = self.v1
        logo, lh, lw, vh, vw, vbg, fps = self.logo, self.lh, self.lw, self.vh, self.vw, self.vbg, self.fps
        gray = self.gray
        dark_gray = self.dark_gray
        light_grey = self.light_grey
        shade_color = self.shade_color
        txt = self.texts[0][0].upper()
        c2 = self.clips[1]

        text_pos = (0.5,0.2)
        v_dur = 5
        start = 0
        bg = solid_color_img((vh,320,3), color=gray, alpha=255)
        bar_alpha = 220
        bar = solid_color_img((vh,20,3), color=dark_gray, alpha=bar_alpha)
        bar2 = solid_color_img((vh,10,3), color=dark_gray, alpha=bar_alpha)
        bars = [bar,bar2,bar,bar2,bar,bar2,bar,bar2,bar,bar2]
        chunks = 5
        starts,durs = seq_start_durs(n=4, chunks=chunks, start=start, dur=None, fps=fps)

        bar_slide = [mp.ImageSequenceClip(move_img(b, bg, x1=1., y1=0., x2=0., y2=0., steps=chunks),
                     fps=fps).set_start(s).set_duration(d) for b,s,d in zip(bars,starts, durs)]
        font = self.font
        font_size = 80
        side = text_template_components(txt, wrap_width=6, font=font, font_size=font_size, align='left',
                                        color='black', text_bg_color='white', text_bg_alpha=0,
                                        temp_color='white', temp_alpha=0, gap=0, full_text_bg=True)[-1]
        wbg = solid_color_img_like(bg, color='white')
        side = paste_img(side, wbg, pos=text_pos)

        side2 = text_template_components(txt, wrap_width=6, font=font, font_size=font_size+5, align='left',
                                        color='black', text_bg_color='white', text_bg_alpha=0,
                                        temp_color='white', temp_alpha=0, gap=0, full_text_bg=True)[-1]
        side2 = paste_img(side2, wbg, pos=text_pos)

        lines = text_template_components(txt, wrap_width=6, font=font, font_size=font_size, align='left',
                                        color='white', text_bg_color='white', text_bg_alpha=0,
                                        temp_color='white', temp_alpha=0, gap=0, full_text_bg=True)[1]
        chunks = 5
        starts,durs = seq_start_durs(n=len(lines), chunks=chunks, start=start, dur=1, fps=fps)
        # print(starts, durs)
        # starts = [(chunks*i)+(chun)/fps for i in range(len(lines))]
        # durs = [1-s for s in starts]
        clips2 = flatten_list([zoom_template(l, vh=vh, vw=vw, num_chunks=1, zoom_scales=[5,1],
                               zoom_chunks=chunks, zoom_scales_2=None, pos=text_pos,
                               bg=solid_color_img_like(bg, alpha=0), fps=fps, vid_bg_color=None,
                               start=s, temp_dur=d, position=(0.,0.))\
                 for l,s,d in zip(lines,starts,durs)])
        clips2 = [x.fadein(chunks/fps) for x in clips2]

        bgc = mp.ImageClip(bg, duration=1).set_start(start)
        sidec = mp.ImageClip(side, duration=1).set_start(start+1)
        side2c = mp.ImageClip(side2, duration=0.5).set_start(start+2)
        clips2 = bar_slide+clips2
        clips2.insert(0,bgc)
        clips2.append(sidec)
        clips2.append(side2c)
        clips2.append(sidec.set_start(start+2.5).set_duration(2.5))
        v2 = mp.CompositeVideoClip([c2]+clips2)

        c3 = self.clips[2]
        c4 = self.clips[3]

        fc3 = c3.get_frame(0)
        fc4 = c4.get_frame(0)

        bar = solid_color_img((50,vw,3), color='white', alpha=shade_color[-1])
        chunks = 5
        starts,durs = seq_start_durs(n=4, chunks=chunks, start=5, dur=None, fps=fps)

        # bar_slide = [mp.ImageSequenceClip(animate_vertical_move(bar, bg=vbg, direction='down', num_chunks=chunks),
        #              fps=fps).set_start(s).set_duration(d) for s,d in zip(starts, durs)]

        bar_slide = [mp.ImageSequenceClip(move_img(bar, bg=vbg, x1=0., y1=0., x2=0., y2=1., steps=chunks),
                     fps=fps).set_start(s).set_duration(d) for s,d in zip(starts, durs)]

        trans_c3 = slide_template(fc3, direction='left', num_chunks=15, num_chunks_2=0,
                               temp_dur=None, temp_start=4.5, fps=fps)
        c3 = c3.set_start(5)
        trans_c3.append(c3)
        trans_c3+=bar_slide
        # v3 = mp.concatenate_videoclips(trans+[c3])

        pos_c4 = (vw//2,0)
        trans_c4 = slide_template(fc4, direction='left', num_chunks=15, num_chunks_2=0,
                                  temp_dur=None, temp_start=7.5, fps=fps, pos=pos_c4)
        c4 = c4.set_start(8).set_position(pos_c4)
        trans_c4.append(c4)

        bar = solid_color_img((vh,65,3), color='white', alpha=shade_color[-1])
        chunks = 5
        starts,durs = seq_start_durs(n=4, chunks=chunks, start=7.8, dur=None, fps=fps)

        bar_slide = [mp.ImageSequenceClip(move_img(bar, bg=vbg, x1=1., y1=0., x2=0., y2=0.,
                                                 steps=chunks), fps=fps)\
                     .set_start(s).set_duration(d) for s,d in zip(starts, durs)]

        # bar_slide = [mp.ImageSequenceClip(animate_horizontal_move(bar, bg=vbg, direction='left',
        #                                                           num_chunks=chunks),
        #              fps=fps).set_start(s).set_duration(d) for s,d in zip(starts, durs)]



        v4 = mp.concatenate_videoclips([v1,mp.CompositeVideoClip([v2]+trans_c3+bar_slide+trans_c4)])
        # play_video(v4)


        cta = self.texts[1]
        if is_list(cta):
            cta = [x.upper() for x in cta]
        else:
            cta = cta.upper()
        cta_blank, cta_text, cta_temp = text_template_components(cta, wrap_width=20, font=font,
                                        font_size=65, align='center', color='white', text_bg_color=dark_gray,
                                        text_bg_alpha=None, temp_color='white', temp_alpha=0, gap=30,
                                        full_text_bg=True)
        # print([c.shape for c in cta_text])
        cta_blank2, cta_text2, cta_temp2 = text_template_components(cta, wrap_width=20, font=font,
                                           font_size=65, align='center', color='black',
                                           text_bg_color='white', text_bg_alpha=None, temp_color='white',
                                           temp_alpha=0, gap=30, full_text_bg=True)

    #     cta_disc = 'Disclaimer text to be added to the bottom of the cta. Random text just for the previews'
    #     _, _, cta_disc = text_template_components(cta_disc, wrap_width=75, font=font, font_size=15,
    #                                     align='center', color='white', text_bg_color='white', text_bg_alpha=None,
    #                                     temp_color='white', temp_alpha=0, gap=0, full_text_bg=True)

        cta_h, cta_w = get_hw(cta_temp)
    #     cta_disc_h, cta_disc_w = get_hw(cta_disc)
    #     cta_disc_diff = cta_h+20
    #     cta_block = solid_color_img((cta_disc_h+cta_disc_diff, max(cta_w, cta_disc_w), 3), alpha=0)
    #     cta_block_h, cta_block_w = get_hw(cta_block)



        clip_dur = 5
        # cta_clips = [mp.ImageClip(img, duration=clip_dur)]
        cta_pos = get_pos(cta_blank[0], vbg)
    #     cta_pos = get_pos(cta_block, vbg)
    #     print(cta_block.shape, vbg.shape, cta_pos[0], cta_pos[1])

        chunks = 5
        dur = 1
        an_dur = chunks/fps
        cta_start = v4.duration-an_dur

        cta_clip = self.clips[4].set_start(cta_start)
        fcta = cta_clip.get_frame(0)
        trans_cta = slide_template(fcta, direction='right', num_chunks=15, num_chunks_2=0,
                                   temp_dur=None, temp_start=cta_start-0.5, fps=fps)
        cta_clips = trans_cta+[cta_clip]

        bar = solid_color_img((vh,50,3), color='white', alpha=shade_color[-1])
        bar_chunks = 5
        bar_starts,bar_durs = seq_start_durs(n=4, chunks=bar_chunks, start=cta_start+an_dur,
                                             dur=None, fps=fps)

        bar_slide = [mp.ImageSequenceClip(move_img(bar, bg=vbg, x1=0., y1=0., x2=1., y2=0.,
                                                   steps=bar_chunks),
                     fps=fps).set_start(s).set_duration(d) for s,d in zip(bar_starts, bar_durs)]
        cta_clips += bar_slide
        starts, durs = seq_start_durs(len(cta_blank), chunks=chunks, start=cta_start, dur=dur, fps=fps)
        cta_clips += [mp.ImageSequenceClip(animate_horizontal_slide(bbg,direction='right',
                                                                    num_chunks=chunks,fps=fps),
                                         fps=fps).set_duration(d).set_position(cta_pos).set_start(s)\
                     for bbg,d,s in zip(cta_blank, durs, starts)]

        cta_clips += flatten_list([zoom_template(t, vh=vh, vw=vw, num_chunks=1, zoom_chunks=chunks,
                                   zoom_scales=[6,1], zoom_scales_2=None, pos=cta_pos, temp_dur=d-an_dur,
                                   start=s+an_dur, vid_bg_color=None, bg=vbg)\
                                   for t,d,s in zip(cta_text, durs, starts)])

        cta_clips += [mp.ImageClip(cta_temp2,
                                   duration=clip_dur-dur).set_start(cta_start+dur).set_position(cta_pos)]
        # cta_v = mp.CompositeVideoClip(cta_clips)
        v4 = mp.CompositeVideoClip([v4]+cta_clips)
        # play_video(v4)



        out_start = v4.duration
        out_dur = 5

        c5 = self.clips[5]
        fc5 = c5.get_frame(0)
        trans_c5 = slide_template(fc5, direction='right', num_chunks=15, num_chunks_2=0,
                                  temp_dur=None, temp_start=out_start-0.5, fps=fps)
        c5 = c5.set_start(out_start)
        c5_clips = trans_c5+[c5]

        ci = self.texts[2]
        if is_list(ci):
            ci = [x.upper() for x in ci]
        else:
            ci = ci.upper()
        ci_font_size = 37
        ci_block = text_template_components(ci, wrap_width=25, font=font, font_size=ci_font_size,
                                            align='center', color='white', text_bg_color='white',
                                            text_bg_alpha=0, temp_color='white', temp_alpha=0,
                                            gap=0, full_text_bg=True)[-1]
        ch,cw = get_hw(ci_block)
        ci_logo_gap = 40
        ci_bg_alpha = 255
        if ch==1 and cw==1:
            ci_bg_alpha = 0
        ci_bg = solid_color_img((ch+ci_logo_gap,cw+ci_logo_gap,3), color=gray, alpha=ci_bg_alpha)

        ci_block = paste_img(ci_block, ci_bg)

        ci_block2 = text_template_components(ci, wrap_width=25, font=font, font_size=ci_font_size,
                                             align='center', color='black', text_bg_color='white',
                                             text_bg_alpha=0, temp_color='white', temp_alpha=0,
                                             gap=0, full_text_bg=True)[-1]
        ch,cw = get_hw(ci_block2)
        ci_bg2 = solid_color_img((ch+ci_logo_gap,cw+ci_logo_gap,3), color='white', alpha=ci_bg_alpha)

        ci_block2 = paste_img(ci_block2, ci_bg2)

        gap = 20
        ch,cw = get_hw(ci_block)
        lh,lw = get_hw(logo)
        out_block = solid_color_img((ch+lh+gap, max(cw,lw), 3))
        block_pos = get_pos(out_block, vbg)
        bx,by = block_pos

        lx,ly = get_pos(logo, vbg)
        ly = by
        # up_block = vbg[:py+lh,:]
        cix,ciy = get_pos(ci_block, vbg)
        ciy = by+lh+gap
        # low_block = vbg[by:, :]

        # plt_show(paste_img(logo, fc4, (lx,ly), relative=False))
        # plt_show(paste_img(ci_block, fc4, (bx,by), relative=False))


        over_logo = prev_logo(font_size=20,font=font, shape=(50,50,3))
        corner_x = 0.97
        corner_y = 0.05

        ci_logo_clips = [mp.ImageSequenceClip(move_img(over_logo, vbg, corner_x, corner_y, x2=lx, y2=ly,
                                             steps=5, h2=lh, w2=lw), fps=fps).set_start(out_start)]
        ci_logo_clips.append(mp.ImageClip(logo, duration=out_dur-0.15)\
                             .set_position((lx,ly)).set_start(out_start+0.15))
        # logo_clips = zoom_template(logo, num_chunks=1, zoom_chunks=5, zoom_scales=[3,1], zoom_scales_2=None,
        #                            pos=(0.5,1.), bg=up_block, temp_dur=out_dur,
        #                            start=out_start, vid_bg_color=None)

        ci_up = mp.ImageSequenceClip(move_img(ci_block, bg=vbg, x1=0.5, y1=1., x2=cix, y2=ciy, steps=5), fps=fps)\
                .set_start(out_start + .15).set_duration(0.5)

        start = out_start + .15 + 0.5
        ci_final = mp.ImageClip(paste_img(ci_block2, bg=vbg, pos=(cix,ciy)))\
        .set_start(start).set_duration(out_dur - 0.15 - 0.5)

        c5_clips = trans_c5+[c5]
        c5_clips += [*ci_logo_clips, ci_up, ci_final]

        v5 = mp.CompositeVideoClip([v4]+c5_clips)

    # play_video(v5)



        lower_txt = self.texts[-1][:2]
        if len(lower_txt) < 2:
            lower_txt.append('')
        overlay = paste_img(over_logo, vbg, (corner_x,corner_y))
        lower_left = text_template_components(lower_txt[0], font=font, font_size=25, color='black',
                                              text_bg_alpha=0, temp_alpha=0, gap=0, full_text_bg=True)[-1]
        overlay = paste_img(lower_left, overlay, (0.03, 0.95))
        lower_right = text_template_components(lower_txt[1], font=font, font_size=25, color='black',
                                              text_bg_alpha=0, temp_alpha=0, gap=0, full_text_bg=True)[-1]
        overlay = paste_img(lower_right, overlay, (0.97, 0.95))
        # plt_show(overlay)
        overlay = mp.ImageClip(overlay, duration=out_start-v1.duration).set_start(v1.duration)

        self.video = mp.CompositeVideoClip([v5,overlay])
    
    def add_music(self, promo, music_file):
        
        background_music = mp.AudioFileClip(music_file)
        bg_duration = background_music.duration
        while bg_duration <= 120:
            background_music = mpa.AudioClip.concatenate_audioclips([background_music,
                                                                     background_music.subclip(bg_duration//2)])
            bg_duration = background_music.duration
        bgm = background_music.subclip(0,promo.duration).audio_fadeout(3.5)
        pa = promo.audio
        if pa is not None:
            print('COMPOSSIIITTEEEEE')
            bgm = mp.CompositeAudioClip([bgm.volumex(0.2),pa]).set_fps(promo.fps)
        promo = promo.set_audio(bgm.subclip(0, promo.duration).audio_fadeout(3.5))
        return promo
    
    def get_text_clips(self):
        paths_dict = {cp:'' for cp in self.clip_paths}
        paths_dict[self.clip_paths[1]] = text_join(self.texts[0])
        paths_dict[self.clip_paths[4]] = text_join(self.texts[1])
        paths_dict[self.clip_paths[5]] = text_join(self.texts[2])
        
        return paths_dict
    
    def create_thumbnail(self, thumbnail_path=''):
         if len(thumbnail_path) > 0:
            plt.imsave(thumbnail_path, self.v.get_frame(1))
    
    def create_video(self):
        v = add_oem(self.video, oem_clip='', duration=self.v_dur, music_file=self.music_file,
                    add_music=self.add_music)
        v = add_wm(v, self.watermark)
        v = add_vo(v, self.vo_file)
        self.v = v
        return v

def create_video(template=FreshTemplate, vh=540, vw=960, duration=60, clip_paths=[], logo='', vo_file='',
                 vo_files=[], music_file='', music_files=[], texts=[], logger=None,**kwargs):
    temp = template(**locals_to_params(locals()))
    promo = temp.v
    paths_dict = temp.get_text_clips()
    return promo, paths_dict


