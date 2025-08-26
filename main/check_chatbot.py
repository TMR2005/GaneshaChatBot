import torch
print(torch.__version__)
print(torch.version.cuda)
print("CUDA Available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("Device:", torch.cuda.get_device_name(0))

import transformers
from transformers import pipeline
print("Transformers OK")

import psycopg2
print("Postgres driver OK")
