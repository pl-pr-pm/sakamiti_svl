"""
TODO
1. Use SSM parameter
2. Use SAM Template
3. Use logging
"""
print('start authorizer')
import os
import logging

# loggerの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

source = os.environ['source']
logger.debug(f'source is {source}')

def _res_func_res(is_collect):
    
    func_res = {
        "isAuthorized":is_collect,
        "context":{}
    }
    
    return func_res

def _check_header(headers, target):
    
    if headers is None:
        return False
    
    if headers[target] is not None:
        return True
"""

"""
def check_source(headers, source):
    
    is_exist_referer = _check_header(headers, 'referer')
    
    if not is_exist_referer:
        return False
    
    referer = headers['referer']

    if referer == source:
        return True  

"""
def check_extention(headers, func):
    
    is_exist_extention = _check_header(headers, 'content-type')
    
    if not is_exist_extention:
        return False
    
    extention = headers['content-type']
    
    if extention is func:
        
        return True 
"""

def lambda_handler(event, context):
    
    try:
        headers = event['headers']
        
        logger.debug(f'headers is {headers}')
        
        if check_source(headers, source):
            aut_res = _res_func_res(is_collect=True)
        
        else:
            aut_res = _res_func_res(is_collect=False)
        
        return aut_res
    
    except:
        aut_res = _res_func_res(is_collect=False)
        return aut_res
        