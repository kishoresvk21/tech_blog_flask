from flask import abort


def get_paginated_list(results, url, start, limit, with_params):
    start = int(start)
    limit = int(limit)
    count = len(results)
    if count < start or limit < 0:
        abort(404)
    # make response
    obj = {}
    obj['start'] = start
    obj['limit'] = limit
    obj['count'] = count
    # make URLs
    # make previous url
    if start == 1:
        obj['previous'] = ''
    else:
        start_copy = max(1, start - limit)
        limit_copy = start - 1
        if with_params:
            obj['previous'] = url + '&start=%d&limit=%d' % (start_copy, limit_copy)
        else:
            obj['previous'] = url + '?start=%d&limit=%d' % (start_copy, limit_copy)
    # make next url
    if start + limit > count:
        obj['next'] = ''
    else:
        start_copy = start + limit
        if with_params:
            obj['next'] = url + '&start=%d&limit=%d' % (start_copy, limit)
        else:
            obj['next'] = url + '?start=%d&limit=%d' % (start_copy, limit)

    # finally extract result according to bounds
    obj['results'] = results[(start - 1):(start - 1 + limit)]
    return obj