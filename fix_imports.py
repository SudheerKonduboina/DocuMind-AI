import os
import re

def fix_imports_in_file(filepath):
    """Fix imports in a single file to use backend. prefix consistently."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix: from config. -> from backend.config.
    content = re.sub(r'from config\.', 'from backend.config.', content)
    
    # Fix: from core. -> from backend.core.
    content = re.sub(r'from core\.', 'from backend.core.', content)
    
    # Fix: from database. -> from backend.database.
    content = re.sub(r'from database\.', 'from backend.database.', content)
    
    # Fix: from modules\. -> from backend.modules.
    content = re.sub(r'from modules\.', 'from backend.modules.', content)
    
    # Fix: from database import -> from backend.database import (without dot)
    content = re.sub(r'from database import', 'from backend.database import', content)
    
    # Fix: from core import -> from backend.core import (without dot)
    content = re.sub(r'from core import', 'from backend.core import', content)
    
    # Fix: from config import -> from backend.config import (without dot)
    content = re.sub(r'from config import', 'from backend.config import', content)
    
    # Fix: from .base -> from backend.database.base (in database folder)
    content = re.sub(r'from \.base import', 'from backend.database.base import', content)
    content = re.sub(r'from \.session import', 'from backend.database.session import', content)
    content = re.sub(r'from \.init_db import', 'from backend.database.init_db import', content)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def fix_all_imports(root_dir):
    """Recursively fix all Python files in the backend directory."""
    fixed_count = 0
    for root, dirs, files in os.walk(root_dir):
        # Skip __pycache__ and tests
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.pytest_cache', 'venv', 'env']]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if fix_imports_in_file(filepath):
                    print(f"Fixed: {filepath}")
                    fixed_count += 1
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == "__main__":
    backend_dir = r"c:\Users\kondu\CascadeProjects\ai-doc-qa-app\backend"
    fix_all_imports(backend_dir)
