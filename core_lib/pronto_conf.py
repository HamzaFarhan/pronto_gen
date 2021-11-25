#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  3 08:45:46 2021

@author: farhan
"""
import numpy as np
import os

deployment_type = os.environ.get('DEPLOYMENT_TYPE','PRODUCTION')
if deployment_type == 'PRODUCTION':
    BASE_URL = 'https://getpronto.ai/'
    DB_NAME = 'prontodb'
elif deployment_type == 'STAGING':
    BASE_URL = 'https://staging.getpronto.ai/'
    DB_NAME = 'prontodb_staging'
elif deployment_type == 'BETA':
    BASE_URL = 'https://getpronto.ai/'
    DB_NAME = 'prontodb_beta'    
elif deployment_type == 'PROD':
    BASE_URL = 'https://getpronto.ai/'
    DB_NAME = 'prontodb_beta'
elif deployment_type == 'WLABEL':
    BASE_URL = 'https://whitelabel.getpronto.ai/'
    DB_NAME = 'prontodb_wl'   
else:
    BASE_URL = 'https://dev.getpronto.ai/'
    #BASE_URL = 'http://localhost:4200/'
    DB_NAME = 'prontodb_staging'
    
    
DB_HOST = os.environ.get('DB_HOST','127.0.0.1')
DB_PORT = int(os.environ.get('DB_PORT',27017))
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')

PRONTO_CERT_FILE =  os.environ.get('PRONTO_CERT_FILE',None) 
PRONTO_KEY_FILE = os.environ.get('PRONTO_KEY_FILE',None) 
CERT_LOCATION = os.environ.get('CERT_LOCATION','/opt/certs') 

WEBSITE_URL = BASE_URL
WEBSITE_BASE = '/'
WEBSITE_SIGNIN = '/pages/login'
WEBSITE_SIGNUP = '/pages/join'
WEBSITE_SUBSCRIPTION_SUCCESS = '/pages/subscription_success'
WEBSITE_SUBSCRIPTION_FAILED = '/pages/subscription_cancel'
WEBSITE_RETURN_FROM_BILLING = '/panel/welcome'

 
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY",None)
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY",None)
STRIPE_PRICE_ID_BASIC = os.environ.get("STRIPE_PRICE_ID_BASIC",None)
STRIPE_PRICE_ID_BP = os.environ.get("STRIPE_PRICE_ID_BP",None)
STRIPE_SIGNUP_COUPON_NAME = os.environ.get('STRIPE_SIGNUP_COUPON_NAME',None)
STRIPE_ENDPOINT_SECRET= os.environ.get("STRIPE_ENDPOINT_SECRET",None)
STRIPE_SIGNUP_COUPON_NAME = os.environ.get('STRIPE_SIGNUP_COUPON_NAME',None)
BLOCK_USER_ON_PAYMENT_FAILED = True

stripe_keys = {
    "secret_key": STRIPE_SECRET_KEY,
    "publishable_key": STRIPE_PUBLISHABLE_KEY,
    "plan_basic": STRIPE_PRICE_ID_BASIC,
    "plan_bp":    STRIPE_PRICE_ID_BP,
    "endpoint_secret": STRIPE_ENDPOINT_SECRET
}

video_quotas = {
                  "plan_basic": int(os.environ.get('PLAN_BASIC_QUOTA',4)),
                  "plan_bp": int(os.environ.get('PLAN_BP_QUOTA',20)),
                  "plan_basic_admin": int(os.environ.get('PLAN_BASIC_ADMIN_QUOTA',4)) ,
                  "plan_bp_admin": int(os.environ.get('PLAN_BP_ADMIN_QUOTA',20)), 
               } 

#ALLOW_PRE_EXISTING_USER_CREATION = True
ALLOW_PRE_EXISTING_USER_CREATION = int(os.environ.get('ALLOW_PRE_EXISTING_USER_CREATION',1))

if ALLOW_PRE_EXISTING_USER_CREATION == 1:
    ALLOW_PRE_EXISTING_USER_CREATION = True
else:
    ALLOW_PRE_EXISTING_USER_CREATION = False
    
DAYS_TO_WAIT_FOR_DELETED_USERS = 0    

CLIP_BUCKET = 'pronto-clip-bucket'
MAIN_BUCKET = 'pronto-videogen-master'
TEMP_BUCKET = 'pronto-videogen-temp1'
CLIP_SEARCH_STRATEGY = 'text'
#TRANSFORMER_MODEL_NAME = 'sbert.net_models_distilbert-base-nli-stsb-mean-tokens'
#TRANSFORMER_MODEL_NAME = 'paraphrase-MiniLM-L6-v2'
TRANSFORMER_MODEL_NAME = 'paraphrase-mpnet-base-v2'
USE_SENT_TO_VECT_MODEL = True

LOCAL_VISUAL_BASE = '/opt/'

USER_VISUAL_BASE = 'user_visuals/'
USER_CLIP_BASE = USER_VISUAL_BASE+'clips/'
USER_IMAGE_BASE = USER_VISUAL_BASE+'images/'
USER_VIDEO_BASE = USER_VISUAL_BASE+'videos/'
USER_AUDIO_BASE = USER_VISUAL_BASE+'audios/'
USER_TEMP_FILES_BASE = USER_VISUAL_BASE+'temp_files/'

GUEST_VIDEO_BASE = '/tmp/guest/'
PRONTO_VISUAL_BASE = 'pronto_visuals/'
LOCAL_PRONTO_VISUAL_BASE = LOCAL_VISUAL_BASE+PRONTO_VISUAL_BASE
LOCAL_TEMPLATE_PREVIEW_PATH = LOCAL_PRONTO_VISUAL_BASE+'templates/previews/'

LOCAL_USER_TEMP_FILES_BASE = LOCAL_VISUAL_BASE+USER_VISUAL_BASE+'temp_files/'
LOCAL_PRONTO_INDUSTRY_BASE = LOCAL_PRONTO_VISUAL_BASE+'industries/'
LOCAL_PRONTO_EXTRA_BASE = LOCAL_PRONTO_VISUAL_BASE+'extra_clips/'
LOCAL_OEM_VISUAL_BASE = LOCAL_VISUAL_BASE+'oem_visuals/'
LOCAL_FONTS_PATH = '/usr/local/share/fonts/'
LOCAL_TEMPLATE_FONTS_PATH = '/usr/local/share/fonts/template_fonts/'

LOCAL_FLASK_STATIC_PATH = '/opt/static'
DF_NAME = 'new_df.parq'
OEM_DF_NAME = DF_NAME
MUSIC_DF_NAME = 'df_music_files.parq'
FONTS_DF_NAME = 'df_fonts.parquet'

BASE_MUSIC_PATH = PRONTO_VISUAL_BASE+'music_files/'
LOCAL_BASE_MUSIC_PATH = LOCAL_PRONTO_VISUAL_BASE+'music_files/'
LOCAL_BASE_FONTS_PATH = '/usr/local/share/fonts/'

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT',6379))

VIDEO_EXT = ['mp4','mov','MOV','MP4','avi']
IMAGE_EXT = ['png','jpeg','jpg','JPG','JPEG','PNG']
AUDIO_EXT = ['mp3']
IMAGE_SIZE_THRESH = 250
BACKGROUND_MUSIC_VOLUME = 0.2
FFMPEG_PATH = os.environ.get('FFMPEG_PATH','/usr/bin/ffmpeg')
PROMO_LEN_DICT = {
                   '15': {'middle_len':0, 'num_vids':2, 'num_extra':1, 'num_pics':1},
             
                   '30': {'middle_len':3, 'num_vids':4, 'num_extra':1, 'num_pics':2},
             
                   '60': {'middle_len':3, 'num_vids':6, 'num_extra':2, 'num_pics':4},
                 }
PRONTO_MOOD_LIST = ['energized','relaxed','hopeful','calm','excited','upbeat']
PRONTO_SUPPORTED_SOCIAL_LIST = ['youtube','facebook','twitter','instagram','linkedin']

PRONTO_VIDEO_TIMEOUTS = {
                     '15': 45,
                     '30': 75,
                     '60': 90
                  }
PRONTO_VIDEO_PARAMS = {
                         'bitrate': str(np.power(10,7)),
                         'fps': 25,
                         'threads': 8
                      }

VO_VOICES = {
            'voice1': {'voice_name':'en-US-Wavenet-A','gender':'male','cps':14,'sample_voice':"pronto_visuals/sample_voices/voice1_sample_male.mp3"},
            'voice2': {'voice_name':'en-US-Wavenet-B','gender':'male','cps':13,'sample_voice':"pronto_visuals/sample_voices/voice2_sample_male.mp3"},
            'voice3': {'voice_name':'en-US-Wavenet-D','gender':'male','cps':14,'sample_voice':"pronto_visuals/sample_voices/voice3_sample_male.mp3"},
            'voice4': {'voice_name':'en-US-Wavenet-I','gender':'male','cps':15,'sample_voice':"pronto_visuals/sample_voices/voice4_sample_male.mp3"},
            'voice5': {'voice_name':'en-US-Wavenet-J','gender':'male','cps':15,'sample_voice':"pronto_visuals/sample_voices/voice5_sample_male.mp3"},
            'voice6': {'voice_name':'en-US-Wavenet-C','gender':'female','cps':14,'sample_voice':"pronto_visuals/sample_voices/voice6_sample_female.mp3"},
            'voice7': {'voice_name':'en-US-Wavenet-E','gender':'female','cps':14,'sample_voice':"pronto_visuals/sample_voices/voice7_sample_female.mp3"},
            'voice8': {'voice_name':'en-US-Wavenet-F','gender':'female','cps':14,'sample_voice':"pronto_visuals/sample_voices/voice8_sample_female.mp3"},
            'voice9': {'voice_name':'en-US-Wavenet-G','gender':'female','cps':15,'sample_voice':"pronto_visuals/sample_voices/voice9_sample_female.mp3"},
            'voice10':{'voice_name':'en-US-Wavenet-H','gender':'female','cps':15,'sample_voice':"pronto_visuals/sample_voices/voice10_sample_female.mp3"}

         }

PRONTO_MIN_IMAGE_RES = 512

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY',None)
WELCOME_EMAIL_SENDER = 'contact@getpronto.ai'
PASSWORD_RESET_EMAIL_SENDER = 'contact@getpronto.ai'
PAYMENT_EMAIL_SENDER = 'contact@getpronto.ai'
SUPPORT_EMAIL_SENDER = 'contact@getpronto.ai'
SUPPORTED_SOCIAL_PLATFORMS = ['youtube','facebook','instagram','twitter','hubspot','linkedin','shopify','hootsuite','']

GOOGLE_CLIENT_SECRETS_FILE = os.environ.get('GOOGLE_CLIENT_SECRETS_FILE','/opt/creds/client_secret_1000874121157-q6rsr2cf6k0b9psq9m56lk1k3lg82l50.apps.googleusercontent.com.json')
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_CALLBACK_URL = os.environ.get('GOOGLE_CALLBACK_URL','https://dev.getpronto.ai/app/google_signin/callback')
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
     
YOUTUBE_CALLBACK_URL = os.environ.get('YOUTUBE_CALLBACK_URL','https://dev.getpronto.ai/app/youtube_upload/callback')
YOUTUBE_SUCCESS_URL = 'panel/yt-share-success'
YOUTUBE_FAILURE_URL = 'panel/yt-share-failed'
YOUTUBE_ANALYTICS_CALLBACK_URL = os.environ.get('YOUTUBE_ANALYTICS_CALLBACK_URL','https://dev.getpronto.ai/app/youtube_analytics/callback')
YOUTUBE_ANALYTICS_SUCCESS_URL = 'panel/yt-analytics-success'
YOUTUBE_ANALYTICS_FAILURE_URL = 'panel/yt-analytics-failed'

FB_CREDS_FILE = 'fb_access_token.json'
FB_GRAPH_BASE_URL = 'https://graph.facebook.com/'
FB_VIDEO_BASE_URL = 'https://graph-video.facebook.com/v9.0/'
FB_SUCCESS_URL = 'panel/fb-share-success'
FB_FAILURE_URL = 'panel/fb-share-failed'
FB_CALLBACK_URL = os.environ.get("FB_CALLBACK_URL",'https://dev.getpronto.ai/app/fb_signin/callback')
FB_CLIENT_ID = os.environ.get('FB_CLIENT_ID')
FB_CLIENT_SECRET = os.environ.get('FB_CLIENT_SECRET')
FB_AUTH_BASE_URL = 'https://www.facebook.com/v9.0/dialog/oauth'
FB_TOKEN_URL = 'https://graph.facebook.com/v9.0/oauth/access_token'

HUBSPOT_CLIENT_ID = os.environ.get('HUBSPOT_CLIENT_ID',None)
HUBSPOT_CLIENT_SECRET = os.environ.get('HUBSPOT_CLIENT_SECRET',None)
HUBSPOT_CALLBACK_URL = os.environ.get('HUBSPOT_CALLBACK_URL','https://dev.getpronto.ai/app/hubspot_upload/callback')
HUBSPOT_SUCCESS_URL = 'panel/hs-share-success'
HUBSPOT_FAILURE_URL = 'panel/hs-share-failed'


LINKEDIN_CLIENT_ID = os.environ.get('LINKEDIN_CLIENT_ID',None)
LINKEDIN_CLIENT_SECRET = os.environ.get('LINKEDIN_CLIENT_SECRET',None)
LINKEDIN_CALLBACK_URL = os.environ.get('LINKEDIN_CALLBACK_URL','https://dev.getpronto.ai/app/linkedin_upload/callback')
LINKEDIN_AUTH_CALLBACK_URL = os.environ.get('LINKEDIN_CALLBACK_URL','https://dev.getpronto.ai/app/linkedin_signin/callback')
LINKEDIN_AUTHORIZATION_URL = 'https://www.linkedin.com/oauth/v2/authorization'
LINKEDIN_TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
LINKEDIN_SCOPE = 'r_liteprofile%20r_emailaddress%20w_member_social'
LINKEDIN_SUCCESS_URL = 'panel/linkedin-share-success'
LINKEDIN_FAILURE_URL = 'panel/linkedin-share-failed'
  
