import pickle
import base64


def dumps(mydict):
    """将字典转化成字符串"""
    bytes_hex = pickle.dumps(mydict)
    bytes_64 = base64.b64encode(bytes_hex)
    return bytes_64.decode()


def loads(mystr):
    """将字符串转为字典"""
    bytes_64 = mystr.encode()
    bytes_hex = base64.b64decode(bytes_64)
    return pickle.loads(bytes_hex)
