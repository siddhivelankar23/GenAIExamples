import json
import os 
import pandas as pd 



# ============================================ WIP =========================================
# from embeddings.BridgeTowerEmbeddings import BridgeTowerEmbeddings
# from vectorstores.MultimodalBase import MultimodalRedis
# from mm_rag_redis.multimodal_config import EMBED_MODEL, INDEX_NAME, INDEX_SCHEMA, REDIS_URL

# def load_json_file(file_path):
#       # Open the JSON file in read mode
#       with open(file_path, 'r') as file:
#           data = json.load(file)
#       return data

# def prepare_data_and_metadata_from_annotation(annotation, path_to_frames, title, description, num_transcript_concat_for_ingesting=2, num_transcript_concat_for_inference=7):
        
#     text_list = []
#     image_list = []
#     metadatas = []
#     for i, frame in enumerate(annotation):
#         frame_index = frame['sub_video_id']
#         path_to_frame = os.path.join(path_to_frames, f"frame_{frame_index}.jpg")
#         lb_ingesting = max(0, i-num_transcript_concat_for_ingesting)
#         ub_ingesting = min(len(annotation), i+num_transcript_concat_for_ingesting+1) 
#         caption_for_ingesting = ' '.join([annotation[j]['caption'] for j in range(lb_ingesting, ub_ingesting)])

#         lb_inference = max(0, i-num_transcript_concat_for_inference)
#         ub_inference = min(len(annotation), i+num_transcript_concat_for_inference+1) 
#         caption_for_inference = ' '.join([annotation[j]['caption'] for j in range(lb_inference, ub_inference)])
        
#         time_of_frame = frame['time']
#         embedding_type = 'pair'
#         text_list.append(caption_for_ingesting)
#         image_list.append(path_to_frame)
#         metadatas.append({
#             'content' : caption_for_ingesting,
#             'source' : path_to_frame,
#             'time_of_frame_ms' : float(time_of_frame),
#             'embedding_type' : embedding_type,
#             'title' : title,
#             'description' : description,
#             'transcript_for_inference' : caption_for_inference,
#         })
        
#     return text_list, image_list, metadatas


def ingest_multimodal(**kwargs):  # title, , description, data_folder):
    """
    Ingest text image pairs to Redis from the data/ directory that
    contains frames and captions from Pats keynotes 2023.
    """
    # Update these 
    # Load annotation file    
    # title = "Chips Making Deal Video"
    # description = "The image is extracted from the President Biden's Chip Making Deal video" 
    # data_folder = "../videos/ChipmakingDeal/video_embeddings/mp4.ChipmakingDeal/"

    title = kwargs['title'] 
    title_for_embedding = kwargs['title_for_embedding']  
    description = kwargs['description']  
    data_folder= kwargs['data_folder'] 
    
    print(title, title_for_embedding, description, data_folder)
    
    return pd.DataFrame()
    
#     data_folder = os.path.abspath(data_folder)
#     annotation_file_path = os.path.join(data_folder, 'annotations.json')
#     path_to_frames = os.path.join(data_folder, 'frames')

#     annotation = load_json_file(annotation_file_path)

#     #prepare data to ingest
#     text_list, image_list, metadatas = prepare_data_and_metadata_from_annotation(annotation, path_to_frames, title, description)

#     # Create vectorstore
#     embedder = BridgeTowerEmbeddings()
#     # index_schema = 'schema.yml'
#     # index_name = 'ringthebell-rag-redis'

#     instance, keys = MultimodalRedis.from_text_image_pairs_return_keys(
#         # appending this little bit can sometimes help with semantic retrieval
#         texts=[f"From {title_for_embedding}. " + text for text in text_list],
#         images=image_list,
#         embedding=embedder,
#         metadatas=metadatas,
#         index_name=INDEX_NAME,
#         index_schema=INDEX_SCHEMA,
#         redis_url=REDIS_URL,
#     )
#     print(f"DONE Ingesting {title}!")


