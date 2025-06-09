from ctypes import cdll, c_char_p, c_char, c_int, POINTER, cast

lib = cdll.LoadLibrary("../libdoublemetaphone.dll")
lib.double_metaphone.argtypes = [c_char_p, c_char, c_int]
lib.double_metaphone.restype = POINTER(c_char)  # ← 🔥 pas c_char_p !

lib.double_metaphone_free.argtypes = [POINTER(c_char)]
lib.double_metaphone_free.restype = None

# Appel
raw = lib.double_metaphone(b"paris|lyon|marseille", b'|'[0], 6)
result = cast(raw, c_char_p).value  # convertir proprement

# Affichage
print(result.decode())

# Libération correcte
lib.double_metaphone_free(raw)
