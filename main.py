from backend_model.planning_agent import *
import os

dataset_dir = "dataset"
image_arr = []
for i in range(10):
    filename = f"T{i}.jpg"
    filepath = os.path.join(dataset_dir, filename)
    if os.path.exists(filepath):
        image_arr.append(f"T{i}")
    elif i == 0: 
        image_arr = ['T0', 'T1']
        break

print(f"Found images to process: {image_arr}")

class_names = 'potato section . onion . eggplant section . tomato . cucumber .'

if __name__ == "__main__":
    #Initualize and load model
    planning_agent = PlanningAgent()

    for name in image_arr:
        image_path = f"dataset/{name}.jpg"
        print(f"Processing image: {image_path}")
        planning_agent.process_image(image_path, class_names)
        