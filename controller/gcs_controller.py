
from handler.gcs_handler import StorageHandler
from fastapi import status


class StorageController:

    def __init__(self, infer_dict):
        self.infer_dict = infer_dict

    def store_video(self):
        obj = StorageHandler(self.infer_dict)
        obj.store_input_file()


