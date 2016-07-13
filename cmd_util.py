import os
#mettre dans a une clé de 24 char
a = os.urandom(24)
# encoder a et recevoir une chaine de char de lettre et de num
a.encode('base-64')

# ------------------------------------------------------------------------------

