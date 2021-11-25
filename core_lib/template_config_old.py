block_config = {
    'SimpleBlock5': {'num_clips': 1, 'clip_pos':[[0.5,0.5]], 'clip_times':[[0,5]], 'clip_dims':[['width','height']],
                    'num_texts':1, 'text_pos':[[0.5,0.5]], 'text_times':[[1,4]], 'duration':5, 'fps':30,
                    },
    'SimpleBlock6': {'num_clips': 1, 'clip_pos':[[0.5,0.5]], 'clip_times':[[0,6]], 'clip_dims':[['width','height']],
                     'num_texts':1, 'text_pos':[[0.5,0.5]], 'text_times':[[1,5]],'duration':6, 'fps':30},
    'SplitBlock5': {'num_clips': 2, 'clip_pos':[[0,0], ['width//2',0]], 'clip_times':[[0,5], [0,5]],
                    'clip_dims':[['width//2','height'], ['width//2','height']], 'num_texts':2, 'text_pos':[[0.1,0.2], [0.9,0.8]],
                    'text_times':[[1,4], [1,4]],'duration':5, 'fps':30,
                    # 'clip_trans': [{'trans_name': 'zoom_transition', 'trans_args': {}},
                                #    {'trans_name': 'slide_transition', 'trans_args': {'direction':'up'}}]
                    },
    'SplitProduct5': {'num_clips': 1, 'clip_pos': [[0,0]], 'clip_times': [[1.5,5]], 'clip_dims': [['width//2','height']],
                      'num_texts':1, 'text_pos':[[0,0]], 'text_times':[[0,5]],'duration':5, 'fps':30,
                      'clip_trans': [{'trans_name': 'slide_transition', 'trans_args': {'direction':'down'}}]
                     }
}

template_config = {
    'SimpleTemplate': {
        6:
            {'blocks': [{'block_name':'SimpleBlock6',
                         'effects': [{'effect_name': 'move_effect',
                                      'effect_args': {'font_size':50, 'x1':0, 'y1':0, 'x2':0.5, 'y2':0.5, 'h2':None, 'w2':None,
                                                      'bg':None, 'vh':'height', 'vw':'width', 'color':'white',
                                                      'font':'/usr/local/share/fonts/relaxed/NotoSansTC-Medium.otf', 'fps':30}}
                                    ]}
                       ]
            },
        15:
            {'blocks': [{'block_name':'SimpleBlock5',
                         'effects': [{'effect_name': 'art_effect', 'effect_args': {'font_size':40, 'color':'white', 'align':'center',
                                     'font':'/usr/local/share/fonts/relaxed/NotoSansTC-Medium.otf', 'theme':[16,184,254], 'fps':30}}
                                    ]},
                       {'block_name':'SplitBlock5',
                        'effects': [{'effect_name': 'art_effect', 'effect_args': {'font_size':40, 'color':'white', 'align':'center',
                                     'font':'/usr/local/share/fonts/relaxed/NotoSansTC-Medium.otf', 'theme':[16,184,254], 'fps':30}}]*2,
                        },
                       
                       {'block_name':'SimpleBlock5',
                        'effects': [{'effect_name': 'art_effect', 'effect_args': {'font_size':40, 'color':'white', 'align':'center',
                                     'font':'/usr/local/share/fonts/relaxed/NotoSansTC-Medium.otf', 'theme':[16,184,254], 'fps':30}},
                                    ]}
                       ]
            }
    },
    'ProductTemplate': {
        15:
            {'blocks': [{'block_name':'SimpleBlock5',
                         'effects': [{'effect_name': 'art_effect', 'effect_args': {'font_size':50, 'color':'white', 'align':'center',
                                      'theme':[16,184,254],
                                      'font':'/usr/local/share/fonts/relaxed/NotoSansTC-Medium.otf', 'direction':'up', 'slide_out':True,
                                      'fps':30}}
                                    ]},
                       {'block_name':'SimpleBlock5',
                        'effects': [{'effect_name': 'slide_effect', 'effect_args': {'font_size':50, 'color':'black', 'align':'center',
                                     'font':'/usr/local/share/fonts/relaxed/NotoSansTC-Medium.otf', 'direction':'up', 'slide_out':True,
                                     'fps':30}}
                                    ]},
                       {'block_name':'SplitProduct5',
                        'effects': [{'effect_name': 'slide_move_effect', 'effect_args': {'font_size':50, 'x1':0.5, 'y1':0.5,
                                     'x2':0.85, 'y2':0.5, 'h2':None, 'w2':None, 'vh':'height', 'vw':'width', 'color':'white',
                                     'align':'center', 'font':'/usr/local/share/fonts/relaxed/NotoSansTC-Medium.otf',
                                     'direction':'right', 'slide_out':False,
                                     'fps':30}},
                                    ]
                        }
                       ]
            }
    }
}