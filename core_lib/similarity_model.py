import nmslib
from core_lib.mongo_models import Embedding
import numpy as np

def get_one_vector(text):
    wordvects = []
    tlist = text.split()
    for word in tlist:
        value = Embedding.objects(word=word).first()
        if value is None:
            #print(tlist)
            print(f'{word} not found')
            continue
        vects = value['vectors']
        wordvects.append(vects)
        
        
    return np.mean(wordvects,axis=0)

def get_combined_vector(terms):
    wordvects = []
    for term in terms:
        wordvects.append(get_one_vector(term))
    return np.mean(wordvects,axis=0)

class SimilarityModel:
    def __init__(self,values=None,saved_model=None):
        if values is None and saved_model is None:
            print()
            raise Exception('need either values or saved model to construct a KNN model--both cannot be None')
        knn = nmslib.init(method='hnsw', space='cosinesimil')
        if values is not None:
            knn.addDataPointBatch(values)
            knn.createIndex({'post': 2}, print_progress=True)
        else:
            knn.loadIndex(saved_model, load_data=True)
            print('saved model loaded')
        self.model = knn
        
    def predict(self,vectors,k=10):
        ids, distances = self.model.knnQuery(vectors,k=k)
        return ids,distances
    def save(self):
        pass
    def load(self):
        pass