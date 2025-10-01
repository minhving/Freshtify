from ultralytics import YOLO
import torch
from torchvision.transforms import Compose, Resize, ToTensor
from torchvision import transforms
import cv2
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
import numpy as np
import requests
from PIL import Image
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
from matplotlib.patches import Rectangle
import math
import cv2, json, re, time
from typing import List, Tuple
from tqdm import tqdm
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from huggingface_hub import login
from ultralytics import SAM