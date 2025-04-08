from client import game_lobby


def main():
    # Example player name, replace with actual input
    player_name = "Player1"

    # Initialize the game lobby
    lobby = game_lobby.GameLobby('Caiden2','0.0.0.0', 53333)  # Replace with actual server IP and port

    # Run the lobby
    lobby.run()


if __name__ == "__main__":
    main()
