import redis
import json 

try: 
    redisClient = redis.Redis(connection_pool=redis.ConnectionPool(host='localhost', port=6379, db=0))
except Exception as connectionError:
    print(connectionError);


def getItemsList():
    try: 
        results     = redisClient.execute_command("scan", 0, "MATCH","category:*","count", 200);
        if results is None: return 
        queryParams = [i.decode('utf-8') for i in results[1]]
        response    = redisClient.mget(queryParams)
        return list(map( lambda x: x.decode('utf-8'), response))
    except Exception as error:
        print(error)

    finally:
        redisClient.close();


class Cache:
    def __init__(self, categoryBlock):
        self.categoryBlock = categoryBlock or dict();

    @staticmethod
    def addToCache(categoryBlock = {}, expire=False):
        if type(categoryBlock) == dict:
            cacheKey        = categoryBlock.get('cacheKey','');
            cacheKeyTimeout = categoryBlock.get('cacheKeyTimeout','');
            originalData    = categoryBlock.get('originalData', {})
            try:
                redisClient.setex(cacheKey, cacheKeyTimeout, json.dumps(originalData) )
            except Exception as msetError:
                print(msetError)
                return

