import asyncio
import json
import sys
import requests
import FreeSimpleGUI as sg
import pygame
from pygame.locals import K_ESCAPE, K_SPACE, K_UP, KEYDOWN, QUIT, K_l
from src.entities import score

from .entities import (
    Background,
    Floor,
    GameOver,
    Pipes,
    Player,
    PlayerMode,
    Score,
    WelcomeMessage,
)
from .utils import GameConfig, Images, Sounds, Window


class Flappy:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Flappy Bird")
        window = Window(288, 512)
        screen = pygame.display.set_mode((window.width, window.height))
        images = Images()

        self.config = GameConfig(
            screen=screen,
            clock=pygame.time.Clock(),
            fps=30,
            window=window,
            images=images,
            sounds=Sounds(),
        )

    async def start(self, apiURL):
        while True:
            self.apiURL = apiURL
            self.raw = None
            self.background = Background(self.config)
            self.floor = Floor(self.config)
            self.player = Player(self.config)
            self.welcome_message = WelcomeMessage(self.config)
            self.game_over_message = GameOver(self.config)
            self.pipes = Pipes(self.config)
            self.score = Score(self.config)
            layout = [
                [sg.Text("please enter in your name")],
                [sg.InputText(key="Input1")],
                [sg.Button("Confirm"), sg.Button("Cancel")],
            ]
            window = sg.Window("Connect to server", layout, finalize=True)
            window["Input1"].bind("<Return>", "_Enter")
            event, values = window.read()
            if event == "Confirm" or event == "Input1" + "_Enter":
                window.close()
                self.name = values["Input1"]
            if event == sg.WIN_CLOSED or event == "Cancel":
                window.close()
                pygame.quit()
                sys.exit()
            await self.splash()
            await self.play()
            await self.game_over()

    async def splash(self):
        """Shows welcome splash screen animation of flappy bird"""

        self.player.set_mode(PlayerMode.SHM)
        highscore = self.get_highscore()
        font = pygame.font.SysFont(None, 24)
        hs_text = font.render(f"Highscore: {highscore}", True, (255, 255, 255))
        lb_text = font.render("press L for Leaderboard", True, (255, 255, 255))

        while True:
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.check_leaderboard(event):
                    await self.leaderboard()
                elif self.is_tap_event(event):
                    return

            self.background.tick()
            self.floor.tick()
            self.player.tick()
            self.welcome_message.tick()
            self.config.screen.blit(hs_text, (10, 10))
            self.config.screen.blit(lb_text, (10, 30))
            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    async def leaderboard(self):
        font = pygame.font.SysFont(None, 24)
        leaderboard_font = pygame.font.SysFont(None, 32)
        if self.raw == None:
            self.raw = requests.get(f"{self.apiURL}/get")
        leaderboard_json = self.raw.json()
        leaderboard_json = leaderboard_json["leaderboard"]
        users = []
        for user in leaderboard_json:
            users += [f"{user['name']}: Score {user['score']}"]
        back_text = font.render("Press ESC to go back", True, (255, 255, 255))
        while True:
            for event in pygame.event.get():
                if event.type == QUIT or (
                    event.type == KEYDOWN and event.key == K_ESCAPE
                ):
                    return
                elif self.is_tap_event(event):
                    return
            self.background.tick()
            self.floor.tick()
            self.player.tick()
            self.config.screen.blit(back_text, (10, 10))  # Adjust position as needed
            for i in range(len(users)):
                j = i * 30
                leaderboard = leaderboard_font.render(users[i], True, (255, 255, 255))
                self.config.screen.blit(
                    leaderboard, (20, 30 + j)
                )  # Adjust position as needed
            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    def get_highscore(self) -> int:
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except (FileNotFoundError, ValueError):
            return 0

    def set_highscore(self, score):
        with open("highscore.txt", "w") as f:
            f.write(str(score))
        return

    def check_quit_event(self, event):
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

    def check_leaderboard(self, event):
        if event.type == KEYDOWN and event.key == K_l:
            return True

    def is_tap_event(self, event):
        m_left, _, _ = pygame.mouse.get_pressed()
        space_or_up = event.type == KEYDOWN and (
            event.key == K_SPACE or event.key == K_UP
        )
        screen_tap = event.type == pygame.FINGERDOWN
        return m_left or space_or_up or screen_tap

    async def play(self):
        self.score.reset()
        self.player.set_mode(PlayerMode.NORMAL)

        while True:
            if self.player.collided(self.pipes, self.floor):
                return

            for i, pipe in enumerate(self.pipes.upper):
                if self.player.crossed(pipe):
                    self.score.add()

            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    self.player.flap()

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
            self.player.tick()

            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    async def game_over(self):
        """crashes the player down and shows gameover image"""

        self.player.set_mode(PlayerMode.CRASH)
        self.pipes.stop()
        self.floor.stop()

        requests.patch(
            f"{self.apiURL / score}",
            json={"name": self.name, "score": str(self.score.current())},
        )
        if self.score.current() > self.get_highscore():
            self.set_highscore(self.score.current())

        while True:
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    if self.player.y + self.player.h >= self.floor.y - 1:
                        return

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
            self.player.tick()
            self.game_over_message.tick()

            self.config.tick()
            pygame.display.update()
            await asyncio.sleep(0)
