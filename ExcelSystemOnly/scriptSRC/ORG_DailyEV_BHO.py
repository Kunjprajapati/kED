import pandas as pd 
from datetime import datetime 
import os 
import warnings
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)
warnings.filterwarnings('ignore', category=FutureWarning)  

def preprocessing_Excel_FOR_BHO(pathing):
    df = pd.read_excel(pathing)

    practice_name_index = df.index[df["Unnamed: 0"] == "Practice Name:"].tolist()
    practice_name_index = practice_name_index[0]

    practice_name = df["Unnamed: 1"][practice_name_index]

    starting_index = df.index[df["Unnamed: 0"] == "Date of Service"].tolist()
    starting_index = starting_index[0]

    data = df[starting_index : ]
    data = df[starting_index:].reset_index(drop=True)

    real_cols = data.iloc[0].to_dict()

    data = data.rename(columns=real_cols)
    data.drop(index=0, inplace=True)

    desized_cols = {
    'Patient Chart Number' : 'Patient Account Number',
    'Date of Birth' : 'Subscriber DOB',
    'Date of Service' : 'DOS/Appt Date', 
    'Location Name' : 'Location', 
    # 'Appointment Type' : 'Visit Type', 
    'Appointment Type' : 'Visit Reasons',
    'Primary Payer Name' : 'Primary Insurance Name'
    }
    data = data.rename(columns=desized_cols) 
    data["Visit Type"] = data["Visit Reasons"]
    data["Facility Name"] = practice_name
    # data["DOS/Appt Date"] = data["DOS/Appt Date"].astype(str).apply(convert_data_dos)
    # data["DOS/Appt Date"] = data["DOS/Appt Date"].apply(convert_date_dob)
    # data["Subscriber DOB"] = data["Subscriber DOB"].apply(convert_date_dob)
    data["Patient DOB"] = data["Subscriber DOB"]
    data["Provider Group NPI"] = 1063067643
    data["Provider NPI"] = 1063067643
    data["Patient Balance"] = "$0.00"
    data["Policy ID"] = data["Insured ID"]


    return data



def apply_logic_FOR_dailyEV_BHO(file1_path, file2_path):
    try:
        old = preprocessing_Excel_FOR_BHO(file1_path)
        new = preprocessing_Excel_FOR_BHO(file2_path)

        # Generating Primary Key Based on New and old Excel file 
        old["PrimaryKey"] = old['DOS/Appt Date'].astype(str) + '_' + old['Patient Account Number'].astype(str)
        new["PrimaryKey"] = new['DOS/Appt Date'].astype(str) + '_' + new['Patient Account Number'].astype(str)
        data = pd.merge(new, old, on='PrimaryKey', how='outer', indicator=True)
        filtered_data = data[data['_merge'] != 'both']
        filtered_data = filtered_data.drop('_merge', axis=1)

        # Removing all the _y labels which are of no use. 
        filtered_data.drop(columns=[col for col in filtered_data.columns if col.endswith('_y')], inplace=True)

        # To Obtain the total number of NaN value are present from index number 0 to 'naIndex'. 
        checker = filtered_data['DOS/Appt Date_x'].isna()
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


        # Adding New Fields by splitting the previous existing fields
        filtered_data['Subscriber First Name'] = filtered_data['Patient Name'].apply(lambda x: x.split(",")[1] if isinstance(x, str) else "")
        filtered_data['Subscriber Last Name'] = filtered_data['Patient Name'].apply(lambda x: x.split(",")[0] if isinstance(x, str) else "")

        filtered_data["Provider First Name"] = "DPT"
        filtered_data["Provider Last Name"] = "DPT"
        filtered_data["Assigned Emp ID#"] = " "
        filtered_data['DOS/Appt Date'] = filtered_data['DOS/Appt Date'].apply(convert_date_dob)
        filtered_data['Patient DOB'] = filtered_data['Patient DOB'].apply(convert_date_dob)
        filtered_data['Subscriber DOB'] = filtered_data['Patient DOB']
        filtered_data["Notes"] = " "
        # # Patient Name

        filtered_data['Patient First Name'] = filtered_data['Patient Name'].apply(lambda x: x.split(",")[1] if isinstance(x, str) else "")
        filtered_data['Patient Last Name'] = filtered_data['Patient Name'].apply(lambda x: x.split(",")[0] if isinstance(x, str) else "")
        # Deleting number of columns which are of no use. 
        filtered_data.drop(columns=["Patient Contact Preference","Cell Phone", "Patient Preferred Phone", "Patient Name", "Calendar Resource Name", "PrimaryKey", "Check-In Time", "Check-Out Time", "Co-Pay", "Appointment Note", "Account Type", "Gender", "Home Phone", "Payment Collected", "Time", "Appointment Length"], inplace=True)


        desired_sequence = ['Facility Name', 'Location', 'Provider First Name',
       'Provider Last Name', 'Provider NPI', 'Provider Group NPI',
       'Patient Account Number', 'Subscriber First Name',
       'Subscriber Last Name', 'Subscriber DOB', 'Patient First Name',
       'Patient Last Name', 'Patient DOB', 'Primary Insurance Name',
       'Policy ID', 'DOS/Appt Date', 'Patient Balance', 'Notes',
       'Visit Reasons', 'Appointment Status', 'Visit Type',
       'Assigned Emp ID#']
        
        filtered_data = filtered_data[desired_sequence]

        filtered_data.loc[filtered_data["Primary Insurance Name"] == "Self-Pay", "Assigned Emp ID#"] = "Calling Account"

        output_dir = 'Results/DailyEV/BHO'
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.basename(file2_path)
        filename_no_ext = os.path.splitext(filename)[0]
        parts = filename_no_ext.split('_')
        kunjdate = parts[-1] 
        output_path = os.path.join(output_dir, f'BHO_EV_{kunjdate}.xlsx')
        # return kunjdate
        # print(filtered_data.isna().sum())

        # Remove rows where all columns are empty
        filtered_data = filtered_data.dropna(how='all')

    
        threshold = len(filtered_data.columns) // 2  # More than half of the columns are NaN
        filtered_data = filtered_data.dropna(thresh=threshold)

        filtered_data.to_excel(output_path, index=False)
        return output_path


    except Exception as e:
        # print("Error", f"An error occurred: {str(e)}")
        return f"An error occurred: {str(e)}"



def convert_date_dob(date_str, input_format='%m/%d/%Y', output_format='%B %d, %Y'):  
    if isinstance(date_str, str):
        # Parse the date string into a datetime object
        date_obj = datetime.strptime(date_str, input_format)
        
        # Format the datetime object into the desired output format
        formatted_date = date_obj.strftime(output_format)
        
        return formatted_date
    else:
        return date_str  # Return the original value if it's not a string
    

def convert_data_dos(date, input_format='%Y-%m-%d %H:%M:%S', output_format='%B %d, %Y'):
    if isinstance(date, pd.Timestamp):  # Check if the input is a Timestamp
        # Format the datetime object into the desired output format
        formatted_date = date.strftime(output_format)
        return formatted_date
    elif isinstance(date, str):  # Handle string inputs
        # Parse the date string into a datetime object
        date_obj = datetime.strptime(date, input_format)
        # Format the datetime object into the desired output format
        formatted_date = date_obj.strftime(output_format)
        return formatted_date
    else:
        return date  # Return the original value if it's not a string or Timestamp


