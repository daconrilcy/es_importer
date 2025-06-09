from ctypes import c_char_p, c_int, c_char
from _ctypes import POINTER

phonex_signature = {
    "phonex_auto_alloc": {
        "argtypes": [c_char_p, c_char_p, c_int],
        "restype": POINTER(c_char)
    },
    "phonex_free": {
        "argtypes": [c_char_p],
        "restype": None
    }
}
