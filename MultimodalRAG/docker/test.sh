# # Set default values

# USE_CASE="mm_rag_medical"
# ZIP_FILE_PATH=$(pwd)/../../../test/CDD-CESM.zip

# # Run the Python script with the parsed arguments
# python data_prepare_entry.py \
#     --set_workload \
#         use_case="$USE_CASE" \
#         zip_file_path="$ZIP_FILE_PATH"




USE_CASE="mm_rag_vision"
TITLE="Title" 
TITLE_FOR_EMBEDDING="TITLE_FOR_EMBEDDING"
DESCRIPTION="dESCRIPTION"
DATA_FOLDER="DATA_FOLDER"

python data_prepare_entry.py \
    --set_workload \
        use_case="$USE_CASE" \
        title="$TITLE" \
        title_for_embedding="$TITLE_FOR_EMBEDDING" \
        description="$DESCRIPTION" \
        data_folder="$DATA_FOLDER"



# python embed_ingest.py \