def sigmaActions(r, occur):
    '''
    Every small step counts.
    '''

    r.lpush('actions', occur)
    # record last 9999 actions timenode
    if r.llen('actions') > 9999:
        r.ltrim('actions', 0, 9999)
