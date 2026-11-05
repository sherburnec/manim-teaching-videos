from manimlib import *


class SmokeScene(Scene):
    def construct(self):
        self.play(ShowCreation(Circle()))
        self.play(Write(Text("hello")))
