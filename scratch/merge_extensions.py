import os

app_js_path = 'app.js'
ext_js_path = os.path.join('scratch', 'app_extensions.js')

with open(app_js_path, 'r', encoding='utf-8') as f:
    content = f.read()

# We look for the start of the extensions block
marker = '// =============================================================\n// NEXTCARE EXTENSIONS: DIRECT SSN ACCEPTANCE & CUSTOM HANDLERS\n// ============================================================='
if marker not in content:
    # Let's try matching with different line endings
    marker = marker.replace('\n', '\r\n')

if marker in content:
    print("Found marker. Split content.")
    parts = content.split(marker)
    base_content = parts[0]
else:
    # If the marker is not found exactly, let's find window.navigateToCompanyPortal
    fallback_marker = 'window.navigateToCompanyPortal = function(piva) {\nwindow.open(`company_portal.html?piva=${encodeURIComponent(piva)}`, \'_blank\');\n};'
    if fallback_marker not in content:
        fallback_marker = fallback_marker.replace('\n', '\r\n')
    
    if fallback_marker in content:
        print("Found fallback_marker. Split content.")
        parts = content.split(fallback_marker)
        base_content = parts[0] + fallback_marker + '\n\n'
    else:
        raise Exception("Could not find start marker for extensions block!")

with open(ext_js_path, 'r', encoding='utf-8') as f:
    ext_content = f.read()

# Create backup
backup_path = 'app.js.bak3'
with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Backup saved to {backup_path}")

# Write new app.js
new_content = base_content + ext_content
with open(app_js_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print("Successfully merged extensions into app.js")
