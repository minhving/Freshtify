from backend_model.imports import *
def cal_probs(results_seg):
    prob_dic = {k: [] for k in ["potato section","onion","eggplant section","tomato","cucumber"]}


    masks = results_seg[0].masks.data
    boxes  = results_seg[0].boxes.xyxy
    names  = results_seg[0].names

    H, W = masks.shape[-2], masks.shape[-1]
    masks_np = (masks > 0).cpu().numpy()

    for i in range(len(names)):
        cls = names[i]
        if cls not in prob_dic:
            continue

        x1, y1, x2, y2 = boxes[i].tolist()
        if x2 < x1: x1, x2 = x2, x1
        if y2 < y1: y1, y2 = y2, y1

        xs = max(0, math.floor(x1))
        xe = min(W, math.ceil(x2))
        ys = max(0, math.floor(y1))
        ye = min(H, math.ceil(y2))
        w = max(0, xe - xs)
        h = max(0, ye - ys)
        total_pixel = w * h
        if total_pixel == 0:
            prob_dic[cls].append(0.0)
            continue

        count_pixel = int(masks_np[i, ys:ye, xs:xe].sum())
        prob_dic[cls].append(count_pixel / float(total_pixel))
    prob_dic_final = {k: [] for k in ["potato section","onion","eggplant section","tomato","cucumber"]}
    for fruit, probs in prob_dic.items():
      total = 0
      for prob in probs:
        total += prob
      prob_dic_final[fruit] = total / len(probs)

    return prob_dic_final

def final_probs_estimation(results_seg, result_gemini):
    prob_dic_final = cal_probs(results_seg)
    for fruit, percentage in result_gemini.items():
        if result_gemini[fruit] == 0:
            result_gemini[fruit] = prob_dic_final[fruit] * 100
        else:
            new_percentage = (result_gemini[fruit] + prob_dic_final[fruit] * 100) / 2
            result_gemini[fruit] = new_percentage

    return result_gemini