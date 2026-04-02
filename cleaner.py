import os
import ast
import re

def process_python(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
            
        # Parse using AST and unparse to rebuild code without comments
        tree = ast.parse(code)
        clean_code = ast.unparse(tree)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(clean_code + '\n')
    except Exception as e:
        print(f"Failed to clean {file_path}: {e}")

def process_js(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Step 1: Remove JSX block comments {/* ... */}
        content = re.sub(r'\{\/\*.*?\*\/\}', '', content, flags=re.DOTALL)
        
        # Step 2: Remove standard JS block comments /* ... */
        content = re.sub(r'\/\*[\s\S]*?\*\/', '', content)
        
        # Step 3: Remove inline comments starting with // (but not inside urls like http://)
        lines = []
        for line in content.split('\n'):
            # simple check for // avoiding http:// or https://
            parts = line.split('//')
            if len(parts) > 1:
                # check if preceding chars are part of a URL or similar
                idx = line.find('//')
                if idx > 0 and line[idx-1] == ':':
                    lines.append(line)
                else:
                    lines.append(line[:idx])
            else:
                lines.append(line)

        # Remove extra empty lines
        final_lines = [l for l in lines if l.strip() != '']
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(final_lines) + '\n')
            
    except Exception as e:
        print(f"Failed to clean {file_path}: {e}")

# Process Backend (Python)
for root, dirs, files in os.walk('./backend/app'):
    for f in files:
        if f.endswith('.py'):
            process_python(os.path.join(root, f))

# Process Main
if os.path.exists('./backend/main.py'): process_python('./backend/main.py')

# Process Frontend (JS/JSX)
for root, dirs, files in os.walk('./frontend/src'):
    for f in files:
        if f.endswith(('.js', '.jsx', '.ts', '.tsx')):
            process_js(os.path.join(root, f))

print("Cleanup complete.")
