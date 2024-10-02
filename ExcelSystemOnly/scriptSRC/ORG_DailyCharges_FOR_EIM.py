import pandas as pd
from datetime import datetime
import os  
import warnings
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)
warnings.filterwarnings('ignore', category=FutureWarning)  

def function_FOR_EIM(pathing):
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
    requiredIndex = list(data[data['Unnamed: 37'].notnull() == True].index)
    # print(f"Reasons Index: {requiredIndex}")
 
    # Creating a new DataFrame
    filtered_data = pd.DataFrame()
 
    # Inserting column of "Reason"
    filtered_data["Reason"] = data['Unnamed: 37'][requiredIndex]
 
    # Insering column of "Location"
    filtered_data["Location"] = list(data.columns)[0]
 
    # Insering column of "Appointment status"
    filtered_data['Appt Status'] = data['Unnamed: 41'][requiredIndex]
 
    # Inserting column of account
    acc = data['Unnamed: 17'][requiredIndex].apply(lambda x: x.split(" ")[-1])
    filtered_data["Account# / #MRN#"] = [acc.iloc[i][1:-1] for i in range(len(acc))]
 
    # Inserting column of Patient Name
    patientName = data['Unnamed: 17'][requiredIndex].apply(lambda x: x.split("(")[0])
    filtered_data['Patient Name'] = patientName
 
    # Inserting column of DOB
    filtered_data["DOB"] = data['Unnamed: 21'][requiredIndex]
    filtered_data["DOB"] = filtered_data["DOB"].apply(convert_date_DOB)
 
    # Attaching all the defauly columns
    filtered_data["File Name"] = " - "
    filtered_data['Page#'] = " - "
    filtered_data["Provider Name"] = " - "
    filtered_data["Insurance"] = " - "
    filtered_data["Batch ID"] = " - "
    filtered_data["Assigned Emp ID#"] = "RAM002"
    filtered_data['Claim# / Visit#'] = "N/A"
   
    desired_cols = ['File Name', 'Page#' ,'Provider Name', 'Location', 'Reason' ,'Claim# / Visit#', 'Appt Status', 'DOS', 'Account# / #MRN#', 'Patient Name', 'DOB', 'Insurance', 'Batch ID', 'Assigned Emp ID#']
    filtered_data = filtered_data.reindex(columns=desired_cols)

    # Inserting the logic for fetching and retriving the DOS from the RAW File. 
    dates = []
    dos_refference_index = list(data[data['Unnamed: 3'].notnull() == True]['Unnamed: 3'].index)
    grouped_indices = group_consecutive(dos_refference_index)
    lengths_of_groups = [len(group) for group in grouped_indices]
    dos_dates = list(data[data['Unnamed: 1'].notna() == True]['Unnamed: 1'])
    if len(lengths_of_groups) == len(dos_dates):
        for checker in range(len(lengths_of_groups)):
            for inserting in range(lengths_of_groups[checker]):
                # print(dos_dates[checker])
                dates.append(dos_dates[checker])
    else:
        filtered_data["DOS"] = "ERROR FETCHING....."

    filtered_data['DOS'] = dates
    filtered_data['DOS'] = filtered_data['DOS'].apply(convert_date_DOS)

    # print(filtered_data['DOS'])
    # Creaing a specific directory for EIM DailyCharges.....
    output_dir = 'Results/DailyCharges/EIM'
    os.makedirs(output_dir, exist_ok=True)

    filename = os.path.basename(pathing)
    filename_no_ext = os.path.splitext(filename)[0]
    parts = filename_no_ext.split('_')
    kunjdate = parts[-1] 

    output_dir = os.path.join(output_dir, f'EIM_Charges_of_{kunjdate}.xlsx')  # Ensure the extension is .xlsx
    filtered_data.to_excel(output_dir, index=False)

    return output_dir

 



def convert_date_DOB(date_str, input_format='%m/%d/%y', output_format='%B %d, %Y'):
    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except ValueError:
        return date_str

def convert_date_DOS(date_input, input_format='%Y-%m-%d %H:%M:%S', output_format='%B %d, %Y'):
    if pd.isnull(date_input):
        return None  # or return a default string like 'Unknown'
    if isinstance(date_input, pd.Timestamp):
        return date_input.strftime(output_format)
    try:
        date_obj = datetime.strptime(str(date_input), input_format)
        return date_obj.strftime(output_format)
    except ValueError:
        return str(date_input)  # Return the original input as string if there's a format error
 

def group_consecutive(lst):
    grouped = []
    temp = [lst[0]]
    
    for i in range(1, len(lst)):
        if lst[i] == lst[i-1] + 1:
            temp.append(lst[i])
        else:
            grouped.append(temp)
            temp = [lst[i]]
    grouped.append(temp)  # Append the last group
    return grouped