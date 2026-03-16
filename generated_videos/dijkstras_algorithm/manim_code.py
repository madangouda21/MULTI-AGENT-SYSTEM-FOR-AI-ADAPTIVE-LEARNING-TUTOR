from manim import *

class DijkstrasAlgorithm(Scene):
    def construct(self):
        # Background color
        self.camera.background_color = "#1e1e2e"

        # Scene 1: Introduction to Graphs
        nodes = VGroup(
            Dot(LEFT * 3 + UP * 2, color=BLUE_C),
            Dot(LEFT * 1 + UP * 1, color=BLUE_C),
            Dot(RIGHT * 1 + UP * 2, color=BLUE_C),
            Dot(RIGHT * 3 + UP * 1, color=BLUE_C),
            Dot(RIGHT * 5 + UP * 2, color=BLUE_C)
        )
        labels = VGroup(
            MathTex("Home").next_to(nodes[0], DOWN),
            MathTex("A").next_to(nodes[1], DOWN),
            MathTex("B").next_to(nodes[2], DOWN),
            MathTex("C").next_to(nodes[3], DOWN),
            MathTex("Ice Cream Shop").next_to(nodes[4], DOWN)
        )
        edges = VGroup(
            Line(nodes[0], nodes[1], color=YELLOW),
            Line(nodes[0], nodes[2], color=YELLOW),
            Line(nodes[1], nodes[3], color=YELLOW),
            Line(nodes[2], nodes[3], color=YELLOW),
            Line(nodes[3], nodes[4], color=YELLOW)
        )
        
        self.play(Create(nodes), Write(labels))
        self.play(Create(edges))
        self.wait()

        # Scene 2: The Algorithm Begins
        self.play(nodes[0].animate.set_color(PURPLE_B))
        arrows = VGroup(
            Arrow(nodes[0], nodes[1], color=GREEN_C),
            Arrow(nodes[0], nodes[2], color=GREEN_C)
        )
        self.play(Create(arrows))
        self.wait()

        # Highlight the shortest path
        shortest_path = edges[0].copy().set_stroke(width=8)
        self.play(Transform(shortest_path, edges[0]))
        self.wait()

        # Scene 3: Path Exploration
        self.play(arrows[0].animate.set_color(YELLOW))
        new_arrows = VGroup(
            Arrow(nodes[1], nodes[3], color=GREEN_C)
        )
        self.play(Create(new_arrows))
        self.wait()

        # Highlight the new shortest path
        new_shortest_path = edges[2].copy().set_stroke(width=8)
        self.play(Transform(new_shortest_path, edges[2]))
        self.wait()

        # Scene 4: Conclusion
        final_path = VGroup(edges[0], edges[2], edges[4]).copy().set_stroke(color=YELLOW, width=8)
        self.play(Transform(final_path, final_path))
        
        moving_dot = Dot(color=GREEN_C).move_to(nodes[0])
        path_animation = MoveAlongPath(moving_dot, final_path)
        self.play(path_animation)
        self.wait()

        self.play(FadeOut(VGroup(nodes, edges, arrows, new_arrows, final_path, labels, moving_dot)))
        self.wait()