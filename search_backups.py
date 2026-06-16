import os

funcs = [
    'renderSsnRecipes', 'loadFseTransmissions', 'viewFseXml', 'resendFse',
    'loadStsInvoices', 'toggleStsSelectAll', 'sendStsSelected', 'exportStsXmlSelected',
    'loadDoctorCompensations', 'renderCompRules', 'renderCompensations', 'saveCompConfig',
    'deleteCompConfig', 'payDoctorCompensations', 'loadLicenseInfo', 'activateNewLicense',
    'closeWhatsNewModal', 'populateDropdownsRIS', 'customCheckinSubmit'
]

files_to_check = ['app.js.bak', 'app.js.bak2', 'additional_js_code.js']
for filename in files_to_check:
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        found = [func for func in funcs if func in content]
        print(f"File {filename} contains functions: {found}")
    else:
        print(f"File {filename} does not exist")
