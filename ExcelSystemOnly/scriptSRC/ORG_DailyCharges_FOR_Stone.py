import pandas as pd 
import os 
import warnings
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)
warnings.filterwarnings('ignore', category=FutureWarning)  

def function_for_stoneCharges(pathing): 
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
    else:
        raise ValueError(f"Unsupported file extension: {file_ext}")

    # Every Columns is 
    start_index = data.index[data["Unnamed: 0"] == "Appointment Date"].tolist()
    start_index = start_index[0]
    # start_index
    # print(f"Start Index Including All the Corresponding Fields is from: {start_index}")

    date_column = pd.to_datetime(data["Unnamed: 0"], errors='coerce')  # 'coerce' will set invalid parsing to NaT
    date_only_rows = data[pd.notnull(date_column)]

    # helper = pd.to_datetime(data["Unnamed: 0"], errors='coerce')
    # date_only_rows = data[pd.notnull(helper)]
    date_only_length = len(date_only_rows)

    end_index = data.index[data["Unnamed: 0"] == f"* Total({date_only_length})"].tolist()
    end_index = end_index[0]


    # Creating Rename for all the Initial columns 
    filtered_data_cols = {
    "Unnamed: 0" : "Appointment Date", 
    "Unnamed: 1" :  "Time", 
    "Unnamed: 2" :  "Check In Time", 
    "Unnamed: 3" :  "Check Out Time",
    "Unnamed: 4" :  "Appointment Duaration",
    "Unnamed: 5" :  "Speciality Name", 
    "Unnamed: 6" :  "Facility", 
    "Unnamed: 7" :  "Scheduler", 
    "Unnamed: 8" :  "Appointment Type", 
    "Unnamed: 9" :  "Patient Name", 
    "Unnamed: 10" : "Chart #", 
    "Unnamed: 11" : "Patient DOB",
    "Unnamed: 12" : "Email" ,
    "Unnamed: 13" : "Contact1" ,
    "Unnamed: 14" : "Contact2" ,
    "Unnamed: 15" : "Appointment Full filled" ,
    "Unnamed: 16" : "Reason" ,
    "Unnamed: 17" : "Appointment Status" ,
    "Unnamed: 18" : "Deleted Date" ,
    "Unnamed: 19" : "Deleted By" ,
    "Unnamed: 20" : "Primary Insurance Name",
    "Unnamed: 21" : "Policy Number" ,
    "Unnamed: 22" : "Verified Status" ,
    "Unnamed: 23" : "Verified On" ,
    "Unnamed: 24" : "Verified By" ,
    "Unnamed: 25" : "Bill#" ,
    "Unnamed: 26" : "BillÂ Status" ,
    "Unnamed: 27" : "Plan Begin" ,
    "Unnamed: 28" : "Plan End" ,
    "Unnamed: 29" : "Secondary Insurance Name" ,
    "Unnamed: 30" : "Secondary Policy Number" ,
    "Unnamed: 31" : "Copay" ,
    "Unnamed: 32" : "Patient Due" ,
    "Unnamed: 33" : "CoÂ Ins(%)" ,
    "Unnamed: 34" : "Deductable" ,
    "Unnamed: 35" : "DeductableMet" ,
    "Unnamed: 36" : "Created Date" ,
    "Unnamed: 37" : "Created By"
    }


    filtered_data = data[start_index + 1 : end_index]
    filtered_data = filtered_data.rename(columns=filtered_data_cols)


    desired_cols = ['File Name', 'Page#', 'Provider Name' ,'Location','Reason',  'Claim# / Visit#', 'Appt Status', 'DOS', 'Account# / #MRN#','Patient Name','DOB', 'Insurance', 'Batch ID', "Assigned Emp ID#"]

    result = pd.DataFrame(columns=desired_cols)

    # result["Location"] = filtered_data["Facility"]
    result["Provider Name"] = filtered_data["Scheduler"]
    result["File Name"] = " - "
    result["Page#"] = " - "
    result["Location"] = " - "
    result["Reason"] = filtered_data["Appointment Type"]
    result["Claim# / Visit#"] = "N/A"
    result["Appt Status"] = filtered_data["Appointment Status"]
    result["DOS"] = pd.to_datetime(filtered_data["Appointment Date"]).dt.strftime("%B %d, %Y")
    result["Account# / #MRN#"] = filtered_data["Chart #"]
    result["Patient Name"] = filtered_data["Patient Name"]
    result["DOB"] = pd.to_datetime(filtered_data["Patient DOB"]).dt.strftime("%B %d, %Y")
    result["Insurance"] = filtered_data["Primary Insurance Name"]
    result["Batch ID"] = " - "
    # result["Assigned Emp ID#"] = "RAM011"
    result['Assigned Emp ID#'] = "RAM121"
    

    # To convert Into Excel Format.
    pathing = pathing.replace(".", "") 
    output_dir = 'Results/DailyCharges/StoneCharges'
    os.makedirs(output_dir, exist_ok=True)


    filename = os.path.basename(pathing)
    filename_no_ext = os.path.splitext(filename)[0]
    parts = filename_no_ext.split('_')
    kunjdate = parts[-1] 

    output_path = os.path.join(output_dir, f'StoneCharges_of_{kunjdate}.xlsx')
    result.to_excel(f'{output_path}', index=False)

    return output_path

