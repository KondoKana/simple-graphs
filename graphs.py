from random import shuffle
from typing import Literal
import pygame
import pygame_gui
import grid

# pygame setup
pygame.init()
info = pygame.display.Info()
screen_percentage = 0.5
screen_height = min(info.current_w, info.current_h)*screen_percentage
screen_width = screen_height*1.5
manager = pygame_gui.UIManager((screen_width, screen_height))

screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
running = True
dt = 0
colors = pygame.colordict.THECOLORS

class options:
    def __init__(self,
                  show_hitboxes: Literal["Full", "Small", "None"] = "None",
                  show_mouse_pos = True):
        self.show_hitboxes = show_hitboxes
        self.show_mouse_pos = show_mouse_pos
options = options()
class binding:
    def __init__(self, event, button=None, key=None, mod=pygame.KMOD_NONE):
        self.event = event
        self.button = button
        self.key = key
        self.mod = mod

class command:
    def __init__(self, name, bindings: list[binding], func = None):
        self.name = name
        self.func = func
        self.bindings = bindings

    def evoke(self, event: pygame.event.Event):
        for binding in self.bindings:
            if event.type == binding.event and (getattr(event, "key", None) is None or event.key == binding.key) and ((binding.mod == pygame.KMOD_NONE) ^ (pygame.key.get_mods() & binding.mod)) and (getattr(event, "button", None) is None or event.button == binding.button):
                if self.func is not None:
                    self.func()
                return True
        return False

class hitbox_type:
    VERTEX = "vertex"
    EDGE = "edge"
class orientation:
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"

class hitbox:
    def __init__ (self, rect: pygame.Rect, type: hitbox_type, orientation_val: orientation, value = None, color = (0,0,0)):
        self.rect : pygame.Rect = rect
        self.type : hitbox_type = type
        self.orientation : orientation = orientation_val
        self.color = color
        self.value = value

# actual display grid which holds the grid backend and also has some display related properties
class d_grid:
    def __init__ (self, grid: grid.Grid, line_width = 1):
        self.update_grid(grid)
        self.line_width = line_width

    def update_grid(self, grid: grid.Grid):
        self.grid_w = grid.width
        self.grid_h = grid.height
        self.grid_size_px = screen_height
        self.num_cr = max(self.grid_w, self.grid_h) #number of columns and rows of the underlying grid
        self.num_lines = self.num_cr + 2 #number of lines to draw
        self.line_spacing = self.grid_size_px / self.num_lines+1 #spacing between lines in pixels
        self.hitboxes = []
        color_list = list(colors.keys())
        shuffle(color_list)
        color_iter = iter(color_list)
        #creates top large hitbox
        rect = pygame.Rect((0, 0), (self.grid_size_px, self.line_spacing*1.25))
        self.hitboxes.append(hitbox(rect, hitbox_type.VERTEX, orientation.HORIZONTAL, value=-1, color=colors[next(color_iter)]))
        #creates a left large hitbox
        rect = pygame.Rect((0, 0), (self.line_spacing*1.25, self.grid_size_px))
        self.hitboxes.append(hitbox(rect, hitbox_type.VERTEX, orientation.VERTICAL, value=-1, color=colors[next(color_iter)]))


        for i in range((self.num_cr*2)-1):
            #makes the vertical hitboxes for the vertices and edges, alternating between the two types and coloring them differently for testing purposes
            rect = pygame.Rect((self.line_spacing*1.25 + i*self.line_spacing*1/2, 0), (self.line_spacing*1/2, self.grid_size_px))
            if i%2 == 0:
                self.hitboxes.append(hitbox(rect, hitbox_type.VERTEX, orientation.VERTICAL, value=int(i/2), color=colors[next(color_iter)]))
            else:
                self.hitboxes.append(hitbox(rect, hitbox_type.EDGE, orientation.VERTICAL, value=int(i/2), color=colors[next(color_iter)]))
            
            #makes the horizontal hitboxes for the vertices and edges, alternating between the two types and coloring them differently for testing purposes
            rect = pygame.Rect((0, self.line_spacing*1.25 + i*self.line_spacing*1/2), (self.grid_size_px, self.line_spacing*1/2))
            if i%2 == 0:
                self.hitboxes.append(hitbox(rect, hitbox_type.VERTEX, orientation.HORIZONTAL, value=int(i/2), color=colors[next(color_iter)]))
            else:
                self.hitboxes.append(hitbox(rect, hitbox_type.EDGE, orientation.HORIZONTAL, value=int(i/2), color=colors[next(color_iter)]))
        
        #creates a right large hitbox
        rect = pygame.Rect((self.grid_size_px - self.line_spacing*1.25, 0), (self.line_spacing*1.25, self.grid_size_px))
        self.hitboxes.append(hitbox(rect, hitbox_type.VERTEX, orientation.VERTICAL, value=self.num_cr, color=colors[next(color_iter)]))
        #creates a bottom large hitbox
        rect = pygame.Rect((0, self.grid_size_px - self.line_spacing*1.25), (self.grid_size_px, self.line_spacing*1.25))
        self.hitboxes.append(hitbox(rect, hitbox_type.VERTEX, orientation.HORIZONTAL, value=self.num_cr, color=colors[next(color_iter)]))

gr = d_grid(grid.Grid(3,3))

def display_grid(grid: d_grid):
    curernt_mouse = (None, None)
    pos = pygame.mouse.get_pos()
    screen.fill("white")
    for hitbox in grid.hitboxes:
        if hitbox.orientation == orientation.HORIZONTAL:
            #various options for displaying the hitboxes for testing purposes
            if options.show_hitboxes == "Full":
                pygame.draw.rect(screen, hitbox.color, hitbox.rect)
            elif options.show_hitboxes == "Small":
                pygame.draw.rect(screen, hitbox.color, hitbox.rect.scale_by(1,0.5))
        else:
            #various options for displaying the hitboxes for testing purposes
            if options.show_hitboxes == "Full":
                pygame.draw.rect(screen, hitbox.color, hitbox.rect)
            elif options.show_hitboxes == "Small":
                pygame.draw.rect(screen, hitbox.color, hitbox.rect.scale_by(0.5,1))

    for i in range(grid.num_lines):
        pygame.draw.line(screen, "black", (grid.line_spacing*(i+0.5), 0), (grid.line_spacing*(i+0.5), grid.grid_size_px))
        pygame.draw.line(screen, "black", (0, grid.line_spacing*(i+0.5)), (grid.grid_size_px, grid.line_spacing*(i+0.5)))
    if options.show_mouse_pos == True and curernt_mouse != (None, None):
        font = pygame.font.SysFont(None, 24)
        img = font.render(str(curernt_mouse), True, "black")
        screen.blit(img, pos)

def get_mouse_grid_pos(grid: d_grid):
    pos = pygame.mouse.get_pos()
    curernt_mouse = (None, None)
    for hitbox in grid.hitboxes:
        if hitbox.rect.collidepoint(pos):
            if hitbox.orientation == orientation.HORIZONTAL:
                curernt_mouse = (curernt_mouse[0], hitbox.value)
            else:
                curernt_mouse = (hitbox.value, curernt_mouse[1])
    return curernt_mouse

"""
Bindings:
create_vertex
create_ghost_vertex
add_edge
delete_vertex
delete_edge
"""
create_vertex = command("create_vertex", 
                        [binding(pygame.MOUSEBUTTONDOWN, button=pygame.BUTTON_LEFT, mod=pygame.KMOD_NONE),
                         binding(pygame.KEYDOWN, pygame.K_q)], 
                         func=lambda: print("create vertex"))
create_ghost_vertex = command("create_ghost_vertex",
                             [binding(pygame.MOUSEBUTTONDOWN, button=pygame.BUTTON_MIDDLE, mod=pygame.KMOD_NONE),
                              binding(pygame.KEYDOWN, pygame.K_w)],
                             func=lambda: print("create ghost vertex"))
delete_vertex = command("delete_vertex",
                        [binding(pygame.MOUSEBUTTONDOWN, button=pygame.BUTTON_LEFT, mod=pygame.KMOD_SHIFT),
                         binding(pygame.MOUSEBUTTONDOWN, button=pygame.BUTTON_MIDDLE, mod=pygame.KMOD_SHIFT),
                         binding(pygame.KEYDOWN, pygame.K_q, mod=pygame.KMOD_SHIFT),
                         binding(pygame.KEYDOWN, pygame.K_w, mod=pygame.KMOD_SHIFT)], 
                         func=lambda: print("delete vertex"))
add_edge = command("add_edge", 
                   [binding(pygame.MOUSEBUTTONDOWN, button=pygame.BUTTON_RIGHT, mod=pygame.KMOD_NONE),
                    binding(pygame.KEYDOWN, pygame.K_e)], 
                    func=lambda: print("add edge"))
cancel_edge = command("cancel_edge", 
                      [binding(pygame.KEYDOWN, pygame.K_ESCAPE)], 
                      func=lambda: print("cancel edge"))

delete_edge = command("delete_edge",
                      [binding(pygame.MOUSEBUTTONDOWN, button=pygame.BUTTON_RIGHT, mod=pygame.KMOD_SHIFT),
                       binding(pygame.KEYDOWN, pygame.K_e, mod=pygame.KMOD_SHIFT)], 
                       func=lambda: print("delete edge"))
bindings = [create_vertex, create_ghost_vertex, add_edge, cancel_edge, delete_vertex, delete_edge]

def check_bindings(event):
    for command in bindings:
        if command.evoke(event):
            continue

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    dt = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        check_bindings(event)
        print(event)
        manager.process_events(event)

    display_grid(gr)
    manager.update(dt)
    manager.draw_ui(screen)
    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    



pygame.quit()