from digi4k.lib.draw_objects import DisplayNote, Note
import nygame
import pygame
from nygame import DigiText as T


class Game(nygame.Game):
    def __init__(self):
        super().__init__(size=(1280, 720), bgcolor=0xAAAAAA)

        self.lanes = [0, 1, 2, 3]
        self.flags = ["normal", "bomb", "death", "gold", "unknown"]

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

        note = DisplayNote(Note(lane, 0, 0, flag = flag))
        note_sprite = note.sprite
        note_rect = note_sprite.get_rect()
        note_rect.center = self.surface.get_rect().center
        self.surface.blit(note_sprite, note_rect)
        label = T(self.flags[self.current_flag] + " " + str(self.current_lane), font = "Lato Medium", size = 48)
        label_rect = label.get_rect()
        label_rect.bottom = note_rect.top
        label_rect.x = note_rect.x
        label_rect.move_ip(0, -10)
        label.render_to(self.surface, label_rect)


def main():
    Game().run()


if __name__ == "__main__":
    main()
