from backend.imports import *


class SegmentationModel:
    def __init__(self, model_name = "sam2.1_l.pt"):
        self.model_name = model_name
        self.model_seg = None

    def load(self):
        self.model_seg = SAM(self.model_name)
        print("Segmentation model loaded")

    def segment(self, image_path, xyxy,labels):
        results = self.model_seg.predict(image_path, bboxes = xyxy)
        for index, names in results[0].names.items():
            results[0].names[index] = f"{labels[index]}"
        results[0].show()
        results[0].save("../Captone_AI/result_images/result_segmentation_image.jpg")
        return results


