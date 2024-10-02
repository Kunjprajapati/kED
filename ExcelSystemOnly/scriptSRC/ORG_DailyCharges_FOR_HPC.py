import pandas as pd 
import numpy as np
import os 
# Reading Both the excel files
# pathing = "HPC_charges_06.20.2024" 
import warnings
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)
warnings.filterwarnings('ignore', category=FutureWarning)  

def function_for_HPC(pathing):
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
    # data.head()
    desired_cols = ['File Name', 'Page#' ,'Provider Name', 'Location', 'Reason' ,'Claim# / Visit#', 'Appt Status', 'DOS', 'Account# / #MRN#', 'Patient Name', 'DOB', 'Insurance', 'Batch ID', 'Assigned Emp ID#']

    # result = data.reindex(desired_cols)
    # Blanks -> File Name, Page#, Claim# / Visit#, Batch ID, Assigned Emp ID#, 
    rename_cols = {
        'Appointment Provider Name' : 'Provider Name', 
        'Appointment Facility Name' : 'Location', 
        'Visit Type' : 'Reason', 
        'Visit Status' : 'Appt Status', 
        'Appointment Date' : 'DOS', 
        'Patient Acct No' : 'Account# / #MRN#', 
        'Patient Name' : 'Patient Name', 
        'Patient DOB' : 'DOB', 
        'Primary Insurance Name' : 'Insurance'
    }


    # Mentioning Certain Changes in the Downloaded Excel Format. 
    result = data.copy()
    result["File Name"] = " "
    result["Page#"] = " "
    result["Claim# / Visit#"] = " "
    result["Batch ID"] = " "
    result["Claim# / Visit#"] = "N/A"
    result['Assigned Emp ID#'] = ""


    result.rename(columns=rename_cols, inplace=True)

    # Initialize 'Assigned Emp ID#' with a default value if it doesn't exist
    if 'Assigned Emp ID#' not in result.columns:
        result['Assigned Emp ID#'] = np.nan  # or any default value you prefer

    # Update Assigned Emp ID# based on conditions
    result['Assigned Emp ID#'] = np.where(
        (result['Appt Status'] == 'CHK : Check Out') & (result['Reason'] != 'NURSE : Nurse Visit'),
        'RAIO006',
        'RAM063'  # Fill all other rows with RAM063
    )

    # Intersection, Between Two list.......To Obtain the resultant File, With Specific File Format. 
    req_cols = result.columns.intersection(desired_cols)


    result = result[req_cols]

    result = result.reindex(columns=desired_cols)

    # To Change the Date Format. 
    from time import time 
    result['DOS'] = pd.to_datetime(result['DOS'])
    result['DOS'] = result['DOS'].dt.strftime('%B %d, %Y')

    result['DOB'] = pd.to_datetime(result['DOB'])
    result['DOB'] = result['DOB'].dt.strftime('%B %d, %Y')

    # To convert Into Excel Format.
    pathing = pathing.replace(".", "") 
    # result.to_excel(f"{pathing}.xlsx", index=0)
    # return result
    output_dir = 'Results/DailyCharges/HPC'
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(pathing)
    filename_no_ext = os.path.splitext(filename)[0]
    parts = filename_no_ext.split('_')
    kunjdate = parts[-1] 
    output_path = os.path.join(output_dir, f'HPC_charges_of_{kunjdate}.xlsx')
    result.to_excel(f'{output_path}', index=False)

    return output_path