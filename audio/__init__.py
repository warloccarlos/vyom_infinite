import pygame
from pygame import mixer
from tkinter import filedialog
from mutagen.mp3 import MP3
from PIL import Image
import customtkinter as ctk
from io import BytesIO
import os
import random

class AudioEngine:
    def __init__(self):
        pygame.init() 
        mixer.pre_init(44100, -16, 2, 2048)
        mixer.init()
        self.SONG_END = pygame.USEREVENT + 1
        mixer.music.set_endevent(self.SONG_END)
        self.playlist = []
        self.current_index = 0
        self.song_length = 0
        self.repeat_mode = "none"

    def add_to_playlist(self):
        files = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if files: self.playlist.extend(list(files))
        return files

    def remove_from_playlist(self, path):
        if path in self.playlist:
            idx = self.playlist.index(path)
            self.playlist.remove(path)
            if idx <= self.current_index and self.current_index > 0:
                self.current_index -= 1

    def shuffle_playlist(self):
        if len(self.playlist) > 1:
            current_path = self.playlist[self.current_index]
            random.shuffle(self.playlist)
            self.current_index = self.playlist.index(current_path)

    def load_metadata(self):
        try:
            path = self.playlist[self.current_index]
            audio = MP3(path)
            self.song_length = audio.info.length
            return True
        except: return False

    def get_album_art(self):
        try:
            path = self.playlist[self.current_index]
            audio = MP3(path)
            tags = audio.tags.getall('APIC')
            if tags:
                return ctk.CTkImage(Image.open(BytesIO(tags[0].data)), size=(320, 320))
        except: pass
        return None

    def play(self):
        if self.playlist:
            mixer.music.stop()
            mixer.music.unload()
            pygame.event.clear()
            mixer.music.load(self.playlist[self.current_index])
            mixer.music.play()

    def set_volume(self, val):
        mixer.music.set_volume(float(val))

    def get_current_pos(self):
        pos = mixer.music.get_pos()
        return max(0, pos / 1000)