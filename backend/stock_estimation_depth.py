from backend.imports import *

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