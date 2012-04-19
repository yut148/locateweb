# -*- coding: utf-8 -*-

import re

def normalize(content):
    return content.lower()

'''
def tokenize(content):
    return re.sub(r'(?=[^a-zA-Z0-9])', ' ', content).split()
'''

def tokenize(content):
    tokens = []
    token = ''
    for c in content:
        if re.match('[ \t\n\r]',c):
            if len(token) > 0:
                tokens.append(token)
                token = ''
        elif re.match('[a-zA-Z0-9]',c):
            token += c
        else:
            if len(token):
                tokens.append(token)
                token = ''
            tokens.append(c)
    if len(token):
        tokens.append(token)
        token = ''
    return tokens
