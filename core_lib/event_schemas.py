#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 17:13:44 2021

@author: farhan
"""

from core_lib.platform_utils import *
from core_lib.mongo_utils import *
userSessionSchema = {
     'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'auth_type':{
                  'type': 'string',
                  'allowed':['pronto','google','facebook']
                }
     
}

prontoSigninSchema = {
     'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'password':{
                  'type': 'string',
                  'required': True,
                  'minlength': 4, 
                  'maxlength': 32,
                }
     
    
}

prontoSignoutSchema = {
     'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                }
     
    
}

verifyConfirmCodeSchema =  {
     'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'code':   {
                  'type': 'integer',
                  'required': True,
                  'min': 0, 
                  'max': 99999,
              }
     
    
}

forgotPasswordSchema = {
     'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     }
}

verifyPasswordCodeSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'code':   {
                  'type': 'integer',
                  'required': True,
                  'min': 0, 
                  'max': 99999,
              }
    
}

updatePasswordSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                },
    
    'password':{
                  'type': 'string',
                  'required': True,
                  'minlength': 4, 
                  'maxlength': 32,
                }
}

userVideoListRequestSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                },
    
    'num_items':   {
                  'type': 'integer',
                  'min': 1, 
                  'max': 500,
              },
    'num_skip':   {
                  'type': 'integer',
                  'min': 0, 
                  'max': 500,
              }
    
}

userVisualListRequestSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                },
    
    'num_items':   {
                  'type': 'integer',
                  'min': 1, 
                  'max': 500,
              },
    'num_skip':   {
                  'type': 'integer',
                  'min': 0, 
                  'max': 500,
              },
    'visual_type':{
                  'type': 'string',
                  'allowed':['image','clip','audio']
                }    
}

userVideoSetRequestSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                },
    'set_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 15, 
                  'maxlength': 24,
                }
    
    
}

userVideoRequestSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                },
    'video_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 12, 
                  'maxlength': 1024,
                }
    
}

deleteVisualRequestSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                },
    'visual_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 12, 
                  'maxlength': 1024,
                }
    
}

updateVisualRequestSchema =  {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                },
    'visual_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 12, 
                  'maxlength': 1024,
                },
    'key_terms': 
              {
               'type': 'list', 
               'schema': {
                          'type': 'string',
                          'minlength': 0, 
                          'maxlength': 1024
                         }
              }
    
}

visualCountRequestSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                },
    'visual_type':{
                  'type': 'string',
                  'allowed':['image','clip','audio']
                }    
}

videoTemplatesRequestSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                }
    
}

scheduledVideoListRequestSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24,
                },
    'schedule_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                }
    
}

userScheduleListRequestSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24,
                }
}

automatedVideoListRequestSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24,
                }
}

getVideoScheduleRequestSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24,
                },
    'schedule_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                }
    
}

deleteVideoScheduleRequestSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24,
                },
    'schedule_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                }
    
}

ytVideoAnalyticsRequestSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                },
    'video_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 12, 
                  'maxlength': 1024,
                }
}

subscribeRequestSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'client_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 2, 
                  'maxlength': 1024
                },
    'success_url':{
                  'check_with':validate_url
                },
    'failed_url':{
                  'check_with':validate_url
                }
}

manageBillingSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                }

}

userProfileSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'password':{
                  'type': 'string',
                  'minlength': 4, 
                  'maxlength': 32,
                },
    'business_type':{
                  'type': 'string',
                  'required': True,
                  'minlength': 2, 
                  'maxlength': 64
                },
    'industry':{
                  'type': 'string',
                  'required': True,
                  'minlength': 2, 
                  'maxlength': 64
                },
    'business_name':{
                  'type': 'string',
                  'required': True,
                  'minlength': 2, 
                  'maxlength': 256
                },
    
    'url':{
                  'check_with':validate_url,
                  'required': True,
          },
    'logo_file':{
                  'type': 'string',
                  'minlength': 0, 
                  'maxlength': 1024
          },
    
    'approved_oem_list': {
        'check_with': validate_oem_list
    },
    'greeting':{
                  'type': 'string',
                  'nullable': True,
                  'minlength': 0, 
                  'maxlength': 256
    },
    'address': {
                'type': 'dict',
                'schema': {
                    'line1': {
                                'type': 'string',
                                'minlength': 0, 
                                'maxlength': 512
                             },
                    'line2': {
                                'type': 'string',
                                'minlength': 0, 
                                'maxlength': 512
                             },
                    'city': {
                                'type': 'string',
                                'minlength': 0, 
                                'maxlength': 64
                             },
                    'state': {
                                'type': 'string',
                                'minlength': 0, 
                                'maxlength': 32
                             },
                    'country': {
                                'type': 'string',
                                'minlength': 0, 
                                'maxlength': 8
                             },
                    'postal_code': {
                                'type': 'string',
                                'minlength': 0, 
                                'maxlength': 6
                             },
                   }         
        
        },
        'phone':{
                  'type': 'string',
                  'nullable': True,
                  'minlength': 0, 
                  'maxlength': 32
                },
         'key_terms': {
                 'type': 'list', 
                 'schema': {
                              'type': 'string',
                              'minlength': 0, 
                              'maxlength': 1024
                             }
                  },
          'color':{
                   'type': 'string',
                   'nullable': True,
                   'empty': True,
                   'maxlength': 32
                  }
                
    }
    
profileRequestSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
     'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                  }
}

checkUserLogoSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                }
}

getFileRequestSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                },
    'filename': {
          'type': 'string',
                  'required': True,
                  'minlength': 2, 
                  'maxlength': 1024
                }
}

putUserFileRequestSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                },
    'is_logo': {
          'type': 'boolean'
    },
    'key_terms': {
                  'type': 'string',
                  'minlength': 0, 
                  'maxlength': 1024
    }
}
    

newGuestSessionSchema = {
     'company_name': {
                  'type': 'string',
                  'minlength': 2, 
                  'maxlength': 256
     },
     'url':{
                  'check_with':validate_url
           },
     'greeting':{
                  'type': 'string',
                  'minlength': 2, 
                  'maxlength': 256
    },
     

} 
updateGuestSessionSchema = {
    'business_type':{
                  'type': 'string',
                  'required': True,
                  'minlength': 2, 
                  'maxlength': 64
                },
    'industry':{
                  'type': 'string',
                  'required': True,
                  'minlength': 2, 
                  'maxlength': 64
                },
     'greeting':{
                  'type': 'string',
                  'minlength': 2, 
                  'maxlength': 256
    },
    'moods' :  {
               'type': 'list', 
               'schema': {
                          'type': 'string',
                          'minlength': 0, 
                          'maxlength': 64
                         }
              }

}
 
manageBillingSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                }
}
returnFromBillingSchema = {
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                }
}

searchAndReplaceSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
             },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                },
    'clip_to_replace': {
                  'type': 'string',
                  'required': True,
                  'minlength': 2, 
                  'maxlength': 1024
                },
    'video_id':{
                  'type': 'string',
                  'empty': True,  
                  'maxlength': 1024
          },
    
    'mood':     {
               'type': 'list', 
               'schema': {
                          'type': 'string',
                          'empty': True, 
                          'maxlength': 64
                         }
              },
    'is_guest_session': {
                  'type': 'boolean'
                },
    'key_terms': 
              {
               'type': 'list', 
               'schema': {
                          'type': 'string',
                          'minlength': 0, 
                          'maxlength': 1024
                         }
              }
    
        
    
}


prepVideoSchema = {
    'email': {
               'type': 'string',
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
             },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'excludes': 'schedule_id',
                  'minlength': 2, 
                  'maxlength': 128
                },
    'schedule_id' : {
                  'type': 'string',
                  'required': True,
                  'excludes': 'session_id',
                  'minlength': 24, 
                  'maxlength': 24
                },
    'is_guest_session': {
                  'type': 'boolean'
                },
    'key_terms': 
              {
               'type': 'list', 
               'schema': {
                          'type': 'string',
                          'empty': True,  
                          'maxlength': 1024
                         }
              },
     'logo':{
                  'type': 'boolean'
          },
     'video_id':{
                  'type': 'string',
                  'empty': True,  
                  'maxlength': 1024
          },
     'thumbnail_path': {
                  'type': 'string',
                  'minlength': 0, 
                  'maxlength': 1024
         
         },
     
     'title': {
                  'type': 'string',
                  'empty': True,
                  'maxlength': 1024
          },
     'intro': {
                  'type': 'string',
                  'empty': True,  
                  'maxlength': 512
          },
     'middle_text': {
                  'type': 'string',
                  'minlength': 0,
                  'empty': True,
                  'maxlength': 512
          },
     'outro': {
                  'type': 'string',
                  'empty': True,  
                  'maxlength': 512
          },
     'middle_index': {
                       'type': 'integer',
                       'min': 0,
                       'max': 100
                       
                     },
     'outro_index': {
                       'type': 'integer',
                       'min': 0,
                       'max': 100
                       
                     },
     
     'call_to_action': {
                  'type': 'string',
                  'empty': True, 
                  'maxlength': 512
          },
     'oem': {
                  'type': 'string',
                  'empty': True,  
                  'maxlength': 512
          },
     'template_name': {
                  'type': 'string',
                  'empty': True,  
                  'maxlength': 512
          },
     'music_file': {
                  'type': 'string',
                  'empty': True,  
                  'maxlength': 1024
          },
     
     'contact_info': { 
             'type': 'dict',
             'schema': {
                     'company_name': {'type': 'boolean'},
                     'email': {'type': 'boolean'},
                     'url': {'type': 'boolean'},
                     'phone': {'type': 'boolean'},
                     'address': {'type': 'boolean'},
                 }
         },
     
      'contact_info_list': { 
             'type': 'list',
             'empty': True,
             'maxlength': 16,
             'schema': {
                           'type': 'string',
                           'empty': True, 
                           'maxlength': 1024
                         }
         },          
             
     'final_clips': {
                        'type': 'list', 
                        'schema': {
                              'type': 'string',
                              'empty': True,  
                              'maxlength': 1024
                         }
              },
     'clips': {
                        'type': 'list', 
                        'schema': {
                              'type': 'string',
                              'empty': True, 
                              'maxlength': 1024
                         }
              },
     'industry_clips': {
                        'type': 'list', 
                        'schema': {
                              'type': 'string',
                              'empty': True, 
                              'maxlength': 1024
                         }
              },
     'return_clip_seq': {
                        'type': 'boolean'
              },
     
     'images': {
                        'type': 'list', 
                        'schema': {
                              'type': 'string',
                              'empty': True, 
                              'maxlength': 1024
                         }
              },
     
     'create_video_durations' : {
                        'type': 'list', 
                        'required': True,
                        'empty': False, 
                        'schema': {
                              'type': 'integer',
                              'allowed': [6,15,30,60]
                         }
                   
         
              },
      'duration': {
                    'type': 'integer',
                    'allowed': [6,15,30,60]
       },
       'voice_file': {
                        'type': 'string',
                        'empty': True,  
                        'maxlength': 1024
               
                     },
        'vo_text': {
                       
                      'type': 'string',
                      'empty': True,  
                      'maxlength': 2048
                
                   },
        'vo_clips': {
                      'type': 'list', 
                      'required': False,
                      'empty': True, 
                      'schema': {
                                    'type': 'dict',
                                    'schema': {
                                                  'vo_text': {
                       
                                                                 'type': 'string',
                                                                 'empty': True,  
                                                                 'maxlength': 2048
                                                            
                                                             },
                                                  'vo_file': {
                                                                    'type': 'string',
                                                                    'empty': True,  
                                                                    'maxlength': 1024
                                                           
                                                                 },       
                                                  'clips_covered': {
                                                                       'type': 'list', 
                                                                       'required': False,
                                                                       'empty': True, 
                                                                       'schema': {
                                                                                     'type': 'integer',
                                                                                     'min': 0,
                                                                                     'max': 100
                                                                                 }
                                                                   }        
                                                          
                                              }
                                    
                                }
                    },
      
       'color':{
                   'type': 'string',
                   'empty': True,  
                   'maxlength': 32
               },
       'mood':     {
                  'type': 'string',
                  'empty': True, 
                  'maxlength': 64
                },
       'ws_connection': {
                'type': 'string',
                'nullable': True,
                'empty': False,  
                'maxlength': 128
           
           }
    
}

commitVideoSetSchema = {
    'set_id': {
               'type': 'string',
               'minlength': 2, 
               'maxlength': 128
             }
}

scheduleVideoSchema = {
 
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
             },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                },
    
    'video_id': {
                  'type': 'string',
                  'required': True,
                  'minlength': 2, 
                  'maxlength': 1024
                },
        
    'interval': {
                  'type': 'string',
                  'allowed':['annually','monthly','weekly','daily']
                },
    'given_day': {
                    'type': 'string',
                    'allowed': ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
        
                 },
    'time_range': {
                    'type': 'string',
                    'allowed': ['morning','afternoon','evening']
                  },
    
    'annual_date': {
                      'type': 'string',
                      'check_with':validate_date
                   },
    
    'publish_on_list': {
                        'type': 'list',
                        'schema': {
                                   'type': 'string',
                                   'allowed': ['youtube','facebook','twitter','instagram','linkedin']       
                        }
                            
                   },
   'approval_required': {
                       'type': 'boolean'
                  }
}
    
keepAliveSchema = {
     'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 2, 
                  'maxlength': 128
                },
    'is_guest_session': {
                  'type': 'boolean',
                  'required': True
                }
    
}    

SignedUrlForUploadSchema = {
      'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
             },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                },
     'filename': {
                  'type': 'string',
                  'required': True,
                  'minlength': 2, 
                  'maxlength': 1024
                },
     'size':   {
                  'type': 'integer',
                  'required': False,
                  'min': 1024, 
                  'max': 15728640,
              },
     'height':   {
                  'type': 'integer',
                  'required': False,
                  'min': 450, 
                  'max': 1280,
              },
     'width':   {
                  'type': 'integer',
                  'required': False,
                  'min': 450, 
                  'max': 1280,
              }                        
            

}

SignedUrlForDownloadSchema = {
      'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
             },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                },
     'fpath': {
                  'type': 'string',
                  'required': True,
                  'minlength': 2, 
                  'maxlength': 2048
                }

}
     
AddUserMediaSchema =  {
     'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
             },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                },
     'filename': {
                  'type': 'string',
                  'required': True,
                  'minlength': 2, 
                  'maxlength': 1024
                }
        
        
}
     
videoDownloadedSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
             },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                },
    'video_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 12, 
                  'maxlength': 1024,
                }        
            
        
}

userRemainingQuotaSchema = {
    'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
             },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                }
        
}

voVoicesListRequestSchema = {
     'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
             },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                }
}

putAudioFileRequestSchema = {
     'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                }
        
}

audioFileRequestSchema = {
      'email': {
               'type': 'string',
               'required': True,
               'minlength': 6, 
               'maxlength': 128,
               'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
     },
    'session_id':{
                  'type': 'string',
                  'required': True,
                  'minlength': 24, 
                  'maxlength': 24
                }       
}

 
guestDemoRequestSchema = {
         'email': {
                   'type': 'string',
                   'required': True,
                   'minlength': 6, 
                   'maxlength': 128,
                   'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
             },
                 
         'url':    {
                      'check_with':validate_url
                   },
                 
         'country': {
                      'type': 'string',
                      'minlength': 0, 
                      'maxlength': 128
                    },
        'company_size': {
                         'type': 'integer',
                         'min': 0, 
                         'max': 1000000,
                        }         
        
}
        