import pandas as pd
import os 
import warnings
import datetime
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)
warnings.filterwarnings('ignore', category=FutureWarning)  

def safe_parse_date(date_str):
    # Check if the input is already a datetime object
    if isinstance(date_str, datetime.datetime):
        return date_str.strftime("%B %d, %Y")
    
    date_formats = ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%B %d, %Y"]
    for fmt in date_formats:
        try:
            return datetime.datetime.strptime(date_str, fmt).strftime("%B %d, %Y")
        except ValueError:
            continue
    raise ValueError(f"Unknown datetime string format, unable to parse: {date_str}")

def function_for_shivDhara(pathing):
    # data = pd.read_excel(pathing)
    # data = pd.read_csv(pathing)
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


    details = []
    first_col = data["Schedule of the Day"]
    for row in first_col:
        details.append(row)


    details_dictionary = {
        "Location" : details[1],
        "Provider Name" : details[2].split(":")[1],
        "Appointment" : details[3].split(":")[1].split(", ")[1:]
    }
    
    
    # Extrac all the pre-build columns from the raw file.
    # Fetching the main data starting index from the raw file. 
    start_index_value = data.index[data["Schedule of the Day"] == "Time"].tolist()
    start_index_value = start_index_value[0]
    
    # Fetching the main data ending index from the raw file. 
    end_index_value = len(data["Schedule of the Day"]) - 1
    # return end_index_value
    
    desired_cols = ['File Name', 'Page#', 'Provider Name' ,'Location','Reason',  'Claim# / Visit#', 'Appt Status', 'DOS', 'Account# / #MRN#','Patient Name','DOB', 'Insurance', 'Batch ID', "Assigned Emp ID#"]
    
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
    
    # Making all the columns according to the raw file
    col_row = list(data.iloc[start_index_value])
    
    # Static cols. 
    raw_cols = {
        "Schedule of the Day" : col_row[0],
        "Unnamed: 1" : col_row[1],
        "Unnamed: 2" : col_row[2],
        "Unnamed: 3" : col_row[3],
        "Unnamed: 4" : col_row[4],
        "Unnamed: 5" : col_row[5],
        "Unnamed: 6" : col_row[6],
        "Unnamed: 7" : col_row[7],
        "Unnamed: 8" : col_row[8],
        "Unnamed: 9" : col_row[9],
        "Unnamed: 10" : col_row[10],
        "Unnamed: 11" : col_row[11],
        "Unnamed: 12" : col_row[12],
        "Unnamed: 13" : col_row[13],
    }

    
    result = data[start_index_value + 1: end_index_value]
    result
    # print(col_row)
    result.rename(columns=raw_cols, inplace=True)



    result_cols = {
        # Add more columns with respect to the desized name. 
        "Time" : "DOS", 
        "Acc. #" : "Account# / #MRN#", 
        "Visit Reason" : "Reason"
    }

    # New inserted columns, for empty. 
    result["File Name"] = " - "
    result["Page#"] = " - "
    result["Insurance"] = " - "
    result["Batch ID"] = " - "

    result["Provider Name"] = details_dictionary["Provider Name"]
    result["Location"] = details_dictionary["Location"]
    result["Appt Status"] = "CONFIRMED"
    result["Claim# / Visit#"] = "NA"
    # result["Assigned Emp ID#"] = "RAC086"
    result['Assigned Emp ID#'] = "RAM099"
    result["DOB"] = result["DOB"].apply(lambda x: safe_parse_date(x) if pd.notnull(x) else x)
    result["Time"] = pd.to_datetime(result["Time"]).dt.strftime("%B %d, %Y")
    result.rename(columns=result_cols, inplace=True)
    result


    # Updating all the columns, By performing the intersection between the columns. 
    intersected_cols = list(set(desired_cols) & set(result.columns))

    # Considering and Desizing all the columns in the desired format. 
    result = result[intersected_cols]
    result = result.reindex(columns=desired_cols)

    output_dir = 'Results/DailyCharges/ShivDhara'
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(pathing)
    filename_no_ext = os.path.splitext(filename)[0]
    parts = filename_no_ext.split('_')
    kunjdate = parts[-1] 

    output_path = os.path.join(output_dir, f'ShivDhara_charges_of_{kunjdate}.xlsx')
    result.to_excel(f'{output_path}', index=False)

    return output_path