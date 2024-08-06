import os
import zipfile
import wget
import shutil
import logging
import pandas as pd
import docx2txt
from PIL import Image
# import Image

from pathlib import Path

root_folder = os.path.dirname(os.path.abspath(__file__))


def download_and_read_excel(url, filename="manual_annotations.xlsx"):
    """Downloads an Excel file from a URL and reads it into a DataFrame. Returns the DataFrame."""    
    if os.path.isfile(filename):
        os.remove(filename)

    # The file is downloaded from the provided URL and saved with the provided filename
    wget.download(url, filename)

    # If the file was not downloaded successfully, an error message is logged and the function returns None
    if not os.path.isfile(filename):
        logging.error(f"{filename} was not downloaded successfully.")
        return None

    # If the file was downloaded successfully, a success message is logged
    logging.info(f"{filename} downloaded successfully.")

    # The function tries to read the downloaded file into a pandas DataFrame
    try:
        df = pd.read_excel(filename, sheet_name="all")
        # If the file is read successfully, the DataFrame is returned
        return df
    except Exception as e:
        # If there is an error while reading the file, an error message is logged and the function returns None
        logging.error(f"Failed to read {filename} as an Excel file: {e}")
        return None


def download_and_extract(url, target_dir):
    """Downloads a zip file from a URL and extracts it to a target directory."""
    # Download the file from the provided URL
    filename = wget.download(url)

    # Check if the file was downloaded successfully
    if not os.path.isfile(filename):
        logging.error(f"{filename} was not downloaded successfully.")
        return

    # Check if the downloaded file is a valid zip file
    if not zipfile.is_zipfile(filename):
        logging.error(f"{filename} is not a valid zip file.")
        return

    # Create the target directory if it doesn't exist
    Path(target_dir).mkdir(parents=True, exist_ok=True)

    # Open the zip file and extract all its contents to a temporary folder
    with zipfile.ZipFile(filename, "r") as zip_ref:
        zip_ref.extractall("temp_folder")
        
    # Get the name of the first folder in the zip file
    temp = zipfile.ZipFile(filename).infolist()[0]
    folder_name = Path("temp_folder") / temp.filename.split('/')[0]

    # Copy all .docx files from the extracted folder to the target directory, excluding files with "~" in their name
    for file in folder_name.glob('*.docx'):
        if "~" not in file.name:
            shutil.copyfile(file, Path(target_dir) / file.name)

    # Log the successful extraction and deletion of the downloaded file
    logging.info(f"Extracted {filename} to {target_dir}")
    
    # remove the downloaded file and the temporary folder
    os.remove(filename)
    shutil.rmtree("temp_folder")
    
    
# Function to read and separate the text related to right and left breast
def read_right_and_left(tx):
    tx_right, tx_left = "", ""
    # Check if both "Right Breast:" and "Left Breast:" are in the text
    if "Right Breast:" in tx and "Left Breast:" in tx:
        tx = tx.split("Left Breast:")
        tx_right = [
            i
            for i in tx[0].split("Right Breast:")[1].splitlines()
            if ("ACR C:" not in i and i != "")
        ]
        tx_left = [i for i in tx[1].splitlines() if ("ACR C:" not in i and i != "")]

    # Check if only "Right Breast:" is in the text
    elif "Right Breast:" in tx and "Left Breast:" not in tx:
        tx = tx.split("Right Breast:")[1].splitlines()
        tx_right = [i for i in tx if i != ""]

    # Check if only "Left Breast:" is in the text
    elif "Right Breast:" not in tx and "Left Breast:" in tx:
        tx = tx.split("Left Breast:")[1].splitlines()
        tx_left = [i for i in tx if i != ""]

    return tx_right, tx_left

# Function to read the content of the file and separate it into different sections
def read_content(file_content):
    # Split the content into different sections based on various keywords
    annotation = file_content.split("OPINION:")  
    mm_revealed = annotation[0].split("REVEALED:")[1]
    mm_revealed_right, mm_revealed_left = read_right_and_left(mm_revealed)

    optinion = annotation[1].split("CONTRAST ENHANCED SPECTRAL MAMMOGRAPHY REVEALED:")
    ces_mm_revealed = optinion[1]
    optinion = optinion[0]
    optinion_right, optinion_left = read_right_and_left(optinion)

    ces_mm_revealed_right, ces_mm_revealed_left = read_right_and_left(ces_mm_revealed)

    return (
        mm_revealed_right,
        mm_revealed_left,
        optinion_right,
        optinion_left,
        ces_mm_revealed_right,
        ces_mm_revealed_left,
    )

# Function to add logs to the DataFrame
def add_df_log(df, dict_text, manual_annotations, f_id, file_path):
    # Iterate over each unique side and type in the manual annotations
    for side in manual_annotations.Side.unique():
        for mm_type in manual_annotations.Type.unique().tolist() + ["OP"]:
            text_list = dict_text[mm_type + "_" + side]
            # Filter the annotations for the current file id, side, and type
            df_temp = manual_annotations[
                (manual_annotations.Patient_ID == int(f_id))
                & (manual_annotations.Side == side)
                & (manual_annotations.Type == mm_type)
            ]
            image_name = df_temp.Image_name.tolist()

            # Check if the type is "OP"
            if mm_type == "OP":
                label = [None]
            else:
                label = df_temp["Pathology Classification/ Follow up"].unique().tolist()

            # Add a new row to the DataFrame for each unique label
            if len(label) == 1:
                df.loc[len(df)] = [
                    f_id,
                    image_name,
                    side,
                    mm_type,
                    label[0],
                    " ".join(text_list),
                    file_path
                ]

    return df

# Function to correct the labels in the DataFrame
def label_correction(df,
                     label_column = "label",
                     data_column = "symptoms",
                     patient_id = "Patient_ID",
                     file_path = "file_path"
                     ):

    # Create a new DataFrame with columns for label, symptoms, and patient id
    df_new = pd.DataFrame(columns=[label_column, data_column, patient_id, file_path])
    # Iterate over each unique patient id in the input DataFrame
    for i in df[patient_id].unique():
        # Concatenate all symptoms for that patient id
        annotation = " ".join(df[df[patient_id].isin([i])][data_column].to_list())
        # Get all unique labels for that patient id
        temp_labels = [
            label_indx
            for label_indx in df[df[patient_id] == i][label_column].unique()
            if label_indx is not None
        ]

        # Get the file path for that patient id
        file_path_i = df[df[patient_id].isin([i])][file_path].unique().tolist()[0]
        
        # Add a new row to the new DataFrame for each unique label
        if len(temp_labels) == 1:
            df_new.loc[len(df_new)] = [temp_labels[0], annotation, i, file_path_i]
        elif len(temp_labels) > 1:
            # Check if "CESM" is in the type list
            # CM images are substracted images, if available use the labels of the CM not DM
            # {patient number}_{breast side}_{image type}_{image view}; example ‘P1_L_CM_MLO’
            # (DM)   Digital mammography
            # (CESM) Contrast-enhanced spectral mammography
            df_temp = df[df[patient_id].isin([i])]

            if "CESM" in df_temp.Type.to_list():
                new_label = df_temp[df_temp.Type == "CESM"].label.to_list()[0]
                df_new.loc[len(df_new)] = [new_label, annotation, i, file_path_i]

        else:
            pass

    return df_new

# Function to prepare the data
def prepare_data(target_folder, manual_annotations):
    # Create a new DataFrame with columns for ID, Image, Side, Type, label, and symptoms
    df = pd.DataFrame(columns=["ID", "Image", "Side", "Type", "label", "symptoms", "file_path"])

    # Iterate over each file in the target folder
    for f in os.listdir(target_folder):
        DM_R, DM_L, OP_R, OP_L, CESM_R, CESM_L = "", "", "", "", "", ""
        f_id = f.split(".docx")[0].split("P")[1]
        file_path = os.path.join(target_folder, f)

        # Try to read the content of the file
        try:
            file_content = docx2txt.process(file_path)
        except Exception as e:
            Warning(e)
        
        # Split the content into different sections
        DM_R, DM_L, OP_R, OP_L, CESM_R, CESM_L = read_content(file_content)
        
        # Create a dictionary of text
        dict_text = {
            "DM_R": DM_R,
            "DM_L": DM_L,
            "OP_R": OP_R,
            "OP_L": OP_L,
            "CESM_R": CESM_R,
            "CESM_L": CESM_L,
        }
        
        # Add logs to the DataFrame
        df = add_df_log(df, dict_text, manual_annotations, f_id, file_path)
        
    # Add a new column for patient id
    df["Patient_ID"] = ["".join([str(df.loc[i, "ID"]), df.loc[i, "Side"]]) for i in df.index]
    # Correct the labels in the DataFrame
    df = label_correction(df)
    
    return df

# Define a function that adds image paths to a dataframe
def add_image_path_to_df(df, subtracted_image_path):
    # Initialize an empty dictionary to store image paths
    img_dict = {}

    # Iterate over all files in the subtracted_image_path directory
    for images in os.listdir(subtracted_image_path):
        # If a file is a .jpg image
        if images.endswith(".jpg"):
            # Construct the full path to the image
            image_path = os.path.join(subtracted_image_path, images)        
            # Split the filename to get the patient ID
            pid = images.split("_")[0]
            sd = images.split("_")[1]
            patient_id =  pid[1:]+sd
            
            # If the patient ID is not already a key in img_dict, add it with an empty list as its value
            if patient_id not in img_dict:
                img_dict[patient_id] = []
            # Append the image path to the list associated with the patient ID
            img_dict[patient_id].append(image_path)

    # Convert the dataframe to a list of dictionaries
    df_dict_list = df.to_dict(orient='records')  

    # Iterate over all dictionaries in df_dict_list
    for i in range(len(df_dict_list)):
        # Get the patient ID
        patient_id = df_dict_list[i]['Patient_ID']
        # Set the 'images' key to the list of image paths associated with the patient ID
        df_dict_list[i]['images'] = img_dict[patient_id]
        
    # Convert df_dict_list back to a dataframe and return it
    return pd.DataFrame(df_dict_list)

def resize_images_in_folder(folder_path, output_folder_path, size=(256, 256)):
    """Resize all images in a folder to the specified size and save them in the output folder."""
    
    # Create the target directory if it doesn't exist
    Path(output_folder_path).mkdir(parents=True, exist_ok=True)
        
    # Iterate over all files in the folder
    for filename in os.listdir(folder_path):
        # If the file is an image
        if filename.endswith(".jpg"):
            # Open the image
            img = Image.open(os.path.join(folder_path, filename))
            # Resize the image
            img_resized = img.resize(size)
            # Save the resized image with the same name in the same directory
            img_resized.save(os.path.join(output_folder_path, filename))

def clean_temp_files_and_folders():
    shutil.rmtree("Medical_reports_for_cases")
    shutil.rmtree("CDD-CESM")
    os.remove("manual_annotations.xlsx")

def create_brca_data(downloaded_zip_file):
    
    with zipfile.ZipFile(downloaded_zip_file, "r") as zip_ref:
        zip_ref.extractall()
        
    # The URL of the Excel file to be downloaded and read into a DataFrame
    annotation_file_url = "https://www.cancerimagingarchive.net/wp-content/uploads/Radiology-manual-annotations.xlsx"

    # file name to save the downloaded file
    filename="manual_annotations.xlsx"

    # The function is called with the URL as an argument, and the resulting DataFrame is stored in the variable df
    manual_annotations = download_and_read_excel(annotation_file_url)

    # Define the URL of the zip file and the target directory
    web_url = "https://www.cancerimagingarchive.net/wp-content/uploads/Medical-reports-for-cases-.zip"
    target_folder = "Medical_reports_for_cases"

    # Call the function to download the zip file and extract its contents
    download_and_extract(web_url, target_folder)

    # Call the function to prepare the data
    df = prepare_data(target_folder, manual_annotations)
    
    # Define the path to the subtracted images
    subtracted_image_path = os.path.join(root_folder, "../CDD-CESM/Subtracted images of CDD-CESM")
    
    # Check if the directory exists
    if not os.path.exists(subtracted_image_path):
        raise Exception(f"Directory {subtracted_image_path} does not exist.")
    
    # Call the function with the path to your folder
    # Resize the image and save with the same name in the same directory
    resized_img_folder = os.path.join(root_folder, "resized_subtracted_images_of_CDD_CESM" )            
    resize_images_in_folder(subtracted_image_path, resized_img_folder)
    
    # Call add_image_path_to_df with df and subtracted_image_path as arguments and assign the result to df_new
    df = add_image_path_to_df(df, resized_img_folder)
    
    clean_temp_files_and_folders()
    
    return df

def data_preperation(**kwargs):    
    return create_brca_data(kwargs['zip_file_path'])
    


    