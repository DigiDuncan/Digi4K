import nygame

from digi4k.lib.gamemanager import GameManager


class Game(nygame.Game):
    def __init__(self):
        super().__init__(size=(1280, 720), bgcolor=0xAAAAAA, fps = 120, showfps = True)
        self.gm = GameManager(self)

    def loop(self, events):
        self.gm.update(events)


def main():
    Game().run()


if __name__ == "__main__":
    main()
