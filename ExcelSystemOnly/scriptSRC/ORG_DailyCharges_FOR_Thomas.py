import pandas as pd 
import numpy as np
from time import time
import os 
# Reading Both the excel files 
# data = pd.read_excel('06182024.xlsx')
import warnings
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)
warnings.filterwarnings('ignore', category=FutureWarning)  

def function_for_Thomas(pathing):
    # data = pd.read_excel(pathing)
    file_ext = os.path.splitext(pathing)[1]
    if file_ext == '.csv':
        data = pd.read_csv(pathing)
        # Convert CSV to XLSX immediately after reading
        temp_xlsx_path = os.path.splitext(pathing)[0] + '.xlsx'
        data.to_excel(temp_xlsx_path, index=False)
        # Update pathing to use the new XLSX file for further processing
        pathing = temp_xlsx_path
        data = pd.read_excel(pathing)
    elif file_ext == '.xlsx':
        data = pd.read_excel(pathing)
    desired_cols = ['File Name', 'Page#', 'Provider Name' ,'Location','Reason',  'Claim# / Visit#', 'Appt Status', 'DOS', 'Account# / #MRN#','Patient Name','DOB', 'Insurance', 'Batch ID', "Assigned Emp ID#"]

    # result = data.reindex(desired_cols)
    # Blanks -> File Name, Page#, Claim# / Visit#, Batch ID, Assigned Emp ID#, 
    rename_cols = {
        'office_name' : 'Location', 
        'checkin_date' : 'DOS', 
        'Provider' : 'Provider Name', 
        'procedure_name' : 'Reason', 
        'patient_name' : 'Patient Name', 
        'patient_bdate' : 'DOB', 
        'carrier_name' : 'Insurance', 
        'patient_no' : 'Account# / #MRN#', 
    }


    # Mentioning Certain Changes in the Downloaded Excel Format. 
    result = data.copy()
    result["Appt Status"] = " "
    result["File Name"] = " "
    result["Page#"] = " "
    result["Batch ID"] = " "
    result["Claim# / Visit#"] = "NA"
    result["Assigned Emp ID#"] = " "

    result.rename(columns=rename_cols, inplace=True)

    # Intersection, Between Two list.......To Obtain the resultant File, With Specific File Format. 
    req_cols = result.columns.intersection(desired_cols)

    result = result[req_cols]

    result = result.reindex(columns=desired_cols)

    # To Change the Date Format.  
    result['DOS'] = pd.to_datetime(result['DOS'])
    result['DOS'] = result['DOS'].dt.strftime('%B %d, %Y')

    result['DOB'] = pd.to_datetime(result['DOB'])
    result['DOB'] = result['DOB'].dt.strftime('%B %d, %Y')

    output_dir = 'Results/DailyCharges/Thomas'
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(pathing)
    filename_no_ext = os.path.splitext(filename)[0]
    parts = filename_no_ext.split('_')
    kunjdate = parts[-1] 
    output_path = os.path.join(output_dir, f'Thomas_charges_of_{kunjdate}.xlsx')
    result.to_excel(f'{output_path}', index=False)

    return output_path