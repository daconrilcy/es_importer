from ctypes import c_char_p, c_ubyte, c_int, c_void_p

metaphone3_signature = {
    "metaphone3_encode_multi_str": {
        "argtypes": [c_char_p, c_ubyte, c_int, c_int, c_int],
        "restype": c_void_p,  # On récupère un pointeur générique !
    },
    "free_result_str": {
        "argtypes": [c_void_p],  # On libère un pointeur générique !
        "restype": None,
    }
}
