def get_bbox(arg):
    return arg['lowerCorner'].replace(' ', ',') + '~' + arg['upperCorner'].replace(' ', ',')