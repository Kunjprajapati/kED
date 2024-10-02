import pandas as pd 
import numpy as np 
import os  # Import os module to handle file path and directory

def MorningStoneChargesCounts(data):
    """
    Counts occurrences of specific values in the 'Unnamed: 7' column of a CSV file.

    Parameters:
    pathing (str): The path to the CSV file.

    Returns:
    dict: A dictionary with counts of 'Clearing house rejected', 'Denial', and 'Pri, Rejected'.
    """
    # Load the data from the specified file
    
    # Define the specific values to count
    specific_values = ["Clearing House Rejected", "Denial", "Pri. Rejected"]
    
    # Get counts of specific values in 'Unnamed: 7'
    counts = data['Unnamed: 7'].value_counts().reindex(specific_values, fill_value=0)
    
    # Convert the Series to a dictionary and return
    return counts.to_dict()



def EveningStoneChargesCounts(data):
    """
    Counts occurrences of 'Hold' and 'Not Claimed' in the 'Unnamed: 7' column for the years 2021, 2022, 2023 combined,
    and separately for 2024.

    Parameters:
    data (DataFrame): The pandas DataFrame containing the data.

    Returns:
    dict: A dictionary with counts for '2021, 2022, 2023' and '2024'.
    """
    service_date_index = data[data.iloc[:, 0] == 'Service Date'].index[0]

    filtered_data = data.iloc[service_date_index + 1:].reset_index(drop=True)

    # Convert 'Aging Detailed Report' to datetime with the correct format
    filtered_data['Aging Detailed Report'] = pd.to_datetime(filtered_data['Aging Detailed Report'], format='%m/%d/%Y', errors='coerce')
    
    # Check for NaT values after conversion
    if filtered_data['Aging Detailed Report'].isna().all():
        print("All entries are NaT. Please check the date format in the data.")
    
    # Filter data for Service Date excluding 2024
    filtered_data_2022_2023 = filtered_data[filtered_data['Aging Detailed Report'].dt.year != 2024]
    
    # Filter data fro Service Date of 2024
    filtered_data_2024 = filtered_data[(filtered_data['Aging Detailed Report'].dt.year == 2024)]
    
    # Count occurrences of "Hold" and "Not Claimed" in the specified column
    hold_count_2022_2023 = int((filtered_data_2022_2023['Unnamed: 7'] == "Hold").sum())
    not_claimed_count_2022_2023 = int((filtered_data_2022_2023['Unnamed: 7'] == "Not Claimed").sum())


    # Count occurrences of "Hold" and "Not Claimed" in the specified column
    hold_count_2024 = int((filtered_data_2024['Unnamed: 7'] == "Hold").sum())
    not_claimed_count_2024 = int((filtered_data_2024['Unnamed: 7'] == "Not Claimed").sum())
    
    result = {
        "2024": {
            "Hold Counts" : hold_count_2024, 
            "Not Claimed Counts" : not_claimed_count_2024
        }, 

        "KUNJ" : {
            "Hold Counts" : hold_count_2022_2023, 
            "Not Claimed Counts" : not_claimed_count_2022_2023
        }
    }

    return result 



def ORG_chargesCounts(pathing):
    file_ext = os.path.splitext(pathing)[1]
    if file_ext == '.csv':
        data = pd.read_csv(pathing, low_memory=False)
        # Convert CSV to XLSX immediately after reading
        temp_xlsx_path = os.path.splitext(pathing)[0] + '.xlsx'
        data.to_excel(temp_xlsx_path, index=False)
        # Update pathing to use the new XLSX file for further processing
        pathing = temp_xlsx_path
        data = pd.read_excel(pathing)
    elif file_ext == '.xlsx':
        data = pd.read_excel(pathing)
    base_dir = "Results/ChargesCounts"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir) 

    base_file_name = os.path.basename(pathing)
    output_file_name = f"Processed_{base_file_name.replace('.csv', '.xlsx')}"
    output_path = os.path.join(base_dir, output_file_name)

    cptcols = data['Unnamed: 17'][data['Unnamed: 17'].first_valid_index() + 1:].astype("string")


    toDeleteCPI = ["99490", "99458", "99489", "99439", "99454", "99457", "99487"]


    def functionToCheckCPT(cpt, deletecptList):
        return all(code in deletecptList for code in cpt)


    counter = 0
    rows_to_drop = []

    # First, remove leading commas and strip whitespacej
    for index, cpt in enumerate(cptcols):
        if pd.notna(cpt):
            cpt = cpt.strip()
            if cpt.startswith(","):
                cpt = cpt[1:].strip()
            data.loc[index + data['Unnamed: 17'].first_valid_index() + 1, 'Unnamed: 17'] = cpt

    # Now apply the logic separately
    for index, cpt in enumerate(cptcols):
        if pd.notna(cpt):
            result = [code.strip() for code in cpt.split(",") if code.strip()]
            
            if functionToCheckCPT(result, toDeleteCPI):
                rows_to_drop.append(index + data['Unnamed: 17'].first_valid_index() + 1)
                counter += 1
    
    data = data.drop(rows_to_drop)
    data.to_excel(output_path, index=False)
    return output_path
 

