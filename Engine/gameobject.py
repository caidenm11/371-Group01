class GameObject:
    def __init__(self, object_id, x, y, armor_type):
        self.object_id = object_id
        self.x = x
        self.y = y
        self.armor_type = armor_type
        self.held_by = None  # None means it's on the ground
