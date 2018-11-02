def inner_area_similarity_from_boxes(b1, b2):  # (left, bottom, right, top)
    if not b1 or not b2:
        return 0.0

    area_a = (b1[2] - b1[0]) * (b1[3] - b1[1])
    area_b = (b2[2] - b2[0]) * (b2[3] - b2[1])

    if area_a > 0 and area_b > 0:
        min_right = b1[2] if b1[2] < b2[2] else b2[2]
        max_left = b1[0] if b1[0] > b2[0] else b2[0]
        min_top = b1[3] if b1[3] < b2[3] else b2[3]
        max_bottom = b1[1] if b1[1] > b2[1] else b2[1]

        right_left_diff = min_right - max_left
        right_left_diff = right_left_diff if right_left_diff > 0.0 else 0.0

        top_bot_diff = min_top - max_bottom
        top_bot_diff = top_bot_diff if top_bot_diff > 0.0 else 0.0

        area_a_and_b = right_left_diff * top_bot_diff

        a = area_a_and_b / area_a
        b = area_a_and_b / area_b
        return a if a > b else b
    else:
        return 0.0
