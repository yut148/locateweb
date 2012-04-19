# -*- coding: utf-8 -*-


import logging
import json
import operator
from models import InvertedIndex,Post
from tokenizer import tokenize, normalize

def search(user, query, type='and'):
    if type == 'phrase':
        ids = _phrase_search(user, query)
    else:
        ids = _and_search(user, query)
    #logging.info(ids)
    posts = Post.get_by_key_name(ids, parent=user)
    #logging.info(posts[0].message)
    return sorted(posts, key=operator.attrgetter('created_time'), reverse=True)


def _phrase_search(user, query):
    n = normalize(query)
    keywords = tokenize(n)
    logging.info('phrase_search: query: '+query)
    logging.info('n: '+n)
    logging.info('keywords:' + str(keywords))
    if not len(keywords):
        return []

    logging.info('%d - %s' % (0, keywords[0]));
    results = _lookup(user, keywords[0])
    if not results:
        return []
    logging.info('%s' % str(results));
    for i in range(1, len(keywords)):
        logging.info('%d - %s' % (i, keywords[i]));
        id_pos_dict = _lookup(user, keywords[i])
        logging.info('%s' % str(id_pos_dict));
        if id_pos_dict:
            for id in results.keys():
                if id not in id_pos_dict:
                    del results[id]
                else:
                    poses = []
                    for pos in id_pos_dict[id]:
                        if pos - 1 in results[id]:
                            poses.append(pos)
                    if not len(poses):
                        del results[id]
                    else:
                        results[id] = poses
        else:
            return []
    return results.keys()

def _and_search(user, query):
    n = normalize(query)
    keywords = tokenize(n)
    logging.info('and_search: query: '+query)
    logging.info('n: '+n)
    logging.info('keywords:' + str(keywords))
    if not len(keywords):
        return []

    results = _lookup(user, keywords[0])
    if not results:
        return []

    for i in range(1, len(keywords)):
        id_pos_dict = _lookup(user, keywords[i])
        if id_pos_dict:
            for id in results.keys():
                if id not in id_pos_dict:
                    del results[id]
        else:
            return []
    return results.keys()

def _lookup(user, keyword):
    ii = InvertedIndex.get_by_key_name(keyword, parent=user)
    if ii is None:
        return None
    else:
        return json.loads(ii.doc_ids)

