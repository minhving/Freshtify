from backend.imports import *
from backend.model_cache import get_model

image_arr =  ['T0', 'T1']
class_names = 'potato section . onion . eggplant section . tomato . cucumber .'

if __name__ == "__main__":
    #Initualize and load model
    detection_model = get_model("detection")
    segmentation_model = get_model("segmentation")
    depth_model = get_model("depth")

    for name in image_arr:
        image_path = f"../Freshtify/dataset/{name}.jpg"
        image = Image.open(image_path)
        xyxy, labels, scores = detection_model.detect(image, class_names)
        results_seg = segmentation_model.segment(image_path, xyxy, labels)
        stock_dict = depth_model.compute_stock(results_seg,image_path)
        print(stock_dict)
        print(f"Image: {name}")
        print(f"Length stock dict {len(stock_dict)}\n")
        depth_model.print_result(stock_dict)
    # # Detection
    # xyxy, labels, scores = detection_model.detect(image, class_names)

    # #Segmentation
    # results_seg = segmentation_model.segment(image_path, xyxy, labels)

    # # Compute fullness (depth-based)
    # stock_dict = depth_model.compute_stock(results_seg,image_path)

    # # Visualize
    # # depth_model.visualize_stock(image_path, results_seg, stock_dict, save_path="depth_estimation_overlay.jpg")

    # # #Calculate probs
    # # probs = depth_model.cal_probs(stock_dict)
    # # print(probs)
    # print(stock_dict)
