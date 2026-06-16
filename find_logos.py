import os

# Search both the workspace and the parent scratch directory for image files
dirs_to_search = [
    ".",
    "..",
    "../.."
]

image_exts = ['.png', '.jpg', '.jpeg', '.svg', '.gif', '.ico', '.webp']

print("Searching for images/logos:")
for d in dirs_to_search:
    abs_d = os.path.abspath(d)
    if os.path.exists(abs_d):
        print(f"Directory: {abs_d}")
        try:
            for item in os.listdir(abs_d):
                path = os.path.join(abs_d, item)
                if os.path.isfile(path):
                    ext = os.path.splitext(item)[1].lower()
                    if ext in image_exts or 'logo' in item.lower():
                        print(f"  Found file: {item} ({os.path.getsize(path)} bytes) at {path}")
        except Exception as e:
            print(f"  Error reading {abs_d}: {str(e)}")
