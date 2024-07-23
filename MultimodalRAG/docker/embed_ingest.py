# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import os
from mm_rag_redis.multimodal_config import EMBED_MODEL, INDEX_NAME, INDEX_SCHEMA, REDIS_URL
import json

# import sys
from embeddings.BridgeTowerEmbeddings import BridgeTowerEmbeddings
from vectorstores.MultimodalBase import MultimodalRedis

from comps import MMRagGateway, MicroService, ServiceOrchestrator, ServiceType

MEGA_SERVICE_HOST_IP = os.getenv("MEGA_SERVICE_HOST_IP", "0.0.0.0")
MEGA_SERVICE_PORT = int(os.getenv("MEGA_SERVICE_PORT", 8888))
EMBEDDING_SERVICE_HOST_IP = os.getenv("EMBEDDING_SERVICE_HOST_IP", "0.0.0.0")
EMBEDDING_SERVICE_PORT = int(os.getenv("EMBEDDING_SERVICE_PORT", 6000))



class MMRagService:
    def __init__(self, host="0.0.0.0", port=8000):
        self.host = host
        self.port = port
        self.megaservice = ServiceOrchestrator()

    def add_remote_service(self):
        embedding = MicroService(
            name="embedding",
            host=EMBEDDING_SERVICE_HOST_IP,
            port=EMBEDDING_SERVICE_PORT,
            endpoint="/v1/embeddings",
            use_remote_service=True,
            service_type=ServiceType.EMBEDDING,
        )
        
        self.megaservice.add(embedding)

        self.gateway = MMRagGateway(megaservice=self.megaservice, host="0.0.0.0", port=self.port)

    def load_json_file(file_path):
      # Open the JSON file in read mode
      with open(file_path, 'r') as file:
          data = json.load(file)
      return data

    def prepare_data_and_metadata_from_annotation(annotation, path_to_frames, title, description, num_transcript_concat_for_ingesting=2, num_transcript_concat_for_inference=7):
      text_list = []
      image_list = []
      metadatas = []
      for i, frame in enumerate(annotation):
          frame_index = frame['sub_video_id']
          path_to_frame = os.path.join(path_to_frames, f"frame_{frame_index}.jpg")
          lb_ingesting = max(0, i-num_transcript_concat_for_ingesting)
          ub_ingesting = min(len(annotation), i+num_transcript_concat_for_ingesting+1) 
          caption_for_ingesting = ' '.join([annotation[j]['caption'] for j in range(lb_ingesting, ub_ingesting)])
  
          lb_inference = max(0, i-num_transcript_concat_for_inference)
          ub_inference = min(len(annotation), i+num_transcript_concat_for_inference+1) 
          caption_for_inference = ' '.join([annotation[j]['caption'] for j in range(lb_inference, ub_inference)])
          
          time_of_frame = frame['time']
          embedding_type = 'pair'
          text_list.append(caption_for_ingesting)
          image_list.append(path_to_frame)
          metadatas.append({
              'content' : caption_for_ingesting,
              'source' : path_to_frame,
              'time_of_frame_ms' : float(time_of_frame),
              'embedding_type' : embedding_type,
              'title' : title,
              'description' : description,
              'transcript_for_inference' : caption_for_inference,
          })
      return text_list, image_list, metadatas
  
    def ingest_multimodal(title, title_for_embedding, description, data_folder):
      """
      Ingest text image pairs to Redis from the data/ directory that
      contains frames and captions from Pats keynotes 2023.
      """
      # Update these 
      # Load annotation file    
      # title = "Chips Making Deal Video"
      # description = "The image is extracted from the President Biden's Chip Making Deal video" 
      # data_folder = "../videos/ChipmakingDeal/video_embeddings/mp4.ChipmakingDeal/"    
      
      data_folder = os.path.abspath(data_folder)
      annotation_file_path = os.path.join(data_folder, 'annotations.json')
      path_to_frames = os.path.join(data_folder, 'frames')
  
      annotation = load_json_file(annotation_file_path)
  
      #prepare data to ingest
      text_list, image_list, metadatas = prepare_data_and_metadata_from_annotation(annotation, path_to_frames, title, description)
      
      # Create vectorstore
      embedder = BridgeTowerEmbeddings()
      # index_schema = 'schema.yml'
      # index_name = 'ringthebell-rag-redis'
      
      instance, keys = MultimodalRedis.from_text_image_pairs_return_keys(
          # appending this little bit can sometimes help with semantic retrieval
          texts=[f"From {title_for_embedding}. " + text for text in text_list],
          images=image_list,
          embedding=embedder,
          metadatas=metadatas,
          index_name=INDEX_NAME,
          index_schema=INDEX_SCHEMA,
          redis_url=REDIS_URL,
      )
      print(f"DONE Ingesting {title}!")


if __name__ == "__main__":
    mmrag = MMRagService(host=MEGA_SERVICE_HOST_IP, port=MEGA_SERVICE_PORT)
    mmrag.add_remote_service()
    #   Write logic to ingest embeddings
