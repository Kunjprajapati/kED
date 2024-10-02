import pandas as pd 
import numpy as np
import os 
import warnings
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)
warnings.filterwarnings('ignore', category=FutureWarning)  

# Reading Both the excel files
# pathing = "MAG_charges_07.01.2024" 
def function_for_MAG(pathing):  
    # data = pd.read_excel(f'{pathing}')
    # data.head()
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
    # result['Assigned Emp ID#'] = "RAC086"
    # result['Assigned Emp ID#'] = "RMM065"
    result['Assigned Emp ID#'] = "RAM099"
    result["Claim# / Visit#"] = "N/A"


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

    pathing = pathing.replace(".", "") 
    output_dir = 'Results/DailyCharges/MAG'
    os.makedirs(output_dir, exist_ok=True)


    filename = os.path.basename(pathing)
    filename_no_ext = os.path.splitext(filename)[0]
    parts = filename_no_ext.split('_')[-1]
    kunjdate = parts[:8]
    output_path = os.path.join(output_dir, f'MAG_Charges_of_{kunjdate}.xlsx')
    result.to_excel(f'{output_path}', index=False)

    return output_path