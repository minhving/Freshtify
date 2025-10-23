from backend_model.imports import *
from backend_model.model_cache import get_model

class PlanningAgent:
    def __init__(self):
        self.detection_model = get_model("detection")
        self.segmentation_model = get_model("segmentation")
        self.depth_model = get_model("depth")
        self.gemini_model = get_model("gemini")

    def process_image(self, image_path, class_names):
        image = Image.open(image_path)

        # Detection
        xyxy, labels, scores = self.detection_model.detect(image, class_names)

        # Segmentation
        results_seg = self.segmentation_model.segment(image_path, xyxy, labels)

        # Depth and compute stock
        stock_dict = self.depth_model.compute_stock(results_seg, image_path)

        # Try to use Gemini for refinement if available
        try:
            if hasattr(self, 'gemini_model') and self.gemini_model:
                pos_dic = {}
                for cls, values in stock_dict.items():
                    index = 0
                    for fullness, layers in values:
                        if fullness == 0:
                            if cls not in pos_dic:
                                pos_dic[cls] = []
                            pos_dic[cls].append(index)
                        index += 1

                if pos_dic:
                    # Get total_pos_dic from depth model's internal state
                    total_pos_dic = getattr(self.depth_model, 'total_pos_dic', {})
                    refined_stock_dict = self.gemini_model.stock_estimation(image_path, pos_dic, total_pos_dic, stock_dict)
                    if refined_stock_dict:
                        stock_dict = refined_stock_dict
        except Exception as e:
            print(f"Gemini refinement failed, using depth-only results: {e}")

        self.depth_model.print_result(stock_dict)