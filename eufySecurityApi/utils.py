
import sys

def getUniqueId(obb):
    a = hex(hash(str(obb)) % ((sys.maxsize + 1) * 2))
    if(len(a) < 10):
        a += (''.join(['0' for i in range(0, 10-len(a))]))
    return a