import os
import json
import random
import string
import uuid
import time
import google
from google.cloud import storage
from google.cloud import texttospeech
import traceback
import pandas as pd
import hashlib
from dateutil.relativedelta import relativedelta
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
import httplib2
import http.client as httplib
import datetime
import pickle
#from core_lib.event_schemas import *
import validators
from werkzeug.utils import secure_filename
from cerberus import Validator
from core_lib.pronto_conf import *
from core_lib.template_config import templateConfig
import moviepy.editor as mp

def get_all_clips(industry_clips=[],
                  user_clips=[],
                  user_pics=[],
                  extra_clips=[],
                  oem_clips=[],
                  template_name='Bold',
                  duration='30',
                  logger=None):
    num_clips = templateConfig[template_name]['durations'][str(duration)]['num_clips']
    
    logger.info(f'TEMPLATE NAME = {template_name} DURATION = {duration} NUM CLIPS = {num_clips}, LEN OF INDUSTRY CLIPS = {len(industry_clips)}, LENG EXTRA CLIPS = {len(extra_clips)}')
    clips_out = []
    if len(user_clips) >= num_clips:
        clips_out = user_clips[:num_clips]
    elif len(user_clips) == 0 and len(user_pics) >= num_clips:
        clips_out = user_pics[:num_clips]
    elif (len(user_clips)+len(user_pics) >= num_clips):
        clips_out = user_clips + user_pics
        clips_out = clips_out[:num_clips]
    else:
        clips_out = user_clips+user_pics
    clips_out = clips_out[:num_clips]
    remaining_clips = num_clips - len(clips_out)
    logger.debug(f'REMAINING CLIPS = {remaining_clips}')
    if remaining_clips > 0:
        #print(f'remaining = {remaining_clips}')
        num_selected_ind = int(2/3*remaining_clips)
        num_selected_extra = int(1/3*remaining_clips)
        if (num_selected_ind+num_selected_extra) < num_clips:
            num_selected_extra += 1    
        clips_ind = industry_clips[:num_selected_ind]
        clips_extra = extra_clips[:num_selected_extra]
        logger.info(f'NUM SLECTED INDUSTRY CLIPS = {num_selected_ind}, NUM SELECTED EXTRA = {num_selected_extra}')
        clips_out += clips_ind + clips_extra
    if len(oem_clips) > 0:
        clips_out[-1] = oem_clips[0]
    logger.info(f'NUM CLIPS OUT = {len(clips_out)}')
    clips_out = clips_out[:num_clips]
    logger.info(f'NUM CLIPS OUT RETURNED = {len(clips_out)}')
    return clips_out      
    
    
def verify_audio(audio_file_path,logger):
    try:
        logger.info(f'############# READING AUDIO {audio_file_path}')
        mp.AudioFileClip(audio_file_path)
        return "success"
    except Exception as e:
        logger.error(f'unable to read audio file: {audio_file_path}')
        raise Exception("unable to read audio file")
        
def get_pronto_audio_file(logger):
    ret = select_music_files(1,logger)
    if len(ret) > 0:
        try:
            f = ret[0]
            if f.startswith(CLIP_BUCKET):
                s = CLIP_BUCKET+'/'
                f = f.replace(s,'')
            elif f.startswith(LOCAL_VISUAL_BASE):
                f = f.replace(LOCAL_VISUAL_BASE,'')    
            url = get_signed_url(CLIP_BUCKET,f)
            result = {'fpath':ret[0],'url':url}
            return result
        except Exception as e:
            error = f'{e}'
            raise Exception(error)
    raise Exception('no suitable audio file found')
    
def convert_vo_data_to_dict(vo_data):
    clips = []
    for clip in vo_data:
        out_clip = {}
        out_clip['vo_text'] = clip.vo_text
        if clip.vo_file:
            out_clip['vo_file'] = clip.vo_file
        else:
            out_clip['vo_file'] = ''
        out_clip['clips_covered'] = clip.clips_covered
        clips.append(out_clip)
    return clips    

def get_vo_text_from_clips(vo_clips):
    vo_text = ''
    for clip in vo_clips:
        if isinstance(clip,dict):
            vo_text = clip.get('vo_text','')
        else:
            vo_text = clip.vo_text
        vo_text += vo_text
        vo_text += ' '
    return vo_text    

def get_vo_text(event,user_video=None):
    vo_text = event.get('vo_text',None)
    vo_clips = event.get('vo_clips',None)
    if vo_text is None:
        if vo_clips is not None:
            vo_text = get_vo_text_from_clips(vo_clips)
        elif user_video is not None:
            if user_video.video.vo_text and len(user_video.video.vo_text) > 0:
                vo_text = user_video.video.vo_text
            elif user_video.video.vo_data:
                vo_text = get_vo_text_from_clips(user_video.video.vo_data)
    return vo_text            

def get_df_file():
    df_file = DF_NAME
    df_file_key = PRONTO_VISUAL_BASE+df_file
    local_base_path = LOCAL_PRONTO_VISUAL_BASE
    local_df_path = local_base_path+df_file
    if not os.path.exists(local_df_path):
        download_file(bucket,df_file_key,folder_name=None,full_local_path=local_df_path)
    return local_df_path
            
def get_df(library='pronto'):
    if library == 'pronto':
        df_file = DF_NAME
        df_file_key = PRONTO_VISUAL_BASE+df_file
        local_base_path = LOCAL_PRONTO_VISUAL_BASE
        local_df_path = local_base_path+df_file
        if not os.path.exists(local_df_path):
            download_file(bucket,df_file_key,folder_name=None,full_local_path=local_df_path)
    return pd.read_parquet(local_df_path)
    
def get_file_hash(fpath,logger):
    with open(fpath,"rb") as f:
        content = f.read()
        h = hashlib.sha256() # Construct a hash object using our selected hashing algorithm
        h.update(content) # Update the hash using a bytes object
        logger.debug(h.hexdigest()) # Print the hash value as a hex string
        #print(h.digest()) # Print the hash value as a bytes object
        return h.hexdigest()
    
def get_visual_files(visuals,logger):
    out_visuals = []
    for v in visuals:
       if not v.startswith(LOCAL_VISUAL_BASE):
           local_v = LOCAL_VISUAL_BASE+v
           remote_v = v
       else:
           local_v = v
           remote_v = v.replace(LOCAL_VISUAL_BASE,'')
       
       folder,f = get_local_fname_parts(local_v)
       os.makedirs(folder,exist_ok=True)
       logger.info(f'FOLDER = {folder}')
       out_visuals.append(local_v)
       fsize = -1
       if os.path.exists(local_v):
           file_stats = os.stat(local_v)
           fsize = file_stats.st_size
           if fsize == 0:
               logger.info(f'@@@@@@@@@@@@ FILE SIZE of {local_v} IS ZERO @@@@@@@@@@')           
       if not os.path.exists(local_v) or fsize <= 0:    
           try:
               logger.info(f'LOCAL PATH = {local_v} REMOTE PATH = {remote_v}')
               download_file(CLIP_BUCKET,remote_v,folder_name=None,full_local_path=local_v)
           except Exception as e:
               logger.error(f'downloading file {CLIP_BUCKET}/{remote_v} failed with error {e}')
               logger.error(traceback.format_exc())
               out_visuals.remove(local_v)
    return out_visuals

def remove_visual_files(visuals,logger):
    for v in visuals:
       if not v.startswith(LOCAL_VISUAL_BASE):
           local_v = LOCAL_VISUAL_BASE+v
           remote_v = v
       else:
           local_v = v
           remote_v = v.replace(LOCAL_VISUAL_BASE,'')
      
       try:
           if os.path.exists(local_v):
               os.remove(local_v)
           logger.debug(f'REMOVING LOCAL PATH = {local_v} REMOTE PATH = {remote_v}')
           delete_file(CLIP_BUCKET,remote_v)
       except Exception as e:
           logger.debug(f'Removing Remote file {CLIP_BUCKET}/{remote_v} failed with error {e}')
           logger.debug(traceback.format_exc())
    

def get_guest_files(visuals,logger):
    out_visuals = []
    for v in visuals:
       if not v.startswith(GUEST_VIDEO_BASE):
           local_v = GUEST_VIDEO_BASE+v
           remote_v = v
       else:
           local_v = v
           remote_v = v.replace(GUEST_VIDEO_BASE,'')
       out_visuals.append(local_v)
       if not os.path.exists(local_v):    
           try:
               logger.debug(f'LOCAL PATH = {local_v} REMOTE PATH = {remote_v}')
               download_file(TEMP_BUCKET,remote_v,folder_name=None,full_local_path=local_v)
           except Exception as e:
               logger.debug(f'downloading file {TEMP_BUCKET}/{remote_v} failed with error {e}')
               logger.debug(traceback.format_exc())
               out_visuals.remove(local_v)
    return out_visuals
       
def get_user_logo_img(userid,logger):
    fpath = LOCAL_VISUAL_BASE+USER_IMAGE_BASE+userid
    logo = None
    remote_fpath = USER_IMAGE_BASE+userid
    files = get_files_list(CLIP_BUCKET,folder=remote_fpath)
    #files = [e[e.rfind('/')+1:] for e in files]
    files = [e for e in files if 'logo.' in e]
    files = [f.replace(CLIP_BUCKET,'') for f in files]
    logger.debug(f'LOGO FILES RECEIVED FROM REMOTE BUCKET {files}')
    local_files = get_visual_files(files, logger)
    if len(local_files) > 0:
        return local_files[0]
    return None

def remove_user_logo_img(userid,logger):
    fpath = LOCAL_VISUAL_BASE+USER_IMAGE_BASE+userid
    logo = None
    for ext in IMAGE_EXT:
        logo = fpath+'/'+'logo.'+ext
        if os.path.exists(logo):
            os.remove(logo)
            logger.debug(f'REMOVED LOGO {logo}')
    remote_fpath = USER_IMAGE_BASE+userid
    files = get_files_list(CLIP_BUCKET,folder=remote_fpath)
    #files = [e[e.rfind('/')+1:] for e in files]
    files = [e for e in files if 'logo.' in e]
    files = [f.replace(CLIP_BUCKET,'') for f in files]
    logger.debug(f'LOGO FILES RECEIVED FROM REMOTE BUCKET {files}')
    remove_visual_files(files,logger)
             

def get_guest_logo_img(userid):
    fpath = GUEST_VIDEO_BASE+userid
    if os.path.exists(fpath):
        files = os.listdir(fpath)
        logo = [e for e in files if 'logo' in e]
        if len(logo) > 0:
            return fpath+'/'+logo[0]
    return None      


def validate_url(field,value,error):
    valid = validators.url(value)
    if valid is False:
        error(field, ' is invalid')      

def validate_date(field,value,error):
    try:
        datetime.datetime.strptime(value,'%Y-%m-%d')
    except Exception as e:
        error(field, ' is invalid')  
        
def get_visual_type(ext):
    if ext in IMAGE_EXT:
        return 'image'
    elif ext in VIDEO_EXT:
        return 'clip'
    elif ext in AUDIO_EXT:
        return 'audio'
    return 'unknown_visual_type'
    
def error_response(error_dict=None,error_type='ValidationError',msg=None):
    result = {}
    errorMessage = ''
    if error_type == 'ValidationError':
        if error_dict is not None:
            error_field = list(error_dict.keys())[0]
            errorMessage = f'{error_field} not validated,'
    if msg is not None:
        errorMessage = errorMessage+' '+msg
    result['errorMessage'] = errorMessage
    result["errorType"] = error_type
    return result
        
def validate_request(data,schema):
    v = Validator(schema)
    v.allow_unknown = True
    if not v.validate(data):
        return False,v.errors
    return True,None

def generate_random_string(N=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=N))

def get_event_hash(event):
    json_dump = json.dumps(event,sort_keys=True).encode("utf-8")
    hash_code = hashlib.md5(json_dump).hexdigest()
    return hash_code
    
def is_duplicate_event(event,pubsub,logger):
    hash_code = get_event_hash(event)
    print(f'DUPLICATE CHECKER: HASH = {hash_code}')
    prev_event = pubsub.kv_store.get(hash_code,logger)
    if prev_event is not None:
        print(f'HASH CODE is {hash_code}, timestamp = {prev_event}')
        return True
    return False
    

def publish_progress_event(event,connection,message,pubsub):
    if connection is not None and isinstance(connection,str) and len(connection) > 0:
        result = {}
        result['ws_connection'] = connection
        result['status'] = 'in_progress'
        result['message'] = message
        pubsub.publish(result,event)
 
def publish_error_event(event,connection,pubsub,errorMessage='',errorType='InternalServerError'):
    if connection is not None and isinstance(connection,str) and len(connection) > 0:
        result = {}
        result['ws_connection'] = connection
        result['status'] = 'error'
        result['errorType'] = errorType
        result['erroMessage'] = errorMessage
        pubsub.publish(result,event)
        
def select_worker(event_prefix,next_worker,max_workers):
     event = event_prefix+str(next_worker+1)
     next_ = (next_worker + 1) % max_workers
     return event,next_  
        
def find_nth(s,sub_str,n):
    val = -1
    for i in range(0, n): 
        val = s.find(sub_str, val + 1) 
    return val

def correct_path(x):
    x = [e.replace('//','/') for e in x] 
    for i in range(len(x)):
        if not x[i].startswith('/opt/') and not x[i].startswith('/tmp/') :
            o = '/opt/'+x[i]
            x[i] = o
    return x

def get_config(logger=None):
    main_bucket = MAIN_BUCKET
    config_file = os.environ.get('CONFIG_FILE')
    local_conf_path = os.environ.get('LOCAL_CONFIG_PATH')
    if local_conf_path[-1] != '/':
        local_conf_path = local_conf_path + '/'
    local_conf_file = local_conf_path+config_file
    if os.path.exists(local_conf_file):
        try:
            with open(local_conf_file,'r') as conf:
                return json.load(conf)
        except Exception as e:
            print(f'error {e} reading local config file: {local_conf_file}')
            print(traceback.format_exc())
            return None

    if logger is not None:
        logger.info(f'******* main bucket = {main_bucket}, config_file = {config_file}')
    else:
        print(f'******* main bucket = {main_bucket}, config_file = {config_file}')
    try:
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(main_bucket)
        blob = bucket.get_blob(config_file)
        return json.loads(blob.download_as_string())
    except Exception as e:
        print(f'error getting config file from bucket {e}')
        print(traceback.format_exc())
        return None


def create_folder(bucket,folder_name):
    raise NotImplementedError('No Need to implement this for GS')

def delete_folder(bucket_name,folder_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=folder_name)
    for blob in blobs:
        blob.delete()
    
def get_file_size(fpath):
    return os.stat(fpath).st_size

def file_exists(bucket, fpath):
   client = storage.Client()
   bucket = client.get_bucket(bucket)
   blob = bucket.blob(fpath)
   return blob.exists()

def upload_file(bucket,folder,source_file, dest_file=None,logger=None):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket)
    if source_file.rfind('/') >= 0:
        source_fname = source_file[source_file.rfind('/')+1:]
    else:
        source_fname = source_file

    if dest_file is None:
        dest = source_fname
    else:
        dest = dest_file

    if folder is not None:
        obj = f'{folder}/{dest}'
    else:
        obj = dest
    
    blob = bucket.blob(obj)
    if logger:
        logger.debug(f'UPLOADING {bucket}/{obj}')
    else:
        print(f'UPLOADING {bucket}/{obj}')
        
    blob.upload_from_filename(source_file)

       
def download_file(bucket,filename,folder_name=None,local_path=LOCAL_PRONTO_VISUAL_BASE,full_local_path=None):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket)
    
    if folder_name is not None:
       if folder_name[-1] == '/':
                f = folder_name+filename
       else:
                f = folder_name+'/'+filename
    else:
       f = filename
    
    if full_local_path is not None:
        local_f = full_local_path
    else:
        if local_path[-1] == '/':
                local_f = local_path+filename
        else:
           local_f = local_path+'/'+filename

    print(f'Downloading {f} to {local_f}')
    blob = bucket.blob(f)
    blob.download_to_filename(local_f)
    return local_f

def get_signed_url(bucket,obj,expires_after_seconds=3600):
    client = storage.Client()
    bucket = client.get_bucket(bucket)
    blob = storage.Blob(obj, bucket)
    expiration_time = int(time.time() + expires_after_seconds)
    url = blob.generate_signed_url(expiration_time)
    return url

def get_upload_signed_url(bucket_name, blob_name,expires_after_seconds=3600,content_type='application/octet-stream',logger=None):
    """Generates a v4 signed URL for uploading a blob using HTTP PUT.

    Note that this method requires a service account key file. You can not use
    this if you are using Application Default Credentials from Google Compute
    Engine or from the Google Cloud SDK.
    """
    # bucket_name = 'your-bucket-name'
    # blob_name = 'your-object-name'

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version="v4",
        # This URL is valid for 15 minutes
        expiration=datetime.timedelta(seconds=expires_after_seconds),
        # Allow PUT requests using this URL.
        method="PUT",
        content_type=content_type
    )

    #logger.debug("Generated PUT signed URL:")
    #logger.debug(url)
    return url


def get_files_list(bucket_name,folder=None):
    files = []
    storage_client = storage.Client()
    for blob in storage_client.list_blobs(bucket_name, prefix=folder):
        f = blob.name
        if f[-1] == '/':
            continue
        files.append(f)
    return files

def convert_to_speech(text,out_path,voice_name='en-US-Wavenet-F',voice_gender='neutral',speaking_rate=0.9):
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text+'!')
    if voice_gender.lower() == 'female':
        gender = texttospeech.SsmlVoiceGender.FEMALE
    elif voice_gender.lower() == 'male':
        gender = texttospeech.SsmlVoiceGender.MALE
    else:
        gender = texttospeech.SsmlVoiceGender.NEUTRAL     
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name=voice_name,
        ssml_gender=gender)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=speaking_rate
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with open(out_path, "wb") as out:
        out.write(response.audio_content)  
        
def select_extra_files(df_path,num,mood,industry):
    df = pd.read_parquet(df_path)
    df2 = df[df['mood'].str.lower() == mood.lower()]
    df2 = df2[df2['business_type'].str.lower() == industry.lower()]
    if len(df2) > num:
        clips = df2.sample(num)['extra_clips'].values
    else:
        clips = df2['extra_clips'].values
    return list(clips)

def select_music_files(num,logger):
    files = get_files_list(CLIP_BUCKET,folder=BASE_MUSIC_PATH)
    files = [e for e in files if '.mp3' in e]
    files = [f[f.rfind('/')+1:] for f in files]
    logger.debug(f'FILES LIST = {files}')
    os.makedirs(LOCAL_BASE_MUSIC_PATH,exist_ok=True)
    if len(files) > num:
        selected = random.sample(files,num)
    else:
        selected = files
    selected = [LOCAL_BASE_MUSIC_PATH+f for f in selected]
    return selected
    

def select_files(bucket,folder,subfolders,num_clips,local_path='/tmp/'):
    clips = []
    print(f'$$$$ BUCKET = {bucket}, FOLDER={folder}, SUBFOLDERS={subfolders},NUMCLIPS={num_clips}')
    for fldr in subfolders:
        fpath = folder+'/'+fldr+'/'
        #print(f'*****fpath={fpath}')
        flist = get_files_list(bucket,fpath)
        clips += flist
        #print(f'$$$$$ FILES LIST AFTER DOWNLOAD = {clips}')

    #print(f'$$$$ LENGTH OF CLIPS LIST = {len(clips)}')
    selected = []
    '''
    while True:
    #for i in range(len(clips)*3):
        clip_idx = random.randint(0,len(clips)-1)
        if clips[clip_idx][-1] != '/' and clips[clip_idx] not in selected:
            selected.append(clips[clip_idx])
            if len(selected) == num_clips:
                break
    selected = selected[:num_clips]
    '''
    clips = [clip for clip in clips if clip[-1] != '/']
    if len(clips) > num_clips:
        selected = random.sample(clips,num_clips)
    else:
        selected = clips
    #print(f'$$$$ {os.getpid()} LENGTH OF SELECTED = {len(selected)}')
    #print(f'$$$$$$ SELECTED = {selected}')
    return selected

def download_files(flist,local_path=LOCAL_PRONTO_VISUAL_BASE):
    #print('downloading files')
    outlist = []
    #print(f'DOWNLOAD FILES = {flist}')
    for f in flist:
        bucket = f[:f.find('/')]
        filename_ = f[f.rfind('/')+1:]
        folder_ = f[f.find('/')+1:f.rfind('/')+1]
        print(f'DOWNLOAD FILES: FOLDER = {folder_}')
        if len(filename_) > 0:
            if len(folder_) > 0:
                local_file = local_path+folder_+'/'+filename_
            else:
                local_file = local_path+filename_
            print(f'DOWNLOAD FILES: LOCAL FILE PATH = {local_file} ')
            if not os.path.isfile(local_file):
                print(f'$$$$ {os.getpid()} DOWNLOADING {filename_}')
                print(download_file(bucket,filename_,folder_name=folder_,local_path=local_path))
            else:
                #print('ELSE PART')
                print(f'{os.getpid()} ####file {local_file} exists')
                #print('AFTER PRINT')
            outlist.append(local_file)
        #else:
        #    print(f'SKIPPING {bucket}/{folder_}')
    return outlist

def get_fname_parts(fpath):
    bucket = fpath[:fpath.find('/')]
    folder = fpath[fpath.find('/')+1:]
    folder = folder[:folder.rfind('/')]
    if folder.find('/') >=0:
        folder = folder[:folder.find('/')]
    fname = fpath[fpath.rfind('/')+1:]
    return bucket,folder,fname

def get_local_fname_parts(fpath):
    folder = fpath[:fpath.rfind('/')+1]
    fname = fpath[fpath.rfind('/')+1:]
    return folder,fname
    
def get_data(bucket,filename,folder_name=None):
     raise NotImplementedError("Use download_file instead")

def put_data(data,bucket,filename,folder_name=None):
    raise NotImplementedError("Use upload_file instead")
       
    
def delete_file(bucket,filename,folder_name=None):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket)
    if folder_name is not None:
        f = f'{folder_name}/{filename}'
    else:
        f = filename
    blob = bucket.blob(f)
    return blob.delete()


def get_db_secrets():
    username = DB_USER
    #print(f'USER NAME = {username}')
    password = DB_PASS
    return username,password

def create_guest_folders(userid,logger=None):
    os.makedirs(GUEST_VIDEO_BASE+userid+'/',exist_ok=True)
    
    
def create_user_folders(email,logger=None):
    user_video_path = LOCAL_VISUAL_BASE+USER_VIDEO_BASE
    user_video_path = user_video_path+email+'/'
    user_image_path = LOCAL_VISUAL_BASE+USER_IMAGE_BASE+email+'/'
    user_clip_path = LOCAL_VISUAL_BASE+USER_CLIP_BASE+email+'/'
    user_audio_path =  LOCAL_VISUAL_BASE+USER_AUDIO_BASE+email+'/'
    user_temp_files_path = LOCAL_VISUAL_BASE+USER_TEMP_FILES_BASE+email+'/'
    if logger is not None:
        logger.debug(f'USER VIDEO PATH = {user_video_path}, USER IMAGE PATH = {user_image_path}, USER CLIP PATH = {user_clip_path}')
    os.makedirs(user_video_path,exist_ok=True)
    os.makedirs(user_image_path,exist_ok=True)
    os.makedirs(user_clip_path,exist_ok=True)
    os.makedirs(user_audio_path,exist_ok=True)
    os.makedirs(user_temp_files_path,exist_ok=True)
    os.makedirs(GUEST_VIDEO_BASE,exist_ok=True)

def create_pronto_folders(industry_buckets,extra_buckets,oems,logger=None):
    os.makedirs(LOCAL_PRONTO_VISUAL_BASE,exist_ok=True)
    os.makedirs(LOCAL_PRONTO_INDUSTRY_BASE,exist_ok=True)
    os.makedirs(LOCAL_PRONTO_EXTRA_BASE,exist_ok=True)
    os.makedirs(LOCAL_TEMPLATE_PREVIEW_PATH,exist_ok=True)
    os.makedirs(LOCAL_FONTS_PATH,exist_ok=True)
    os.makedirs(LOCAL_TEMPLATE_FONTS_PATH,exist_ok=True)
    os.makedirs(LOCAL_FLASK_STATIC_PATH,exist_ok=True)
    
    for bucket in industry_buckets:
        os.makedirs(LOCAL_PRONTO_INDUSTRY_BASE+bucket,exist_ok=True)
        if len(oems[bucket]) > 0:
            for oem in oems[bucket]:
                os.makedirs(LOCAL_PRONTO_INDUSTRY_BASE+bucket+'/oem_clips/'+oem,exist_ok=True)
            
            
    for bucket in extra_buckets:
        os.makedirs(LOCAL_PRONTO_EXTRA_BASE+bucket,exist_ok=True)
    
def create_local_folder(root_path,folder_name):
    if folder_name[-1] == '/':
        f = root_path+folder_name
    else:
        f = root_path+'/'+folder_name
    os.makedirs(f,exist_ok = True)

def get_path_components(p):
    bucket = p[:p.find('/')]
    folder = p[p.find('/')+1:p.rfind('/')]
    f = p[p.rfind('/')+1:]
    return bucket,folder,f

def get_file_extension(fname):
    return fname[fname.rfind('.')+1:]
def get_filename(fname):
    if '/' not in fname:
        return fname
    return fname[fname.rfind('/')+1:]

def is_filename_present(f):
    fname = get_filename(f)
    if len(fname) == 0:
        return False
    return True
def is_valid_extension(f):
    ext = get_file_extension(f)
    if ext not in VIDEO_EXT and ext not in IMAGE_EXT and ext not in AUDIO_EXT:
        return False
    return True

def create_user_visual_path(fname,email,is_logo=False):
    ext = get_file_extension(fname)
    if is_logo:
        f = 'logo.'+ext
    else:
        f = get_filename(fname)
    
    '''
    if '/videos/' in fname:
        return USER_VIDEO_BASE+email+'/'+f,ext
    if '/clips/' in fname:
        return USER_CLIP_BASE+email+'/'+f,ext
    elif '/images/' in fname:
        return USER_IMAGE_BASE+email+'/'+f, ext
    else:
    ''' 
    if '/videos/' in fname:
        return USER_VIDEO_BASE+email+'/'+f,ext
        
    if ext in AUDIO_EXT:
         return USER_AUDIO_BASE+email+'/'+f,ext
    if ext in IMAGE_EXT:
         return USER_IMAGE_BASE+email+'/'+f, ext
    elif ext in VIDEO_EXT:
         return USER_CLIP_BASE+email+'/'+f,ext
    else:
         return '', None

def create_guest_visual_path(fname,userid,is_logo=False):
    ext = get_file_extension(fname)
    f = get_filename(fname)
    return userid+'/'+f, ext
        
    
def create_user_local_visual_path(fname,email,is_logo=False):
    ext = get_file_extension(fname)
    f = get_filename(fname)
    if '/videos/' in fname:
        return LOCAL_VISUAL_BASE+USER_VIDEO_BASE+email+'/'+f,ext
    if is_logo:
        f = 'logo.'+ext
    if '/clips/' in fname:
        return LOCAL_VISUAL_BASE+USER_CLIP_BASE+email+'/'+f,ext
    elif '/images/' in fname:
        return LOCAL_VISUAL_BASE+USER_IMAGE_BASE+email+'/'+f, ext
    else:
        if ext in AUDIO_EXT:
            return LOCAL_VISUAL_BASE+USER_AUDIO_BASE+email+'/'+f, ext
        if ext in IMAGE_EXT:
            return LOCAL_VISUAL_BASE+USER_IMAGE_BASE+email+'/'+f, ext
        elif ext in VIDEO_EXT:
            return LOCAL_VISUAL_BASE+USER_CLIP_BASE+email+'/'+f,ext
        else:
            return '',None
    

def get_user_file_path(fpath):
    fpath = fpath.replace(LOCAL_VISUAL_BASE,'')
    fpath = fpath.replace(CLIP_BUCKET+'/','')
    return fpath

def get_guest_file_path(fpath):
    fpath = fpath.replace(LOCAL_VISUAL_BASE,'')
    fpath = fpath.replace(TEMP_BUCKET+'/','')
    return TEMP_BUCKET+'/'+fpath

def generate_file_name(fname,folder,guest=False):
    video_name = fname[:fname.rfind('.')]
    video_ext = fname[fname.rfind('.'):]
    video_new_name = video_name+'_'+str(uuid.uuid1().hex[:12])
    if guest:
        return TEMP_BUCKET+'/'+folder+'/'+video_new_name+video_ext
    return CLIP_BUCKET+'/'+folder+'/'+video_new_name+video_ext

    
def get_user_video_for_upload(video_id,email,logger):
    filekey,_ = create_user_visual_path(video_id,email)
    local_fpath,_ = create_user_local_visual_path(video_id,email)
    logger.debug(f'filekey = {filekey}')
    logger.debug(f'local fpath = {local_fpath}')
    if not os.path.exists(local_fpath):
        if file_exists(CLIP_BUCKET,filekey):
            logger.debug(f'FILE KEY {filekey} exists')
            try:
                download_file(CLIP_BUCKET,filekey,folder_name=None,full_local_path=local_fpath)
            except Exception as e:
                logger.error(f'downloading file {video_id} failed with error {e}')
                logger.error(traceback.format_exc())
                return None,None,f'downloading file {video_id} failed with error {e}'
               
        else:
            return None,None,f'file {video_id} not found locally or in cloud storage'
    return filekey,local_fpath,''
           

    