import os

scratch_dir = r"C:\Users\robpiron\.gemini\antigravity\brain\b6a0698d-44d4-4051-93fe-d78e80182f55\scratch"
target_words = ['renderSsnRecipes', 'loadFseTransmissions', 'loadStsInvoices', 'loadDoctorCompensations', 'loadLicenseInfo']

for filename in os.listdir(scratch_dir):
    path = os.path.join(scratch_dir, filename)
    if os.path.isfile(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            found = [w for w in target_words if w in content]
            if found:
                print(f"File {filename} contains target words: {found}")
        except Exception as e:
            pass
