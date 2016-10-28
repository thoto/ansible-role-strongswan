class TestModule(object):
    tests=lambda self: {'in': lambda l,v: v in l, '==':  lambda a,b: a==b,
            'inoreq': lambda l,v: v in l if type(l) is list else v==l,}
