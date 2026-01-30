import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from google.cloud import storage
import uuid

class StorageHandler:

    def __init__(self, infer_dict):
        self.infer_dict = infer_dict


    def store_input_file(self):
        file = self.infer_dict["file"]
