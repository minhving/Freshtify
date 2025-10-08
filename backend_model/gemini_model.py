from backend.imports import *


class Gemini:
    def __init__(self, model_id = "gemini-2.5-pro"):
        self.model_id = model_id
        self.api_key = None
    def load(self):
        self.api_key = os.getenv('GEMINI_API')
        print("Gemini model loaded")


    def show_result(self, image):
        plt.figure(figsize=(12, 8))
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.axis("off")
        plt.show()

        annotated_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        plt.imsave(os.path.join("../Captone_AI/result_images", "annotated_rgb.png"), annotated_rgb)

    def annotate_crates_stock_percentage(self,
            image_path,
            boxes,
            names: List[str],
            wait_base_seconds: float = 1.5
    ) -> Tuple[any, List[Tuple[str, str]]]:
        if not self.api_key:
            raise ValueError("api_keys must be non-empty")

        img_bgr = cv2.imread(image_path)
        key_idx = 0
        client = genai.Client(api_key=self.api_key)

        H, W = img_bgr.shape[:2]
        out_img = img_bgr.copy()
        predictions: List[Tuple[str, str]] = []

        norm_boxes: List[Tuple[int, int, int, int]] = []
        for b in boxes:
            try:
                x1, y1, x2, y2 = [int(getattr(v, "item", lambda: v)()) for v in b]
            except Exception:
                x1, y1, x2, y2 = map(int, b)
            x1, y1 = max(0, min(x1, W - 1)), max(0, min(y1, H - 1))
            x2, y2 = max(0, min(x2, W)), max(0, min(y2, H))
            if x2 <= x1 or y2 <= y1:
                norm_boxes.append((0, 0, 0, 0))
            else:
                norm_boxes.append((x1, y1, x2, y2))

        for i, (x1, y1, x2, y2) in enumerate(tqdm(norm_boxes, desc="Processing status")):
            fruit_name = names[i] if i < len(names) else "UNKNOWN"

            if x2 <= x1 or y2 <= y1:
                predictions.append((fruit_name, "ERROR"))
                continue

            json_example = f'{{"type": "{fruit_name}", "stock percentage": "85%"}}'
            prompt = (
                "You are a strict JSON generator.\n"
                "Task: Look at the crate in the image.\n"
                f"This is the fruit name: {fruit_name}\n"
                "Estimate how full the crate is as a percentage (0-100%).\n"
                "Return ONLY valid JSON with keys exactly: type, stock percentage.\n"
                f"Example: {json_example}\n"
                "Rules:\n"
                "- Do not include code fences, markdown, or explanations.\n"
                '- stock percentage MUST be a string ending with a percent sign, e.g. "73%".'
            )

            ok, buf = cv2.imencode(".jpg", out_img[y1:y2, x1:x2])
            if not ok:
                predictions.append((fruit_name, "ERROR"))
                continue
            payload = types.Part.from_bytes(data=buf.tobytes(), mime_type="image/jpeg")

            attempts = 0
            while attempts < len(self.api_key):
                try:
                    resp = client.models.generate_content(
                        model=self.model_id,
                        contents=[payload, prompt]
                    )

                    text = (getattr(resp, "text", None) or "").strip()
                    if not text and getattr(resp, "candidates", None):
                        try:
                            text = "".join(getattr(p, "text", "") for p in resp.candidates[0].content.parts).strip()
                        except Exception:
                            text = ""

                    parsed = None
                    if text:
                        try:
                            parsed = json.loads(text)
                        except Exception:
                            cleaned = re.sub(r"```[a-zA-Z]*", "", text).replace("```", "").strip()
                            m = re.search(r"\{.*\}", cleaned, flags=re.S)
                            if m:
                                try:
                                    parsed = json.loads(m.group(0))
                                except Exception:
                                    parsed = None

                    t = parsed.get("type") if isinstance(parsed, dict) else None
                    f = parsed.get("stock percentage") if isinstance(parsed, dict) else None
                    if not isinstance(t, str): t = "UNKNOWN"
                    if not isinstance(f, str): f = "ERROR"

                    predictions.append((t, f))

                    label = f"{t}: {f}"
                    cv2.rectangle(out_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)
                    cv2.rectangle(out_img, (x1, y1), (x1 + tw + 8, y1 + th + 10), (0, 0, 0), cv2.FILLED)
                    cv2.putText(out_img, label, (x1 + 4, y1 + th + 2),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_AA)
                    break
                except ClientError as e:
                    status = getattr(e, "status_code", None) or getattr(getattr(e, "response", None), "status_code",
                                                                        None)
                    if status == 429:
                        delay = wait_base_seconds * (2 ** attempts)
                        time.sleep(delay)
                        key_idx = (key_idx + 1) % len(self.api_key)
                        client = genai.Client(api_key=self.api_key)
                        attempts += 1
                        continue
                    else:
                        predictions.append((fruit_name, "0%"))
                        break
                except Exception:
                    predictions.append((fruit_name, "0%"))
                    break
        prob_dic_final_1 = {k: [] for k in ["potato section", "onion", "eggplant section", "tomato", "cucumber"]}
        fruit_dic = {k: [] for k in ["potato section", "onion", "eggplant section", "tomato", "cucumber"]}

        for index in range(len(predictions)):
            fruit, percentage = predictions[index]
            if fruit in fruit_dic:
                percentage = float(percentage[:-1])
                fruit_dic[fruit].append(percentage)

        for fruit, percentages in fruit_dic.items():
            total = 0

            for i in percentages:
                total += i

            prob_dic_final_1[fruit] = float(total / len(percentages))

        self.show_result(out_img)
        return prob_dic_final_1


