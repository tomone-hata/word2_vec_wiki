#!/usr/bin/env python
# coding: utf-8

# ## 必要なライブラリのインポート

# In[1]:


from gensim.models import word2vec
import pandas as pd
import gc
from tqdm import tqdm
import logging


# ## 学習ファイルの読み込み(words)

# In[ ]:


df_words = pd.read_csv('output/wiki_text.txt', header=0, sep='\t', dtype=str, usecols=['words'])


# ## 学習用コーパスの前処理(words)
# 手元で実行した際にメモリSwapを起こしたので手動でガーベジコレクションの実施。

# In[ ]:


def texts_to_words(text):
    text_list = text.split(' ')
    return text_list

texts = [texts_to_words(str(item)) for item in tqdm(df_words['words']) if item]
del df_words
gc.collect()


# ## モデルの学習および保存(words)

# In[ ]:


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
texts_model = word2vec.Word2Vec(texts,size=200,min_count=5,window=5,iter=5)


# In[ ]:


texts_model.save('output/words_model.model')


# In[ ]:


del texts
del texts_model
gc.collect()


# ## モデルの作成(basic_words)
# basic_wordsも同様にモデルを作成する。

# In[ ]:


df_basic_words = pd.read_csv('output/wiki_text.txt', header=0, sep='\t', dtype=str, usecols=['basic_words'])
basic_texts = [texts_to_words(str(item)) for item in tqdm(df_basic_words['basic_words']) if item]
del df_basic_words
gc.collect()
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
basic_texts_model = word2vec.Word2Vec(basic_texts,size=200,min_count=5,window=5,iter=5)
basic_texts_model.save('output/basic_words_model.model')


# In[ ]:
