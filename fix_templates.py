import os
import re

files = [
    r"c:\Users\VICTUS 16\OneDrive\Desktop\detch website\flask deutchAI\templates\dashboard.html",
    r"c:\Users\VICTUS 16\OneDrive\Desktop\detch website\flask deutchAI\templates\setting.html",
    r"c:\Users\VICTUS 16\OneDrive\Desktop\detch website\flask deutchAI\templates\chat.html",
    r"c:\Users\VICTUS 16\OneDrive\Desktop\detch website\flask deutchAI\templates\call.html"
]

for f_path in files:
    if not os.path.exists(f_path):
        print(f"File not found: {f_path}")
        continue
        
    with open(f_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Match the weird { \n % if ... % \n } pattern
    # Pattern: optional whitespace, then '{', then newline/whitespace, then '% if lang_dir=='rtl' %', then newline/whitespace, then '}'
    # We'll use a regex that matches this block specifically.
    
    new_content = re.sub(
        r'\s*{\s*%\s*if\s+lang_dir\s*==\s*\'rtl\'\s*%\s*}', 
        "\n        {% if lang_dir == 'rtl' %}", 
        content
    )
    new_content = re.sub(
        r'\s*{\s*%\s*endif\s*%\s*}', 
        "\n        {% endif %}", 
        new_content
    )
    
    if new_content != content:
        with open(f_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed: {f_path}")
    else:
        print(f"No changes needed or could not match patterns in: {f_path}")
