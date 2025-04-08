from enum import IntEnum


class ClientPacketType(IntEnum):
    MOVE_PLAYER = 1
    PICKUP_ITEM = 2
    DROP_ITEM = 3
    REQUEST_START_GAME = 4  # so the player can start from the lobby.


class ServerPacketType(IntEnum):
    MOVE_PLAYER = 1
    SPAWN_PLAYER = 2
    PICKUP_ITEM = 3
    DROP_ITEM = 4
    SPAWN_ITEM = 5
    DESPAWN_ITEM = 6
    SPAWN_CHEST = 7  # ServerPacketType.SPAWN_STAND:<Player ID>:<Stand ID>:<x>:<y>
    START_GAME = 8  # newly added for the game lobby -- starting game


class PacketMaker:
    @staticmethod
    def make(action, player_id=None, chest_id=None, object_id=None, x=None, y=None, state=None, armor_type=None):
        packet = [str(action)]
        if player_id is not None:
            packet.append(str(player_id))
        if chest_id is not None:
            packet.append(str(chest_id))
        if object_id is not None:
            packet.append(str(object_id))
        if x is not None and y is not None:
            packet.append(str(x))
            packet.append(str(y))
        if state is not None:
            packet.append(str(state))
        if armor_type is not None:
            packet.append(str(armor_type))
        return ":".join(packet) + "\n"
