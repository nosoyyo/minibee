import redis


def sigmaActions(occur):
    '''
    Every small step counts.
    '''
    cpool = redis.ConnectionPool(host='localhost',
                             port=6379,
                             decode_responses=True,
                             db=0,)
    r = redis.Redis(connection_pool=cpool)

    r.lpush('actions', occur)
    # record last 9999 actions timenode
    if r.llen('actions') > 9999:
        r.ltrim('actions', 0, 9999)
