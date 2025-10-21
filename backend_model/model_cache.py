
from backend_model.detection_model import *
from backend_model.segmentation_model import *
#from backend_model.gemini_model import *
from backend_model.prob_calculation import *
from backend_model.stock_estimation_depth import *

_models = {}

def get_model(name):
    if name not in _models:
        if name == "detection":
            model = DetectionModel()
            model.load_model()
        elif name == "segmentation":
            model = SegmentationModel("sam2.1_l.pt")
            model.load()
        elif name == "depth":
            model = DepthModel()
            model.load()
        else:
            raise ValueError(f"Unknown model: {name}")
        _models[name] = model
    return _models[name]