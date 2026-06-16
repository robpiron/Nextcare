import pandas as pd
import json
import os
import math

def generate_lis_seeds():
    xlsx_path = r"C:\Users\robpiron\scratch\esami_lis.xlsx"
    if not os.path.exists(xlsx_path):
        # fallback to current folder
        xlsx_path = "../esami_lis.xlsx"
        
    print(f"Reading LIS from {xlsx_path}...")
    df = pd.read_excel(xlsx_path)
    
    # Fill nan in ESAME with forward fill or drop? Usually they are grouped
    df['ESAME'] = df['ESAME'].ffill()
    
    services = []
    groups = df.groupby('ESAME', sort=False)
    
    for exam_name, group in groups:
        if not isinstance(exam_name, str) or exam_name.strip() == "":
            continue
            
        # Determine parent sample type
        sample_types = group['TIPO CAMPIONE'].dropna().unique()
        parent_sample = sample_types[0] if len(sample_types) > 0 else "TAPPO VIOLA"
        if not isinstance(parent_sample, str):
            parent_sample = "TAPPO VIOLA"
            
        parameters = []
        for idx, row in group.iterrows():
            param_name = row['PARAMETRO']
            if not isinstance(param_name, str) or param_name.strip() == "":
                continue
                
            unit = row['UNITA MISURA']
            if pd.isna(unit):
                unit = ""
            else:
                unit = str(unit).strip()
                
            ref_range = row['VALORI NORMALI']
            if pd.isna(ref_range):
                ref_range = ""
            else:
                ref_range = str(ref_range).strip()
                
            res_type = row['TIPO RISULTATO']
            if pd.isna(res_type):
                res_type = "ALFABETICO"
            else:
                res_type = str(res_type).strip().upper()
                if "NUM" in res_type:
                    res_type = "NUMERICO"
                else:
                    res_type = "ALFABETICO"
            
            param_sample = row['TIPO CAMPIONE']
            param_sample_val = None
            if not pd.isna(param_sample):
                param_sample_str = str(param_sample).strip()
                if param_sample_str != parent_sample:
                    param_sample_val = param_sample_str
            
            param_obj = {
                "name": param_name.strip(),
                "unit": unit,
                "reference_range": ref_range,
                "result_type": res_type
            }
            if param_sample_val:
                param_obj["sample_type"] = param_sample_val
                
            parameters.append(param_obj)
            
        services.append({
            "name": exam_name.strip(),
            "type": "lis",
            "sample_type": parent_sample,
            "parameters": parameters
        })
        
    out_path = "lis_services_seed.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(services, f, indent=4, ensure_ascii=False)
        
    print(f"Generated {len(services)} LIS exams in {out_path}")

def generate_ris_visite_seeds():
    xlsx_path = r"C:\Users\robpiron\scratch\poli.xlsx"
    if not os.path.exists(xlsx_path):
        xlsx_path = "../poli.xlsx"
        
    print(f"Reading RIS/Visite from {xlsx_path}...")
    df = pd.read_excel(xlsx_path)
    
    # Filter out Laboratorio
    df = df[df['Branca1'] != 'Laboratorio']
    
    services = []
    
    for idx, row in df.iterrows():
        # Code from DM column
        code = row['DM']
        if pd.isna(code):
            code = row['CUR 2024']
        if pd.isna(code):
            continue
        code = str(code).strip()
        
        # Name from DESCRIZIONE DM or fallback
        name = row['DESCRIZIONE DM']
        if pd.isna(name):
            name = row['DESCRIZIONE CUR 2024 (PRESTAZIONE SANITARIA)']
        if pd.isna(name):
            continue
        name = str(name).strip()
        
        # Branch
        branch = row['Branca1']
        if pd.isna(branch):
            branch = "Altre"
        else:
            branch = str(branch).strip()
            
        # Price
        price = row['Tariffa (dicembre 2024)']
        if pd.isna(price):
            price = 0.0
        else:
            try:
                price = float(price)
                if math.isnan(price):
                    price = 0.0
            except ValueError:
                price = 0.0
                
        # Type: ris if branch is Diagnostica per immagini, else visita
        is_ris = branch == "Diagnostica per immagini"
        srv_type = "ris" if is_ris else "visita"
        
        services.append({
            "name": name,
            "type": srv_type,
            "code": code,
            "branch": branch,
            "price": price,
            "clinic_id": 2 if is_ris else 1,
            "equipment_id": 1 if is_ris else None
        })
        
    out_path = "ris_visite_services_seed.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(services, f, indent=4, ensure_ascii=False)
        
    print(f"Generated {len(services)} RIS and Visite services in {out_path}")

if __name__ == "__main__":
    generate_lis_seeds()
    generate_ris_visite_seeds()
