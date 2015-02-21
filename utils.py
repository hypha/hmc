__author__ = 'raquel'

uni, byt, xinput = str, bytes, input


def utf8_encode(x):
    return x.encode("utf8") if isinstance(x, uni) else x

def utf8_decode(x):
    return x.decode("utf8") if isinstance(x, byt) else x