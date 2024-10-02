import pandas as pd 
import numpy as np
import os 
# Reading Both the excel files 
# pathing = "RPL_charges_06.20.2024"
import warnings
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)
warnings.filterwarnings('ignore', category=FutureWarning)  

def function_for_RPL(pathing):
    # data = pd.read_csv(pathing)  # Read CSV file
    # data = pd.read_excel(pathing)  # Read CSV file
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
        'rndrng prvdr' : 'Provider Name', 
        'svc dprtmnt' : 'Location', 
        'appttype' : 'Reason', 
        'apptcancelreason' : 'Appt Status', 
        'apptdate' : 'DOS', 
        'patientid' : 'Account# / #MRN#', 
        'patient name' : 'Patient Name', 
        'patientdob' : 'DOB', 
        'appt ins pkg name' : 'Insurance'
    }

    # Mentioning Certain Changes in the Downloaded Excel Format. 
    result = data.copy()
    result["File Name"] = "-"
    result["Page#"] = "-"
    # result["Claim# / Visit#"] = " "
    result["Batch ID"] = "-"
    result['Assigned Emp ID#'] = "RAM112"
    result["Claim# / Visit#"] = "NA"


    result.rename(columns=rename_cols, inplace=True)

    # Intersection, Between Two list.......To Obtain the resultant File, With Specific File Format. 
    req_cols = result.columns.intersection(desired_cols)


    result = result[req_cols]

    result = result.reindex(columns=desired_cols)

    # To Change the Date Format. 
    from time import time 
    result['DOS'] = pd.to_datetime(result['DOS'])
    result['DOS'] = result['DOS'].dt.strftime('%B %d, %Y')

    # Adjusting the date format for 'DOB' to handle multiple formats
    result['DOB'] = pd.to_datetime(result['DOB'], infer_datetime_format=True)  # Automatically infer the correct format
    result['DOB'] = result['DOB'].dt.strftime('%B %d, %Y')


    # Arrange all 'Self Pay' the data at the bottom of the records. 
    first = result[result['Insurance'] == '*SELF PAY*']
    second = result[result['Insurance'] != '*SELF PAY*']

    # Concatenate to arrange 'Self pay' records at the bottom
    resultant = pd.concat([second, first]) 

    # Inserting "SOTOMAYOR_M" in Provider Name 
    resultant["Provider Name"] = resultant["Provider Name"].fillna("Watman_M")
    resultant["Appt Status"] = resultant["Appt Status"].fillna("Confirmed")

    # Removing all the unusuall data
    mask = resultant['Account# / #MRN#'].isnull() & resultant['DOB'].isnull() & resultant['Insurance'].str.contains(r'\*SELF PAY\*', case=False, na=False)
    filtered_data = resultant[~mask]

    # To convert Into Excel Format.
    pathing = pathing.replace(".", "") 
    output_dir = 'Results/DailyCharges/RPL'
    os.makedirs(output_dir, exist_ok=True)


    filename = os.path.basename(pathing)
    filename_no_ext = os.path.splitext(filename)[0]
    parts = filename_no_ext.split('_')
    kunjdate = parts[-1] 

    output_path = os.path.join(output_dir, f"RPL_charges_of_{kunjdate}.xlsx")
    filtered_data.to_excel(f'{output_path}', index=False)

    return output_path