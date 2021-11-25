from core_lib.similarity_model import SimilarityModel, get_combined_vector
import pandas as pd
import numpy as np
from core_lib.pronto_conf import *
from core_lib.platform_utils import *
from core_lib.mongo_utils import *
import random
import os
from core_lib.core_utils import *
from sentence_transformers import SentenceTransformer

def setup_model():
    local_base_path = LOCAL_PRONTO_VISUAL_BASE
    model_name = TRANSFORMER_MODEL_NAME
    print(f'MODEL PATH = {local_base_path+model_name}')
    sent_to_vect_model = SentenceTransformer(local_base_path+model_name,device='cpu')
    print('Sentence Transformer model initialized')
    return sent_to_vect_model


    
def get_clips_by_sent_to_vect(bucket,
                           model,
                           key_terms=[],
                           k=6,
                           industry=None,
                           business_type=None,
                           vo_text=None,
                           num_industry_clips=6,
                           library='pronto',
                           sim_model=None,
                           logger=None):
    
    
    try:
        df = get_df(library=library)
    except Exception as e:
        raise Exception(f'getting dataframe failed with exception {e}')
    #df_ind = None
    
    sim_model_ind = None
    if len(key_terms) == 0 and industry is not None:
        key_terms = [industry]
    logger.info(f'KEY TERMS = {key_terms}')
    if industry is not None and num_industry_clips > 0:
        try:
            #df_ind = df[df['visual_bucket'] == industry].reset_index()
            df = df[df['visual_bucket'] == industry].reset_index()
            logger.info(f'INDUSTRY CASE: DF LENGTH = {len(df)}')
            #df = df[df['category'] == 'extra'].reset_index()
        except Exception as e:
            logger.error(f'getting dataframe for industry {industry} failed with exception {e}')
            df = None
    else:
        logger.info(f'EXTRA CASE: DF LENGTH = {len(df)}')
        df = df[df['category'] == 'extra'].reset_index()
        
    k_for_search = k
    if sim_model is None:
        try:
            desc_emb = pd.DataFrame.from_records(df['vectors'].values)
            sim_model = SimilarityModel(values=desc_emb)
        except Exception as e:
            raise Exception(f'creating similarity model failed with exception {e}')
    #if df_ind is not None:
    #    try:
    #        desc_emb_ind = pd.DataFrame.from_records(df_ind['vectors'].values)
    #        sim_model_ind = SimilarityModel(values=desc_emb_ind)
    #        k_for_search = k_for_search - num_industry_clips
    #    except Exception as e:
    #        raise Exception(f'creating industry similarity model failed with exception {e}')
        
    query = ' '
    if vo_text is not None:
        query = vo_text   
    if len(key_terms) > 0:
        q = key_terms 
        q = ', '.join(key_terms)
        query = q + ' ,' + query
    q = model.encode([query])
    
    #searched_ind = []
    #if df_ind is not None:
    #    ind_ids, ind_distances = sim_model_ind.predict(q,k=num_industry_clips)
    #    logger.info(f'IND IDS = {ind_ids}')
    #    logger.info(f'IND DISTANCES = {ind_distances}')
    #    df_filtered_ind = df_ind.loc[ind_ids] 
    #    searched_ind = list(df_filtered_ind['Video'].values)
        
    ids, distances = sim_model.predict(q,k=k_for_search)
    logger.info(f'DISTANCES = {distances}')
    df_filtered = df.loc[ids] 
    searched = list(df_filtered['Video'].values)
    #searched = searched_ind + searched
    logger.debug(f'////// SEARCHED CLIPS = {searched}')
    #first = searched[0]
    #logger.debug(f'SEARCHED 0 is {first}')
    return list(dict.fromkeys(searched))

                           
def get_clips_by_random_search(bucket,
                           model,
                           key_terms=[],
                           k=6,
                           industry=None,
                           business_type=None,
                           library='pronto',
                           logger=None):
    
    try:
        df = get_df(library=library)
    except Exception as e:
        raise Exception(f'getting dataframe failed with exception {e}')
        
    k_for_search = k
    df_filtered = df[df['visual_bucket'] == industry.lower()]
    df_filtered = df_filtered.sample(k_for_search)
    #df_filtered = df_filtered[6:k+6]
    searched = list(df_filtered['Video'].values)
    if logger:
        logger.debug('SEARCHED')
        logger.debug(searched)
    logger.debug('SEARCHED')
    logger.debug(searched) 
    return list(dict.fromkeys(searched))

def get_replacement_clip(selected_clips,clip_to_replace):
    count = 0
    while True:
        new_clip = random.sample(selected_clips,1)
        if new_clip[0] != clip_to_replace:
            ret = new_clip
            break
        count +=1
        if count >= 100:
            ret = []
            break
    return ret
    
 
def get_extra_clips(business_type,visual_bucket,num_clips=6,logger=None):
    local_df_path = get_df_file()
    try:
        df = pd.read_parquet(local_df_path)
    except Exception as e:
        raise Exception(f'read_parquet failed with exception {e}')    
    extras_list = get_extra_buckets_for_btypes(business_type)
    logger.debug(f'NUM SAMPLES = {num_clips} BUSINESS TYPE {business_type} EXTRAS = {extras_list}')
    df_filtered = df[(df['category'] == 'extra') & (df['visual_bucket'].isin(extras_list))]
    logger.debug(f'WWWWWWWWWWWWW :LEN OF DF FILTERED = {len(df_filtered)}')
    df_final = df_filtered.sample(n=num_clips,replace=True)
    clip_list = list(df_final.Video.values)
    return clip_list
    


def search_footage(
                model,
                industry,
                business_type,
                key_terms=[],
                images=None,
                clips=None,
                k=6,
                clip_to_replace='',
                library='pronto',
                vo_text=None,
                num_industry_clips=6,
                logger=None):

    master_bucket = MAIN_BUCKET

    #if industry is not None:
    #    key_terms += [industry.lower()]
        
    local_base_path=LOCAL_PRONTO_VISUAL_BASE
    #if vo_text is not None and CLIP_SEARCH_STRATEGY == 'text':
    if CLIP_SEARCH_STRATEGY == 'text':
        return get_clips_by_sent_to_vect(
                           master_bucket,
                           model,
                           key_terms,
                           k=k,
                           industry=industry,
                           vo_text=vo_text,
                           num_industry_clips=num_industry_clips,
                           logger=logger)
    else:
        selected_clips = []
        ret = get_clips_by_random_search(
                               master_bucket,
                               model,
                               key_terms,
                               k=k,
                               industry=industry,
                               logger=logger)
        
        if ret is not None and len(ret) > 0:
           selected_clips += ret
        return selected_clips    
    
    