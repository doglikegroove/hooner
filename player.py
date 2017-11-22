import pygame


def play_track(track):
    pygame.mixer.init()
    pygame.mixer.music.load(track)
    pygame.mixer.music.play(0)
