from ctypes import c_char_p, c_int
from _ctypes import POINTER

metaphone_signature = {
    "metaphone_api": {
        "argtypes": [c_char_p, POINTER(c_char_p), c_char_p, c_int],
        "restype": None
    },
    "free_output": {
        "argtypes": [c_char_p],
        "restype": None
    }
}