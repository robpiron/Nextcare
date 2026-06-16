import os

scratch_dir = r"C:\Users\robpiron\.gemini\antigravity\brain\b6a0698d-44d4-4051-93fe-d78e80182f55\scratch"
funcs = [
    'renderSsnRecipes', 'loadFseTransmissions', 'viewFseXml', 'resendFse',
    'loadStsInvoices', 'toggleStsSelectAll', 'sendStsSelected', 'exportStsXmlSelected',
    'loadDoctorCompensations', 'renderCompRules', 'renderCompensations', 'saveCompConfig',
    'deleteCompConfig', 'payDoctorCompensations', 'loadLicenseInfo', 'activateNewLicense',
    'closeWhatsNewModal', 'populateDropdownsRIS', 'customCheckinSubmit'
]

for filename in os.listdir(scratch_dir):
    path = os.path.join(scratch_dir, filename)
    if os.path.isfile(path) and filename.endswith('.py'):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            found = [func for func in funcs if func in content]
            if found:
                print(f"File {filename} contains functions: {found}")
        except Exception as e:
            pass
