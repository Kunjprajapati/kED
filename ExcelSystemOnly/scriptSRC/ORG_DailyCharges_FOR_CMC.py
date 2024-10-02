import pandas as pd 
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)
warnings.filterwarnings('ignore', category=FutureWarning)  

def function_for_CMC(pathing): 
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
    rename_cols = {
        'Physicain' : 'Provider Name', 
        'Service Location' : 'Location', 
        'Type Of Visit' : 'Reason', 
        'Visit Date' : 'DOS', 
        'MRN' : 'Account# / #MRN#', 
        'Patient' : 'Patient Name', 
        'DOB' : 'DOB', 
        'Primary Insurance' : 'Insurance'
    }

    # Perform data transformations
    result = data.copy()
    result["File Name"] = " "
    result["Page#"] = " "
    result["Appt Status"] = "Claim Not Generated"
    result["Batch ID"] = " "
    result['Assigned Emp ID#'] = "RAM115"
    result["Claim# / Visit#"] = "NA"

    result.rename(columns=rename_cols, inplace=True)

    req_cols = result.columns.intersection(desired_cols)
    result = result[req_cols]

    result = result.reindex(columns=desired_cols)

    result['DOS'] = pd.to_datetime(result['DOS']).dt.strftime('%B %d, %Y')
    result['DOB'] = pd.to_datetime(result['DOB']).dt.strftime('%B %d, %Y')

    # Creating a new dataframe for the output
    output_df = result.copy()

    # Save the processed Excel file
    output_dir = 'Results/DailyCharges/CMC'  
    os.makedirs(output_dir, exist_ok=True)

    filename = os.path.basename(pathing)
    filename_no_ext = os.path.splitext(filename)[0]
    parts = filename_no_ext.split('_')
    kunjdate = parts[-1]

    # Remove '.csv' from kunjdate if present
    if kunjdate.endswith('.csv'):
        kunjdate = kunjdate[:-4]  # Remove last 4 characters

    output_path = os.path.join(output_dir, f'CMC_Charges_of_{kunjdate}.xlsx')
    output_df.to_excel(output_path, index=False)  
    print(f"File saved at: {output_path}")
    return output_path