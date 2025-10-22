from backend.imports import *


class Gemini:
    def __init__(self, model_id = "gemini-2.5-flash"):
        self.model_id = model_id
        self.api_key = None
    def load(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        print("Gemini model loaded")

    def show_result(self, image):
        plt.figure(figsize=(12, 8))
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.axis("off")
        plt.show()

        annotated_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        plt.imsave(os.path.join("../Captone_AI/result_images", "annotated_rgb.png"), annotated_rgb)
    

    def stock_estimation(self, image_path, pos_dic, total_pos_dic, stock_dict):
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        config = types.GenerateContentConfig(response_mime_type="application/json")
        fruit_dic = {}

        for fruit, position in pos_dic.items():
            if fruit not in fruit_dic:
                fruit_dic[fruit] = []
            for pos in position:
                box = total_pos_dic[fruit][pos]
                fruit_dic[fruit].append(box)
        
        prompt = f"""
        You are a STRICT JSON generator.
        Given the image and the positions of fruits in the image, estimate the stock level for each fruit based on the fullness of the fruits at the given positions.
        {fruit_dic}

        The stock level for each fruit at each position should be estimated as a percentage (0-100), where 0 means empty and 100 means full.
        Return the result in the following JSON format: for example    
        {{
            "fruit_name": [
                76,78,
                ...
            ],
            ...
        }}
        """
        try:
            client = genai.Client()
            response =client.models.generate_content(
                model=self.model_id,
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type="image/jpeg"
                    ),
                    prompt
                ], config = config
            )
            stock_estimation = json.loads(response.text)
            for fruit, fullness_list in stock_estimation.items():
                for index in range(len(fullness_list)):
                    fullness = fullness_list[index]
                    if fruit in stock_dict and index < len(stock_dict[fruit]):
                        temp = list(stock_dict[fruit][pos_dic[fruit][index]])
                        temp[0] = fullness
                        stock_dict[fruit][pos_dic[fruit][index]] = tuple(temp)
            return stock_dict
        except ClientError as e:
            print(f"An error occurred: {e}")
            return None