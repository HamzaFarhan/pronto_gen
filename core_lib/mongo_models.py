from mongoengine import *
import os
import datetime
from core_lib.pronto_conf import *

class Embedding(Document):
    word = StringField(max_length=64,required=True,
                       primary_key=True)
    vectors = ListField(FloatField())
    indexes: [
                 'word',  # hashed index
             ]
    #meta = {'db_alias': 'testdb'}

class PaymentInfo(DynamicEmbeddedDocument):
    cc_num = StringField(max_length=20,required=True)
    cc_cvv = IntField(required=True)
    cc_expires_year = IntField(required=True)
    cc_expires_month = IntField(required=True)
    
class BillingInfo(EmbeddedDocument):
    cc_info = EmbeddedDocumentField(PaymentInfo,required=True)
    plan_id = StringField(max_length=50,required=True)



class Address(DynamicEmbeddedDocument):
    line1 = StringField(max_length=512,default='')
    line2 = StringField(max_length=512,default='')
    city =  StringField(max_length=128,default='')
    state = StringField(max_length=64,default='')
    country = StringField(max_length=8,default='')
    postal_code = StringField(max_length=6,default='') 
    

class OEM(DynamicDocument):
    name = StringField(max_length=128,required=True,primary_key=True)
    industry = StringField(max_length=128,default='')
    hex_color = StringField(max_length=32,default='')

                      
class VisualBucket(DynamicDocument):
    name = StringField(max_length=128,required=True,primary_key=True)
    category = StringField(max_length=128,choices=['industry','industry_oem','extra'],default='industry')
    industry = StringField(max_length=64,default='')
    bt =       StringField(max_length=64,default='')
    meta = {'auto_create_index': False,
            'indexes': [{'fields': ['category','bt']}]
           }

class VideoTemplate(DynamicDocument):
    name = StringField(max_length=128,required=True,primary_key=True)
    text_fields = ListField(StringField(max_length=128),default=list)
    
class BusinessType(DynamicDocument):
    name = StringField(max_length=128,required=True,primary_key=True)
    extra_buckets = ListField(ReferenceField(VisualBucket),default=list)
    
    
class BusinessInfo(DynamicEmbeddedDocument):
    business_type = StringField(max_length=32,default='')
    industry = StringField(max_length=32,default='')
    company_name = StringField(max_length=256,default='')
    greeting = StringField(max_length=256,default='')
    moods = ListField(StringField(max_length=30,choices= PRONTO_MOOD_LIST),default=list) 
    address = EmbeddedDocumentField(Address,default=None)
    url = StringField(max_length=1024,default='')
    phone = StringField(max_length=32,default='')
    email = StringField(max_length=128,default='')
    images = ListField(StringField(max_length=512), default=list)
    #people_images = ListField(StringField(), default=list)
    colors = ListField(StringField(max_length=32),default=list)
    key_terms = ListField(StringField(max_length=512), default=list)
    logo_file = StringField(max_length=1024,default=str)
    approved_oem_list =ListField(ReferenceField(OEM),default=list)
    approved_bucket_list =ListField(ReferenceField(VisualBucket),default=list)

   
class UserProfile(DynamicDocument):
    created = DateTimeField(default=datetime.datetime.utcnow())
    email = StringField(max_length=128,required=True,primary_key=True)
    username = StringField(max_length=128)
    first_name = StringField(max_length=128)
    last_name = StringField(max_length=128)
    role = StringField(max_length=128,choices=['user','super_admin','admin'],default='user')
    p_hash = StringField(max_length=256,default='')
    business_info = EmbeddedDocumentField(BusinessInfo)
    status = StringField(max_length=32,choices=['unconfirmed','pending_subscription','active','blocked','cancelled','paused','deleted'],default='unconfirmed')
    subscription_plan_id = StringField(max_length=512,default=str)
    subscription_customer_id = StringField(max_length=512,default=str)
    subscription_id = StringField(max_length=512,default=str)
    plan_name = StringField(max_length=128,default=str)
    last_billing_date = DateTimeField(default=None)
    trial_start_date = DateTimeField(default=None)
    trial_end_date = DateTimeField(default=None)
    blocking_date = DateTimeField(default=None)
    unblocking_date = DateTimeField(default=None)
    cancellation_date = DateTimeField(default=None)
    paused_date = DateTimeField(default=None)
    resumed_date = DateTimeField(default=None)
    deletion_date = DateTimeField(default=None)
    youtube_creds = StringField(max_length=8192,default='')
    fb_creds = StringField(max_length=512,default='')
    has_logged_in_once = BooleanField(default=False)
    meta = {'auto_create_index': False,
            'indexes': [{'fields': ['created','subscription_customer_id','role']}]
           }
    #meta = {'db_alias': db_alias}

class SocialToProntoUser(DynamicDocument):
    platform = StringField(max_length=30,choices=SUPPORTED_SOCIAL_PLATFORMS,required=True)
    username = StringField(max_length=128,required=True, primary_key=True)
    user = ReferenceField(UserProfile,required=True)
    created = DateTimeField(default=datetime.datetime.utcnow())
    meta = {'auto_create_index': False,
            'indexes': [{'fields': ['created','platform','username','user']}]
           }
    #password=StringField(max_length=64)
    #secret_key= StringField(max_length=2048)
    #meta = {'db_alias': db_alias}

class ShopifyData(DynamicDocument):
    shop_id = StringField(max_length=256,required=True,primary_key=True)
    user = ReferenceField(UserProfile,required=True)
    
class PendingSignup(DynamicDocument):
    created = DateTimeField(default=datetime.datetime.utcnow())
    email = StringField(max_length=128,required=True,primary_key=True)
    code = IntField(required=True)
    meta = {
              'auto_create_index': False,
              'indexes': [
               {'fields': ['created'], 'expireAfterSeconds': 900}
           ]
        }
    
class ForgotPW(DynamicDocument):
    created = DateTimeField(default=datetime.datetime.utcnow())
    email = StringField(max_length=128,required=True,primary_key=True)
    code = IntField(required=True)
    meta = {
              'auto_create_index': False,
              'indexes': [
               {'fields': ['created'], 'expireAfterSeconds': 900}
           ]
        }

class GoogleSigninContext(DynamicDocument):
    created = DateTimeField(default=datetime.datetime.utcnow())
    client_id = StringField(max_length=128,required=True,primary_key=True)
    session_id = StringField(max_length=128,default='')
    meta = {
               'auto_create_index': False,
               'indexes': [
               {'fields': ['created'], 'expireAfterSeconds': 900}
           ]
        }
    
    
class Clip(DynamicDocument):
    created = DateTimeField(default=datetime.datetime.utcnow())
    bucket_name = StringField(max_length=128,required=True)
    object_path = StringField(max_length=512,required=True,primary_key=True)
    ext = StringField(max_length=16)
    thumbnail_path = StringField(max_length=256,default='')
    owner = ReferenceField(UserProfile,required=True)
    is_monetized = BooleanField(default=False)
    mood = StringField(max_length=32,default='')
    business_type = StringField(max_length=64,default='')
    industry = StringField(max_length=64,default='')
    category = StringField(max_length=64,default='')
    key_terms = ListField(StringField(max_length=2048), default=list)
    visual_bucket = ReferenceField(VisualBucket,default=None)
    meta = {'auto_create_index': False,
            'indexes': [{'fields': ['created','owner']}]}


class Image(DynamicDocument):
    created = DateTimeField(default=datetime.datetime.utcnow())
    bucket_name = StringField(max_length=128)
    object_path = StringField(max_length=512,required=True,primary_key=True)
    ext = StringField(max_length=16)
    thumbnail_path = StringField(max_length=256,default='')
    owner = ReferenceField(UserProfile,required=True)
    is_monetized = BooleanField(default=False)
    key_terms = ListField(StringField(max_length=2048), default=list)
    visual_bucket = ReferenceField(VisualBucket,default=None)
    meta = {
        'auto_create_index': False,
        'indexes': [{'fields': ['created','owner']}]
    }
    #meta = {'db_alias': db_alias}

class UserAudio(DynamicDocument):
    created = DateTimeField(default=datetime.datetime.utcnow())
    bucket_name = StringField(max_length=128)
    object_path = StringField(max_length=512,required=True,primary_key=True)
    ext = StringField(max_length=16,default='mp3')
    owner = ReferenceField(UserProfile,required=True)
    meta = {
        'auto_create_index': False,
        'indexes': [{'fields': ['created','owner']}]
    }
    
def _allow_empty(val):
    pass
    #if len(val) == 0:
    #    raise ValidationError('value can not be empty')

class VoiceOverData(DynamicEmbeddedDocument):
    vo_text = StringField(max_length=1024,default=str)
    vo_file = StringField(max_length=256,default=None)
    clips_covered = ListField(IntField(min_value=0, max_value=128),default=list)
        
class Video(DynamicEmbeddedDocument):
    hex_digest = StringField(max_length=128,default=str)
    bucket_name = StringField(max_length=128)
    thumbnail_path = StringField(max_length=256,default=str)
    title = StringField(max_length=128)
    duration = IntField()
    is_guest_video = BooleanField(default=False)
    text_list = ListField(StringField(max_length=256,validation=_allow_empty),default=list)
    intro_text = StringField(max_length=512)
    middle_text = StringField(max_length=512)
    outro_text = StringField(max_length=512)
    intro_vo_path = StringField(max_length=512,default=str)
    middle_vo_path = StringField(max_length=512,default=str)
    outro_vo_path = StringField(max_length=512,default=str)
    lower_third_text = StringField(max_length=512)
    contact_info = ListField(StringField(max_length=1024),default=list)
    ci_dict = DictField(dfault=dict)
    mood = StringField(max_length=32,default='')
    music_file =  StringField(max_length=256)
    images = ListField(StringField(max_length=1024),default=list)
    clips = ListField(StringField(max_length=1024),default=list)
    key_terms = ListField(StringField(max_length=1024), default=list)
    oem = StringField(max_length=256,default=str)
    color= StringField(max_length=16,default='#0000FF')
    template_name = StringField(max_length=64,default=str)
    vo_text = StringField(max_length=2048,default=str)
    vo_file = StringField(max_length=1024,default=None)
    voice_file = StringField(max_length=1024,default=None)
    vo_data = ListField(EmbeddedDocumentField(VoiceOverData),default=list)
    selected_voice = StringField(max_length=32,default='')
    video_type = StringField(max_length=32,required=True,choices=['custom','instant'],default='custom')
    

class YoutubePropData(DynamicEmbeddedDocument):
    last_updated = DateTimeField(default=datetime.datetime.utcnow()) 
    description = StringField(max_length=1024)
    fpath = StringField(max_length=512)
    title = StringField(max_length=512)
    category = StringField(max_length=16)
    keywords = StringField(max_length=1024)
    privacyStatus = StringField(max_length=64)
    video_id = StringField(max_length=1024,default=str)
    views = IntField(default=0)
    estimatedMinutesWatched = IntField(default=0)
    averageViewDuration = IntField(default=0)
    comments = IntField(default=0)
    likes = IntField(default=0)
    dislikes = IntField(default=0)
    shares = IntField(default=0)
    
    
                   
class UserVideo(DynamicDocument):
    created = DateTimeField(default=datetime.datetime.utcnow())
    fpath = StringField(max_length=1024,required=True,primary_key=True)
    video = EmbeddedDocumentField(Video)
    status = StringField(max_length=16,required=True,choices=['editable','committed'],default='editable')
    published_on = ListField(StringField(max_length=64,choices=SUPPORTED_SOCIAL_PLATFORMS),default=list)
    owner = ReferenceField(UserProfile,required=True)
    set_id = StringField(max_length=128)
    youtube_prop_data = EmbeddedDocumentField(YoutubePropData,default=None)
    fb_video_id = StringField(max_length=1024,default=str)
    schedule_id = StringField(max_length=256,default=str)
    automated = BooleanField(default=False)
    meta = {
        'auto_create_index': False,
        'indexes': [{'fields': ['created','owner','set_id','schedule_id','automated','youtube_prop_data.last_updated']}]
    }
    #meta = {'db_alias': db_alias}
class ScheduledVideo(DynamicDocument):
    created = DateTimeField(default=datetime.datetime.utcnow())
    video = ReferenceField(UserVideo,required=True)
    owner = ReferenceField(UserProfile)
    duration = IntField()
    title = StringField(max_length=256,default=str)
    interval = StringField(max_length=32,choices=['daily','weekly','monthly','annually'],default='weekly')
    given_day = StringField(max_length=32,choices=['monday','tuesday','wednesday','thursday','friday','saturday','sunday'],default=None)
    time_range = StringField(max_length=32,choices=['morning','afternoon','evening'],default='morning')
    last_scheduled_time = DateTimeField()
    last_scheduled_timestamp = IntField()
    next_scheduled_time = DateTimeField(required=True)
    next_scheduled_timestamp = IntField(required=True)
    annual_date =  DateTimeField(default=None)
    in_progress_start_timestamp = IntField(default=0)
    publish_on = ListField(StringField(max_length=32,choices=SUPPORTED_SOCIAL_PLATFORMS),default=list)
    #publish_result = ListField(StringField(max_length=30,choices=['youtube','facebook','instagram','twitter']),default=list)
    youtube_prop_data = EmbeddedDocumentField(YoutubePropData)
    approval_required = IntField(default=1)
    state = StringField(max_length=32,choices=['scheduled','in_progress'],default='scheduled')
    created_videos = ListField(ReferenceField(UserVideo),default=list)
    meta = {
        'auto_create_index': False,
        'indexes': [{'fields': ['next_scheduled_timestamp','owner','video']}]
    }
    
class UserVideoEvent(DynamicDocument):
    created = DateTimeField(default=datetime.datetime.utcnow())
    user = ReferenceField(UserProfile,required=True)
    video = ReferenceField(UserVideo,required=True)
    hex_digest= StringField(max_length=128,default=str)
    event_type = StringField(max_length=32,choices=['downloaded','shared'],required=True)
    published_on = StringField(max_length=32,choices=SUPPORTED_SOCIAL_PLATFORMS,default=str)
    meta = {
               'auto_create_index': False,
               'indexes': [
               {'fields': ['created','user','video']}
           ]
        }
    
       

class GuestVideo(DynamicDocument):
    created = DateTimeField(default=datetime.datetime.utcnow())
    fpath = StringField(max_length=1024,required=True,primary_key=True)
    video = EmbeddedDocumentField(Video)
    meta = {
        'auto_create_index': False,
        'indexes': [
            {'fields': ['created'], 'expireAfterSeconds': 7200}
        ]
    }
    
class Session(DynamicDocument):
    created = DateTimeField(default=datetime.datetime.utcnow())
    meta = {
        'abstract': True,
        'auto_create_index': False,
        'indexes': [
            {'fields': ['created'], 'expireAfterSeconds': 7200}
        ],
        
    }

class GuestSession(Session):
    business_info =  EmbeddedDocumentField(BusinessInfo)
    url = StringField(max_length=1024,required=True,primary_key=True)
    videos = ListField(ReferenceField(GuestVideo),default=list)
    searched_clips = ListField(StringField(max_length=1024),default=list)
    key_terms = ListField(StringField(max_length=1024), default=list)
    scrape_result = StringField(max_length=128,default='')
    clip_sequence = ListField(StringField(max_length=1024),default=list)
    #meta = {'db_alias': db_alias}

class ProntoGuest(DynamicDocument):
    email = StringField(max_length=128,required=True,primary_key=True)
    url = StringField(max_length=1024,default='')
    country = StringField(max_length=128,default='')
    company_size = IntField(min_value=0, max_value=1000000,default=0)
    
class GoogleAuthData(DynamicEmbeddedDocument):
    access_token =StringField(max_length=1024,required=True)
    expires_at =IntField(required=True,default=int(datetime.datetime.timestamp(datetime.datetime.utcnow()))+3600)
    id_token = StringField(max_length=8192,required=True)

   
class UserSession(Session):
    user =  ReferenceField(UserProfile,required=True)
    email = StringField(max_length=128,required=True)
    auth_type = StringField(max_length=32,choices=['pronto','google','facebook','linkedin'],default='pronto')
    videos = ListField(ReferenceField(UserVideo),default=list)
    key_terms = ListField(StringField(max_length=1024), default=list)
    searched_clips = ListField(StringField(max_length=1024),default=list)
    clip_sequence = ListField(StringField(max_length=1024),default=list)
    google_auth_data = EmbeddedDocumentField(GoogleAuthData)
    youtube_uploads = ListField(ReferenceField(UserVideo),default=list)
    meta = {'indexes': ['email']}

class AdminSession(Session):
    admin_user =  ReferenceField(UserProfile,required=True)
    email = StringField(max_length=128,required=True)
    auth_type = StringField(max_length=32,choices=['pronto','google','facebook','linkedin'],default='pronto')
    google_auth_data = EmbeddedDocumentField(GoogleAuthData)
    meta = {'indexes': ['email']}
        
        
    


