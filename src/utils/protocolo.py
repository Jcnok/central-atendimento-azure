import datetime
import random
import string

def gerar_protocolo() -> str:
    """
    Gera um número de protocolo único no formato YYYYMMDDHHMMSS-XXXX.
    Exemplo: 20231027103000-A1B2
    """
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{timestamp}-{suffix}"
