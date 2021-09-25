from digi4k.lib.objects import Note
import nygame
import pygame


class Game(nygame.Game):
    def __init__(self):
        super().__init__(size=(1280, 720))

        self.lanes = [0, 1, 2, 3]
        self.flags = ["normal", "unknown"]

        self.current_lane = 0
        self.current_flag = 0

    def loop(self, events):
        # Inputs
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT:
                    self.current_lane -= 1
                elif e.key == pygame.K_RIGHT:
                    self.current_lane += 1
                elif e.key == pygame.K_LEFTBRACKET:
                    self.current_flag -= 1
                elif e.key == pygame.K_RIGHTBRACKET:
                    self.current_flag += 1

        self.current_lane %= len(self.lanes)
        self.current_flag %= len(self.flags)
        lane = self.lanes[self.current_lane]
        flag = self.flags[self.current_flag]

        note = Note(lane, 0, 0, flag = flag)
        note_sprite = note.sprite
        note_rect = note_sprite.get_rect()
        note_rect.center = self.surface.get_rect().center
        self.surface.blit(note_sprite, (0, 0))


def main():
    Game().run()


if __name__ == "__main__":
    main()
