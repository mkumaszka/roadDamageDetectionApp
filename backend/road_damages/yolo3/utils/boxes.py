
def correct_boxes(boxes):
    """
    from (left, right, bottom, top)
    to (left, bottom, right, top)
    """

    return [(b[0], b[2], b[1], b[3]) for b in boxes]
