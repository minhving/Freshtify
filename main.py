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

        #detection
        xyxy, labels, scores = detection_model.detect(image, class_names)

        #segmentation
        results_seg = segmentation_model.segment(image_path, xyxy, labels)

        #depth and compute stock
        stock_dict = depth_model.compute_stock(results_seg,image_path)
        print(stock_dict)
        print(f"Image: {name}")
        print(f"Length stock dict {len(stock_dict)}\n")
        depth_model.print_result(stock_dict)