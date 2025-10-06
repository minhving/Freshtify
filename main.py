from backend.imports import *
from backend.detection_model import *
from backend.segmentation_model import *
#from backend.gemini_model import *
from backend.prob_calculation import *
from backend.stock_estimation_depth import *
image = Image.open("../Captone_AI/dataset/test_image.jpg")
image_path = "../Captone_AI/dataset/test_image.jpg"
class_names = 'potato section . onion . eggplant section . tomato . cucumber .'

if __name__ == "__main__":
    #Initualize and load model
    detection_model = DetectionModel()
    segmentation_model = SegmentationModel("sam2.1_l.pt")
    depth_model = DepthModel()
    #gemini_model = Gemini()

    detection_model.load_model()
    segmentation_model.load()
    depth_model.load()

    # Detection
    xyxy, labels, scores = detection_model.detect(image, class_names)

    #Segmentation
    results_seg = segmentation_model.segment(image_path, xyxy, labels)

    # Compute fullness (depth-based)
    stock_dict = depth_model.compute_stock(results_seg,image_path)

    # Visualize
    depth_model.visualize_stock(image_path, results_seg, stock_dict, save_path="depth_estimation_overlay.jpg")

    #Calculate probs
    probs = depth_model.cal_probs(stock_dict)
    print(probs)
