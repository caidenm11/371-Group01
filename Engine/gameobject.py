class GameObject:
    def __init__(self, object_id, x, y):
        self.object_id = object_id
        self.x = x
        self.y = y
        self.held_by = None  # None means it's on the ground
