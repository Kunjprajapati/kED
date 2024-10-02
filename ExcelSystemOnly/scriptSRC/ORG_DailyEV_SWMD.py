import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os
from datetime import datetime  
import warnings
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)
warnings.filterwarnings('ignore', category=FutureWarning)  

def apply_logic_FOR_dailyEV_SWMD(file1_path, file2_path):
    try:
        old = pd.read_excel(file1_path)
        new = pd.read_excel(file2_path)

        # Generating Primary Key Based on New and old Excel file 
        old["PrimaryKey"] = old['Appointment Date'].astype(str) + '_' + old['Patient Acct No'].astype(str)
        new["PrimaryKey"] = new['Appointment Date'].astype(str) + '_' + new['Patient Acct No'].astype(str)
        data = pd.merge(new, old, on='PrimaryKey', how='outer', indicator=True)
        filtered_data = data[data['_merge'] != 'both']
        filtered_data = filtered_data.drop('_merge', axis=1)

        # Removing all the _y labels which are of no use. 
        filtered_data.drop(columns=[col for col in filtered_data.columns if col.endswith('_y')], inplace=True)

        # To Obtain the total number of NaN value are present from index number 0 to 'naIndex'. 
        checker = filtered_data['Appointment Date_x'].isna()
        naIndex = 0
        for i in checker: 
            if i == True:
                naIndex = naIndex + 1

        # Removing all those rows which were starting from index ZERO to 'naIndex' 
        filtered_data = filtered_data.iloc[naIndex:]
        filtered_data.reset_index(drop=True, inplace=True)

        # Renaming all the column name by removing '_X' From last.....
        column_names = filtered_data.columns
        new_column_names = [name.rstrip('_x') for name in column_names]
        filtered_data.columns = new_column_names

        # Formating All the Date fields as required.  
        filtered_data_columns = ['Appointment Date', 'Patient DOB']
        for column in filtered_data_columns:
            filtered_data[column] = pd.to_datetime(filtered_data[column]).dt.strftime('%Y-%m-%d')

        # Adding New Fields by splitting the previous existing fields
        filtered_data['Subscriber First Name'] = filtered_data['Patient Name'].apply(lambda x: x.split(",")[1] if isinstance(x, str) else "")
        filtered_data['Subscriber Last Name'] = filtered_data['Patient Name'].apply(lambda x: x.split(",")[0] if isinstance(x, str) else "")
        # Provider Name 
        filtered_data['Provider First Name'] = filtered_data['Appointment Provider Name'].apply(lambda x: x.split(",")[1] if isinstance(x, str) else "")
        filtered_data['Provider Last Name'] = filtered_data['Appointment Provider Name'].apply(lambda x: x.split(",")[0] if isinstance(x, str) else "")
        # Patient Name
        filtered_data['Patient First Name'] = filtered_data['Patient Name'].apply(lambda x: x.split(",")[1] if isinstance(x, str) else "")
        filtered_data['Patient Last Name'] = filtered_data['Patient Name'].apply(lambda x: x.split(",")[0] if isinstance(x, str) else "")

        # Apply column name transformation
        filtered_data.rename(columns=col_dict(), inplace=True)

        # Perform any other required data processing
        resultant_data = classic_upgradation(filtered_data)


        desired_order = ['Facility Name', 'Location', 'Provider First Name', 'Provider Last Name', 'Provider NPI', 'Provider Group NPI', 'Patient Account Number', 'Subscriber First Name', 'Subscriber Last Name', 'Subscriber DOB', 'Patient First Name', 'Patient Last Name', 'Patient DOB', 'Primary Insurance Name', 'Policy ID', 'DOS/Appt Date', 'Patient Balance', 'Notes', 'Visit Reasons', 'Appointment Status', 'Visit Type', 'Assigned Emp ID#']
        resultant_data = resultant_data[desired_order]
        
        resultant_data['Subscriber DOB'] = resultant_data['Subscriber DOB'].apply(convert_date)
        resultant_data['Patient DOB'] = resultant_data['Patient DOB'].apply(convert_date)
        resultant_data['DOS/Appt Date'] = resultant_data['DOS/Appt Date'].apply(convert_date)
        resultant_data.loc[resultant_data["Primary Insurance Name"] == "Self-Pay", "Assigned Emp ID#"] = "Calling Account"


        # Remove rows that are empty except for "Provider Group NPI" and "Patient Balance"
        columns_to_check = resultant_data.columns.difference(['Provider Group NPI', 'Patient Balance'])
        resultant_data = resultant_data[~resultant_data[columns_to_check].isnull().all(axis=1)]

        # Write resultant data to Excel file
        
        # messagebox.showinfo("Success", "Logic applied and new Excel file generated successfully!")
        output_dir = 'Results/DailyEV/SWMD'
        os.makedirs(output_dir, exist_ok=True)

        filename = os.path.basename(file2_path)
        filename_no_ext = os.path.splitext(filename)[0]
        parts = filename_no_ext.split('_')
        kunjdate = parts[-1] 
        output_path = os.path.join(output_dir, f'SWMD_EV_{kunjdate}.xlsx')
        # print(resultant_data.isna().sum())

        # Remove rows where all columns are empty
        resultant_data = resultant_data.dropna(how='all')

        # Optionally, remove rows where more than half of the columns are empty
        # Adjust the threshold as needed
        threshold = len(resultant_data.columns) // 2  # More than half of the columns are NaN
        resultant_data = resultant_data.dropna(thresh=threshold)

        resultant_data.to_excel(output_path, index=False)
        return output_path
    
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")



def convert_date(date_str, input_format='%Y-%m-%d', output_format='%B %d, %Y'):
    if isinstance(date_str, str):
        # Parse the date string into a datetime object
        date_obj = datetime.strptime(date_str, input_format)
        
        # Format the datetime object into the desired output format
        formatted_date = date_obj.strftime(output_format)
        
        return formatted_date
    else:
        return date_str  # Return the original value if it's not a string

def classic_upgradation(filtered_data):
    desired_sequence = [
        'Facility Name', 'Location', 'Provider First Name', 'Provider Last Name',
        'Provider NPI', 'Provider Group NPI', 'Patient Account Number',
        'Subscriber First Name', 'Subscriber Last Name', 'Subscriber DOB',
        'Patient First Name', 'Patient Last Name', 'Patient DOB',
        'Primary Insurance Name', 'Policy ID', 'DOS/Appt Date',
        'Patient Balance', 'Notes', 'Visit Reasons', 'Appointment Status','Assigned Emp ID#', 'Visit Type'
    ]
    filtered_data['Location'] = filtered_data['Facility Name']
    filtered_data['Patient DOB'] = filtered_data["Subscriber DOB"]
    filtered_data["Provider Group NPI"] = 1134293491
    
    #
    filtered_data['Visit Reasons'] = filtered_data["Visit Type"]
    #

    filtered_data['Visit Type'] = filtered_data['Appointment Status']

    filtered_data["Notes"] = " "
    filtered_data["Patient Balance"] = "$0.00"
    # filtered_data['Visit Reasons'] = " "
    filtered_data['Assigned Emp ID#'] = " "
    # filtered_data['Visit Type'] = " "

    common_columns = filtered_data.columns.intersection(desired_sequence)
    filtered_data = filtered_data[common_columns]
    return filtered_data

def col_dict():
    return {
    'Appointment Facility Name': 'Facility Name',
    'Appointment Facility POS': 'Location',
    'Appointment Date': 'DOS/Appt Date',
    'Appointment Start Time': 'Appointment Start Time',
    'Visit Type': 'Visit Type',
    'Visit Status': 'Appointment Status',
    'Visit Count': 'Total(Visit Count)',
    'Patient Count': 'Patient Count',
    'Patient Acct No': 'Patient Account Number',
    'Patient DOB': 'Subscriber DOB',
    'Patient First Name': 'Patient First Name',
    'Patient Last Name': 'Patient Last Name',
    'Appointment Provider Name': 'Appointment Provider Name', # Keep this separate
    'Appointment Provider NPI': 'Provider NPI',
    'Primary Insurance Name': 'Primary Insurance Name',
    'Primary Insurance Subscriber No': 'Policy ID',
    'Secondary Insurance Name': 'Secondary Insurance Name',
    'Secondary Insurance Subscriber No': 'Secondary Insurance Subscriber No',
    'Tertiary Insurance Name': 'Tertiary Insurance Name',
    'Tertiary Insurance Subscriber No': 'Tertiary Insurance Subscriber No',
    'Sliding Fee Schedule': 'Sliding Fee Schedule',
    'Appointment Employer': 'Assigned Emp ID#',
    'Total(Visit Count)': 'Total(Visit Count)',
    'Count Distinct(Patient Acct No)': 'Count Distinct(Patient Acct No)',
    'PrimaryKey': 'PrimaryKey'}