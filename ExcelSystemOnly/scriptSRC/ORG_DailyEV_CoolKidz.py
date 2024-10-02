import pandas as pd
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)
warnings.filterwarnings('ignore', category=FutureWarning)  

def apply_logic_FOR_dailyEV_CoolKidz(file1_path, file2_path):
    try:
        old = pd.read_excel(file1_path)
        new = pd.read_excel(file2_path)

        # Generating Primary Key Based on New and old Excel file 
        # Create a primary key for both old and new data by combining 'Appointment Date' and 'Patient Acct No' as strings
        old["PrimaryKey"] = old['Appointment Date'].astype(str) + '_' + old['Patient Acct No'].astype(str)
        new["PrimaryKey"] = new['Appointment Date'].astype(str) + '_' + new['Patient Acct No'].astype(str)
        
        # Merge the old and new data on the primary key, keeping all rows from both dataframes
        # The 'indicator=True' parameter adds a column to the result called '_merge' to indicate the source of each row
        data = pd.merge(new, old, on='PrimaryKey', how='outer', indicator=True)
        
        # Filter out rows that are present in both old and new data
        filtered_data = data[data['_merge'] != 'both']
        
        # Drop the '_merge' column as it is no longer needed
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
        filtered_data.rename(columns=col_dict_dailyev(), inplace=True)

        # Perform any other required data processing
        resultant_data = classic_upgradation_dailyev(filtered_data)

        desired_order = ['Facility Name', 'Location', 'Provider First Name', 'Provider Last Name', 'Provider NPI', 'Provider Group NPI', 'Patient Account Number', 'Subscriber First Name', 'Subscriber Last Name', 'Subscriber DOB', 'Patient First Name', 'Patient Last Name', 'Patient DOB', 'Primary Insurance Name', 'Policy ID', 'DOS/Appt Date', 'Patient Balance', 'Notes', 'Visit Reasons', 'Appointment Status', 'Visit Type', 'Assigned Emp ID#']
        resultant_data = resultant_data[desired_order]
        resultant_data['Subscriber DOB'] = resultant_data['Subscriber DOB'].apply(convert_date_dailyev)
        resultant_data['Patient DOB'] = resultant_data['Patient DOB'].apply(convert_date_dailyev)
        resultant_data['DOS/Appt Date'] = resultant_data['DOS/Appt Date'].apply(convert_date_dailyev) 

        # Write resultant data to Excel file
        # resultant_data.loc[resultant_data["Primary Insurance Name"] == "Self-Pay", "Assigned Emp ID#"] = "Calling Account"
        resultant_data.loc[
            (resultant_data["Primary Insurance Name"] == "Self-Pay") | 
            (resultant_data["Primary Insurance Name"] == "Self-Pay-CKP St.Pete") | 
            (resultant_data["Primary Insurance Name"] == "Self-Pay-CKP Brandon") | 
            (resultant_data["Primary Insurance Name"] == "Self-Pay-CKP MLK"), "Assigned Emp ID#"] = "Calling Account"

        # output_file_path = os.path.join(os.path.dirname(file2_path), f"ExcelAutomation.xlsx")
        output_dir = 'Results/DailyEV/CoolKidz'
        os.makedirs(output_dir, exist_ok=True)
        
        filename = os.path.basename(file2_path)
        filename_no_ext = os.path.splitext(filename)[0]
        parts = filename_no_ext.split('_')
        kunjdate = parts[-1] 
        output_path = os.path.join(output_dir, f'Coolkidz_EV_{kunjdate}.xlsx')
        # return kunjdate
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
        return f"An error occurred: {str(e)}"

def convert_date_dailyev(date_str, input_format='%Y-%m-%d', output_format='%B %d, %Y'):
    if isinstance(date_str, str):
        date_obj = datetime.strptime(date_str, input_format)
        formatted_date = date_obj.strftime(output_format)
        
        return formatted_date
    else:
        return date_str
    
def classic_upgradation_dailyev(filtered_data):
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
    filtered_data["Provider Group NPI"] = 1710468848
    filtered_data['Visit Reasons'] = filtered_data["Visit Type"]
    filtered_data['Visit Type'] = filtered_data['Appointment Status']
    filtered_data["Notes"] = " "
    filtered_data["Patient Balance"] = "$0.00"
    filtered_data['Assigned Emp ID#'] = " "

    common_columns = filtered_data.columns.intersection(desired_sequence)
    filtered_data = filtered_data[common_columns]
    return filtered_data

def col_dict_dailyev():
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
        'Appointment Provider Name': 'Appointment Provider Name',
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
        'Count Distinct(Patient Acct No)': 'Count Distinct(Patient Acct No', 
        'Count Distinct(Patient Acct No)': 'Count Distinct(Patient Acct No)',
        'PrimaryKey': 'PrimaryKey'
    }