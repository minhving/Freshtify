from backend_model.imports import *
CLASSES = ["potato section", "onion", "eggplant section", "tomato", "cucumber"]
class DepthModel:
    def __init__(self, model_type="DPT_Hybrid"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_id = model_type
        self.model_depth = None
        self.transform = None
    def load(self):
        load_dotenv()
        hugging_face_token = os.getenv('HF_TOKEN')
        login(token=hugging_face_token)

        self.model_depth = torch.hub.load("intel-isl/MiDaS", self.model_id)
        self.model_depth.eval().to(self.device)
        self.transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
        self.transform = self.transforms.dpt_transform if "large" in self.model_id.lower() else self.transforms.small_transform
        print("Loaded depth model sucessfully")
    def get_depth(self, img_path, normalize=True):
        img = cv2.imread(img_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        input_batch = self.transform(img_rgb).to(self.device)

        with torch.no_grad():
            prediction = self.model_depth(input_batch)
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

    def check_has_stock(self,mask, depth_map, bbox, min_diff=0.01, min_obj_pixels=200):
        x1, y1, x2, y2 = map(int, bbox)
        submask = mask[y1:y2, x1:x2]
        subdepth = depth_map[y1:y2, x1:x2]

        obj_depths = subdepth[submask > 0]
        bg_depths = subdepth[submask == 0]

        # Nếu không có object → empty
        if obj_depths.size == 0:
            return False, None, None

        depth_obj = np.median(obj_depths)

        # Nếu không có background (mask full object) → coi như có stock
        if bg_depths.size == 0:
            return True, depth_obj, None

        depth_bg = np.median(bg_depths)
        diff = abs(depth_bg - depth_obj)
        # Avoid empty box due object pixel overlap background pixel
        if diff < min_diff and obj_depths.size > min_obj_pixels:
            return True, depth_obj, depth_bg

        return diff >= min_diff, depth_obj, depth_bg
    def extract_masks(self, results):
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

    def estimate_fullness(self, mask, depth_map, bbox, min_pixels=50):

        # Tính fullness theo pixel ratio, tạm thời layers chỉ 0/1.

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

    def compute_stock(self, results_seg,img_path):
        items = self.extract_masks(results_seg)
        depth_map = self.get_depth(img_path)
        stock_dict = {}

        for cls, box, mask in items:
            has_stock, d_obj, d_bg = self.check_has_stock(mask, depth_map, box)
            if not has_stock:
                val = (0.0, 0)
            else:
                fullness, layers = self.estimate_fullness(mask, depth_map, box)
                val = (float(fullness), int(layers))

            stock_dict.setdefault(cls, []).append(val)

        return stock_dict

    def visualize_stock(self,img_path, results_seg, stock_dict, save_path="stock_overlay.jpg"):
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

        idx_map = {cls: 0 for cls in stock_dict.keys()}
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
            c = color_map.get(cls, (0, 255, 0))
            cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), c, 2)

            # vẽ label
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(img, (int(x1), int(y1) - th - 4), (int(x1) + tw + 4, int(y1)), c, -1)
            cv2.putText(img, label, (int(x1) + 2, int(y1) - 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imwrite(save_path, img)
        return img
    def print_result(self,stock_dict):
        print("\nStock estimation results (depth-based):")
        for cls, values in stock_dict.items():
            for fullness, layers in values:
                print(f"{cls}: {fullness:.1f}% ")

    def cal_probs(self , stock_dict):
        prob_dic = {}
        for cls, values in stock_dict.items():
            total = 0
            for fullness, layers in values:
                total += fullness
            prob_dic[cls] = total / len(values)
        return prob_dic
