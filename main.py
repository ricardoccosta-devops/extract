"""Ponto de entrada principal da aplicação Streamlit."""

import sys
from pathlib import Path

# Configura o path antes de qualquer import
# Isso garante que os módulos possam ser encontrados
_script_dir = Path(__file__).resolve().parent
if str(_script_dir) not in sys.path:
    sys.path.insert(0, str(_script_dir))

# Agora importa a aplicação
from frontend.app import main

# Executa quando o script é chamado diretamente ou pelo Streamlit
if __name__ == "__main__":
    main()
else:
    # Se executado pelo Streamlit, também executa
    main()
