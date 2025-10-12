
from backend_model.imports import *
from backend_model.detection_model import *
from backend_model.segmentation_model import *
from backend_model.prob_calculation import *
from backend_model.stock_estimation_depth import *
import json

image = Image.open("dataset/test_image.jpg")
image_path = "dataset/test_image.jpg"
class_names = ' '.join(['banana', 'broccoli', 'avocado', 'tomato', 'onion'])

if __name__ == "__main__":
    # Initialize and load models
    detection_model = DetectionModel()
    segmentation_model = SegmentationModel("sam2.1_l.pt")
    depth_model = DepthModel()

    detection_model.load_model()
    segmentation_model.load()
    depth_model.load()

    # Detection
    xyxy, labels, scores = detection_model.detect(image, class_names)

    # Segmentation
    results_seg = segmentation_model.segment(image_path, xyxy, labels)

    # Compute fullness (depth-based)
    stock_dict = depth_model.compute_stock(results_seg, image_path)

    # Visualize
    depth_model.visualize_stock(image_path, results_seg, stock_dict, save_path="depth_estimation_overlay.jpg")

    # Calculate probs
    probs = depth_model.cal_probs(stock_dict)
    
    # Prepare results in the format expected by the API
    results = []
    for product in ['banana', 'broccoli', 'avocado', 'tomato', 'onion']:
        if product in stock_dict:
            results.append({
                "product": product,
                "stock_percentage": stock_dict[product] / 100,
                "confidence": probs.get(product, 0.5) if probs else 0.5,
                "reasoning": f"AI model detected {product} with {stock_dict[product]:.1f}% stock level"
            })
    
    # Output results as JSON
    print(json.dumps(results))
