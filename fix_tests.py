import os
import re

tests_dir = 'backend/tests'

for root, _, files in os.walk(tests_dir):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Fix single line calls: client.post("/auth/login", json={"email": ...})
            # Also multiline json that might start on the same line or next line
            # It's easier to find the index of "/auth/login", find the next {"email": and replace it.
            
            parts = content.split('"/auth/login"')
            if len(parts) > 1:
                for i in range(1, len(parts)):
                    # Look ahead in parts[i] for the first "email": and replace with "identifier":
                    # but only if it's within a few characters (like in the json payload)
                    match = re.search(r'^\s*,?\s*json_data=\s*\{\s*"email"|^\s*,?\s*json=\s*\{\s*"email"|^\s*,?\s*json=\s*\{\s*\n\s*"email"', parts[i])
                    if match:
                        parts[i] = parts[i][:match.start()] + match.group(0).replace('"email"', '"identifier"') + parts[i][match.end():]
                
                new_content = '"/auth/login"'.join(parts)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
