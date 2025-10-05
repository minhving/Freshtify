from backend.imports import *
from backend.detection_model import *
from backend.segmentation_model import *
#from backend.gemini_model import *
from backend.prob_calculation import *
from backend.stock_estimation_depth import *
image = Image.open("C:/Users/Admin/Freshtify/dataset/test_image.jpg")
image_path = "C:/Users/Admin/Freshtify/dataset/test_image.jpg"
class_names = 'potato section . onion . eggplant section . tomato . cucumber .'


if __name__ == "__main__":
    detection_model = DetectionModel()
    segmentation_model = SegmentationModel("sam2.1_l.pt")
    #gemini_model = Gemini()

    detection_model.load_model()
    segmentation_model.load()

    # Detection
    print("Running detection...")
    xyxy, labels, scores = detection_model.detect(image, class_names)

    #Segmentation
    print("Running segmentation...")
    results_seg = segmentation_model.segment(image_path, xyxy, labels)
    masks_dict = extract_masks(results_seg)
    #: Depth estimation
    print("Loading MiDaS depth model...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    depth_model, depth_tf = load_midas("DPT_Hybrid", device)
    depth_map = get_depth_map(image_path, depth_model, depth_tf, device)

    # Compute fullness (depth-based)
    stock_dict = compute_stock(results_seg, depth_map)

    print("\nStock estimation results (depth-based):")
    for cls, values in stock_dict.items():
        for fullness, layers in values:
            print(f"{cls}: {fullness:.1f}% ")

    # Visualize
    print("\nSaving visualization...")
    visualize_stock(image_path, results_seg, stock_dict, save_path="depth_estimation_overlay.jpg")