from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.AudioClip import AudioClip, CompositeAudioClip
import os, tempfile
from threading import Thread
import subprocess as sp
from moviepy.compat import DEVNULL, PY3
import time
import sys
import numpy as np
from moviepy.decorators import (convert_to_seconds, outplace, apply_to_audio)
import copy
from abc import ABC, abstractmethod
import traceback

def is_list(x):
    return isinstance(x, list)

def is_tuple(x):
    return isinstance(x, tuple)

def list_or_tuple(x):
    return (is_list(x) or is_tuple(x))

class CustomVideoClip(ABC):

    def __init__(self):
        self.fade_out   = 0
        self.fade_in    = 0
        self.x          = 0
        self.y          = 0
        self.out_w      = 0
        self.out_h      = 0
        self.audio      = None
        self.raw_clips  = []
        self.start      = 0
        self.mask = None

    def copy(self):
        newclip = copy.copy(self)
        if hasattr(self, 'audio'):
            newclip.audio = copy.copy(self.audio)
            
        return newclip

    def subclip(self, t_start=0, t_end=None):
        newclip = self.copy()

        newclip.t_start = t_start
        
        if (t_end is None):
            newclip.t_end = t_start + self.duration
        else:
            newclip.t_end = t_end
            newclip.duration = newclip.t_end - newclip.t_start
            newclip.end = newclip.t_start + newclip.duration
        
        if (self.audio is not None):
            newclip.audio = self.audio.subclip(t_start, t_end)
        
        return newclip

    @convert_to_seconds(['t'])
    def is_playing(self, t):
        """

        If t is a time, returns true if t is between the start and
        the end of the clip. t can be expressed in seconds (15.35),
        in (min, sec), in (hour, min, sec), or as a string: '01:03:05.35'.
        If t is a numpy array, returns False if none of the t is in
        theclip, else returns a vector [b_1, b_2, b_3...] where b_i
        is true iff tti is in the clip.
        """

        if isinstance(t, np.ndarray):
            # is the whole list of t outside the clip ?
            tmin, tmax = t.min(), t.max()

            if (self.end is not None) and (tmin >= self.end):
                return False

            if tmax < self.start:
                return False

            # If we arrive here, a part of t falls in the clip
            result = 1 * (t >= self.start)
            if self.end is not None:
                result *= (t <= self.end)
            return result

        else:

            return((t >= self.start) and
                   ((self.end is None) or (t < self.end)))
    
    @convert_to_seconds(['t'])
    @outplace
    def set_start(self, t, change_end=True):
        self.start = t
        if (self.duration is not None) and change_end:
            self.end = t + self.duration
        elif self.end is not None:
            self.duration = self.end - self.start
    
    @convert_to_seconds(['t'])
    @outplace
    def set_duration(self, t, change_end=True):
        self.duration = t

        if change_end:
            self.end = None if (t is None) else (self.start + t)
        else:
            if self.duration is None:
                raise Exception("Cannot change clip start when new"
                                "duration is None")
            self.start = self.end - t

    @apply_to_audio
    @convert_to_seconds(['t'])
    @outplace
    def set_end(self, t):
        self.end = t
        if self.end is None: return
        if self.start is None:
            if self.duration is not None:
                self.start = max(0, t - self.duration)
        else:
            self.duration = self.end - self.start
    
    @outplace
    def set_position(self, pos):
        x,y = pos
        self.x = x
        self.y = y
    
    @outplace
    def set_fps(self, fps):
        self.fps = fps

    @outplace
    def set_audio(self, audioclip):
        self.audio = audioclip
    
    @outplace
    def set_fadeout(self, fadeout):
        self.fade_out = fadeout
    
    @outplace
    def set_fadein(self, fadein):
        self.fade_in = fadein
    
    @outplace
    def set_resolution(self, width=None, height=None):
        if (width is not None and height is None):
            self.out_w = width
            self.out_h = round(self.h * width / self.w)
        elif (width is None and height is not None):
            self.out_h = height
            self.out_w = round(self.w * height / self.h)
        elif (width is not None and height is not None):
            self.out_w = width
            self.out_h = height

    def __add_input(self, clip, ffmpeg_in_cmd, filter_complex, in_start_nb, clip_prefix):
        
        def add_piped_input(raw_clips, clip):
            tmp_dir = tempfile.mkdtemp()
            pipe_name = os.path.join(tmp_dir, 'video_pipe')

            try:
                os.mkfifo(pipe_name)
            except OSError as e:
                print("Failed to create pipe for communication with ffmpeg: %s" % e)
            else:
                raw_clips.append((pipe_name, tmp_dir, clip))

        if (isinstance(clip, ConcatenatedVideoClip)):
            return self.__add_concat_clip(clip, ffmpeg_in_cmd, filter_complex, in_start_nb, clip_prefix)
        
        elif (isinstance(clip, CustomCompositeVideoClip)):
            return self.__add_composite_clip(clip, ffmpeg_in_cmd, filter_complex, in_start_nb, clip_prefix)

        elif (isinstance(clip, VideoFileClip)):
            ffmpeg_in_cmd.extend([
                '-i', clip.filename
            ])
            
            filter_complex += '[%d:v] setpts=PTS+%.02f/TB,scale=w=%d:h=%d' % (in_start_nb, clip.start, clip.out_w, clip.out_h)

            if (clip.fade_in > 0):
                filter_complex += ',fade=type=in:start_time=%.2f:duration=%.2f' % (clip.start, clip.fade_in)
            
            if (clip.fade_out > 0):
                filter_complex += ',fade=type=out:start_time=%.2f:duration=%.2f' % (clip.start + clip.duration - clip.fade_out, clip.fade_out)
            
            filter_complex += ' [%s];' % clip_prefix

            output_tag = clip_prefix
            in_start_nb += 1
            
            return (ffmpeg_in_cmd, filter_complex, in_start_nb, output_tag)
        
        else:
            add_piped_input(self.raw_clips, clip)
            pipe_name = self.raw_clips[-1][0]
            
            ffmpeg_in_cmd.extend([
                '-f', 'rawvideo',
                '-pix_fmt', 'rgb24' if clip.mask == None else 'rgba',
                '-s', '%dx%d' % (clip.size[0], clip.size[1]),
                '-r', '%.02f' % clip.fps if hasattr(clip, 'fps') else '25',
                '-i', '%s' % pipe_name
            ])

            filter_complex += '[%d:v] setpts=PTS+%.02f/TB,scale=w=%d:h=%d' % (in_start_nb, clip.start, clip.out_w, clip.out_h)

            if (clip.fade_in > 0):
                filter_complex += ',fade=type=in:start_time=%.2f:duration=%.2f' % (clip.start, clip.fade_in)
            
            if (clip.fade_out > 0):
                filter_complex += ',fade=type=out:start_time=%.2f:duration=%.2f' % (clip.start + clip.duration - clip.fade_out, clip.fade_out)
            
            filter_complex += ' [%s];' % clip_prefix

            output_tag = clip_prefix
            in_start_nb += 1

            return (ffmpeg_in_cmd, filter_complex, in_start_nb, output_tag)

    def __add_composite_clip(self, clip, ffmpeg_in_cmd, filter_complex, in_start_nb, clip_prefix):

        def get_position(clip, overlay):
            if (isinstance(overlay, ConcatenatedVideoClip) or isinstance(overlay, CustomCompositeVideoClip)):
                # print(overlay.x, overlay.y)
                return overlay.x, overlay.y
            else:
                hf, wf = 0, 0

                if (isinstance(clip, ConcatenatedVideoClip) or isinstance(clip, CustomCompositeVideoClip)):
                    hf, wf = clip.w, clip.h
                else:
                    picture = clip.get_frame(0)
                    hf, wf = picture.shape[:2]

                # GET IMAGE AND MASK IF ANY
                img = overlay.get_frame(0)
                mask = overlay.mask.get_frame(0) if overlay.mask else None                
                
                if mask is not None and ((img.shape[0] != mask.shape[0]) or (img.shape[1] != mask.shape[1])):
                    img = clip.fill_array(img, mask.shape)

                hi, wi = img.shape[:2]
                
                pos = overlay.pos(0)

                # preprocess short writings of the position
                if isinstance(pos, str):
                    pos = {'center': ['center', 'center'],
                        'left': ['left', 'center'],
                        'right': ['right', 'center'],
                        'top': ['center', 'top'],
                        'bottom': ['center', 'bottom']}[pos]
                else:
                    pos = list(pos)

                # is the position relative (given in % of the clip's size) ?
                if overlay.relative_pos:
                    for i, dim in enumerate([wf, hf]):
                        if not isinstance(pos[i], str):
                            pos[i] = dim * pos[i]

                if isinstance(pos[0], str):
                    D = {'left': 0, 'center': (wf - wi) / 2, 'right': wf - wi}
                    pos[0] = D[pos[0]]

                if isinstance(pos[1], str):
                    D = {'top': 0, 'center': (hf - hi) / 2, 'bottom': hf - hi}
                    pos[1] = D[pos[1]]

                pos = map(int, pos)
                return pos

        if (len(clip.clips) == 1):
            return self.__add_input(clip.clips[0], ffmpeg_in_cmd, filter_complex, in_start_nb, clip_prefix+'-clip%d' % 0)
        else:
            output_tags = []

            for i in range(len(clip.clips)):
                ffmpeg_in_cmd, filter_complex, in_start_nb, output_tag = self.__add_input(clip.clips[i], ffmpeg_in_cmd, filter_complex, in_start_nb, clip_prefix+'-clip%d' % i)

                output_tags.append(output_tag)
            
            overlay_base = output_tags[0]

            for i in range(1, len(clip.clips)):
                x, y = get_position(clip.clips[0], clip.clips[i])
                if list_or_tuple(x): x = x[0]
                if list_or_tuple(y): y = y[0]
                filter_complex += '[%s][%s] overlay=x=%d:y=%d:enable=\'between(t,%.2f,%.2f)\'' \
                                    % (overlay_base, output_tags[i], x, y, clip.clips[i].start, clip.clips[i].end)
                
                overlay_base = 'overlay-%d' % (i-1)
                
                if i < len(clip.clips) -1:
                    filter_complex += ' [%s];' % overlay_base
            
            filter_complex += ',select=between(t\,%.2f\,%.2f), setpts=PTS-%.2f/TB+%.2f/TB' % (clip.t_start, clip.t_end, clip.t_start, clip.start)

            if (clip.fade_in > 0):
                filter_complex += ',fade=type=in:duration=%.2f' % (clip.fade_in)
            
            if (clip.fade_out > 0):
                filter_complex += ',fade=type=out:start_time=%.2f:duration=%.2f' % (clip.clips[0].duration - clip.fade_out, clip.fade_out)
            
            filter_complex += ',scale=w=%d:h=%d [%s];' % (clip.out_w, clip.out_h, clip_prefix)

            return (ffmpeg_in_cmd, filter_complex, in_start_nb, clip_prefix)

    def __add_concat_clip(self, clip, ffmpeg_in_cmd, filter_complex, in_start_nb, clip_prefix):
        fps = clip.fps if clip.fps is not None else 25
        concat_inputs = ''

        for i in range(len(clip.clips)):
            ffmpeg_in_cmd, filter_complex, in_start_nb, output_tag = self.__add_input(clip.clips[i], ffmpeg_in_cmd, filter_complex, in_start_nb, clip_prefix+'-clip%d' % i)
            
            filter_complex += ' [%s] fps=%.2f,scale=%dx%d [%s-concat_in-%d];' % (output_tag, fps, clip.out_w, clip.out_h, clip_prefix, i)
            concat_inputs += ' [%s-concat_in-%d]' % (clip_prefix, i)
        
        filter_complex += '%s concat=n=%d, select=between(t\,%.2f\,%.2f), setpts=PTS-%.2f/TB+%.02f/TB' \
            % (concat_inputs, len(clip.clips), clip.t_start, clip.t_end, clip.t_start, clip.start)
        
        if (clip.fade_in > 0):
            filter_complex += ',fade=type=in:start_time=%.2f:duration=%.2f ' % (clip.start, clip.fade_in)
        
        if (clip.fade_out > 0):
            filter_complex += ',fade=type=out:start_time=%.2f:duration=%.2f ' % (clip.start + clip.duration - clip.fade_out, clip.fade_out)
        
        filter_complex += ' [%s];' % clip_prefix
        
        return (ffmpeg_in_cmd, filter_complex, in_start_nb, clip_prefix)
    
    def save(self, codec='h264_nvenc', preset='fast', bitrate=None,
             ffmpeg_path='/usr/bin/ffmpeg', output_file='output.mp4',logger=None):
        
        ffmpeg_cmd = [
            ffmpeg_path,
            '-hide_banner',
            '-loglevel', 'error',
            '-y'
        ]

        filter_complex = ''
        in_start_nb = 0
        clip_prefix = 'clip-0'
        
        if (isinstance(self, ConcatenatedVideoClip)):
            ffmpeg_cmd, filter_complex, in_start_nb, output_tag = self.__add_concat_clip(self, ffmpeg_cmd, filter_complex, in_start_nb, clip_prefix)
        elif (isinstance(self, CustomCompositeVideoClip)):
            ffmpeg_cmd, filter_complex, in_start_nb, output_tag = self.__add_composite_clip(self, ffmpeg_cmd, filter_complex, in_start_nb, clip_prefix)
        else:
            print("Clip not supported")
            return

        if (codec == 'h264_vaapi'):
            filter_complex += '[%s] format=nv12,hwupload [%s-hw];' % (output_tag, clip_prefix)
            output_tag = '%s-hw' % clip_prefix
        elif (codec == 'h264_nvenc'):
            filter_complex += '[%s] hwupload_cuda [%s-hw];' % (output_tag, clip_prefix)
            output_tag = '%s-hw' % clip_prefix

        if (self.audio is not None):
            self.audio_tmp_dir = tempfile.mkdtemp()
            self.audio_pipe_name = os.path.join(self.audio_tmp_dir, 'audio_pipe')

            try:
                os.mkfifo(self.audio_pipe_name)
            except OSError as e:
                print("Failed to create pipe for communication with ffmpeg: %s" % e)
            
            if (isinstance(self.audio, CompositeAudioClip)):
                fpss = [c.fps for c in self.audio.clips if getattr(c, 'fps', None)]
                sample_rate = max(fpss) if fpss else 44100
                
                nbytess = [c.reader.nbytes for c in self.audio.clips if getattr(c, 'reader', None)]
                nbytes = max(nbytess) if nbytess else 2

                ffmpeg_cmd.extend([
                    '-t', '%.2f' % self.audio.duration,
                    '-ac', '%d' % self.audio.nchannels,
                    '-ar', '%d' % sample_rate,
                    '-f', 's%dle' % (8*nbytes),
                    '-acodec', 'pcm_s%dle' % (8*nbytes),
                    '-i', self.audio_pipe_name
                ])
            else:
                sample_rate = self.audio.fps
            
                ffmpeg_cmd.extend([
                    '-t', '%.2f' % self.audio.duration,
                    '-ac', '%d' % self.audio.nchannels,
                    '-ar', '%d' % sample_rate,
                    '-f', 's%dle' % (8*self.audio.reader.nbytes),
                    '-acodec', 'pcm_s%dle' % (8*self.audio.reader.nbytes),
                    '-i', self.audio_pipe_name
                ])

            filter_complex += '[%d:a] asetpts=PTS+%.02f/TB' % (in_start_nb, self.audio.start)
            map = True
        else:
            # add a dummy filter 
            filter_complex += '[%s] null' % output_tag
            map = False

        fc_tmp_dir = tempfile.mkdtemp()
        filter_complex_filename = os.path.join(fc_tmp_dir, 'filter_complex_script')
        filter_complex_file = open(filter_complex_filename, 'w')
        filter_complex_file.write(filter_complex)
        filter_complex_file.close()

        #print(filter_complex)
        """ ffmpeg_cmd.extend([
            '-filter_complex', '%s' % filter_complex,
            '-map', '[%s]' % output_tag
        ]) """

        ffmpeg_cmd.extend([
            '-filter_complex_script', filter_complex_filename
        ])

        if (map is True):
            ffmpeg_cmd.extend([
                '-map', '[%s]' % output_tag
            ])

        if (codec == 'h264_vaapi'):
            ffmpeg_cmd.extend([
                '-vaapi_device', '/dev/dri/renderD128'
            ])
        
        if (self.audio is not None):
            ffmpeg_cmd.extend([
                '-acodec', 'aac'
            ])
        else:
            ffmpeg_cmd.extend([
                '-an'
            ])

        ffmpeg_cmd.extend([
            '-vcodec', codec
        ])

        if (codec == 'libx264'):
            ffmpeg_cmd.extend([
                '-preset', preset
            ])
        
        if (bitrate != None):
            ffmpeg_cmd.extend([
                '-b:v', bitrate,
                '-maxrate:v', bitrate
            ])

            if (codec == 'libx264'):
                ffmpeg_cmd.extend([
                    '-bufsize', bitrate
                ])

        ffmpeg_cmd.extend([
            '-f', 'mp4',
            output_file
        ])

        popen_params = {"stdout": DEVNULL,
                        "stderr": sp.PIPE,
                        "stdin": sp.PIPE}

        self.proc = sp.Popen(ffmpeg_cmd, **popen_params)

        for i in range(len(self.raw_clips)):
            if (self.raw_clips[i][1] != None):
                worker = ClipWriter(self.raw_clips[i][0], self.raw_clips[i][2], self.proc)
                worker.start()
        
        if (self.audio is not None):
            worker = ClipWriter(self.audio_pipe_name, self.audio, self.proc)
            worker.start()
        
        _, ffmpeg_error = self.proc.communicate()
        error = ''
        
        if b"Unknown encoder" in ffmpeg_error:
            logger.error(f'FFMPEG ERROR = {ffmpeg_error}')
            error += f"The video save failed because FFMPEG didn't find the specified codec for video encoding {codec}. Please install this codec or change the codec."

        elif b"incorrect codec parameters ?" in ffmpeg_error:

                error = error+("\n\nThe video save "
                "failed, possibly because the codec specified for "
                "the video (%s) is not compatible with the given "
                "extension (%s). Please specify a valid 'codec' "
                "argument in save file. This would be 'libx264' "
                "or 'h264_vaapi', or 'h264_nvenc'.") % codec

        elif  b"encoder setup failed" in ffmpeg_error:

            error = error+("\n\nThe video export "
                "failed, possibly because the bitrate you specified "
                "was too high or too low for the video codec.")

        elif b"Invalid encoder type" in ffmpeg_error:

            error = error + ("\n\nThe video export failed because the codec "
                "or file extension you provided is not a video")
        
        else:
            error = ffmpeg_error
        try:
            error = error.decode('utf-8')
            if (len(error) > 0):
                print(error)
        except Exception as e:
            logger.error(f'############# error = {error}%%%%%%%%%%%%%%%%')
            logger.error(traceback.format_exc())
            
            
        
        self.proc.wait()

        os.remove(filter_complex_filename)
        os.rmdir(fc_tmp_dir)
    
    def close(self):
        for i in range(len(self.raw_clips)):
            if (self.raw_clips[i][1] != None):
                pipe_name = self.raw_clips[i][0]
                dir_name = self.raw_clips[i][1]

                os.remove(pipe_name)
                os.rmdir(dir_name)
        
        if (self.audio is not None):
            os.remove(self.audio_pipe_name)
            os.rmdir(self.audio_tmp_dir)

        if self.proc:
            self.proc.stdin.close()
            if self.proc.stderr is not None:
                self.proc.stderr.close()

        self.proc = None
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

class ConcatenatedVideoClip(CustomVideoClip):

    def __init__(self, clips):

        CustomVideoClip.__init__(self)

        self.clips      = clips

        tt = np.cumsum([0] + [c.duration for c in clips])

        self.start, self.duration, self.end = 0, tt[-1] , tt[-1]

        self.t_start = self.start
        self.t_end   = self.end

        fpss = [c.fps for c in clips if getattr(c, 'fps', None) is not None]
        self.fps = max(fpss) if fpss else None

        sizes = [v.size for v in clips]

        self.w = self.out_w = max(r[0] for r in sizes)
        self.h = self.out_h = max(r[1] for r in sizes)

        self.size = (self.w, self.h)

        audio_t = [(c.audio, t) for c, t in zip(clips,tt) if c.audio is not None]
        if audio_t:
            self.audio = CompositeAudioClip([a.set_start(t) for a,t in audio_t])

class ClipWriter(Thread):

    def __init__(self, pipe_name, clip, proc):
        super(ClipWriter, self).__init__()
        self.pipe_name = pipe_name
        self.clip = clip
        self.proc = proc
    
    def run(self):
        input_pipe = open(self.pipe_name, 'wb', buffering=0)
        
        #cProfile.runctx('self.write_frames(input_pipe)', globals(), locals())
        self.write_frames(input_pipe)
    
        input_pipe.close()
    
    def write_frames(self, input_pipe):
        if (isinstance(self.clip, AudioClip)):
            if (isinstance(self.clip, CompositeAudioClip)):
                fpss = [c.fps for c in self.clip.clips if getattr(c, 'fps', None)]
                fps = max(fpss) if fpss else 44100
                
                nbytess = [c.reader.nbytes for c in self.clip.clips if getattr(c, 'reader', None)]
                nbytes = max(nbytess) if nbytess else 2
            else:
                fps = self.clip.reader.fps
                nbytes = self.clip.reader.nbytes
            
            for chunk in self.clip.iter_chunks(chunksize=2000, quantize=True, nbytes=nbytes, fps=fps):
                self.write_frame(input_pipe, chunk)
        else:
            for t,frame in self.clip.iter_frames(with_times=True, fps=self.clip.fps if hasattr(self.clip, 'fps') else 25,dtype="uint8"):
                if self.clip.mask != None:
                    mask = (255 * self.clip.mask.get_frame(t))
                    if mask.dtype != "uint8":
                        mask = mask.astype("uint8")
                    frame = np.dstack([frame,mask])
                
                self.write_frame(input_pipe, frame)

    def write_frame(self, input_pipe, frame):
        try:
            if PY3:
                input_pipe.write(frame.tobytes())
            else:
                input_pipe.write(frame.tostring())
        except IOError as err:
            raise IOError(err)

class CustomCompositeVideoClip(CustomVideoClip):

    def __init__(self, clips):

        CustomVideoClip.__init__(self)
        
        self.clips      = clips

        # compute duration
        ends = [c.end for c in self.clips]
        if None not in ends:
            duration = max(ends)
            self.duration = duration
            self.end = duration
        
        self.t_start = self.start
        self.t_end   = self.end

        fpss = [c.fps for c in clips if getattr(c, 'fps', None) is not None]
        self.fps = max(fpss) if fpss else None

        self.w = self.out_w = clips[0].size[0]
        self.h = self.out_h = clips[0].size[1]

        self.size = (self.w, self.h)

        # compute audio
        audioclips = [v.audio for v in self.clips if v.audio is not None]
        if audioclips:
            self.audio = CompositeAudioClip(audioclips)
