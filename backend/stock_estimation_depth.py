from backend.imports import *
import numpy as np
import torch
import cv2

CLASSES = ["potato section", "onion", "eggplant section", "tomato", "cucumber"]

def load_midas(model_type="DPT_Hybrid", device="cuda"):
    model = torch.hub.load("intel-isl/MiDaS", model_type)
    model.eval().to(device)

    transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
    transform = transforms.dpt_transform if "large" in model_type.lower() else transforms.small_transform
    return model, transform


def get_depth_map(img_path, model, transform, device="cuda", normalize=True):
    img = cv2.imread(img_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    input_batch = transform(img_rgb).to(device)

    with torch.no_grad():
        prediction = model(input_batch)
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=img_rgb.shape[:2],
            mode="bicubic",
            align_corners=False,
        ).squeeze()

    depth = prediction.cpu().numpy()

    if normalize:
        depth = (depth - depth.min()) / (depth.max() - depth.min())

    return depth

def extract_masks(results):
    out = []
    names = results[0].names
    boxes = results[0].boxes.xyxy.cpu().numpy().tolist()
    classes = [names[int(c)] for c in results[0].boxes.cls]

    if results[0].masks is None:
        print("No masks found in results")
        return out

    for i, mask_tensor in enumerate(results[0].masks.data):
        class_id = int(results[0].boxes.cls[i])
        class_name = names[class_id]
        mask = mask_tensor.cpu().numpy().astype(np.uint8)
        box = boxes[i]
        out.append((class_name, box, mask))

    return out

def check_has_stock(mask, depth_map, bbox, min_diff=0.01):
    
    #Check if section has stock by comparing min depth of object vs background.
    #mask: binary mask
    #min_diff: threshold for stock detection
    x1, y1, x2, y2 = map(int, bbox)
    submask = mask[y1:y2, x1:x2]
    subdepth = depth_map[y1:y2, x1:x2]

    obj_depths = subdepth[submask > 0]
    bg_depths  = subdepth[submask == 0]

    # Nếu không có object pixel → chắc chắn empty
    if obj_depths.size == 0:
        return False, None, None

    # Nếu không có background pixel (mask full object) thì overide là có stock
    if bg_depths.size == 0:
        return True, obj_depths.min(), None

    depth_obj_min = obj_depths.min()
    depth_bg_min  = bg_depths.min()

    diff = abs(depth_obj_min - depth_bg_min)
    has_stock = diff >= min_diff

    return has_stock, depth_obj_min, depth_bg_min


def estimate_fullness(mask, depth_map, bbox, min_pixels=50):
    
    #Tính fullness theo pixel ratio, tạm thời layers chỉ 0/1.
    
    x1, y1, x2, y2 = map(int, bbox)
    submask = mask[y1:y2, x1:x2]

    mask_pixels = submask.sum()
    bbox_area = submask.size

    if mask_pixels < min_pixels:
        return 0.0, 0

    fullness_pct = (mask_pixels / bbox_area) * 100

    # Layers chỉ: 0 (empty) hoặc 1 (non-empty)
    layers = 1 if fullness_pct > 1 else 0

    return fullness_pct, layers


def compute_stock(results_seg, depth_map):
    items = extract_masks(results_seg)
    stock_dict = {}

    for cls, box, mask in items:
        has_stock, d_obj, d_bg = check_has_stock(mask, depth_map, box)
        if not has_stock:
            val = (0.0, 0)
        else:
            fullness, layers = estimate_fullness(mask, depth_map, box)
            val = (float(fullness), int(layers))


        stock_dict.setdefault(cls, []).append(val)

    return stock_dict

def visualize_stock(img_path, results_seg, stock_dict, save_path="stock_overlay.jpg"):
    img = cv2.imread(img_path)
    boxes = results_seg[0].boxes.xyxy.cpu().numpy().tolist()
    classes = [results_seg[0].names[int(c)] for c in results_seg[0].boxes.cls]

    color_map = {
        "potato section": (0, 255, 0),
        "onion": (255, 0, 0),
        "eggplant section": (128, 0, 128),
        "tomato": (0, 165, 255),
        "cucumber": (255, 255, 0)
    }

    idx_map = {cls:0 for cls in stock_dict.keys()}  
    for i, (x1, y1, x2, y2) in enumerate(boxes):
        cls = classes[i]
        if cls not in stock_dict:
            continue

        # lấy kết quả fullness/layers theo index object
        if idx_map[cls] < len(stock_dict[cls]):
            fullness, layers = stock_dict[cls][idx_map[cls]]
            idx_map[cls] += 1
        else:
            fullness, layers = (0.0, 0)

        # text hiển thị
        label = f"{cls}: {fullness:.1f}% | L{layers}"

        # vẽ bbox
        c = color_map.get(cls, (0,255,0))
        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), c, 2)

        # vẽ label
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.rectangle(img, (int(x1), int(y1)-th-4), (int(x1)+tw+4, int(y1)), c, -1)
        cv2.putText(img, label, (int(x1)+2, int(y1)-2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    cv2.imwrite(save_path, img)
    return img
