from enum import IntEnum


class ClientPacketType(IntEnum):
    MOVE_PLAYER = 1
    PICKUP_ITEM = 2
    DROP_ITEM = 3


class ServerPacketType(IntEnum):
    MOVE_PLAYER = 1
    SPAWN_PLAYER = 2
    PICKUP_ITEM = 3
    DROP_ITEM = 4
    SPAWN_ITEM = 5
    DESPAWN_ITEM = 6
    SPAWN_CHEST = 7 # ServerPacketType.SPAWN_STAND:<Player ID>:<Stand ID>:<x>:<y>


class PacketMaker:
    @staticmethod
    def make(action, player_id=None, chest_id=None, object_id=None, x=None, y=None, state=None):
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
        return ":".join(packet) + "\n"
