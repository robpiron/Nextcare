import os

funcs = [
    'renderSsnRecipes', 'loadFseTransmissions', 'viewFseXml', 'resendFse',
    'loadStsInvoices', 'toggleStsSelectAll', 'sendStsSelected', 'exportStsXmlSelected',
    'loadDoctorCompensations', 'renderCompRules', 'renderCompensations', 'saveCompConfig',
    'deleteCompConfig', 'payDoctorCompensations', 'loadLicenseInfo', 'activateNewLicense',
    'closeWhatsNewModal', 'populateDropdownsRIS', 'customCheckinSubmit'
]

for filename in os.listdir('.'):
    if filename.endswith('.js'):
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        found_funcs = []
        for func in funcs:
            if func in content:
                found_funcs.append(func)
        if found_funcs:
            print(f"File {filename} contains: {found_funcs}")
