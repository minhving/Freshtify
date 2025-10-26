from backend_model.imports import *
CLASSES = ["potato section", "onion", "eggplant section", "tomato", "cucumber"]
class DepthModel:
    def __init__(self, model_type="DPT_Hybrid"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_id = model_type
        self.model_depth = None
        self.transform = None
        self.result_root_seg = None
    def load(self):
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


    def _boxes_iou(self,b1, b2):
        N, M = b1.size(0), b2.size(0)
        b1 = b1[:, None, :]
        b2 = b2[None, :, :] 
        x1 = torch.max(b1[..., 0], b2[..., 0])
        y1 = torch.max(b1[..., 1], b2[..., 1])
        x2 = torch.min(b1[..., 2], b2[..., 2])
        y2 = torch.min(b1[..., 3], b2[..., 3])
        inter = (x2 - x1).clamp(min=0) * (y2 - y1).clamp(min=0)
        a1 = (b1[..., 2]-b1[..., 0]).clamp(min=0) * (b1[..., 3]-b1[..., 1]).clamp(min=0)
        a2 = (b2[..., 2]-b2[..., 0]).clamp(min=0) * (b2[..., 3]-b2[..., 1]).clamp(min=0)
        union = a1 + a2 - inter + 1e-6
        return inter / union

    def _pairwise_center_dist(self, b1, b2):
        c1 = torch.stack([(b1[:,0]+b1[:,2])/2, (b1[:,1]+b1[:,3])/2], dim=1)  # [N,2]
        c2 = torch.stack([(b2[:,0]+b2[:,2])/2, (b2[:,1]+b2[:,3])/2], dim=1)  # [M,2]
        return torch.cdist(c1, c2)  # [N,M]

    def _scale_aware_thr(self, b1, base_px=0.15):
        w = (b1[:,2]-b1[:,0]).clamp(min=1.0)
        h = (b1[:,3]-b1[:,1]).clamp(min=1.0)
        diag = torch.sqrt(w*w + h*h)
        return base_px * diag  # [N]

    def _binarize_and_morph(self, mask, thr=0.5, dilate_ks=0, close_ks=0):
        out = (mask >= thr).float()
        if dilate_ks and dilate_ks > 1:
            k = dilate_ks if dilate_ks % 2 == 1 else dilate_ks+1
            pad = k//2
            out = F.max_pool2d(out.unsqueeze(0).unsqueeze(0), k, stride=1, padding=pad).squeeze()
        if close_ks and close_ks > 1:
            k = close_ks if close_ks % 2 == 1 else close_ks+1
            pad = k//2
            dil = F.max_pool2d(out.unsqueeze(0).unsqueeze(0), k, stride=1, padding=pad)
            ero = -F.max_pool2d(-dil, k, stride=1, padding=pad)
            out = ero.squeeze()
        return out

    def replace_masks_robust(self,
        results, results_2,
        iou_thr=0.1,
        center_rel=0.15, 
        src_thresh=0.5,  
        merge_mode="union", 
        dilate_ks=3,  
        close_ks=0    
    ):
        r1, r2 = results[0], results_2[0]
        boxes1 = r1.boxes.xyxy.float()
        boxes2 = r2.boxes.xyxy.float()
        if boxes1.numel() == 0 or boxes2.numel() == 0:
            return results

        masks1 = r1.masks.data 
        masks2 = r2.masks.data
        device = masks1.device
        dtype  = masks1.dtype
        boxes1, boxes2 = boxes1.to(device), boxes2.to(device)
        masks2 = masks2.to(device)

        if masks1.shape[-2:] != masks2.shape[-2:]:
            masks2 = F.interpolate(
                masks2.unsqueeze(1).float(), size=masks1.shape[-2:], mode="bilinear", align_corners=False
            ).squeeze(1)
        IoU = self._boxes_iou(boxes1, boxes2) 
        best2_for_1 = IoU.argmax(dim=1)
        best1_for_2 = IoU.argmax(dim=0)


        mutual = torch.arange(boxes1.size(0), device=device)
        is_mutual_best = (best1_for_2[best2_for_1] == mutual)
        good_iou = IoU[mutual, best2_for_1] >= iou_thr
        matched = is_mutual_best & good_iou
        if (~matched).any():
            d = self._pairwise_center_dist(boxes1, boxes2)
            idx2 = d.argmin(dim=1) 
            per_box_thr = self._scale_aware_thr(boxes1, center_rel)
            ok_center = d[torch.arange(d.size(0), device=device), idx2] <= per_box_thr
            use_center = (~matched) & ok_center
            final_idx2 = best2_for_1.clone()
            final_idx2[use_center] = idx2[use_center]
            matched = matched | use_center
        else:
            final_idx2 = best2_for_1

        if not matched.any():
            return results 

        new_masks = masks1.clone()

        inds = torch.nonzero(matched, as_tuple=False).flatten()
        src_sel = masks2[final_idx2[inds]].float()
        src_sel = torch.stack([self._binarize_and_morph(m, thr=src_thresh, dilate_ks=dilate_ks, close_ks=close_ks) for m in src_sel], dim=0)
        src_sel = src_sel.to(dtype)

        if merge_mode == "overwrite":
            new_masks[inds] = src_sel
        else: 
            new_masks[inds] = torch.maximum(new_masks[inds].to(dtype), src_sel)

        r1.masks.data = new_masks.detach().clone()
        return results
    def compute_stock(self, results_seg,img_path):
        if self.result_root_seg is None:
            self.result_root_seg = results_seg

        else:
            mask = torch.zeros(self.result_root_seg[0].masks.data.shape, dtype=torch.bool)
            self.result_root_seg[0].masks.data = mask

            self.result_root_seg = self.replace_masks_robust(
                self.result_root_seg, results_seg,
                iou_thr=0.15,   
                center_rel=0.20,     
                src_thresh=0.4,     
                merge_mode="union", 
                dilate_ks=3,        
                close_ks=3
            )
            # self.result_root_seg[0].show()

        items = self.extract_masks(self.result_root_seg)
        depth_map = self.get_depth(img_path)
        stock_dict = {}
        pos_dic = {}
        for cls, box, mask in items:
            has_stock, d_obj, d_bg = self.check_has_stock(mask, depth_map, box)
            if not has_stock:
                val = (0.0, 0)
            else:
                fullness, layers = self.estimate_fullness(mask, depth_map, box)
                val = (float(fullness), int(layers))
            pos_dic.setdefault(cls, []).append(box)
            stock_dict.setdefault(cls, []).append(val)
        # self.visualize_stock(img_path, self.result_root_seg, stock_dict, save_path=f"{img_path}_depth_estimation_overlay.jpg")
        return stock_dict, pos_dic

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
            index = 1
            for fullness, layers in values:
                print(f"{cls} - section {index}: {fullness:.1f}% ")
                index += 1