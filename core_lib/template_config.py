effect_names = ['move_effect','art_effect','slide_effect','slide_move_effect']
durations = [6,15,30,60]
block_params = ['num_clips','num_texts','text_times','text_titles']

# Block config is a dictionary of blocks.
# Each block is a dictionary of parameters.

# The parameters are:

# num_clips: The number of clips in the block.
# clip_pos: A list of [x,y] positons of the clips.
# clip_times: A list of [start_time,end_time] times of the clips.
# clip_dims: A list of [width,height] dimensions of the clips.
# clip_trans (optional): A list of trans dicts where each dict includes the 'trans_name' and the 'trans_args'.

# num_texts: The number of texts in the block.
# text_pos: A list of [x,y] positons of the texts.
# text_times: A list of [start_time,end_time] times of the texts.

# duration: The duration of the block.
# fps: The frames per second of the block.

# logo_pos (optional): A list of [x,y] positons of the logo.
# logo_times (optional): A list of [start_time,end_time] times of the logo.
# logo_dims (optional): A list of [width,height] dimensions of the logo.

block_config = {
    'SimpleBlock4': {'num_clips':1, 'clip_pos':[[0,0]], 'clip_times':[[0,4]], 'clip_dims':[['width','height']],
                     'num_texts':1, 'text_pos':[[0.5,0.5]], 'text_times':[[0,-1]],'text_titles':['text1'], 'duration':4, 'fps':30,
                    },
    'SimpleBlock5': {'num_clips':1, 'clip_pos':[[0,0]], 'clip_times':[[0,5]], 'clip_dims':[['width','height']],
                     'num_texts':1, 'text_pos':[[0.5,0.5]], 'text_times':[[0,4.5]],'text_titles':['text1'], 'duration':5, 'fps':30,
                    },
    'SimpleBlock6': {'num_clips':1, 'clip_pos':[[0.5,0.5]], 'clip_times':[[0,6]], 'clip_dims':[['width','height']],
                     'num_texts':1, 'text_pos':[[0.5,0.5]], 'text_times':[[0,5.5]],'text_titles':['Heading','Sub-heading'],
                     'duration':6, 'fps':30},
    'SimpleBlock9': {'num_clips':1, 'clip_pos':[[0.5,0.5]], 'clip_times':[[0,-1]], 'clip_dims':[['width','height']],
                     'num_texts':1, 'text_pos':[[0.5,0.5]], 'text_times':[[0,8]],'text_titles':['Heading','Sub-heading'],
                     'duration':9, 'fps':30},    
    'SplitBlock5': {'num_clips':2, 'clip_pos':[[0,0], ['width//2',0]], 'clip_times':[[0,5], [0,5]],
                    'clip_dims':[['width//2','height'], ['width//2','height']], 'num_texts':2, 'text_pos':[[0.1,0.2], [0.9,0.8]],
                    'text_times':[[1,4], [1,4]], 'text_titles':['text1','text2'],
                    'duration':5, 'fps':30,
                    },
    'BoldEndBlock2':{'num_clips':1, 'clip_pos':[[0.5,0.5]], 'clip_times':[[0,-1]], 'clip_dims':[['width','height']],
                     'num_texts':1, 'text_pos':[[0.5,0.75]], 'text_times':[[0,-1]],'text_titles':['text1'], 'duration':2, 'fps':30,
                     'logo_pos': [[0.5,0.3]], 'logo_times': [[0,-1]], 'logo_dims': [[None, 'height//3']],
                    },
    'BoldEndBlock3':{'num_clips':1, 'clip_pos':[[0.5,0.5]], 'clip_times':[[0,-1]], 'clip_dims':[['width','height']],
                     'num_texts':1, 'text_pos':[[0.5,0.75]], 'text_times':[[0,-1]],'text_titles':['text1'], 'duration':3, 'fps':30,
                     'logo_pos': [[0.5,0.3]], 'logo_times': [[0,-1]], 'logo_dims': [[None, 'height//3']],
                    },    
    'BoldEndBlock5':{'num_clips':1, 'clip_pos':[[0.5,0.5]], 'clip_times':[[0,5]], 'clip_dims':[['width','height']],
                     'num_texts':1, 'text_pos':[[0.5,0.75]], 'text_times':[[0,4.5]],'text_titles':['text1'], 'duration':5, 'fps':30,
                     'logo_pos': [[0.5,0.3]], 'logo_times': [[0,4.5]], 'logo_dims': [[None, 'height//3']],
                    },
    'BoldEndBlock6':{'num_clips':1, 'clip_pos':[[0.5,0.5]], 'clip_times':[[0,-1]], 'clip_dims':[['width','height']],
                     'num_texts':1, 'text_pos':[[0.5,0.75]], 'text_times':[[0,-1]],'text_titles':['text1'], 'duration':6, 'fps':30,
                     'logo_pos': [[0.5,0.3]], 'logo_times': [[0,-1]], 'logo_dims': [[None, 'height//3']],
                    },
    'CandidEndBlock2':{'num_clips':1, 'clip_pos':[[0.5,0.5]], 'clip_times':[[0,-1]], 'clip_dims':[['width','height']],
                       'num_texts':1, 'text_pos':[[0.5,0.85]], 'text_times':[[0,-1]],'text_titles':['text1'], 'duration':2, 'fps':30,
                       'logo_pos': [[0.5,'fwd_posy-height//3-50']], 'logo_times': [[0,1.8]], 'logo_dims': [[None, 'height//3']],
                    },
    'CandidEndBlock3':{'num_clips':1, 'clip_pos':[[0.5,0.5]], 'clip_times':[[0,-1]], 'clip_dims':[['width','height']],
                       'num_texts':1, 'text_pos':[[0.5,0.85]], 'text_times':[[0,-1]],'text_titles':['text1'], 'duration':3, 'fps':30,
                       'logo_pos': [[0.5,'fwd_posy-height//3-50']], 'logo_times': [[0,2.8]], 'logo_dims': [[None, 'height//3']],
                    },    
    'CandidEndBlock5':{'num_clips':1, 'clip_pos':[[0.5,0.5]], 'clip_times':[[0,5]], 'clip_dims':[['width','height']],
                       'num_texts':1, 'text_pos':[[0.5,0.85]], 'text_times':[[0,4.5]],'text_titles':['text1'], 'duration':5, 'fps':30,
                       'logo_pos': [[0.5,'fwd_posy-height//3-50']], 'logo_times': [[0,4.8]], 'logo_dims': [[None, 'height//3']],
                    },
    'CandidEndBlock6':{'num_clips':1, 'clip_pos':[[0.5,0.5]], 'clip_times':[[0,-1]], 'clip_dims':[['width','height']],
                       'num_texts':1, 'text_pos':[[0.5,0.85]], 'text_times':[[0,-1]],'text_titles':['text1'], 'duration':6, 'fps':30,
                       'logo_pos': [[0.5,'fwd_posy-height//3-50']], 'logo_times': [[0,5.8]], 'logo_dims': [[None, 'height//3']],
                    },
    'SplitProduct5': {'num_clips':1, 'clip_pos': [[0,0]], 'clip_times': [[1.5,5]], 'clip_dims': [['width//2','height']],
                      'num_texts':1, 'text_pos':[[0,0]], 'text_times':[[0,5]],'text_titles':['text1'],'duration':5, 'fps':30,
                      'clip_trans': [{'trans_name': 'slide_transition', 'trans_args': {'direction':'down'}}]
                     }
}

template_config = {
    
          'Bold1': {
                  'categories': ['Bold'],
                  'allowed_fonts': ['Poppins-ExtraBold.ttf'],
                  6:
                        {
                          'blocks': [
                                        {
                                           'block_name':'SimpleBlock4',
                                           'effects': [
                                                   {
                                                      'effect_name': 'bold_effect',
                                                      'effect_args': {
                                                                       'font_size':95,
                                                                       'color':'white',
                                                                       'font':'Poppins-ExtraBold.ttf',
                                                                       'theme':'blue',
                                                                       'vh':'height',
                                                                       'vw':'width',
                                                                       'pos':[0.5,0.5],
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },
                                        {
                                           'block_name':'BoldEndBlock2',
                                           'effects': [
                                                   {
                                                      'effect_name': 'zoom_effect',
                                                      'effect_args': {
                                                                       'font_size':25,
                                                                       'color':'white',
                                                                       'font':'Poppins-ExtraBold.ttf',
                                                                       'align':'center',
                                                                       'theme':'blue',
                                                                       'vh':'height',
                                                                       'vw':'width',
                                                                       'pos':[0.5,0.75],
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       }
                            ]
        
                        },
                  15:
                        {
                          'blocks': [
                                        {
                                           'block_name':'SimpleBlock4',
                                           'effects': [
                                                   {
                                                      'effect_name': 'bold_effect',
                                                      'effect_args': {
                                                                       'font_size':95,
                                                                       'color':'white',
                                                                       'font':'Poppins-ExtraBold.ttf',
                                                                       'theme':'blue',
                                                                       'vh':'height',
                                                                       'vw':'width',
                                                                       'pos':[0.5,0.5],
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },
                                        {
                                           'block_name':'SimpleBlock4',
                                           'effects': [
                                                   {
                                                      'effect_name': 'bold_effect',
                                                      'effect_args': {
                                                                       'font_size':95,
                                                                       'color':'white',
                                                                       'font':'Poppins-ExtraBold.ttf',
                                                                       'theme':'blue',
                                                                       'vh':'height',
                                                                       'vw':'width',
                                                                       'pos':[0.5,0.5],
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },
                                        {
                                           'block_name':'SimpleBlock4',
                                           'effects': [
                                                   {
                                                      'effect_name': 'bold_effect',
                                                      'effect_args': {
                                                                       'font_size':95,
                                                                       'color':'white',
                                                                       'font':'Poppins-ExtraBold.ttf',
                                                                       'theme':'blue',
                                                                       'vh':'height',
                                                                       'vw':'width',
                                                                       'pos':[0.5,0.5],
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },
                                        {
                                           'block_name':'BoldEndBlock3',
                                           'effects': [
                                                   {
                                                      'effect_name': 'zoom_effect',
                                                      'effect_args': {
                                                                       'font_size':25,
                                                                       'color':'white',
                                                                       'font':'Poppins-ExtraBold.ttf',
                                                                       'align':'center',
                                                                       'theme':'blue',
                                                                       'vh':'height',
                                                                       'vw':'width',
                                                                       'pos':[0.5,0.75],
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       }
                            ]
        
                        },
                  30:
                        {
                          'blocks': [
                                        {
                                           'block_name':'SimpleBlock5',
                                           'effects': [
                                                   {
                                                      'effect_name': 'bold_effect',
                                                      'effect_args': {
                                                                       'font_size':95,
                                                                       'color':'white',
                                                                       'font':'Poppins-ExtraBold.ttf',
                                                                       'theme':'blue',
                                                                       'vh':'height',
                                                                       'vw':'width',
                                                                       'pos':[0.5,0.5],
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },
                                        {
                                           'block_name':'SimpleBlock5',
                                           'effects': [
                                                   {
                                                      'effect_name': 'bold_effect',
                                                      'effect_args': {
                                                                       'font_size':95,
                                                                       'color':'white',
                                                                       'font':'Poppins-ExtraBold.ttf',
                                                                       'theme':'blue',
                                                                       'vh':'height',
                                                                       'vw':'width',
                                                                       'pos':[0.5,0.5],
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },
                                        {
                                           'block_name':'SimpleBlock5',
                                           'effects': [
                                                   {
                                                      'effect_name': 'bold_effect',
                                                      'effect_args': {
                                                                       'font_size':95,
                                                                       'color':'white',
                                                                       'font':'Poppins-ExtraBold.ttf',
                                                                       'theme':'blue',
                                                                       'vh':'height',
                                                                       'vw':'width',
                                                                       'pos':[0.5,0.5],
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },
                                        {
                                           'block_name':'SimpleBlock5',
                                           'effects': [
                                                   {
                                                      'effect_name': 'bold_effect',
                                                      'effect_args': {
                                                                       'font_size':95,
                                                                       'color':'white',
                                                                       'font':'Poppins-ExtraBold.ttf',
                                                                       'theme':'blue',
                                                                       'vh':'height',
                                                                       'vw':'width',
                                                                       'pos':[0.5,0.5],
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },
                                        {
                                           'block_name':'SimpleBlock5',
                                           'effects': [
                                                   {
                                                      'effect_name': 'bold_effect',
                                                      'effect_args': {
                                                                       'font_size':95,
                                                                       'color':'white',
                                                                       'font':'Poppins-ExtraBold.ttf',
                                                                       'theme':'blue',
                                                                       'vh':'height',
                                                                       'vw':'width',
                                                                       'pos':[0.5,0.5],
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },
                                        {
                                           'block_name':'BoldEndBlock5',
                                           'effects': [
                                                   {
                                                      'effect_name': 'zoom_effect',
                                                      'effect_args': {
                                                                       'font_size':25,
                                                                       'color':'white',
                                                                       'font':'Poppins-ExtraBold.ttf',
                                                                       'align':'center',
                                                                       'theme':'blue',
                                                                       'vh':'height',
                                                                       'vw':'width',
                                                                       'pos':[0.5,0.75],
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       }
                            ]
        
                        },
                  60:
                        {
                          'blocks': [
                                        {
                                           'block_name':'SimpleBlock9',
                                           'effects': [
                                                   {
                                                      'effect_name': 'bold_effect',
                                                      'effect_args': {
                                                                       'font_size':95,
                                                                       'color':'white',
                                                                       'font':'Poppins-ExtraBold.ttf',
                                                                       'theme':'blue',
                                                                       'vh':'height',
                                                                       'vw':'width',
                                                                       'pos':[0.5,0.5],
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },
                                        {
                                           'block_name':'SimpleBlock9',
                                           'effects': [
                                                   {
                                                      'effect_name': 'bold_effect',
                                                      'effect_args': {
                                                                       'font_size':95,
                                                                       'color':'white',
                                                                       'font':'Poppins-ExtraBold.ttf',
                                                                       'theme':'blue',
                                                                       'vh':'height',
                                                                       'vw':'width',
                                                                       'pos':[0.5,0.5],
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },
                                        {
                                           'block_name':'SimpleBlock9',
                                           'effects': [
                                                   {
                                                      'effect_name': 'bold_effect',
                                                      'effect_args': {
                                                                       'font_size':95,
                                                                       'color':'white',
                                                                       'font':'Poppins-ExtraBold.ttf',
                                                                       'theme':'blue',
                                                                       'vh':'height',
                                                                       'vw':'width',
                                                                       'pos':[0.5,0.5],
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },
                                        {
                                           'block_name':'SimpleBlock9',
                                           'effects': [
                                                   {
                                                      'effect_name': 'bold_effect',
                                                      'effect_args': {
                                                                       'font_size':95,
                                                                       'color':'white',
                                                                       'font':'Poppins-ExtraBold.ttf',
                                                                       'theme':'blue',
                                                                       'vh':'height',
                                                                       'vw':'width',
                                                                       'pos':[0.5,0.5],
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },
                                        {
                                           'block_name':'SimpleBlock9',
                                           'effects': [
                                                   {
                                                      'effect_name': 'bold_effect',
                                                      'effect_args': {
                                                                       'font_size':95,
                                                                       'color':'white',
                                                                       'font':'Poppins-ExtraBold.ttf',
                                                                       'theme':'blue',
                                                                       'vh':'height',
                                                                       'vw':'width',
                                                                       'pos':[0.5,0.5],
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },
                                        {
                                           'block_name':'SimpleBlock9',
                                           'effects': [
                                                   {
                                                      'effect_name': 'bold_effect',
                                                      'effect_args': {
                                                                       'font_size':95,
                                                                       'color':'white',
                                                                       'font':'Poppins-ExtraBold.ttf',
                                                                       'theme':'blue',
                                                                       'vh':'height',
                                                                       'vw':'width',
                                                                       'pos':[0.5,0.5],
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },
                                        {
                                           'block_name':'BoldEndBlock6',
                                           'effects': [
                                                   {
                                                      'effect_name': 'zoom_effect',
                                                      'effect_args': {
                                                                       'font_size':25,
                                                                       'color':'white',
                                                                       'font':'Poppins-ExtraBold.ttf',
                                                                       'align':'center',
                                                                       'theme':'blue',
                                                                       'vh':'height',
                                                                       'vw':'width',
                                                                       'pos':[0.5,0.75],
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       }
                            ]
        
                        }

       },
            
       'Candid1': {
             'allowed_fonts': ['NotoSansTC-Medium.otf'],
             'categories': ['Candid'],
             6: {
                    'blocks': [
                                   {
                                       'block_name':'SimpleBlock4',
                                       'effects': [
                                                {
                                                   'effect_name': 'candid_effect',
                                                   'effect_args': {
                                                                     'font_size':30,
                                                                     'color':'white',
                                                                     'font':'NotoSansTC-Medium.otf',
                                                                     'theme':'blue',
                                                                     'fps':30
                                                                 }
                                                    }
                                            ]
                                       },
                                        {
                                           'block_name':'CandidEndBlock2',
                                           'effects': [
                                                   {
                                                      'effect_name': 'candid_effect',
                                                      'effect_args': {
                                                                       'font_size':30,
                                                                       'color':'white',
                                                                       'font':'NotoSansTC-Medium.otf',
                                                                       'theme':'blue',
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       }
                            ]
                    },
             15: {
                    'blocks': [
                                   {
                                       'block_name':'SimpleBlock5',
                                       'effects': [
                                                {
                                                   'effect_name': 'candid_effect',
                                                   'effect_args': {
                                                                     'font_size':30,
                                                                     'color':'white',
                                                                     'font':'NotoSansTC-Medium.otf',
                                                                     'theme':'blue',
                                                                     'fps':30
                                                                 }
                                                    }
                                            ]
                                       },
                                        {
                                           'block_name':'SimpleBlock5',
                                           'effects': [
                                                   {
                                                      'effect_name': 'candid_effect',
                                                      'effect_args': {
                                                                       'font_size':30,
                                                                       'color':'white',
                                                                       'font':'NotoSansTC-Medium.otf',
                                                                       'theme':'blue',
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },
                                        {
                                           'block_name':'CandidEndBlock5',
                                           'effects': [
                                                   {
                                                      'effect_name': 'candid_effect',
                                                      'effect_args': {
                                                                       'font_size':30,
                                                                       'color':'white',
                                                                       'font':'NotoSansTC-Medium.otf',
                                                                       'theme':'blue',
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       }
                            ]
                    },
             30: {
                    'blocks': [
                                   {
                                       'block_name':'SimpleBlock5',
                                       'effects': [
                                                {
                                                   'effect_name': 'candid_effect',
                                                   'effect_args': {
                                                                     'font_size':30,
                                                                     'color':'white',
                                                                     'font':'NotoSansTC-Medium.otf',
                                                                     'theme':'blue',
                                                                     'fps':30
                                                                 }
                                                    }
                                            ]
                                       },
                                        {
                                           'block_name':'SimpleBlock5',
                                           'effects': [
                                                   {
                                                      'effect_name': 'candid_effect',
                                                      'effect_args': {
                                                                       'font_size':30,
                                                                       'color':'white',
                                                                       'font':'NotoSansTC-Medium.otf',
                                                                       'theme':'blue',
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },{
                                           'block_name':'SimpleBlock5',
                                           'effects': [
                                                   {
                                                      'effect_name': 'candid_effect',
                                                      'effect_args': {
                                                                       'font_size':30,
                                                                       'color':'white',
                                                                       'font':'NotoSansTC-Medium.otf',
                                                                       'theme':'blue',
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },{
                                           'block_name':'SimpleBlock5',
                                           'effects': [
                                                   {
                                                      'effect_name': 'candid_effect',
                                                      'effect_args': {
                                                                       'font_size':30,
                                                                       'color':'white',
                                                                       'font':'NotoSansTC-Medium.otf',
                                                                       'theme':'blue',
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },{
                                           'block_name':'SimpleBlock5',
                                           'effects': [
                                                   {
                                                      'effect_name': 'candid_effect',
                                                      'effect_args': {
                                                                       'font_size':30,
                                                                       'color':'white',
                                                                       'font':'NotoSansTC-Medium.otf',
                                                                       'theme':'blue',
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },
                                        {
                                           'block_name':'CandidEndBlock5',
                                           'effects': [
                                                   {
                                                      'effect_name': 'candid_effect',
                                                      'effect_args': {
                                                                       'font_size':30,
                                                                       'color':'white',
                                                                       'font':'NotoSansTC-Medium.otf',
                                                                       'theme':'blue',
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       }
                            ]
                    },
             60: {
                    'blocks': [
                                   {
                                       'block_name':'SimpleBlock9',
                                       'effects': [
                                                {
                                                   'effect_name': 'candid_effect',
                                                   'effect_args': {
                                                                     'font_size':30,
                                                                     'color':'white',
                                                                     'font':'NotoSansTC-Medium.otf',
                                                                     'theme':'blue',
                                                                     'fps':30
                                                                 }
                                                    }
                                            ]
                                       },
                                        {
                                           'block_name':'SimpleBlock9',
                                           'effects': [
                                                   {
                                                      'effect_name': 'candid_effect',
                                                      'effect_args': {
                                                                       'font_size':30,
                                                                       'color':'white',
                                                                       'font':'NotoSansTC-Medium.otf',
                                                                       'theme':'blue',
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },{
                                           'block_name':'SimpleBlock9',
                                           'effects': [
                                                   {
                                                      'effect_name': 'candid_effect',
                                                      'effect_args': {
                                                                       'font_size':30,
                                                                       'color':'white',
                                                                       'font':'NotoSansTC-Medium.otf',
                                                                       'theme':'blue',
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },{
                                           'block_name':'SimpleBlock9',
                                           'effects': [
                                                   {
                                                      'effect_name': 'candid_effect',
                                                      'effect_args': {
                                                                       'font_size':30,
                                                                       'color':'white',
                                                                       'font':'NotoSansTC-Medium.otf',
                                                                       'theme':'blue',
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },{
                                           'block_name':'SimpleBlock9',
                                           'effects': [
                                                   {
                                                      'effect_name': 'candid_effect',
                                                      'effect_args': {
                                                                       'font_size':30,
                                                                       'color':'white',
                                                                       'font':'NotoSansTC-Medium.otf',
                                                                       'theme':'blue',
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },
                                       {
                                           'block_name':'SimpleBlock9',
                                           'effects': [
                                                   {
                                                      'effect_name': 'candid_effect',
                                                      'effect_args': {
                                                                       'font_size':30,
                                                                       'color':'white',
                                                                       'font':'NotoSansTC-Medium.otf',
                                                                       'theme':'blue',
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       },
                                        {
                                           'block_name':'CandidEndBlock6',
                                           'effects': [
                                                   {
                                                      'effect_name': 'candid_effect',
                                                      'effect_args': {
                                                                       'font_size':30,
                                                                       'color':'white',
                                                                       'font':'NotoSansTC-Medium.otf',
                                                                       'theme':'blue',
                                                                       'fps':30
                                                                      }
                                                    }
                                            ]
                                       }
                            ]
        
             }
        }
            
           
    
}

# from core_lib.templates import *    
# templateConfig = {
                  
#                   'Candid':{
#                           'max_text_box_length': 50,
#                           'durations': {
#                                 '15': {
#                                 'num_texts': 3,
#                                 'text_boxes': 3,
#                                 'display_times': ['At 0 seconds','At 7 seconds','At 12 seconds'],
#                                 'num_clips': 4,
#                                 'clip_durations': [4, 4, 4, 4]
#                              },
#                              '30': {
#                                 'num_texts': 5,
#                                 'text_boxes': 5,
#                                 'display_times': ['At 0 seconds','At 4 seconds','At 8 seconds','At 12 seconds','At 20 seconds'],
#                                 'num_clips': 6,
#                                 'clip_durations': [4, 4, 4, 4, 4, 4]
#                              },
#                              '60': {
#                                 'num_texts': 7,
#                                 'text_boxes': 7,
#                                 'display_times': ['At 0 seconds','At 5 seconds','At 10 seconds','At 15 seconds','At 20 seconds','At 25 seconds','At 35 seconds'],
#                                 'num_clips': 8,
#                                 'clip_durations': [4, 4, 4, 4, 4, 4, 4, 4]
#                              }
                              
#                           }
#                   },
#                   'Bold':{
#                            'max_text_box_length': 35,
#                            'durations': {
#                                  '15': {
#                                  'num_texts': 3,
#                                  'num_clips': 4,
#                                  'text_boxes': 3,
#                                  'display_times': ['At 0 seconds','At 5 seconds','At 10 seconds'],
#                                  'clip_durations': [4, 4, 4, 3]
#                               },
#                               '30': {
#                                  'num_texts': 4,
#                                  'num_clips': 5,
#                                  'text_boxes': 4,
#                                  'display_times': ['At 0 seconds','At 5 seconds','At 10 seconds','At 15 seconds'],
#                                  'clip_durations': [5, 5, 5, 5, 5]
#                               },
#                               '60': {
#                                  'num_texts': 7,
#                                  'num_clips': 8,
#                                  'text_boxes': 7,
#                                  'display_times': ['At 0 seconds','At 8 seconds','At 16 seconds','At 24 seconds','At 32 seconds','At 40 seconds','At 46 seconds'],
#                                  'clip_durations': [8, 8, 8, 8, 7, 7, 7, 7]
#                               }
                           
#                            }
#                   },
#                   'Fresh':{
#                            'max_text_box_length': 80,
#                            'durations': {
#                               '15': {
#                                  'num_texts': 2,
#                                  'num_clips': 3,
#                                  'text_boxes': 2,
#                                  'display_times': ['At 0 seconds','At 4 seconds'],
#                                  'clip_durations': [4, 4, 4]
#                               },
#                               '30': {
#                                  'num_text': 3,
#                                  'num_clips': 5,
#                                  'text_boxes': 3,
#                                  'display_times': ['At 0 seconds','At 5 seconds','At 10 seconds'],
#                                  'clip_durations': [5, 5, 5, 5, 5]
#                               },
#                               '60': {
#                                  'num_texts': 5,
#                                  'num_clips': 7,
#                                  'text_boxes': 5,
#                                  'display_times': ['At 0 seconds','At 8 seconds','At 16 seconds','At 24 seconds','At 32 seconds'],
#                                  'clip_durations': [8, 8, 8, 8, 7, 7, 7]
#                               }
                           
#                            }
#                   },
#                   'Clean':{
#                           'max_text_box_length': 50,
#                            'durations': {
#                               '15': {
#                                  'num_texts': 2,
#                                  'num_clips': 4,
#                                  'text_boxes': 2,
#                                  'display_times': ['At 0 seconds','At 4 seconds'],
#                                  'clip_durations': [4, 4, 4, 4]
#                               },
#                               '30': {
#                                  'num_text': 4,
#                                  'num_clips': 6,
#                                  'text_boxes': 4,
#                                  'display_times': ['At 0 seconds','At 5 seconds','At 10 seconds','At 15 seconds'],
#                                  'clip_durations': [5, 5, 5, 5, 5, 5]
#                               },
#                               '60': {
#                                  'num_texts': 6,
#                                  'num_clips': 8,
#                                  'text_boxes': 6,
#                                  'display_times': ['At 0 seconds','At 8 seconds','At 16 seconds','At 24 seconds','At 32 seconds','At 39 seconds'],
#                                  'clip_durations': [8, 8, 8, 8, 7, 7, 7, 7]
#                               }
                           
#                            }
#                   },           
#                   'Bright':{
#                            'max_text_box_length': 40,
#                            'durations': {
#                                  '15': {
#                                  'num_texts': 4,
#                                  'num_clips': 2,
#                                  'text_boxes': 4,
#                                  'display_times': ['At 0 seconds','At 4 seconds','At 8 seconds','At 12 seconds'],
#                                  'clip_durations': [4, 4]
#                               },
#                               '30': {
#                                  'num_texts': 6,
#                                  'num_clips': 4,
#                                  'text_boxes': 6,
#                                  'display_times': ['At 0 seconds','At 5 seconds','At 10 seconds','At 15 seconds','At 20 seconds','At 25 seconds'],
#                                  'clip_durations': [5, 5, 5, 5]
#                               },
#                               '60': {
#                                  'num_texts': 8,
#                                  'num_clips': 6,
#                                  'text_boxes': 8,
#                                  'display_times': ['At 0 seconds','At 8 seconds','At 16 seconds','At 24 seconds','At 32 seconds','At 39 seconds','At 46 seconds','At 51 seconds'],
#                                  'clip_durations': [8, 8, 8, 8, 7, 7]
#                               }
                           
#                            }
                           
#                   }
                             
                             
#         }
                    
               

# templateNameToClassDict = {
#                              'Candid':CandidTemplate,
#                              'Bold':BoldTemplate,
#                              'Fresh':FreshTemplate,
#                              'Bright': SAPTemplate,
#                              'Clean': ArtTemplate
#                           }
    