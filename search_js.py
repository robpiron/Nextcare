import os

funcs = [
    'renderSsnRecipes', 'loadFseTransmissions', 'viewFseXml', 'resendFse',
    'loadStsInvoices', 'toggleStsSelectAll', 'sendStsSelected', 'exportStsXmlSelected',
    'loadDoctorCompensations', 'renderCompRules', 'renderCompensations', 'saveCompConfig',
    'deleteCompConfig', 'payDoctorCompensations', 'loadLicenseInfo', 'activateNewLicense',
    'closeWhatsNewModal', 'populateDropdownsRIS', 'customCheckinSubmit'
]

for filename in ['app.js', 'additional_js_code.js']:
    if not os.path.exists(filename):
        print(f"File {filename} does not exist")
        continue
    print(f"\n=== Searching in {filename} ===")
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    for func in funcs:
        idx = content.find(func)
        if idx != -1:
            print(f"Function {func} found! Snippet:")
            print(content[idx:idx+300])
            print("-" * 50)
        else:
            print(f"Function {func} NOT found")
