import pandas as pd 
import datetime 
import numpy as np
import os  
import zipfile
import warnings


warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)
warnings.filterwarnings('ignore', category=FutureWarning)  

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def apply_logic_FOR_AR_Oak_Hills_Preprocessing(pathing1, pathing2):
    # List to store paths of all generated Excel files
    generated_files = []

    data = pd.read_excel(pathing1)
    date = datetime.date.today() 
    data_Dictionary = pd.read_excel(pathing2, sheet_name='page')
    data['Service Date'] = pd.to_datetime(data['Service Date'])
    data['Patient DOB'] = pd.to_datetime(data['Patient DOB'])
    today = pd.Timestamp(datetime.date.today())
    data['Number of Days'] = (today - data['Service Date']).dt.days

    # Creating a dictionary for npi. For Oak Hills, we have only one provider. 
    npi_dict = {
    "Stoops, Peter" : 1518912526, 
    "Martinez, Diana" : 1356807143
    }

    data_Dictionary.rename(columns={'Claim No' : 'Claim ID #'}, inplace=True)

    feature_mapping = {
    'Claim No' : 'Claim ID #', 
    'Patient Acct No' : 'Patient Acc#',
    'Patient Date Of Birth' : 'Patient DOB',
    'Payer Subscriber No' : 'Subscriber ID', 
    'Payer Name' : 'Insurance Name', 
    'Service Date' : 'Date Of Service',
    'Charges' : 'Charges Amount', 
    'Patient DOB' : 'Patient Date Of Birth',
    'Balance' : 'Total Outstanding Balance'
    }

    data['Payer Subscriber No']  = data['Payer Subscriber No'].astype(str) 
    data['Payer Subscriber No'].fillna("NaN", inplace=True)

    data['Charges'] = data['Charges'].astype(float)
    data['Charges Amount'] = data['Charges'].apply(lambda x: f"${x:,.2f}")
    
    data['Balance'] = data['Balance'].astype(float)
    data['Total Outstanding Balance'] = data['Balance'].apply(lambda x: f"${x:,.2f}")
    
    filtered_data = data[['Claim No','Patient DOB', 'Patient Acct No', 'Payer Subscriber No', 'Payer Name', 'Charges Amount', 'Number of Days', 'Service Date', 'Total Outstanding Balance']]
    filtered_data.rename(columns=feature_mapping, inplace=True)
    filtered_data['Patient First Name'] = data['Patient Name'].apply(lambda x: x.split(",")[0])
    filtered_data['Patient Last Name'] = data['Patient Name'].apply(lambda x: x.split(",")[1])

    filtered_data['Subscriber First Name'] = data['Patient Name'].apply(lambda x: x.split(",")[0])
    filtered_data['Subscriber Last Name'] = data['Patient Name'].apply(lambda x: x.split(",")[1])

    filtered_data['Patient Date Of Birth'] = filtered_data['Patient Date Of Birth'].apply(convert_date)
    filtered_data['Date Of Service'] = filtered_data['Date Of Service'].apply(convert_date)
    # print(filtered_data.columns)

    filtered_data['Subscriber DOB'] = filtered_data['Patient Date Of Birth'] 

    data_dictionary_unique = data_Dictionary.drop_duplicates(subset=['Claim ID #'], keep='first')
    resultant_data = pd.merge(filtered_data, data_dictionary_unique[['Claim ID #', 'Rendering Provider Name', 'CPT Code']], on='Claim ID #', how='left')

    resultant_data['Provider First Name'] = resultant_data['Rendering Provider Name'].astype(str).apply(lambda x: x.split(",")[1].strip() if "," in x else "")
    resultant_data['Provider Last Name'] = resultant_data['Rendering Provider Name'].astype(str).apply(lambda x: x.split(",")[0] if "," in x else "")

    resultant_data = resultant_data[ : resultant_data['CPT Code'].last_valid_index() + 1]
    resultant_data['Assigned Emp ID#'] = " "
    resultant_data['Rendering Provider Name'] = resultant_data['Rendering Provider Name'].str.replace('XXX', '').str.strip()
    resultant_data['Provider NPI'] = resultant_data['Rendering Provider Name'].map(npi_dict)
    resultant_data["Provider Group NPI"] = 1851867758
    resultant_data["Provider Group Name"] = "Peter Stoops D.O Inc DBA Oak Hills Family Care"

    output_directory = "Results/AR/AR_Oak-Hills/Reference Files"
    ensure_directory_exists(output_directory)
    output_path = f"{output_directory}/Reference_AR_Oak-Hills_File.xlsx"
    resultant_data.to_excel(output_path, index=False)
    generated_files.append(output_path)

    resultant_data = resultant_data.drop(columns=['Rendering Provider Name'])

    resultant_data_above_120 = resultant_data[resultant_data['Number of Days'] > 120]
    resultant_data_between_91_and_120 = resultant_data[(resultant_data['Number of Days'] >= 91) & (resultant_data['Number of Days'] <= 120)]
    resultant_data_between_61_and_90 = resultant_data[(resultant_data['Number of Days'] >= 61) & (resultant_data['Number of Days'] <= 90)]
    resultant_data_between_31_and_60 = resultant_data[(resultant_data['Number of Days'] >= 31) & (resultant_data['Number of Days'] <= 60)]
    resultant_data_less_30 = resultant_data[resultant_data['Number of Days'] < 30]

    columns_arrangment = ['Claim ID #', 'Patient Acc#', 'Patient First Name', 'Patient Last Name',
       'Patient Date Of Birth', 'Subscriber ID', 'Subscriber First Name',
       'Subscriber Last Name', 'Subscriber DOB', 'Insurance Name',
       'Date Of Service', 'CPT Code', 'Provider First Name',
       'Provider Last Name', 'Provider NPI', 'Provider Group Name',
       'Provider Group NPI', 'Charges Amount', 'Total Outstanding Balance',
       'Assigned Emp ID#']

    resultant_data_above_120 = resultant_data_above_120.drop(columns=['Number of Days'])
    resultant_data_above_120 = resultant_data_above_120[columns_arrangment]
    ensure_directory_exists('Results/AR/AR_Oak-Hills/Insurances_Above_120')  # Ensure the directory exists
    insurance_groups_above_120 = resultant_data_above_120.groupby('Insurance Name')
    counter = 0
    for insurance_name, group in insurance_groups_above_120:
        group_same = group[group['Charges Amount'] == group['Total Outstanding Balance']]
        group_different = group[group['Charges Amount'] != group['Total Outstanding Balance']]

        if not group_same.empty:
            filename_same = "Oak-Hills_120+_" + insurance_name.replace('/', '_').replace('\\', '_') + f"_As of {date}_Primary" + ".xlsx"
            group_same.to_excel(f'Results/AR/AR_Oak-Hills/Insurances_Above_120/{filename_same}', index=False)
            counter += 1
            # print(f"Saved {filename_same} - Group {counter}")
            generated_files.append(f'Results/AR/AR_Oak-Hills/Insurances_Above_120/{filename_same}')

        if not group_different.empty:
            filename_different = "Oak-Hills_120+_" + insurance_name.replace('/', '_').replace('\\', '_') + f"_As of {date}_Partial" + ".xlsx"
            group_different.to_excel(f'Results/AR/AR_Oak-Hills/Insurances_Above_120/{filename_different}', index=False)
            counter += 1
            # print(f"Saved {filename_different} - Group {counter}")
            generated_files.append(f'Results/AR/AR_Oak-Hills/Insurances_Above_120/{filename_different}')

    resultant_data_between_91_and_120 = resultant_data_between_91_and_120.drop(columns=['Number of Days'])
    resultant_data_between_91_and_120 = resultant_data_between_91_and_120[columns_arrangment]
    ensure_directory_exists('Results/AR/AR_Oak-Hills/Insurances_Between_91_To_120')  # Ensure the directory exists
    insurance_groups_between_91_to_120 = resultant_data_between_91_and_120.groupby('Insurance Name')
    counter = 0
    for insurance_name, group in insurance_groups_between_91_to_120:
        group_same = group[group['Charges Amount'] == group['Total Outstanding Balance']]
        group_different = group[group['Charges Amount'] != group['Total Outstanding Balance']]

        if not group_same.empty:
            filename_same = "Oak-Hills_91_To_120_" + insurance_name.replace('/', '_').replace('\\', '_') + f"_As of {date}_Primary" + ".xlsx"
            group_same.to_excel(f'Results/AR/AR_Oak-Hills/Insurances_Between_91_To_120/{filename_same}', index=False)
            counter += 1
            # print(f"Saved {filename_same} - Group {counter}")
            generated_files.append(f'Results/AR/AR_Oak-Hills/Insurances_Between_91_To_120/{filename_same}')

        if not group_different.empty:
            filename_different = "Oak-Hills_91_To_120_" + insurance_name.replace('/', '_').replace('\\', '_') + f"_As of {date}_Partial" + ".xlsx"
            group_different.to_excel(f'Results/AR/AR_Oak-Hills/Insurances_Between_91_To_120/{filename_different}', index=False)
            counter += 1
            # print(f"Saved {filename_different} - Group {counter}")
            generated_files.append(f'Results/AR/AR_Oak-Hills/Insurances_Between_91_To_120/{filename_different}')

    resultant_data_between_61_and_90 = resultant_data_between_61_and_90.drop(columns=['Number of Days'])
    resultant_data_between_61_and_90 = resultant_data_between_61_and_90[columns_arrangment]
    ensure_directory_exists('Results/AR/AR_Oak-Hills/Insurances_Between_61_To_90')  # Ensure the directory exists
    insurance_groups_between_61_to_90 = resultant_data_between_61_and_90.groupby('Insurance Name')
    counter = 0
    for insurance_name, group in insurance_groups_between_61_to_90:
        group_same = group[group['Charges Amount'] == group['Total Outstanding Balance']]
        group_different = group[group['Charges Amount'] != group['Total Outstanding Balance']]

        if not group_same.empty:
            filename_same = "Oak-Hills_61_To_90_" + insurance_name.replace('/', '_').replace('\\', '_') + f"_As of {date}_Primary" + ".xlsx"
            group_same.to_excel(f'Results/AR/AR_Oak-Hills/Insurances_Between_61_To_90/{filename_same}', index=False)
            counter += 1
            # print(f"Saved {filename_same} - Group {counter}")
            generated_files.append(f'Results/AR/AR_Oak-Hills/Insurances_Between_61_To_90/{filename_same}')

        if not group_different.empty:
            filename_different = "Oak-Hills_61_To_90_" + insurance_name.replace('/', '_').replace('\\', '_') + f"_As of {date}_Partial" + ".xlsx"
            group_different.to_excel(f'Results/AR/AR_Oak-Hills/Insurances_Between_61_To_90/{filename_different}', index=False)
            counter += 1
            # print(f"Saved {filename_different} - Group {counter}")
            generated_files.append(f'Results/AR/AR_Oak-Hills/Insurances_Between_61_To_90/{filename_different}')

    resultant_data_between_31_and_60 = resultant_data_between_31_and_60.drop(columns=['Number of Days'])
    resultant_data_between_31_and_60 = resultant_data_between_31_and_60[columns_arrangment]
    ensure_directory_exists('Results/AR/AR_Oak-Hills/Insurances_Between_31_To_60')  # Ensure the directory exists
    insurance_groups_between_31_to_60 = resultant_data_between_31_and_60.groupby('Insurance Name')
    counter = 0
    for insurance_name, group in insurance_groups_between_31_to_60:
        group_same = group[group['Charges Amount'] == group['Total Outstanding Balance']]
        group_different = group[group['Charges Amount'] != group['Total Outstanding Balance']]

        if not group_same.empty:
            filename_same = "Oak-Hills_31_To_60_" + insurance_name.replace('/', '_').replace('\\', '_') + f"_As of {date}_Primary" + ".xlsx"
            group_same.to_excel(f'Results/AR/AR_Oak-Hills/Insurances_Between_31_To_60/{filename_same}', index=False)
            counter += 1
            # print(f"Saved {filename_same} - Group {counter}")
            generated_files.append(f'Results/AR/AR_Oak-Hills/Insurances_Between_31_To_60/{filename_same}')

        if not group_different.empty:
            filename_different = "Oak-Hills_31_To_60_" + insurance_name.replace('/', '_').replace('\\', '_') + f"_As of {date}_Partial" + ".xlsx"
            group_different.to_excel(f'Results/AR/AR_Oak-Hills/Insurances_Between_31_To_60/{filename_different}', index=False)
            counter += 1
            # print(f"Saved {filename_different} - Group {counter}")
            generated_files.append(f'Results/AR/AR_Oak-Hills/Insurances_Between_31_To_60/{filename_different}')

    resultant_data_less_30 = resultant_data_less_30.drop(columns=['Number of Days'])
    resultant_data_less_30 = resultant_data_less_30[columns_arrangment]
    ensure_directory_exists('Results/AR/AR_Oak-Hills/Insurances_Below_30')  # Ensure the directory exists
    insurance_groups_less_30 = resultant_data_less_30.groupby('Insurance Name')
    counter = 0
    for insurance_name, group in insurance_groups_less_30:
        group_same = group[group['Charges Amount'] == group['Total Outstanding Balance']]
        group_different = group[group['Charges Amount'] != group['Total Outstanding Balance']]

        if not group_same.empty:
            filename_same = "Oak-Hills_30-_" + insurance_name.replace('/', '_').replace('\\', '_') + f"_As of {date}_Primary" + ".xlsx"
            group_same.to_excel(f'Results/AR/AR_Oak-Hills/Insurances_Below_30/{filename_same}', index=False)
            counter += 1
            # print(f"Saved {filename_same} - Group {counter}")
            generated_files.append(f'Results/AR/AR_Oak-Hills/Insurances_Below_30/{filename_same}')

        if not group_different.empty:
            filename_different = "Oak-Hills_30-_" + insurance_name.replace('/', '_').replace('\\', '_') + f"_As of {date}_Partial" + ".xlsx"
            group_different.to_excel(f'Results/AR/AR_Oak-Hills/Insurances_Below_30/{filename_different}', index=False)
            counter += 1
            # print(f"Saved {filename_different} - Group {counter}")
            generated_files.append(f'Results/AR/AR_Oak-Hills/Insurances_Below_30/{filename_different}')


    # time_frames = {
    #     'above_120': {'data': resultant_data_above_120, 'folder': 'Insurances_Above_120'},
    #     'between_91_and_120': {'data': resultant_data_between_91_and_120, 'folder': 'Insurances_Between_91_To_120'},
    #     'between_61_and_90': {'data': resultant_data_between_61_and_90, 'folder': 'Insurances_Between_61_To_90'},
    #     'between_31_and_60': {'data': resultant_data_between_31_and_60, 'folder': 'Insurances_Between_31_To_60'},
    #     'less_30': {'data': resultant_data_less_30, 'folder': 'Insurances_Below_30'}
    # }

    # for key, value in time_frames.items():
    #     folder_path = f"Results/AR/AR_Oak-Hills/{value['folder']}"
    #     ensure_directory_exists(folder_path)
    #     file_path = f"{folder_path}/Data_{key}.xlsx"
    #     value['data'].to_excel(file_path, index=False)
    #     generated_files.append(file_path)
    resultant_data_above_120.to_excel('Results/AR/AR_Oak-Hills/Reference Files/Data_Above_120.xlsx', index = False)
    generated_files.append('Results/AR/AR_Oak-Hills/Reference Files/Data_Above_120.xlsx')
    resultant_data_between_91_and_120.to_excel('Results/AR/AR_Oak-Hills/Reference Files/Data_Between_91_To_120.xlsx', index = False)
    generated_files.append('Results/AR/AR_Oak-Hills/Reference Files/Data_Between_91_To_120.xlsx')
    resultant_data_between_61_and_90.to_excel('Results/AR/AR_Oak-Hills/Reference Files/Data_Between_61_To_90.xlsx', index = False)
    generated_files.append('Results/AR/AR_Oak-Hills/Reference Files/Data_Between_61_To_90.xlsx')
    resultant_data_between_31_and_60.to_excel('Results/AR/AR_Oak-Hills/Reference Files/Data_Between_31_To_60.xlsx', index = False)
    generated_files.append('Results/AR/AR_Oak-Hills/Reference Files/Data_Between_31_To_60.xlsx')
    resultant_data_less_30.to_excel('Results/AR/AR_Oak-Hills/Reference Files/Data_Less_30.xlsx', index = False)
    generated_files.append('Results/AR/AR_Oak-Hills/Reference Files/Data_Less_30.xlsx')

    zip_file_path = 'temp/AR_Oak_Hills_output_files.zip'
    os.makedirs(os.path.dirname(zip_file_path), exist_ok=True)
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in generated_files:
            archive_path = os.path.relpath(file_path, 'Results/AR/AR_Oak-Hills')
            zipf.write(file_path, archive_path)
    # print(f"ZIP file created at: {zip_file_path}")
    return zip_file_path

def convert_date(date_obj, input_format="%Y-%m-%d %H:%M:%S", output_format='%B %d, %Y'):
    if isinstance(date_obj, datetime.date):
        formatted_date = date_obj.strftime(output_format)       
        return formatted_date
    else:
        return date_obj