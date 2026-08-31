import os
import re

def fix_crud_files():
    crud_dir = os.path.join(os.path.dirname(__file__), "app", "crud")
    pattern = re.compile(r"(result = self\.db\.execute\(stmt\))\s*self\.db\.commit\(\)\s*return result\.scalar_one_or_none\(\)")
    replacement = r"\1\n        item = result.scalar_one_or_none()\n        self.db.commit()\n        return item"
    
    for filename in os.listdir(crud_dir):
        if filename.endswith(".py"):
            filepath = os.path.join(crud_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            new_content = pattern.sub(replacement, content)
            
            if new_content != content:
                print(f"Fixed {filename}")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_content)

if __name__ == "__main__":
    fix_crud_files()
