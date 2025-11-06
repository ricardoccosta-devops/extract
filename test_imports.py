"""Script de teste para verificar imports."""

import sys
from pathlib import Path

print("Python path:")
for p in sys.path:
    print(f"  {p}")

print(f"\nDiretório atual: {Path.cwd()}")
print(f"Arquivo main.py existe: {Path('main.py').exists()}")

print("\nTestando imports...")
try:
    print("1. Importando config...")
    from config import get_settings
    print("   ✓ config importado com sucesso")
except Exception as e:
    print(f"   ✗ Erro ao importar config: {e}")

try:
    print("2. Importando modules...")
    from modules.file_ingestion import FileIngestionService
    print("   ✓ modules importado com sucesso")
except Exception as e:
    print(f"   ✗ Erro ao importar modules: {e}")

try:
    print("3. Importando providers...")
    from providers import OpenAIProvider
    print("   ✓ providers importado com sucesso")
except Exception as e:
    print(f"   ✗ Erro ao importar providers: {e}")

try:
    print("4. Importando frontend...")
    from frontend.app import main
    print("   ✓ frontend importado com sucesso")
except Exception as e:
    print(f"   ✗ Erro ao importar frontend: {e}")

