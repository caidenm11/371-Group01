class Player:
    def __init__(self, player_id, x=0, y=0):
        self.player_id = player_id
        self.x = x
        self.y = y
        self.inventory = []  # List of held object IDs

    def move(self, keys):
        speed = 7
        if "w" in keys:
            self.y -= speed
        if "s" in keys:
            self.y += speed
        if "a" in keys:
            self.x -= speed
        if "d" in keys:
            self.x += speed