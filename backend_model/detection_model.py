from transformers import DataProcessor, AutoModel

from backend_model.imports import *

class DetectionModel:
    def __init__(self, model_id = "IDEA-Research/grounding-dino-base"):
        self.model_id = model_id
        self.device = None
        self.processor = None
        self.model_dec = None

    def load_model(self):
        try:
            load_dotenv()
        except Exception as e:
            print(f"Warning: Could not load .env file: {e}")
        
        hugging_face_token = os.getenv('HF_TOKEN')
        if hugging_face_token and hugging_face_token != 'hf_your_token_here':
            login(token=hugging_face_token)
        else:
            print("Warning: No valid HF_TOKEN found, using public models")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = AutoProcessor.from_pretrained(self.model_id)
        self.model_dec = AutoModelForZeroShotObjectDetection.from_pretrained(self.model_id).to(self.device)
        print("Loaded model successfully")

    def show_gd_results(self ,img, results, score_thr = 0.2):
        if isinstance(img, str):
            img = Image.open(img).convert("RGB")
        elif isinstance(img, torch.Tensor):
            if img.ndim == 3 and img.shape[0] in (1, 3):
                img = img.permute(1, 2, 0).detach().cpu().numpy()
            else:
                img = img.detach().cpu().numpy()
            img = (img * 255).astype(np.uint8) if img.max() <= 1 else img.astype(np.uint8)
            img = Image.fromarray(img)
        elif not isinstance(img, Image.Image):
            img = Image.fromarray(img)

        r = results[0] if isinstance(results, (list, tuple)) else results
        boxes = r["boxes"].detach().cpu().numpy()
        scores = r["scores"].detach().cpu().numpy()
        labels = r.get("labels", r.get("text_labels", []))

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.imshow(np.asarray(img))
        for (x1, y1, x2, y2), s, lab in zip(boxes, scores, labels):
            if s < score_thr:
                continue
            ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False, linewidth=2, edgecolor='blue'))
            ax.text(x1, max(0, y1 - 5), f"{lab} {s:.2f}",
                    fontsize=9, color="white",
                    bbox=dict(facecolor="blue", alpha=0.5, pad=2))
        ax.axis("off")
        plt.show()

    def detect_fruits(self, image, class_name):
        text = class_name
        inputs = self.processor(images=image, text=text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model_dec(**inputs)
        results = self.processor.post_process_grounded_object_detection(
            outputs,
            inputs.input_ids,
            target_sizes=[image.size[::-1]],
            text_threshold=0.1,
            threshold=0.1
        )
        #self.show_gd_results(image, results)
        return results

    def iou_matrix(self, box, boxes):
        x1 = np.maximum(box[0], boxes[:, 0])
        y1 = np.maximum(box[1], boxes[:, 1])
        x2 = np.minimum(box[2], boxes[:, 2])
        y2 = np.minimum(box[3], boxes[:, 3])
        inter = np.maximum(0, x2 - x1) * np.maximum(0, y2 - y1)
        area_box = (box[2] - box[0]) * (box[3] - box[1])
        area_boxes = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
        union = area_box + area_boxes - inter + 1e-9
        return inter / union
# Update contain_thr = 0 .9 for extra step 2
    def nms_class_agnostic(self,xyxy, scores, labels, iou_thr=0.5, contain_thr=0.9):
        xyxy = np.asarray(xyxy, dtype=float)
        scores = np.asarray(scores, dtype=float)
        idxs = np.argsort(-scores)

        keep = []
        while idxs.size > 0:
            i = idxs[0]
            keep.append(i)
            if idxs.size == 1:
                break
            rest = idxs[1:]
            ious = self.iou_matrix(xyxy[i], xyxy[rest])

            # Step 2: containment filter
            # If a smaller box j is covered > contain_thr (90%) by box i,
            # then drop j even if IoU is low (nested box case).
            contain = []
            for j in rest:
                inter_x1 = max(xyxy[i][0], xyxy[j][0])
                inter_y1 = max(xyxy[i][1], xyxy[j][1])
                inter_x2 = min(xyxy[i][2], xyxy[j][2])
                inter_y2 = min(xyxy[i][3], xyxy[j][3])
                inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
                area_j = (xyxy[j][2] - xyxy[j][0]) * (xyxy[j][3] - xyxy[j][1])
                if area_j > 0 and inter_area / area_j > contain_thr:
                    contain.append(j)
            #Step 1 + 2 combined
            mask = (ious <= iou_thr)
            idxs = rest[mask & (~np.isin(rest, contain))]

        return sorted(keep)


    def detect(self, image, class_name,score_thr=0, max_per_class=20):
        results_dec = self.detect_fruits(image, class_name)
        dic_ind = {"potato section": [], "onion": [], "eggplant section": [], "tomato": [], 'cucumber': []}

        for idx, label in enumerate(results_dec[0]['text_labels']):
            score = float(results_dec[0]['scores'][idx])
            if label not in dic_ind:
                continue
            if score >= score_thr:  # lọc score thấp
                dic_ind[label].append(idx)

        xyxy, labels, scores = [], [], []

        for fruit, index_list in dic_ind.items():
            for i in index_list:
                x1, y1, x2, y2 = results_dec[0]['boxes'][i]
                xyxy.append([float(x1), float(y1), float(x2), float(y2)])
                labels.append(fruit)
                scores.append(float(results_dec[0]['scores'][i]))

        keep = self.nms_class_agnostic(xyxy, scores, labels, iou_thr=0.5)

        xyxy_final = [xyxy[i] for i in keep]
        labels_final = [labels[i] for i in keep]
        scores_final = [scores[i] for i in keep]

        return xyxy_final, labels_final, scores_final
