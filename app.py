import customtkinter as ctk
import pygame
import os
from PIL import Image, ImageTk
from audio import AudioEngine

class VyomBoldPlayer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("VYOM INFINITE - BOLD MUSIC PLAYER")
        self.geometry("550x850")
        ctk.set_appearance_mode("dark")
        
        self.engine = AudioEngine()
        self.accent = "#00FFC8"
        self.playback_id = 0
        self.is_playing = False
        self.is_paused = False

        # --- THE FIX: Robust Icon Loading ---
        self.load_app_icon()

        # --- Tabs ---
        self.tabs = ctk.CTkTabview(self, corner_radius=30, segmented_button_selected_color=self.accent)
        self.tabs.pack(padx=20, pady=20, fill="both", expand=True)
        self.tab_player = self.tabs.add("PLAYER")
        self.tab_list = self.tabs.add("PLAYLIST")

        # --- PLAYER TAB ---
        self.art_label = ctk.CTkLabel(self.tab_player, text="VYOM", font=("Impact", 80), 
                                      width=320, height=320, fg_color="#111111", corner_radius=25)
        self.art_label.pack(pady=40)

        self.song_label = ctk.CTkLabel(self.tab_player, text="VYOM INFINITE", font=("Segoe UI", 22, "bold"))
        self.song_label.pack()

        self.progress = ctk.CTkProgressBar(self.tab_player, width=420, height=12, progress_color=self.accent)
        self.progress.pack(pady=20)
        self.progress.set(0)

        self.time_label = ctk.CTkLabel(self.tab_player, text="00:00 / 00:00", font=("Consolas", 16))
        self.time_label.pack()

        # Controls
        self.ctrl_frame = ctk.CTkFrame(self.tab_player, fg_color="transparent")
        self.ctrl_frame.pack(pady=30)

        self.btn_shuf = ctk.CTkButton(self.ctrl_frame, text="🔀", width=60, height=60, 
                                      fg_color="#222", command=self.shuffle)
        self.btn_shuf.grid(row=0, column=0, padx=10)

        self.btn_play = ctk.CTkButton(self.ctrl_frame, text="▶", width=100, height=100, corner_radius=50, 
                                      font=("Arial", 40), fg_color=self.accent, text_color="black", command=self.toggle_play)
        self.btn_play.grid(row=0, column=1, padx=20)

        self.btn_rep = ctk.CTkButton(self.ctrl_frame, text="🔁", width=60, height=60, 
                                     fg_color="#222", command=self.toggle_repeat)
        self.btn_rep.grid(row=0, column=2, padx=10)

        self.vol_slider = ctk.CTkSlider(self.tab_player, from_=0, to=1, width=250, button_color=self.accent, command=self.engine.set_volume)
        self.vol_slider.pack(pady=20)
        self.vol_slider.set(0.7)

        # --- PLAYLIST TAB ---
        self.scroll_frame = ctk.CTkScrollableFrame(self.tab_list, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkButton(self.tab_list, text="UPLOAD TRACKS", fg_color=self.accent, text_color="black", 
                      font=("Segoe UI", 16, "bold"), height=50, command=self.add_tracks).pack(pady=15, padx=20, fill="x")

    def load_app_icon(self):
        """Loads icon using standard PIL to avoid pyimage conflicts"""
        try:
            if os.path.exists("icon.png"):
                img = Image.open("icon.png")
                self.icon_tk = ImageTk.PhotoImage(img)
                self.wm_iconphoto(True, self.icon_tk)
        except: pass

    def shuffle(self):
        if self.engine.playlist:
            self.engine.shuffle_playlist()
            self.refresh_list()
            self.btn_shuf.configure(text_color=self.accent)

    def toggle_repeat(self):
        modes = ["none", "all", "one"]
        idx = (modes.index(self.engine.repeat_mode) + 1) % 3
        self.engine.repeat_mode = modes[idx]
        color = self.accent if self.engine.repeat_mode != "none" else "#222"
        self.btn_rep.configure(fg_color=color, text="🔂" if idx == 2 else "🔁")

    def refresh_list(self):
        for w in self.scroll_frame.winfo_children(): w.destroy()
        for f in self.engine.playlist:
            btn = ctk.CTkButton(self.scroll_frame, text=f"• {os.path.basename(f)}", fg_color="transparent", 
                                anchor="w", command=lambda p=f: self.play_specific(p))
            btn.pack(fill="x")
            btn.bind("<Button-3>", lambda e, p=f: self.remove_track(p))

    def remove_track(self, path):
        self.engine.remove_from_playlist(path)
        self.refresh_list()

    def add_tracks(self):
        if self.engine.add_to_playlist():
            self.refresh_list()
            if not self.is_playing: self.play_specific(self.engine.playlist[0])

    def play_specific(self, path):
        if path in self.engine.playlist:
            self.engine.current_index = self.engine.playlist.index(path)
            self.start_playback()
            self.tabs.set("PLAYER")

    def start_playback(self):
        if self.engine.load_metadata():
            self.playback_id += 1
            self.engine.play()
            self.is_playing, self.is_paused = True, False
            self.btn_play.configure(text="⏸")
            name = os.path.basename(self.engine.playlist[self.engine.current_index])
            self.song_label.configure(text=name[:25].upper())
            art = self.engine.get_album_art()
            self.art_label.configure(image=art, text="" if art else "VYOM")
            self.update_loop(self.playback_id)

    def toggle_play(self):
        if not self.is_playing and self.engine.playlist: self.start_playback()
        elif self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.btn_play.configure(text="⏸")
        elif self.is_playing:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.btn_play.configure(text="▶")

    def update_loop(self, loop_id):
        if loop_id != self.playback_id: return
        for event in pygame.event.get():
            if event.type == self.engine.SONG_END:
                if self.engine.repeat_mode == "one": self.start_playback()
                elif self.engine.current_index < len(self.engine.playlist) - 1:
                    self.engine.current_index += 1
                    self.start_playback()
                elif self.engine.repeat_mode == "all":
                    self.engine.current_index = 0
                    self.start_playback()
                else: self.is_playing = False
                return
        if self.is_playing and not self.is_paused:
            curr, total = self.engine.get_current_pos(), self.engine.song_length
            if total > 0:
                self.progress.set(curr / total)
                self.time_label.configure(text=f"{int(curr//60):02d}:{int(curr%60):02d} / {int(total//60):02d}:{int(total%60):02d}")
        self.after(100, lambda: self.update_loop(loop_id))

if __name__ == "__main__":
    app = VyomBoldPlayer()
    app.mainloop()