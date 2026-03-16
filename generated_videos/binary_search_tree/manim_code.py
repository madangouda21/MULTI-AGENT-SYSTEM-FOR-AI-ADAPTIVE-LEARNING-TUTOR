from manim import *

class BinarySearchTree(Scene):
    def construct(self):
        self.camera.background_color = "#1e1e2e"
        
        # Scene 1: Root Node
        root_node = Circle(color=WHITE).move_to(UP*2)
        root_text = MathTex("Root").move_to(root_node.get_center())
        self.play(Create(root_node), Write(root_text))
        self.wait()

        left_arrow = Arrow(root_node.get_bottom(), root_node.get_bottom() + LEFT*2 + DOWN)
        right_arrow = Arrow(root_node.get_bottom(), root_node.get_bottom() + RIGHT*2 + DOWN)
        self.play(Create(left_arrow), Create(right_arrow))
        self.wait()

        # Scene 2: Tree Structure
        left_node = Circle(color=WHITE).shift(LEFT*2 + DOWN)
        left_value = MathTex("3").move_to(left_node.get_center())
        right_node = Circle(color=WHITE).shift(RIGHT*2 + DOWN)
        right_value = MathTex("20").move_to(right_node.get_center())

        self.play(Create(left_node), Write(left_value), Create(right_node), Write(right_value))
        self.wait()

        left_child = Circle(color=WHITE).shift(LEFT*4 + DOWN*2)
        left_child_value = MathTex("5").move_to(left_child.get_center())
        right_child = Circle(color=WHITE).shift(RIGHT*4 + DOWN*2)
        right_child_value = MathTex("25").move_to(right_child.get_center())

        self.play(Create(left_child), Write(left_child_value), Create(right_child), Write(right_child_value))
        self.wait()

        self.play(Create(Line(root_node.get_center(), left_node.get_center())), 
                  Create(Line(root_node.get_center(), right_node.get_center())))
        self.wait()

        # Scene 3: Highlighted Search Path
        search_path = VGroup(Line(root_node.get_center(), right_node.get_center(), color=YELLOW),
                             Line(right_node.get_center(), right_child.get_center(), color=YELLOW))
        self.play(Create(search_path))
        self.wait()

        # Scene 4: Balancing Animation
        self.play(left_child.animate.shift(RIGHT))
        self.play(right_child.animate.shift(LEFT))
        self.wait()