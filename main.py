from backend.planning_agent import *

image_arr =  ['T0', 'T1']
class_names = 'potato section . onion . eggplant section . tomato . cucumber .'

if __name__ == "__main__":
    #Initualize and load model
    planning_agent = PlanningAgent()

    for name in image_arr:
        image_path = f"../Freshtify/dataset/{name}.jpg"
        print(f"Processing image: {image_path}")
        planning_agent.process_image(image_path, class_names)
        