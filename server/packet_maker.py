from enum import IntEnum


class ClientPacketType(IntEnum):
    MOVE_PLAYER = 1
    PICKUP_ITEM = 2
    DROP_ITEM = 3
    REQUEST_START_GAME = 4  # so the player can start from the lobby.
    CHEST_DROP = 5  # ClientPacketType.CHEST_DROP:<Player ID>:<Chest ID>
    DESPAWN_ITEM = 6


class ServerPacketType(IntEnum):
    MOVE_PLAYER = 1  # ServerPacketType.MOVE_PLAYER:<Player ID>:<x>:<y>:<state>
    SPAWN_PLAYER = 2  # ServerPacketType.SPAWN_PLAYER:<Player ID>:<x>:<y>
    PICKUP_ITEM = 3  # ServerPacketType.PICKUP_ITEM:<Player ID>:<Object ID>
    DROP_ITEM = 4  # ServerPacketType.DROP_ITEM:<Player ID>:<Object ID>:<x>:<y>
    SPAWN_ITEM = 5  # ServerPacketType.SPAWN_ITEM:<Object ID>:<x>:<y>:<armor type>
    DESPAWN_ITEM = 6  # ServerPacketType.DESPAWN_ITEM:<Object ID>
    SPAWN_CHEST = 7 # ServerPacketType.SPAWN_CHEST:<Player ID>:<Chest ID>:<x>:<y>
    OBJECT_IN_CHEST = 8 # ServerPacketType.OBJECT_IN_CHEST:<Chest ID>:<Object ID>
    WIN_PLAYER = 9 # ServerPacketType.WIN_PLAYER:<Player ID>
    START_GAME = 10


class PacketMaker:
    @staticmethod
    def make(action, player_id=None, chest_id=None, object_id=None, x=None, y=None, state=None, armor_type=None):
        packet = [str(action.value)] # used to be packet = [str(action)]
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
