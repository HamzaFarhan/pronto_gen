from core_lib.pronto_conf import *
from core_lib.mongo_models import *
from core_lib.template_config import templateConfig

from core_lib.video_utils import rgb_to_hex, hex_to_rgb
import secrets
import uuid
import datetime
import json
from dateutil.relativedelta import relativedelta
from collections import Counter
import random
import traceback
from core_lib.platform_utils import get_signed_url

MAX_IN_PROGRESS_TIME = 360

def get_total_social_minutes_viewed(videos):
    try:
        videos.remove(None)
    except Exception as e:
        pass
    return sum([v.youtube_prop_data.estimatedMinutesWatched for v in videos if v.youtube_prop_data is not None])

def get_total_social_views(videos):
    try:
        videos.remove(None)
    except Exception as e:
        pass
    return sum([v.youtube_prop_data.views for v in videos if v.youtube_prop_data is not None])

def get_platform_wise_minutes_viewed(videos):
     try:
        videos.remove(None)
     except Exception as e:
        pass
     stats = {}
     stats['facebook'] = 0
     stats['instagram'] = 0
     stats['youtube'] = sum([v.youtube_prop_data.estimatedMinutesWatched for v in videos if v.youtube_prop_data is not None])
     return stats
            
def get_top_viewed_videos(videos,num_videos=5):
    try:
        videos.remove(None)
    except Exception as e:
        pass
    vids = dict([(v,v.youtube_prop_data.views) for v in videos if v.youtube_prop_data is not None])
    vids = list(sorted(vids.items(), key=lambda item: item[1],reverse=True))[:num_videos]
    vids = [e[0] for e in vids]
    vids = [{'fpath':e.fpath,'url':get_signed_url(CLIP_BUCKET,e.fpath),'title':e.video.title,'owner':e.owner.email} for e in vids]
    return vids
    
def get_user_videos_by_time_range(email,date_start,date_end):
    videos = []
    owner = get_user_profile(email)
    if owner:
        videos =  list(UserVideo.objects(created__gte=date_start,created__lte=date_end,owner=owner))
    return videos

   
def get_stats_by_time_range(date_start,date_end,num_top_users=5):
     stats = {}
     videos =  get_videos_by_time_range(date_start,date_end)      
     industries = [v.owner.business_info.industry for v in videos if v.owner is not None]
     industry_counts = Counter(industries)
     users = [v.owner.email for v in videos]
     unique_users = list(set(users))
     user_counts = Counter(users)
     sorted_user_counts = {k: v for k, v in sorted(user_counts.items(), key=lambda item: item[1],reverse=True)}
     top_users = [k for k,v in sorted_user_counts.items()]
     top_users = top_users[:num_top_users]
     stats['total_users'] = len(unique_users)
     stats['total_videos'] = len(videos)
     stats['top_users'] = top_users
     stats['industry_counts'] = dict(industry_counts)
     videos_social = get_videos_by_time_range_social(date_start,date_end)
     stats['total_minutes_viewed'] = get_total_social_minutes_viewed(videos_social)
     stats['total_views'] = get_total_social_views(videos)
     stats['platform_minutes_viewed'] = get_platform_wise_minutes_viewed(videos_social)
     stats['trending_videos'] = get_top_viewed_videos(videos_social)
     return stats
    
    
def get_user_stats_by_time_range(email,date_start,date_end,num_top_users=5):
     stats = {}
     videos = get_user_videos_by_time_range(email,date_start,date_end)
     if len(videos) > 0:
          industries = [v.owner.business_info.industry for v in videos]
          industry_counts = Counter(industries)
          stats['email'] = email
          stats['total_videos'] = len(videos)
          stats['industry_counts'] = dict(industry_counts)
          videos_social = get_videos_by_time_range_social(date_start,date_end,email=email)
          stats['total_minutes_viewed'] = get_total_social_minutes_viewed(videos_social)
          stats['total_views'] = get_total_social_views(videos)
          stats['platform_minutes_viewed'] = get_platform_wise_minutes_viewed(videos_social)
          stats['trending_videos'] = get_top_viewed_videos(videos_social)
          return stats
     return None     

def get_video_stats_by_time_range(vid,time_start,time_end):
     stats = {}
     video =  UserVideo.objects(fpath=vid).first()
     if video is None:
         return {}
     stats['total_minutes_viewed'] = get_total_social_minutes_viewed([video])
     stats['platform_minutes_viewed'] = get_platform_wise_minutes_viewed([video])
     stats['title'] = video.video.title
     return stats
        
def filter_valid_videos(videos):
    videos_filtered = []
    for v in videos:
         try:
             o = v.owner
             #print(v.owner.email)
             videos_filtered.append(v)
             #print('appended')
         except Exception as e:
             #print(f'continuing for {v.fpath}')
             continue
    #print(f'length of filtered = {len(videos_filtered)}')     
    return videos_filtered

def get_videos_by_time_range_social(date_start,date_end,email=None):
    videos = []
    if email is not None:
        owner = get_user_profile(email)
        if not owner:
            return []
        #video_list = list(UserVideo.objects(youtube_prop_data__last_updated__gte=date_start,youtube_prop_data__last_updated__lte=date_end,owner=owner))
        video_list = list(UserVideo.objects(created__gte=date_start,created__lte=date_end,owner=owner))
    else:
        #video_list = list(UserVideo.objects(youtube_prop_data__last_updated__gte=date_start,youtube_prop_data__last_updated__lte=date_end))
        video_list = list(UserVideo.objects(created__gte=date_start,created__lte=date_end))
    videos = videos + video_list    
    videos = filter_valid_videos(videos)
    return videos
    
def get_videos_by_time_range(date_start,date_end):
    videos = list(UserVideo.objects(created__gte=date_start,created__lte=date_end))
    videos = filter_valid_videos(videos)
    return videos

def get_videos_by_youtube_props():
    return list(UserVideo.objects(youtube_prop_data__exists=True))
    

def validate_oem_list(field,value,error):
    if not isinstance(value,list):
        error(field,' must be a list')
    oem_list = list(OEM.objects())
    for oem in value:
        if oem not in oem_list:
            error(field, f' unknown oem {oem}')
            
def get_days_ago(given_date):
    current_time = datetime.datetime.utcnow()
    diff = abs(current_time - given_date)
    return diff.days

def prepare_video_dict(v):
    template_names = list(templateConfig.keys())
    v_dict = {}
    v_dict['fpath'] = v.fpath
    v_dict['status'] = v.status
    v_dict['bucket_name'] = v.video.bucket_name
    if v.set_id is not None:
        v_dict['set_id'] = v.set_id
    v_dict['title'] = v.video.title
    v_dict['duration'] = v.video.duration
    v_dict['key_terms'] = v.video.key_terms
    v_dict['is_guest_video'] = v.video.is_guest_video
    v_dict['text_list'] = v.video.text_list
    v_dict['paths_dict'] = dict(zip(v.video.clips,v.video.text_list))
    if hasattr(v.video, "lower_third_text"):
        v_dict['call_to_action'] = v.video.lower_third_text
    if hasattr(v.video, "mood"):
        v_dict['mood'] = v.video.mood
    v_dict['music_file'] = v.video.music_file
    v_dict['images'] = v.video.images
    v_dict['clips'] = v.video.clips
    v_dict['sequence'] = v.video.clips
    v_dict['created'] = str(v.created)
    v_dict['days_ago'] =  get_days_ago(v.created)
    v_dict['thumb'] = v.video.thumbnail_path
    v_dict['oem'] = v.video.oem
    v_dict['color'] = v.video.color
    v_dict['automated'] = v.automated
    if hasattr(v.video,'template_name'):
        v_dict['template_name'] = v.video.template_name
    else:
        v_dict['template_name'] = template_names[0]
    if len(v.published_on) > 0:
        v_dict['shared'] = True
        v_dict['published_on'] = v.published_on
    if len(v.schedule_id) > 0:
        v_dict['schedule_id'] = v.schedule_id
    if v.video.video_type:
        v_dict['video_type'] = v.video.video_type
    if v.video.vo_text and len(v.video.vo_text) > 0:
        v_dict['vo_text'] = v.video.vo_text
    if v.video.voice_file and len(v.video.voice_file):
        v_dict['vo_file'] = v.video.voice_file
    if v.video.selected_voice:
        v_dict['selected_voice'] = v.video.selected_voice    
    if v.video.vo_data and len(v.video.vo_data) > 0:
        vo_clips = []
        for vo_clip in v.video.vo_data:
            clip = {}
            clip['vo_text'] = vo_clip.vo_text
            if vo_clip.vo_file:
                clip['vo_file'] = vo_clip.vo_file
            clip['clips_covered'] = list(vo_clip.clips_covered)
            vo_clips.append(clip)
        v_dict['vo_clips'] = vo_clips     
            
    
    return v_dict

def prepare_video_schedule_dict(schedule):
    s_dict = {}
    s_dict['schedule_id'] = str(schedule.id)
    s_dict['video_id'] = str(schedule.video.fpath)
    s_dict['duration'] = schedule.duration
    if schedule.given_day is not None:
        s_dict['given_day'] = schedule.given_day
    s_dict['interval'] = schedule.interval
    if hasattr(schedule,'title'):
        s_dict['title'] = schedule.title
    else:
        s_dict['title'] = schedule.video.video.title
    s_dict['time_range'] = schedule.time_range
    s_dict['publish_on'] = schedule.publish_on
    s_dict['approval_required'] = schedule.approval_required
    s_dict['state'] = schedule.state
    s_dict['created_videos'] = []
    for v in schedule.created_videos:
        s_dict['created_videos'].append(v.fpath)
    return s_dict
    
    
def get_final_clips(selected_clips):
    final_clips = []
    final_clip_ids = []
    for c in selected_clips:
        clip = Clip.objects(object_path=c).first()
        if clip is not None:
            #print(f'c = {c}, is_monetized = {clip.is_monetized}')
            if clip.is_monetized:
                final_clips.append(clip)
                final_clip_ids.append(clip.object_path)
    return final_clips,final_clip_ids
            
def get_guest_session(session_id):
    if session_id is None:
        print('guest session id not given, returning')
        return None
    try:    
        #session = GuestSession.objects(id=session_id).first()
        session = GuestSession.objects(url=session_id).first()
    except Exception as e:
        print(f'cannot retrieve guest session: error = {e}')
        session = None
    return session

def get_user_session(session_id):
    if session_id is None:
        print('user session id not given, returning')
        return None
    try:
        session = UserSession.objects(id=session_id).first()
    except Exception as e:
        print(f'cannot retrieve user session: error = {e}')
        session = None
    return session

def create_schedule_time(d,time_range='morning',logger=None):
    day = d.day
    month = d.month
    year =  d.year
    given_date  = datetime.datetime(year=year,month=month,day=day)
    if time_range == 'morning':
        date_range_start  = given_date
        date_range_end = datetime.datetime(year=year,month=month,day=day,hour=8)
    elif time_range == 'afternoon':
        date_range_start = datetime.datetime(year=year,month=month,day=day,hour=8)
        date_range_end = datetime.datetime(year=year,month=month,day=day,hour=16)
    elif time_range == 'evening':
        date_range_start = datetime.datetime(year=year,month=month,day=day,hour=16)
        date_range_end = datetime.datetime(year=year,month=month,day=day+1)
    else:
        logger.error('unsupported time_range')
        raise Exception(f'unsupported time_range {time_range}')
    ts1 = date_range_start.timestamp()
    ts2 = date_range_end.timestamp()
    new_ts = random.randint(int(ts1),int(ts2))
    return datetime.datetime.fromtimestamp(new_ts)

def get_next_schedule_time(interval,time_range,days_to_go=None,annual_date=None,logger=None):
     current_time = datetime.datetime.now()
     if days_to_go is not None:
         next_scheduled_time = current_time + relativedelta(days=+days_to_go)
     else:
         scheduled_time = current_time
         if interval.lower() == 'monthly':
             next_scheduled_time = scheduled_time + relativedelta(months=+1)
         elif interval.lower() == 'weekly':
              next_scheduled_time = scheduled_time + relativedelta(weeks=+1)
         elif interval.lower() == 'daily':
              next_scheduled_time = scheduled_time + relativedelta(days=+1)
         elif interval.lower() == 'annually' and annual_date is not None:
              scheduled_time = annual_date
              next_scheduled_time = scheduled_time + relativedelta(years=+1)
              #next_scheduled_time = scheduled_time + relativedelta(years=+1)   
         elif interval.lower() == 'once':
              next_scheduled_time = scheduled_time
         else:
              logger.error('unsupported interval')
              raise Exception('unsupported interval')   
     
     try:
        next_scheduled_time = create_schedule_time(next_scheduled_time,time_range=time_range)
     except Exception as e:
        logger.error(f'create_scehdule_time failed with error: {e}')
        raise Exception(e)  
    
     next_scheduled_timestamp = int(datetime.datetime.timestamp(next_scheduled_time))
     return next_scheduled_time,next_scheduled_timestamp

def create_video_schedule(video,
                          interval='weekly',
                          title='',
                          time_range='morning',
                          days_to_go=None,
                          annual_date=None,
                          publish_on_list=[],
                          youtube_prop_data=None,
                          approval_required=True,
                          duration=None,
                          given_day=None,
                          schedule_id=None,
                          logger=None):
    
    next_scheduled_time,next_scheduled_timestamp = get_next_schedule_time(interval,time_range,days_to_go=days_to_go,
                                                                          annual_date=annual_date,logger=logger)
    
    if duration is None:
        duration = video.video.duration
        
    try:
        if schedule_id is None:
            schedule = ScheduledVideo(
                                      created=datetime.datetime.now(),
                                      video=video,
                                      owner=video.owner,
                                      interval=interval,
                                      title=title,
                                      time_range=time_range,
                                      publish_on=publish_on_list,
                                      next_scheduled_time=next_scheduled_time,
                                      next_scheduled_timestamp=next_scheduled_timestamp,
                                      annual_date=annual_date,
                                      approval_required=approval_required,
                                      duration=duration,
                                      given_day=given_day,
                                      state='scheduled'
                                  )
        else:
            schedule = get_video_schedule(schedule_id)
            if schedule is not None:
                schedule.interval=interval
                schedule.title = title
                schedule.time_range=time_range
                schedule.publish_on=publish_on_list
                schedule.next_scheduled_time = next_scheduled_time
                schedule.next_scheduled_timestamp = next_scheduled_timestamp
                schedule.approval_required=approval_required
                schedule.duration=duration
                schedule.given_day=given_day
                schedule.annual_date=annual_date
                schedule.state='scheduled'
                
            
        if youtube_prop_data is not None:
            schedule.youtube_prop_data = youtube_prop_data
        schedule.save()
        video.automated = True
        video.schedule_id = str(schedule.id)
        video.save()
    except Exception as e:
        logger.error(f'cannot create schedule: error = {e}')
        logger.error(traceback.format_exc())
        raise Exception(f'cannot create schedule: error = {e}')
    
    return str(schedule.id)

def update_video_schedule(schedule_id,logger):
    try:
        schedule = ScheduledVideo.objects(id=schedule_id).first()
    except Exception as e:
        logger.error(f'cannot retrieve scehdule: error = {e}')
        return
    interval = schedule.interval
    time_range = schedule.time_range
    next_scheduled_time,next_scheduled_timestamp = get_next_schedule_time(interval,time_range,days_to_go=None,annual_date=schedule.annual_date,logger=logger)
    try:
        schedule.last_scheduled_time = datetime.datetime.now()
        schedule.next_scheduled_time = next_scheduled_time
        schedule.next_scheduled_timestamp = next_scheduled_timestamp
        schedule.state = 'scheduled'
        schedule.in_progress_start_timestamp = None
        schedule.save()
        logger.debug(f'SCHEDULE {schedule.id} UPDATED ')
    except Exception as e:
        logger.error(f'cannot update schedule: error = {e}')
        raise Exception(f'update schedule failed with error {e}')
    return str(schedule.id)

def get_expired_video_schedules():
    current_time = datetime.datetime.now()
    current_timestamp = int(datetime.datetime.timestamp(current_time))
    schedules = ScheduledVideo.objects(next_scheduled_timestamp__lte=current_timestamp)
    return schedules

def get_in_progress_too_long_schedules():
    current_time = datetime.datetime.now()
    current_timestamp = int(datetime.datetime.timestamp(current_time))
    schedules = ScheduledVideo.objects(state='in_progress')
    too_long_schedules = []
    for schedule in schedules:
        if schedule.in_progress_start_timestamp > 0:
            if int(current_timestamp - schedule.in_progress_start_timestamp) > MAX_IN_PROGRESS_TIME:
               too_long_schedules.append(schedule)
        #else:
        #    schedule.in_progress_start_timestamp = current_timestamp
        #    schedule.save()
            
    return too_long_schedules


def get_video_schedule_dict(schedule_id,logger):
    try:
        schedule = ScheduledVideo.objects(id=schedule_id).first()
        if schedule:
            v = schedule.video
            schedule_dict = prepare_video_schedule_dict(schedule)
            return schedule_dict
        else:
            return None
    except Exception as e:
        raise Exception(f'getting video schedule failed with error {e}')
        
def get_video_schedule(schedule_id):
    try:
        return ScheduledVideo.objects(id=schedule_id).first()
    except Exception as e:
        return None

def get_video_schedule_by_video(video_obj):
    try:
        return ScheduledVideo.objects(video=video_obj).first()
    except Exception as e:
        return None
        
def del_video_schedule(schedule_id,logger):
    try:
        schedule = ScheduledVideo.objects(id=schedule_id).first()
        v = schedule.video
        v.automated = False
        v.schedule_id = ''
        v.save()
        #for vid in schedule.created_videos:
        #    vid.schedule_id = ''
        #    vid.save()
        schedule.delete()
    except Exception as e:
        logger.error(f'schedule deletion failed with error {e}')
        raise Exception(f'schedule deletion failed with error {e}')
    return f'{schedule_id} deleted successfully'

    
        
def get_videos_by_schedule_id(schedule_id,logger):
    if schedule_id is not None:
        schedule = get_video_schedule(schedule_id)
        if schedule is None:
            return []
        #return UserVideo.objects(schedule=get_video_schedule(schedule_id)).all()
        return schedule.created_videos
    return []

def get_automated_user_videos(email,logger):
    user = UserProfile.objects(email=email).first()
    if user:
        videos = UserVideo.objects(owner=user,automated=True)
        return videos
    return []

def get_schedules_by_user(email,logger):
    try:
        user = get_user_profile(email)
        schedule_list = ScheduledVideo.objects(owner=user)
        schedule_dict_list = []
        for schedule in schedule_list:
            schedule_dict = prepare_video_schedule_dict(schedule)
            schedule_dict_list.append(schedule_dict)
        return schedule_dict_list
    except Exception as e:
       raise Exception(f'getting video schedules list failed with error {e}')
    
def extract_keywords(s):
    x = ''.join(s)
    y = x.split(',')[:6]
    y = [e.strip() for e in y]
    y = list(set(y))
    y = ','.join(y)
    return y

    
def save_youtube_props(session_id,event):
    session = get_user_session(session_id)
    if not session:
        return None
    youtube_prop_data = YoutubePropData(description=event.get('description','Video for Youtube upload testing'),
                                        fpath=event.get('local_fpath'))
    youtube_prop_data.title = event.get('title','User Video')
    youtube_prop_data.category = event.get('category',"22")
    keywords = event.get('keywords',"uploaded,promo")
    youtube_prop_data.keywords =  extract_keywords(keywords)
    youtube_prop_data.privacyStatus = event.get('privacyStatus',"public")
    video_id =  event.get('video_id','')
    if video_id is not None:
        video = get_user_video(video_id)
        if video is not None:
            video.youtube_prop_data = youtube_prop_data
            session.youtube_uploads.append(video)
            video.save()
            session.save()
    return session

def create_youtube_props(event):
    youtube_prop_data = YoutubePropData(description=event.get('description','Video for Youtube upload testing'),
                                        fpath=event.get('local_fpath'))
    youtube_prop_data.title = event.get('title','User Video')
    youtube_prop_data.category = event.get('category',"22")
    keywords = event.get('keywords',"uploaded,promo")
    youtube_prop_data.keywords =  extract_keywords(keywords)
    youtube_prop_data.privacyStatus = event.get('privacyStatus',"public")
    return youtube_prop_data
 
    
def get_user_video(video_id,logger=None):
    if video_id is None:
        if logger:
            logger.info('video id not given, returning')
        return None
    try:
        video = UserVideo.objects(fpath=video_id).first()
    except Exception as e:
        if logger:
            logger.error(f'cannot retrieve user video: error = {e}')
        video = None
    return video

def add_video_event(user,video,event_type,published_on,logger):
    prev_ev =  UserVideoEvent.objects(user=user,video=video).first()
    if prev_ev is not None:
        if prev_ev.hex_digest == video.video.hex_digest:
           return 'success'
    try:
        ev = UserVideoEvent(user=user,video=video,hex_digest=video.video.hex_digest,event_type=event_type,published_on=published_on)
        ev.save()
        return "success"
    except Exception as e:
        logger.error(f'error {e} while adding video event')
        logger.error(traceback.format_exc())
        return 'failed'
        
def get_remaining_quota(email,logger):
    current_time = datetime.datetime.now()
    user = get_user_profile(email)
    if user is None:
        raise Exception("user not found")    
    d = user.last_billing_date.date()
    last_billing_date = datetime.datetime(year=d.year,month=d.month,day=d.day)
    videos_after_last_billing = UserVideoEvent.objects(created__gte=last_billing_date,user=user).count()
    logger.debug(f'Videos made after last billing = {videos_after_last_billing}')
    plan_name = user.plan_name
    video_quota = video_quotas.get(plan_name,0)
    if video_quota == 0:
        return 0
    if videos_after_last_billing > video_quota:
        return 0
    return video_quota - videos_after_last_billing
        
    
def get_user_image(image_id):
    if image_id is None:
        print('image id not given, returning')
        return None
    try:
        image = Image.objects(object_path=image_id).first()
    except Exception as e:
        print(f'cannot retrieve user image: error = {e}')
        image = None
    return image

def get_user_clip(clip_id):
    if clip_id is None:
        print('clip id not given, returning')
        return None
    try:
        clip = Clip.objects(object_path=clip_id).first()
    except Exception as e:
        print(f'cannot retrieve user clip: error = {e}')
        clip = None
    return clip

def get_user_audio(clip_id):
    if clip_id is None:
        print('audio clip id not given, returning')
        return None
    try:
        clip = UserAudio.objects(object_path=clip_id).first()
    except Exception as e:
        print(f'cannot retrieve user audio: error = {e}')
        clip = None
    return clip

def get_video_name_from_thumb(img):
    vid_name = img.replace('_thumb','')
    vid_name = vid_name.replace('images','videos')
    vid_name = vid_name[:vid_name.rfind('.')+1]
    vid_name = vid_name+'mp4'
    return vid_name

def get_thumb_name_from_visual(visual):
    thumb = visual[:visual.rfind('.')]
    ext = visual[visual.rfind('.')+1:]
    thumb = thumb + '_thumb' + '.'+ 'jpg'
    thumb = thumb.replace('videos','images')
    thumb = thumb.replace('clips','images')
    return thumb

def find_in_dict_list(key,value,l):
    for obj in l:
        x = obj.get(key,None)
        if x == value:
            return obj
    return None
        

def build_user_visual_list(l,visual_type,logger):
    out_list = []
    for v in l:
        visual_key = v.object_path
        #logger.debug(f'VISUAL KEY = {visual_key}')
        obj = {}
        if '_thumb.' in visual_key:
            vid = get_video_name_from_thumb(visual_key)
            video = get_user_video(vid)
            if video is not None:
                logger.debug('VIDEO {vid} FOUND-IGNORNING')
                continue
            vid = visual_key.replace('_thumb','')
            if visual_type == 'images':
                db_obj = get_user_image(vid)
            else:
                db_obj = get_user_clip(vid)
            if db_obj is not None:
                obj['visual_path'] = vid
                obj['key_terms'] = db_obj.key_terms
                obj['thumb'] = visual_key
                out_list.append(obj)
        else: 
             if visual_type == 'images':
                 obj['visual_type'] = 'image'
                 db_obj = get_user_image(visual_key)
             elif visual_type == 'audio':
                 obj['visual_type'] = 'audio'
                 db_obj = get_user_audio(visual_key)
             else:
                 obj['visual_type'] = 'clip'
                 db_obj = get_user_clip(visual_key)
             if db_obj is not None:
                if  db_obj.ext:
                    obj['ext'] = db_obj.ext  
                if visual_type != 'audio':  
                    visual = find_in_dict_list('visual_path',visual_key,out_list)
                    if visual is not None:
                        logger.debug(f'VISUAL {visual_key} FOUND-IGNORNING')
                        continue
                    obj['key_terms'] = db_obj.key_terms
                    obj['thumb'] = get_thumb_name_from_visual(visual_key)
                obj['visual_path'] = visual_key    
                out_list.append(obj)
    return out_list            
    
def get_conn_string(conf):
    db_name =  DB_NAME
    username = DB_USER
    password = DB_PASS
    conn_str = 'mongodb://'+username+':'+password+'@'+cluster_id+'?'+params
    return conn_str
    
def connect_to_db():
    conn_id='default'
    username = DB_USER
    password = DB_PASS
    c = connect(DB_NAME,alias=conn_id,host=DB_HOST,port=DB_PORT)
    return c

def new_oem(name,industry='',hex_color=''):
    if name is None:
        raise Exception('Name Not Given')
    if not isinstance(name,str):
        raise Exception('Name not string')
    if len(name) == 0:
        raise Exception('Name is of 0 length')

    if not isinstance(industry, str):
        industry = ''
    oem = OEM(name=name,industry=industry,hex_color=hex_color)
    oem.save()
    industry_obj = VisualBucket.objects(name=industry).first()
    if industry_obj is not None:
        new_visual_bucket(industry+'_oem_'+name,industry_obj.bt,cat='industry_oem')
    

def delete_oem(name):
    oem = OEM.objects(name=name).first()
    if oem is not None:
        oem.delete()
    
    
def new_google_context(client_id):
    google_context =  GoogleSigninContext(client_id=client_id)
    google_context.save()
    return google_context

def update_google_context(client_id,session_id):
    google_context =  GoogleSigninContext(client_id=client_id)
    google_context.session_id = session_id
    google_context.save()

def get_google_context(client_id):
    return GoogleSigninContext.objects(client_id=client_id).first()

def delete_google_context(client_id):
    context = GoogleSigninContext.objects(client_id=client_id).first()
    context.delete()


def new_forgot_pw(email,code):
    forgot_pw =  ForgotPW(email=email,code=code)
    forgot_pw.save()
    return forgot_pw
    
def get_forgot_pw(email):
    if email is None:
        print('email not given, returning')
        return None
    try:
        forgot_pw = ForgotPW.objects(email=email).first()
    except Exception as e:
        print(f'cannot retrieve forgot PW object for email {email}: error = {e}')
        forgot_pw = None
    return forgot_pw
    
def new_guest_session(company_name,url):
    
    business_info = BusinessInfo(company_name=company_name,
                                 url=url)
    session = GuestSession(business_info=business_info)
    session.url = url
    session.created = datetime.datetime.utcnow()
    session.save()
    return session

def update_guest_session(session_id,
                         industry=None,
                         business_type=None,
                         greeting=None,
                         moods=None,
                         images=None,
                         colors=None,
                         key_terms=None,
                         session_key_terms=None,
                         searched_clips=None,
                         videos=[],
                         scrape_result=None):
    
    if session_id is None:
        print('session id not given, returning')
        return None
    #try:
    #print('IN UPDATE GUEST SESSION')    
    #q = GuestSession.objects(id=session_id)
    session = GuestSession.objects(url=session_id).first()
    if session is None:
        print('session not found, returning')
        return None

    if industry is not None:
        session.business_info.industry = industry
    if business_type is not None:
        session.business_info.business_type = business_type
    if greeting is not None:
        session.business_info.greeting = greeting
    if moods is not None:
        session.business_info.moods = moods
    if images is not None:
        session.business_info.images = images
    #if people_images is not None:
    #    session.business_info.people_images = people_images
    if colors is not None:
        session.business_info.colors = colors
    if key_terms is not None:
        session.business_info.key_terms = key_terms
    if session_key_terms is not None:
        session.key_terms = key_terms

    if searched_clips is not None:
        session.searched_clips = searched_clips
    
    session.videos += videos
    if scrape_result is not None:
        session.scrape_result = scrape_result

    session.save()
    #except Exception as e:
    #    print('exception occurred: {e} '.format(e))
    #    session = None
    return session

def new_user_profile(email,
                     p_hash=None,
                     username=None,
                     business_info=None,billing_info=None,oem_list=[],signup_flow=True,
                     first_name='',
                     last_name='',
                     status=None,
                     plan_name=''):
    if not isinstance(email,str):
        print('email must be a string for creating user profile')
        return None,None
    if email is None or len(email) == 0:
        print(f'invalid email {email} for creating user profile')
        return None,None

    if business_info is not None:
        business_info.email = email
        
    print(f'BILLING INFO = {billing_info}')
    user = UserProfile(email=email,p_hash=p_hash,username=username,business_info=business_info,
                       billing=billing_info,status='unconfirmed',first_name=first_name,last_name=last_name,
                       plan_name=plan_name,
                       role='user')
   
    today = datetime.datetime.utcnow()
    created = user.created
    user.last_billing_date = created
        
    for oem_name in oem_list:
        oem = OEM.objects(name=oem_name).first()
        if oem:
            user.approved_oem_list.append(oem)
    
    #confirmation_token = secrets.token_urlsafe(32)
    if signup_flow:
        code = secrets.randbelow(100000) 
        pending = PendingSignup(email=email,code=code)
        if pending is not None:
            pending.save()
            user.save()
            return user,code
        print('unable to create pending signup record')
        return None,None
    
    if status is not None:
        user.status = status
        
    user.save()
    return user,None

def delete_user_profile(user):
    email = user.email
    user.delete()
    return email

def new_admin(email,
              role='admin',
              p_hash=None,username=None,
              business_info=None,
              first_name='',
              last_name='',
              status=None,
              logger=None):
    if not isinstance(email,str):
        logger.error('email must be a string for creating user profile')
        return None
    if email is None or len(email) == 0:
        logger.error(f'invalid email {email} for creating user profile')
        return None

    if business_info is not None:
        business_info.email = email
        
    user = UserProfile(email=email,
                     role=role,
                     p_hash=p_hash,
                     username=username,
                     business_info=business_info,
                     first_name=first_name,
                     last_name=last_name)
   
    if status is not None:
        user.status = status
        
    user.save()
    return user
        
def set_user_oem_list(email,oem_list=[]):
     user = UserProfile.objects(email=email).first()
     if user is None:
         raise Exception('user not found')
     for oem_name in oem_list:
         oem = OEM.objects(name=oem_name).first()
         if oem:
              user.business_info.approved_oem_list.append(oem)
     user.save()
         
def get_user_oem_list(email):
     user = UserProfile.objects(email=email).first()
     if user is None:
         raise Exception('user not found')
     oem_list = []
     for oem in user.business_info.approved_oem_list:
         oem_list.append(oem.name)
     return oem_list

def set_user_bucket_list(email,bucket_list=[]):
     user = UserProfile.objects(email=email).first()
     if user is None:
         raise Exception('user not found')
     for bucket_name in bucket_list:
         bucket = VisualBucket.objects(name=bucket_name).first()
         if bucket:
              user.business_info.approved_bucket_list.append(bucket)
     user.save()
         
def get_user_bucket_list(email):
     user = UserProfile.objects(email=email).first()
     if user is None:
         raise Exception('user not found')
     bucket_list = []
     for bucket in user.business_info.approved_bucket_list:
         bucket_list.append(bucket.name)
     return bucket_list
def get_visual_bucket_by_name(bucket_name) :
    return VisualBucket.objects(name=bucket_name).first()

def remove_user_oem(email,oem_name):
    user = UserProfile.objects(email=email).first()
    if user is None:
         raise Exception('user not found')
    for oem in user.approved_oem_list:
        if oem.name == oem_name:
            user.approved_oem_list.remove(oem)
            break
    user.save()

def remove_user_bucket(email,bucket_name):
    user = UserProfile.objects(email=email).first()
    if user is None:
         raise Exception('user not found')
    for bucket in user.business_info.approved_bucket_list:
        if bucket.name == bucket_name:
            user.business_info.approved_bucket_list.remove(bucket)
            break
    user.save()

def get_business_types():
    return BusinessType.objects()

def new_business_type(bt,extra_buckets,logger=None):
     extras = [get_visual_bucket_by_name(e) for e in extra_buckets]
     if logger:
         logger.debug(f'extras = {extras}')
     new_bt = BusinessType(name=bt,extra_buckets=extras)
     new_bt.save()
     return new_bt
     
def delete_business_tye(name):
    bt = BusinessType.objects(name=name).first()
    if bt is not None:
        bt.delete()
        
def update_business_type(bt,extra_buckets):
     bt = BusinessType.objects(name=bt).first()
     extras = [get_visual_bucket_by_name(e) for e in extra_buckets]
     if bt is not None:
         bt.extra_buckets = extras
         bt.save()
         return bt
     return None
     
def get_visual_buckets_by_bt_obj(bt_obj):
    buckets = VisualBucket.objects(business_type=bt_obj)
    for b in buckets:
        if '_oem_' in b.name:
            buckets.remove(b)
    return buckets
            
def get_extra_buckets():
    buckets =  list(VisualBucket.objects(category='extra'))
    buckets = [b.name for b in buckets]
    return buckets

def get_industry_buckets():
    buckets =  list(VisualBucket.objects(category='industry'))
    buckets = [b.name for b in buckets]
    return buckets
    
    
def get_visual_buckets_by_bt(bt):
    buckets = list(VisualBucket.objects(bt=bt))
    for b in buckets:
        #print(b.name)
        if '_oem_' in b.name:
            #print(f'removing {b.name}')
            buckets.remove(b)
    return buckets

def new_visual_bucket(bucket_name,bt_name,cat='industry'):
    vb = VisualBucket(name=bucket_name)
    if vb is not None:
        vb.bt=bt_name
        vb.category=cat
        vb.industry = bucket_name
        vb.save()
        return vb
    return None

def update_visual_bucket(bucket_name,bt_name=None,cat=None):
    vb = VisualBucket.objects(name=bucket_name).first()
    if vb is not None:
        if bt_name is not None:
            vb.bt=bt_name
        if cat is not None:
            vb.category=cat
        vb.save()
        return vb
    return None
        
def delete_visual_bucket(name):
    bucket = VisualBucket.objects(name=name).first()
    if bucket is not None:
        bucket.delete()

def get_system_meta_info(logger,admin=True):
    result = {}
    result['video_timeouts'] = PRONTO_VIDEO_TIMEOUTS
    result['data'] = []
    result['industries'] = {}
    plan_names = list(video_quotas.keys())
    result['admin_plan_names'] = [e for e in plan_names if 'admin' in e]
    result['stripe_plan_names'] = [e for e in plan_names if 'admin' not in e]
    
    try:
        result['supported_social_list'] = PRONTO_SUPPORTED_SOCIAL_LIST
        result['moods'] = PRONTO_MOOD_LIST
        extra_buckets = get_extra_buckets()
        result['extra_buckets'] = extra_buckets
        business_types = get_business_types()
       
        for t in business_types:
            if len(t.name) == 0:
                logger.debug('No business type: continuing')
                continue
            buckets = get_visual_buckets_by_bt(t.name)
            if not admin:
                if len(buckets) == 0:
                     logger.debug(f'No Industry for Business Type {t.name}--continuing')
                     continue
            o = {}
            o['business_type'] = t.name
            o['industries'] = []
            result['industries'][t.name] = []
            ext_buckets = list(t.extra_buckets)
            o['extra_buckets'] = [b.name for b in ext_buckets]
            buckets = get_visual_buckets_by_bt(t.name)
            for b in buckets:
                bo = {}
                bo['industry'] = b.name
                result['industries'][t.name].append(b.name)
                bo['key_terms'] = []
                bo['oem_list'] = []
                oem_list = list(get_oem_by_industry(b.name))
                for oem in oem_list:
                    oem_obj = {}
                    oem_obj['name'] = oem.name
                    oem_obj['default_color'] = oem.hex_color
                    bo['oem_list'].append(oem_obj)
                if len(oem_list) > 0:
                    l = bo['oem_list']
                    logger.debug(f'OEM LIST = {l}')
                o['industries'].append(bo)
            result['data'].append(o)
        result['status'] = 'success'
    except Exception as e:
         logger.error(traceback.format_exc())
         raise Exception(str(e))        
    return result


def get_extra_buckets_for_btypes(business_type):
    bt = BusinessType.objects(name=business_type).first()
    extras = bt.extra_buckets
    return [e.name for e in extras]

def get_user_profile(email):
    return UserProfile.objects(email=email).first()
def get_admin(email):
    user = UserProfile.objects(email=email).first()
    if user.role != 'admin' and user.role != 'super_admin':
        return None
    return user

def get_user_profile_by_subscription(cust_id,sub_id):
    user = UserProfile.objects(subscription_customer_id=cust_id).first()
    if user is None:
        return None
    if user.subscription_id:
        if user.subscription_id == sub_id:
            return user
        else:
            return None
    else:
        return user
        

def verify_pending_signup(email,code):
    signup = PendingSignup.objects(email=email).first()
    if signup is None:
        print(f'verify pending signup: signup record not found')
        return False
    #print(f'verify pending signup 1--email = {email}-signup code = {signup.code}, code = {code}')
    if signup.code == code:
        user = get_user_profile(email)
        if user is None:
            print(f'verify pending signup user is None')
            return False
        user.status = 'pending_subscription'
        #user.status = 'active'
        user.save()
        signup.delete()
        return True
    return False
         
    
def save_user_video(video,fpath,user):
    user_video = UserVideo(video=video,owner=user,fpath=fpath)
    user_video.save()
    return user_video

def save_user_clip(bucket,fpath,email,key_terms=[],is_monetized=True,ext='mp4'):
    user_profile = get_user_profile(email)
    user_clip = Clip(bucket_name=bucket,object_path=fpath,owner=user_profile,is_monetized=is_monetized,
                     key_terms=key_terms,ext=ext)
    user_clip.save()
    return user_clip

def save_user_image(bucket,fpath,email,key_terms=[],is_monetized=True,ext='jpg'):
    user_profile = get_user_profile(email)
    user_img = Image(bucket_name=bucket,object_path=fpath,owner=user_profile,is_monetized=is_monetized,
                     key_terms=key_terms,ext=ext)
    user_img.save()
    return user_img

def update_user_image(bucket,fpath,email,key_terms=[],is_monetized=True):
    user_profile = get_user_profile(email)
    user_img = get_image(fpath)
    user_image.key_terms = key_terms
    user_img.save()
    return user_img

def save_user_audio_in_db(bucket,fpath,email,logger,ext='mp3'):
    user_profile = get_user_profile(email)
    if user_profile is None:
        logger.error(f'user {email} not found while adding audio file to DB')
        return None
    user_audio = UserAudio(bucket_name=bucket,object_path=fpath,owner=user_profile,ext=ext)
    user_audio.save()
    return user_audio
    
def get_clip(clip_id):
    if clip_id is None:
        print('clip id not given, returning')
        return None
    try:
        clip = Clip.objects(object_path=clip_id).first()
    except Exception as e:
        print(f'cannot retrieve clip: error = {e}')
        clip = None
    return clip

def get_audio(clip_id):
    if clip_id is None:
        print('clip id not given, returning')
        return None
    try:
        clip = UserAudio.objects(object_path=clip_id).first()
    except Exception as e:
        print(f'cannot retrieve clip: error = {e}')
        clip = None
    return clip

def get_image(image_id):
    if image_id is None:
        print('image id not given, returning')
        return None
    try:
        image = Image.objects(object_path=image_id).first()
    except Exception as e:
        print(f'cannot retrieve image: error = {e}')
        image = None
    return image

    
def del_clip(clip_id):
    clip = Clip.objects(object_path=clip_id).first()
    if clip:
        clip.delete()
        
def del_image(image_id):
    image = Image.objects(fpath=image_id).first()
    if image:
        image.delete()
        
def del_audio(audio_id):
    clip = UserAudio.objects(object_path=clip_id).first()
    if clip:
        clip.delete()
        
def del_user_video(video_id):
    user_video = UserVideo.objects(fpath=video_id).first()
    if user_video:
        user_video.delete()
        
def get_set_videos(set_id):
     return list(UserVideo.objects(set_id=set_id))
     
def get_oem_by_name(oem):
    return OEM.objects(name=oem).first()

def get_oem_by_industry(industry):
    return OEM.objects(industry=industry)
def get_oem_list_by_industry(industry):
    oems = list(OEM.objects(industry=industry))
    return [e.name for e in oems]
     
def set_user_delete_status(user):
    user.status = 'deleted'
    user.deletion_date = datetime.datetime.utcnow()
    user.save()
    
def new_user_session(email,videos=[],key_terms=[],searched_clips=[],auth_type='pronto',logger=None):
    if not isinstance(email,str):
        logger.error('email must be a string for creating user session')
        raise 'email must be a string for creating user session'
    if email is None or len(email) == 0:
        logger.error(f'invalid email {email} for creating user session')
        raise f'invalid email {email} for creating user session'

    user = get_user_profile(email)
    if user is None:
        logger.error(f'user not found for {email}')
        raise Exception(f'user {email} not found in DB')
    logger.debug(f'EMAIL = {email} STATUS = {user.status}')
    if user.status == 'cancelled':
        current_time = datetime.datetime.now()
        if user.last_billing_date is not None:
            next_billing_date = user.last_billing_date + relativedelta(days=+30)
            if current_time.date() >= next_billing_date.date():
                cancel = str(user.cancellation_date.date())
                next_billing = str(next_billing_date.date())
                user.status = 'deleted'
                user.save()
                raise Exception(f"user subscription was cancelled on {cancel} and expired on {next_billing}")
    elif user.status == 'deleted':
            deletion_date = str(user.deletion_date.date())
            raise Exception(f"user subscription expired on {deletion_date}")                  
              
    if user.status == 'blocked':
       status = user.status
       logger.error(f'user status is {status}')
       raise Exception(f'user status is {status}')
    if (user.status == 'unconfirmed' or user.status == 'pending_subscription') and (auth_type.lower() == 'google' or auth_type.lower() == 'facebook' or auth_type.lower() == 'linkedin'):
            user.status = 'active'
            user.save()
        
    session = UserSession(user=user,email=user.email)
    session.videos = videos
    session.key_terms = key_terms
    #session.searched_clips = searched_clips
    session.created = datetime.datetime.utcnow()
    session.save()
    return session

def new_admin_session(email,auth_type='pronto',logger=None):
    if not isinstance(email,str):
        logger.error('email must be a string for creating user session')
        raise 'email must be a string for creating user session'
    if email is None or len(email) == 0:
        logger.error(f'invalid email {email} for creating user session')
        raise f'invalid email {email} for creating user session'

    admin_user = get_admin(email)
    if admin_user is None:
        logger.error(f'admin user not found for {email}')
        raise Exception('admin user {email} not found')
    logger.debug(f'EMAIL = {email} STATUS = {admin_user.status}')
    if admin_user.status != 'active' and auth_type == 'pronto':
        logger.error(f'user status is {admin_user.status}')
        raise Exception(f'user status is {admin_user.status}')
    elif (admin_user.status != 'blocked' and admin_user.status != 'deleted') and auth_type.lower() == 'google':
        admin_user.status = 'active'
        admin_user.save()
    
    session = AdminSession(admin_user=admin_user,email=admin_user.email)
    session.created = datetime.datetime.utcnow()
    session.save()
    return session

def get_admin_session_(session_id,logger):
    if session_id is None:
        logger.error('user session id not given, returning')
        return None
    try:
        session = AdminSession.objects(id=session_id).first()
    except Exception as e:
        logger.error(f'cannot retrieve user session: error = {e}')
        session = None
    return session
    
def update_user_session(session_id,key_terms=[],searched_clips=[],videos=[]):
    if len(session_id) == 0:
        print(f'invalid email {session_id} for updating user session')
        return None

    session = UserSession.objects(id=session_id).first()
    if session is None:
        print(f'user session session not found for update for session_id = {session_id}')
        return None

    session.key_terms += key_terms
    #session.searched_clips += searched_clips
    session.videos += videos
    session.save()
    return session

def delete_guest_session(session_id,logger=None):
    #q = GuestSession.objects(id=session_id)
    sessiion = GuestSession.objects(url=session_id).first()
    if not session:
       raise Exception('guest session not found') 
    session.delete()
    return session_id

def delete_user_session(session_id):
    session = UserSession.objects(id=session_id).first()
    if not session:
        raise Exception('user session not found')
    session.delete()
    return session_id
def delete_admin_session(session_id,logger=None):
    session = AdminSession.objects(id=session_id).first()
    if not session:
        raise Exception('admin session not found')
    session.delete()
    return session_id


def get_session_clip_list(session_id,guest=True):
    if guest:
        session = get_guest_session(session_id)
        return session.searched_clips
    session = get_user_session(session_id)
    return session.searched_clips

def get_business_info(session_id,guest=True):
    if guest:
        session = get_guest_session(session_id)
        return session.business_info
    session = get_user_session(session_id)
    return session.user.business_info
    
        
def move_guest_session_to_user(email,guest_session,conf):
    user = new_user_profile(email,business_info=guest_session.business_info)
    user_session = new_user_session(email)
    for video in guest_session.videos:
        fpath = video.fpath
        src_bucket = video.bucket_name
        fname = fpath[fpath.rfind('/')+1:]
        folder = user_session.user.email
        new_fpath = generate_file_name(fname,folder)
        new_bucket = new_fpath[:new_fpath.find('/')]
        new_file_key = new_fpath[new_fpath.rfind('/')+1:]
        copy_file(src_bucket,new_bucket,fname,new_file_key)
        delete_object(src_bucket,fname)
        new_video = UserVideo(fpath=new_fpath)
        new_video.video = video
        new_video.video.bucket_name = new_bucket
        new_video.owner = user
        new_video.set_id = str(uuid.uuid1().hex[:16])
        new_video.save()
        #user_session.videos.append(new_video)
        #user_session.save()
    return user_session
        



def create_or_update_video_obj(
                            session_id,
                            is_guest_video,
                            bucket,
                            object_path,
                            thumbnail_path,
                            duration,
                            title,
                            text_list,
                            call_to_action,
                            music_file,
                            final_clip_sequence,
                            key_terms,
                            session_in=None,
                            video_id=None,
                            set_id=None,
                            schedule_id=None,
                            userid=None,
                            contact_info=[],
                            ci_dict={},
                            oem='',
                            color='#0000FF',
                            intro_vo_path='',
                            middle_vo_path='',
                            outro_vo_path='',
                            template_name='',
                            hex_digest='',
                            vo_text='',
                            vo_file=None,
                            voice_file=None,
                            vo_data=None,
                            selected_voice='',
                            video_type='instant',
                            logger=None):
    
    
    session = None
    logger.warning(f'CREATE OR UPDATE 1--session_in = {session_in}, session_id = {session_id}, TEXT LIST = {text_list}')
    vo_data_list = []
    if vo_data is not None:
        for data in vo_data:
            vo_text_ = data.get('vo_text','')
            vo_file_ = data.get('vo_file',None)
            clips_covered = data.get('clips_covered',[])
            vo_data_obj = VoiceOverData(vo_text=vo_text_,vo_file=vo_file_,clips_covered=clips_covered)
            vo_data_list.append(vo_data_obj)
    
    logger.info(f'FFFFFFFZZZZZZZZZ 11111 VO FILE = {vo_file}')    
    video = Video(
                  hex_digest=hex_digest,
                  bucket_name=bucket,
                  title=title,
                  duration=duration,
                  thumbnail_path = thumbnail_path,
                  is_guest_video = is_guest_video,
                  text_list=text_list,
                  contact_info=contact_info,
                  ci_dict=ci_dict,
                  music_file=music_file,
                  clips=final_clip_sequence,
                  key_terms=key_terms,color=color,
                  template_name=template_name,
                  oem=oem,
                  vo_text=vo_text,
                  vo_file=vo_file,
                  voice_file=voice_file,
                  vo_data=vo_data_list,
                  selected_voice=selected_voice,
                  video_type=video_type
                  )
    logger.debug('CREATE OR UPDATE 2')
    if session_in is not None:
        logger.warning('SESSION IN IS NOT NONE CASE')
        session = session_in
    logger.info(f'FFFFFFFZZZZZZZZZ 22222 VO FILE IN VIDEO  = {video.vo_file}')  
    
    if session_id is not None and isinstance(session_id,str) and len(session_id) > 0:
        if is_guest_video:
            video.clips = []
            video.sequence = []
            #session = GuestSession.objects(id=session_id).first()
            if session is None:
                session = get_guest_session(session_id)
            if session is None:
                logger.info('guest session not found')
                return None
            guest_video = GuestVideo(fpath=object_path)
            guest_video.video = video
            session.videos.insert(0,guest_video)
            if set_id is not None:
                guest_video.set_id = set_id
            guest_video.save()
            return guest_video,str(guest_video.fpath)
            
        else:
            if session is None:
                session = get_user_session(session_id)
            if session is None:
                print('user session not found')
                return None
    else:
        logger.warning('SESSION ID IS NONE CASE')
            
    logger.debug('CREATE OR UPDATE 4')        
    if userid is not None:
        user = get_user_profile(userid)
    elif session is not None:
        user = session.user
    logger.debug('CREATE OR UPDATE 5')    
    if video_id is not None:
        user_video = get_user_video(video_id)
    else:
        logger.debug(f'CREATE OR UPDATE: CREATING NEW VIDEO')
        user_video = UserVideo(fpath=object_path,owner=user,status='editable',created=datetime.datetime.utcnow())
    if user_video is None:
        logger.warning('USER VIDEO IS NONE')
        return None,None
    user_video.video = video
    logger.info(f'FFFFFFFZZZZZZZZZ 33333 VO FILE IN VIDEO  = {user_video.video.vo_file}')  
    logger.debug('CREATE OR UPDATE 6')
    if call_to_action is not None:
        user_video.video.lower_third_text = call_to_action
    if set_id is not None:
        user_video.set_id = set_id
    if schedule_id is not None:
        user_video.schedule_id = str(schedule_id)
        #schedule = get_video_schedule(schedule_id)
        #if schedule:
        
    user_video.save()
    logger.warning(f'RETURNING VIDEO ID {user_video.fpath}')    
    return user_video,str(user_video.fpath)

def save_user_event(session_id,video_id,logger, published_on):
    logger.debug('ADDING SHARED EVENT FOR VIDEO')
    session = get_user_session(session_id)
    if session is None:
        raise Exception('session not found')
    user = session.user
    video = get_user_video(video_id)
    if video is None:
        raise Exception('video not found')
    
    ret = add_video_event(user,video,event_type='shared',published_on=published_on,logger=logger)
    if ret != 'success':
        raise Exception('ading video event failed')

def get_pronto_id_from_social_id(social_id, platform, logger):

    social_to_pronto = SocialToProntoUser.objects(platform=platform,username=social_id).first()
    if social_to_pronto is not None:
        return social_to_pronto.user.email

    return None

def set_pronto_id_from_social_id(logger, email, social_id, platform):

    user = UserProfile.objects(email=email).first()

    if user is not None:
        try:
            social_to_pronto = SocialToProntoUser(user=user, username=social_id, platform=platform)
            social_to_pronto.save()
            return
        except Exception as e:
            logger.error(f'Saving to Pronto user failed with exception {e}')
            raise Exception(f'Saving to Pronto user failed with exception {e}')
    else:
        logger.error('User not found')
        raise Exception('User not found')
        
def get_session_by_email(email, logger):

    return UserSession.objects(email=email).first()


def disconnect_pronto_id_from_social_id(pronto_id, platform, logger):
    
    user = UserProfile.objects(email=pronto_id).first()
    if user is None:
        logger.error('User not found')
        raise Exception('User not found')

    try:
        social_to_pronto = SocialToProntoUser.objects(platform=platform,user=user).first()
        if social_to_pronto is not None:
            social_to_pronto.delete()

    except Exception as e:
        logger.error(f'Deleting social to pronto user failed with error {e}')
        raise Exception(f'Deleting social to pronto user failed with error {e}')
