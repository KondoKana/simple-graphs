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
bindings = []
used_mods = set()


class State:
    def __init__(self):
        self.creating_edge = False
        self.edge_start = None
        self.can_input = True
state = State()


#im having way more fun with shit like this but its not the project. Still cool organization
class Options:
    def __init__(self,
                  show_hitboxes: Literal["Full", "Small", "None"] = "None"):
        self.show_hitboxes = show_hitboxes
        self.show_mouse_pos = True
        self.show_hitbox_on_hover = True
        self.rainbow_boxes = False
        self.grid_width = 1
        self.ghost_width = 3
        self.vertex_color = pygame.colordict.THECOLORS["black"]
        self.vertex_width = 0   #0 means filled
        self.ghost_color = pygame.colordict.THECOLORS["red"]
        self.ghost_width = 0
        self.edge_color = pygame.colordict.THECOLORS["black"]
        self.edge_width = 1
        self.min_dm = 4
options = Options()

"""
This is me having fun with bindings and stuff. Unfortunately doing bitwise & with no mod doesnt work when things like capslock are pressed. This has a function
to handle that - get_mods - which returns only the mods I care about from the currently active ones. 
"""
class Binding:
    def __init__(self, event, button=None, key=None, mod=pygame.KMOD_NONE):
        self.event = event
        self.button = button
        self.key = key
        self.mod = mod

class Command:
    def __init__(self, name, bindings: list[Binding], func = None):
        self.name = name
        self.func = func
        self.bindings = bindings


    def get_mods(self):
        mods = pygame.key.get_mods()
        current_used = pygame.KMOD_NONE
        for mod in used_mods:
            if mods & mod:
                current_used |= mod
        return current_used
        
    def evoke(self, event: pygame.event.Event):
        mods = self.get_mods()
        for binding in self.bindings:
            #check key, mod, and button. Seeing as how mouse is based on button probably could do some shortcutting but eeh
            if (event.type == binding.event and                                                                 #correct event type
                (binding.key is  None or event.key == binding.key) and                                          #correct key if applicable
                ((binding.mod & mods) or (binding.mod == pygame.KMOD_NONE and mods == pygame.KMOD_NONE)) and    #correct mod or nomod if none are pressed
                (getattr(event, "button", None) is None or event.button == binding.button)):                    #correct button if applicable
                if self.func is not None:
                    self.func(event)
                return True
        return False

"""
Bindings:
create_vertex
create_ghost_vertex
add_edge
delete_vertex
delete_edge
"""

def create_bindings():
    create_vertex  = Command("create_vertex",[
        Binding(pygame.MOUSEBUTTONDOWN, button=pygame.BUTTON_LEFT, mod=pygame.KMOD_NONE),
        Binding(pygame.KEYDOWN, key =pygame.K_q, mod=pygame.KMOD_NONE)], 
        func= create_vertex_func)
    
    create_ghost_vertex = Command("create_ghost_vertex",[
        Binding(pygame.MOUSEBUTTONDOWN, button=pygame.BUTTON_MIDDLE, mod=pygame.KMOD_NONE),
        Binding(pygame.KEYDOWN, key=pygame.K_w)],
        func=create_ghost_vertex_func)
    
    delete_vertex = Command("delete_vertex",[
        Binding(pygame.MOUSEBUTTONDOWN, button=pygame.BUTTON_LEFT, mod=pygame.KMOD_SHIFT),
        Binding(pygame.MOUSEBUTTONDOWN, button=pygame.BUTTON_MIDDLE, mod=pygame.KMOD_SHIFT),
        Binding(pygame.KEYDOWN, key=pygame.K_q, mod=pygame.KMOD_SHIFT),
        Binding(pygame.KEYDOWN, key=pygame.K_w, mod=pygame.KMOD_SHIFT)], 
        func=delete_vertex_func)
    
    add_edge = Command("add_edge",[
        Binding(pygame.MOUSEBUTTONDOWN, button=pygame.BUTTON_RIGHT, mod=pygame.KMOD_NONE),
        Binding(pygame.KEYDOWN, key=pygame.K_e, mod=pygame.KMOD_NONE)], 
        func=create_edge_func)
    
    cancel_edge = Command("cancel_edge",[
        Binding(pygame.KEYDOWN, key=pygame.K_ESCAPE, mod=pygame.KMOD_NONE)], 
        func=cancel_edge_func)
    
    delete_edge = Command("delete_edge",[
        Binding(pygame.MOUSEBUTTONDOWN, button=pygame.BUTTON_RIGHT, mod=pygame.KMOD_SHIFT),
        Binding(pygame.KEYDOWN, key=pygame.K_e, mod=pygame.KMOD_SHIFT)], 
        func=delete_edge_func)
    

    #any_key = command("any_key", [binding(pygame.KEYDOWN)], func=check_mods())
    bindings = [create_vertex, create_ghost_vertex, add_edge, cancel_edge, delete_vertex, delete_edge]
    used_mods = set()
    print(bindings)
    for command in bindings:
        for binding in command.bindings:
            if binding.mod is not None and binding.mod != pygame.KMOD_NONE:
                used_mods.add(binding.mod)
    print(bindings)
    print(used_mods)
    print(pygame.KMOD_SHIFT)
    return bindings,used_mods

def check_bindings(event):
    for command in bindings:
        if command.evoke(event):
            continue


def create_vertex_func(event=None, ghost = False):
    if not state.can_input:
        return
    state.can_input = False
    mouse_grid_pos = get_mouse_grid_pos(gr)
    if mouse_grid_pos != (None, None):
        (x,x_t), (y,y_t) = mouse_grid_pos
        if x_t != hitbox_type.VERTEX:
            gr.grid.add_row(-1)
            gr.grid.add_row(gr.grid.height-1)
            gr.grid.add_col(x)
            if x >= (gr.grid.width-2)/2:
                gr.grid.add_col(-1)
                x+=1
            else:
                gr.grid.add_col(gr.grid.width-1)
            
            gr.update_grid(gr.grid)
            x+=1
            y+=1
        if y_t != hitbox_type.VERTEX:
            gr.grid.add_col(-1)
            gr.grid.add_col(gr.grid.width-1)
            gr.grid.add_row(y)
            if y >= (gr.grid.height-2)/2:
                gr.grid.add_row(-1)
                y+=1
            else:
                gr.grid.add_row(gr.grid.height-1)
            
            y+=1
            x+=1
            gr.update_grid(gr.grid)

        if gr.grid.get_vertex(x,y) is not None and not gr.grid.get_vertex(x,y).ghost:
            print("vertex already exists at", mouse_grid_pos)
            return
        print(f"create vertex at {mouse_grid_pos}")
        if ghost:
            print("ghost vertex")
        gr.grid.add_vertex(x,y,ghost=ghost, 
                              color=options.ghost_color if ghost else options.vertex_color,
                              width=options.ghost_width if ghost else options.vertex_width)
        gr.grid.trim(options.min_dm)
        gr.update_grid(gr.grid)
            

def create_ghost_vertex_func(event=None):
    create_vertex_func(event, ghost=True)

def create_edge_func(event=None):
    print("add edge")

def delete_vertex_func(event=None):
    print("delete vertex")

def cancel_edge_func(event=None):
    print("cancel edge")

def delete_edge_func(event=None):
    print("delete edge")


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
        self.grid = grid
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
        self.hitboxes.append(hitbox(rect, hitbox_type.VERTEX, orientation.HORIZONTAL, value=-1, color=(colors[next(color_iter)] if options.rainbow_boxes else "grey")))
        #creates left large hitbox
        rect = pygame.Rect((0, 0), (self.line_spacing*1.25, self.grid_size_px))
        self.hitboxes.append(hitbox(rect, hitbox_type.VERTEX, orientation.VERTICAL, value=-1, color=(colors[next(color_iter)] if options.rainbow_boxes else "grey")))


        for i in range((self.num_cr*2)-1):
            #makes the vertical hitboxes for the vertices and edges, alternating between the two types and coloring them differently for testing purposes
            rect = pygame.Rect((self.line_spacing*1.25 + i*self.line_spacing*1/2, 0), (self.line_spacing*1/2, self.grid_size_px))
            if i%2 == 0:
                self.hitboxes.append(hitbox(rect, hitbox_type.VERTEX, orientation.VERTICAL, value=int(i/2), color=(colors[next(color_iter)] if options.rainbow_boxes else "grey")))
            else:
                self.hitboxes.append(hitbox(rect, hitbox_type.EDGE, orientation.VERTICAL, value=int(i/2), color=(colors[next(color_iter)] if options.rainbow_boxes else "grey")))
            
            #makes the horizontal hitboxes for the vertices and edges, alternating between the two types and coloring them differently for testing purposes
            rect = pygame.Rect((0, self.line_spacing*1.25 + i*self.line_spacing*1/2), (self.grid_size_px, self.line_spacing*1/2))
            if i%2 == 0:
                self.hitboxes.append(hitbox(rect, hitbox_type.VERTEX, orientation.HORIZONTAL, value=int(i/2), color=(colors[next(color_iter)] if options.rainbow_boxes else "grey")))
            else:
                self.hitboxes.append(hitbox(rect, hitbox_type.EDGE, orientation.HORIZONTAL, value=int(i/2), color=(colors[next(color_iter)] if options.rainbow_boxes else "grey")))
        
        #creates a right large hitbox
        rect = pygame.Rect((self.grid_size_px - self.line_spacing*1.25, 0), (self.line_spacing*1.25, self.grid_size_px))
        self.hitboxes.append(hitbox(rect, hitbox_type.VERTEX, orientation.VERTICAL, value=self.num_cr, color=(colors[next(color_iter)] if options.rainbow_boxes else "grey")))
        #creates a bottom large hitbox
        rect = pygame.Rect((0, self.grid_size_px - self.line_spacing*1.25), (self.grid_size_px, self.line_spacing*1.25))
        self.hitboxes.append(hitbox(rect, hitbox_type.VERTEX, orientation.HORIZONTAL, value=self.num_cr, color=(colors[next(color_iter)] if options.rainbow_boxes else "grey")))

gr = d_grid(grid.Grid(3,3))

def display_grid(grid: d_grid):
    pos = pygame.mouse.get_pos()
    screen.fill("white")
    for hitbox in grid.hitboxes:
        if hitbox.orientation == orientation.HORIZONTAL:
            #various options for displaying the hitboxes for testing purposes
            if options.show_hitboxes == "Full" or (options.show_hitbox_on_hover and hitbox.rect.collidepoint(pos)):
                pygame.draw.rect(screen, hitbox.color, hitbox.rect)
            elif options.show_hitboxes == "Small":
                pygame.draw.rect(screen, hitbox.color, hitbox.rect.scale_by(1,0.5))
        else:
            #various options for displaying the hitboxes for testing purposes
            if options.show_hitboxes == "Full" or (options.show_hitbox_on_hover and hitbox.rect.collidepoint(pos)):
                pygame.draw.rect(screen, hitbox.color, hitbox.rect)
            elif options.show_hitboxes == "Small":
                pygame.draw.rect(screen, hitbox.color, hitbox.rect.scale_by(0.5,1))

    for i in range(grid.num_lines):
        pygame.draw.line(screen, "black", (grid.line_spacing*(i+0.5), 0), (grid.line_spacing*(i+0.5), grid.grid_size_px))
        pygame.draw.line(screen, "black", (0, grid.line_spacing*(i+0.5)), (grid.grid_size_px, grid.line_spacing*(i+0.5)))
    

    for vertex in grid.grid.get_all_vertices():
        if vertex is not None:
            x, y = vertex.x, vertex.y
            pygame.draw.circle(screen, color=vertex.color, width=vertex.width, center=(grid.line_spacing*(x+1.5), grid.line_spacing*(y+1.5)), radius=grid.line_spacing/4)


    if options.show_mouse_pos == True: 
        font = pygame.font.SysFont(None, 24)
        img = font.render(str(get_mouse_grid_pos(grid)), True, "black")
        screen.blit(img, pos)


def get_mouse_grid_pos(grid: d_grid):
    """Get the grid position the mouse is currently hovering over.
    
    Args:
        grid: d_grid - the display grid object
        
    Returns:
        (x,y) coordinates of the grid position the mouse is currently hovering over, 
        or (None, None) if the mouse is not hovering over any grid position. 
        The coordinates are based on the hitboxes defined in the d_grid class.
    """
    pos = pygame.mouse.get_pos()
    curernt_mouse = (None, None)
    for hitbox in grid.hitboxes:
        if hitbox.rect.collidepoint(pos):
            if hitbox.orientation == orientation.HORIZONTAL:
                curernt_mouse = (curernt_mouse[0], (hitbox.value,hitbox.type))
            else:
                curernt_mouse = ((hitbox.value,hitbox.type), curernt_mouse[1])
    return (None, None) if None in curernt_mouse else curernt_mouse


def check_mods():
    mods = pygame.key.get_mods()
    current_used = 0
    for mod in used_mods:
        if mods & mod:
            current_used |= mod
    pygame.key.set_mods(current_used)



pygame.event.set_blocked(pygame.MOUSEMOTION)
bindings, used_mods = create_bindings()
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    dt = clock.tick(60) / 1000.0
    state.can_input = True
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