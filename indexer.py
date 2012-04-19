import logging
import json

from models import InvertedIndex
from tokenizer import tokenize,normalize

def add_page_to_index(index, url, content):
    keywords = tokenize(normalize(content))
    pos = 0
    for keyword in keywords:
        add_to_index(index, keyword, url, pos)
        pos += 1

def add_to_index(index, keyword, url, pos):
    if keyword in index:
        if url in index[keyword]:
            index[keyword][url].append(pos)
        else:
            index[keyword][url] = [pos]
    else:
        index[keyword] = {url:[pos]}

def store_index_in_db(index, user):
    for keyword, value in index.iteritems():
        ii = InvertedIndex.get_by_key_name(keyword, parent=user)
        if ii is None:
            ii = InvertedIndex(parent=user, key_name=keyword, keyword=keyword, doc_ids=json.dumps(value))
            ii.put()
        else:
            doc_ids = json.loads(ii.doc_ids)
            doc_ids.update(value)
            ii.doc_ids = json.dumps(doc_ids)
            ii.put()
