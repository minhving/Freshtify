from backend.imports import *
from backend.detection_model import *
from backend.segmentation_model import *
from backend.gemini_model import *
from backend.prob_calculation import *
image = Image.open("../Captone_AI/dataset/test_image.jpg")
image_path = "../Captone_AI/dataset/test_image.jpg"
class_names = 'potato section . onion . eggplant section . tomato . cucumber .'


if __name__ == "__main__":
    detection_model = DetectionModel()
    segmentation_model = SegmentationModel("sam2.1_l.pt")
    gemini_model = Gemini()

    detection_model.load_model()
    segmentation_model.load()
    gemini_model.load()


    xyxy, labels, scores = detection_model.detect(image,   class_names)
    results_seg = segmentation_model.segment(image_path, xyxy, labels)
    preds = gemini_model.annotate_crates_stock_percentage(image_path, results_seg[0].boxes.xyxy, results_seg[0].names)

    final_probs = final_probs_estimation(results_seg, preds)
    print(final_probs)