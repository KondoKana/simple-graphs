from random import shuffle
from typing import Literal
import pygame
import pygame.gfxdraw
import pygame_gui
import grid
import math
import numpy as np
from collections import deque
# pygame setup
pygame.init()
info = pygame.display.Info()
screen_percentage = 0.5
screen_height = min(info.current_w, info.current_h)*screen_percentage
screen_width = screen_height
manager = pygame_gui.UIManager((screen_width, screen_height))

screen = pygame.display.set_mode((screen_width, screen_height))
region_surface = pygame.Surface((screen_width, screen_height))
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
        self.update = True
        self.filling_color = False
        self.color_max_cycles = 200
        self.color_fill = None
        self.color_index = 0
state = State()


#im having way more fun with shit like this but its not the project. Still cool organization
class Options:
    def __init__(self,
                  show_hitboxes: Literal["Full", "Small", "None"] = "None"):
        self.background_color = pygame.colordict.THECOLORS["white"]
        self.show_hitboxes = show_hitboxes
        self.show_mouse_pos = False
        self.show_xy_hitbox_on_hover = False
        self.show_hitbox_on_hover = False
        self.rainbow_boxes = False
        self.grid_scale = 2
        self.grid_width = 1
        self.vertex_hitbox_extra = 0.15 #scalar for making the "on the line" hitboxes bigger and the "between lines" hitboxes smaller. [0,0.5]
        self.vertex_scale_min = 0.8
        self.vertex_scale_increase_max = 1.2
        self.vertex_scale_step = 0.2
        self.start_dim = 3
        self.ghost_width = 3
        self.vertex_color = pygame.colordict.THECOLORS["blue"]
        self.vertex_width = 0   #0 means filled
        self.ghost_color = pygame.colordict.THECOLORS["grey"]
        self.ghost_scale = 0.6
        self.ghost_width = 0
        self.edge_color = pygame.colordict.THECOLORS["black"]
        self.edge_hitbox_color = pygame.colordict.THECOLORS["red"]
        self.vertex_hitbox_color = pygame.colordict.THECOLORS["orange"]
        self.color_hitbox_color = pygame.colordict.THECOLORS["white"]
        self.edge_width = 0.6
        self.edge_hitbox_scaling = 0.5
        self.edge_hitbox_color_rect_scaling = 0.2
        self.min_dm = 4
        self.vertex_hitbox_scale = 1.2
        self.show_ghost_vertex = True
        self.show_grid_lines = True
        self.color_hitboxes_stride = 3
        self.color_cycles_mod = 0.05
        self.target_fps = 30
        self.vertex_ring = True
        self.vertex_ring_color =  pygame.colordict.THECOLORS["black"]
        self.edge_vertex_color_set = [pygame.colordict.THECOLORS["black"],pygame.colordict.THECOLORS["crimson"],pygame.colordict.THECOLORS["chocolate1"],pygame.colordict.THECOLORS["darkgoldenrod1"],
                                      pygame.colordict.THECOLORS["darkgreen"],pygame.colordict.THECOLORS["darkblue"],pygame.colordict.THECOLORS["darkorchid1"],
                                      pygame.colordict.THECOLORS["darkmagenta"],pygame.colordict.THECOLORS["white"],pygame.colordict.THECOLORS["teal"]]
        self.region_color_set = [pygame.colordict.THECOLORS["lightblue4"],pygame.colordict.THECOLORS["lightcoral"],pygame.colordict.THECOLORS["lightsalmon"],pygame.colordict.THECOLORS["lightgoldenrod1"],
                                 pygame.colordict.THECOLORS["lightgreen"],pygame.colordict.THECOLORS["lightskyblue"],pygame.colordict.THECOLORS["lightpink"],
                                 pygame.colordict.THECOLORS["lightslateblue"],pygame.colordict.THECOLORS["white"],pygame.colordict.THECOLORS["lightseagreen"]]
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
    restart = Command("restart",[
        Binding(pygame.KEYDOWN, key=pygame.K_r, mod=pygame.KMOD_NONE)],
        func=restart_func)
    toggle_ghost_vertecies = Command("toggle ghosts",[
        Binding(pygame.KEYDOWN, key=pygame.K_g, mod=pygame.KMOD_NONE)],
        func=ghost_toggle_func)
    toggle_grid_lines = Command("toggle grid lines",[
        Binding(pygame.KEYDOWN, key=pygame.K_l, mod=pygame.KMOD_NONE)],
        func=grid_lines_toggle_func)
    toggle_paint = Command("toggle paint",[
        Binding(pygame.KEYDOWN, key=pygame.K_k, mod=pygame.KMOD_NONE)],
        func=toggle_paint_func)
    set_1 = Command("toggle paint",[
        Binding(pygame.KEYDOWN, key=pygame.K_1, mod=pygame.KMOD_NONE)],
        func=set_1_func)
    set_2 = Command("toggle paint",[
        Binding(pygame.KEYDOWN, key=pygame.K_2, mod=pygame.KMOD_NONE)],
        func=set_2_func)
    set_3 = Command("toggle paint",[
        Binding(pygame.KEYDOWN, key=pygame.K_3, mod=pygame.KMOD_NONE)],
        func=set_3_func)
    set_4 = Command("toggle paint",[
        Binding(pygame.KEYDOWN, key=pygame.K_4, mod=pygame.KMOD_NONE)],
        func=set_4_func)
    set_5 = Command("toggle paint",[
        Binding(pygame.KEYDOWN, key=pygame.K_5, mod=pygame.KMOD_NONE)],
        func=set_5_func)
    set_6 = Command("toggle paint",[
        Binding(pygame.KEYDOWN, key=pygame.K_6, mod=pygame.KMOD_NONE)],
        func=set_6_func)
    set_7 = Command("toggle paint",[
        Binding(pygame.KEYDOWN, key=pygame.K_7, mod=pygame.KMOD_NONE)],
        func=set_7_func)
    set_8 = Command("toggle paint",[
        Binding(pygame.KEYDOWN, key=pygame.K_8, mod=pygame.KMOD_NONE)],
        func=set_8_func)
    set_9 = Command("toggle paint",[
        Binding(pygame.KEYDOWN, key=pygame.K_9, mod=pygame.KMOD_NONE)],
        func=set_9_func)
    set_0 = Command("toggle paint",[
        Binding(pygame.KEYDOWN, key=pygame.K_0, mod=pygame.KMOD_NONE)],
        func=set_0_func)
    paint = Command("paint",[
        Binding(pygame.KEYDOWN, key=pygame.K_c, mod=pygame.KMOD_NONE)],
        func=paint_vertex_edge_func)
    paint_area = Command("paint",[
        Binding(pygame.KEYDOWN, key=pygame.K_c, mod=pygame.KMOD_SHIFT)],
        func=color_area)
    toggle_hitbox_hover = Command("toggle hitbox hover",[
        Binding(pygame.KEYDOWN, key=pygame.K_d, mod=pygame.KMOD_NONE)],
        func = toggle_hitbox_hover_func)
    

    #any_key = command("any_key", [binding(pygame.KEYDOWN)], func=check_mods())
    bindings = [create_vertex, create_ghost_vertex, add_edge, cancel_edge, delete_vertex, delete_edge, restart, toggle_ghost_vertecies, toggle_grid_lines,
                set_1,set_2,set_3,set_4,set_5,set_6,set_7,set_8,set_9,set_0,paint,paint_area,toggle_hitbox_hover]
    used_mods = set()
    for command in bindings:
        for binding in command.bindings:
            if binding.mod is not None and binding.mod != pygame.KMOD_NONE:
                used_mods.add(binding.mod)
    return bindings,used_mods

def check_bindings(event):
    for command in bindings:
        if command.evoke(event):
            state.update = True
            continue




class hitbox_type:
    VERTEX = "vertex"
    INSERT = "insert"
    EDGE = "edge"
    COLOR = "color"
class orientation:
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"

class Hitbox:
    def __init__ (self, rect: pygame.Rect, type: hitbox_type, orientation_val: orientation = None, value = None, color = (0,0,0)):
        self.rect : pygame.Rect = rect
        self.collide_rect : pygame.Rect = pygame.Rect.copy(rect)
        self.collide_rect.height = float(self.collide_rect.height)/options.grid_scale
        self.collide_rect.width = float(self.collide_rect.width)/options.grid_scale
        self.collide_rect.x = float(self.collide_rect.x)//options.grid_scale
        self.collide_rect.y = float(self.collide_rect.y)//options.grid_scale
        self.type : hitbox_type = type
        self.orientation : orientation = orientation_val
        self.color = color
        self.value = value
        self.visited = False
        self.adjacent = []

class Edge_Hitbox:
    def __init__(self, edge: grid.Edge, hitboxes = None):
        self.edge = edge
        self.color = pygame.colordict.THECOLORS["red"]
        self.hitboxes = hitboxes
        self.color_hitboxes = []


# actual display grid which holds the grid backend and also has some display related properties
class d_grid:
    def __init__ (self, grid: grid.Grid):
        self.grid = grid
        self.start_lines = options.min_dm+2
        self.update_grid(grid)

    

    def update_grid(self, grid: grid.Grid):
        print("update")
        self.grid_w = grid.width
        self.grid_h = grid.height
        self.grid_size_px = screen_height * options.grid_scale
        self.num_cr = max(self.grid_w, self.grid_h) #number of columns and rows of the underlying grid
        self.num_lines = self.num_cr + 2 #number of lines to draw
        self.line_spacing = self.grid_size_px // self.num_lines #spacing between lines in pixels
        self.vertex_hitbox_scale = options.vertex_hitbox_extra  #makes vertex hitboxes a tiny bit bigger
        self.vertex_scale_increase = min(((self.num_lines-self.start_lines)/self.start_lines)*options.vertex_scale_step,options.vertex_scale_increase_max)
        self.region_surface = pygame.Surface((self.grid_size_px, self.grid_size_px))
        self.region_surface.fill(options.background_color)
        self.hitboxes = []
        self.edge_hitboxes = []
        self.vertex_hitboxes = []
        color_list = list(colors.keys())
        shuffle(color_list)
        color_iter = iter(color_list)
        #creates top large hitbox
        rect = pygame.Rect((0, 0), (self.grid_size_px, self.line_spacing*1.25))
        self.hitboxes.append(Hitbox(rect, hitbox_type.VERTEX, orientation.HORIZONTAL, value=-1, color=(colors[next(color_iter)] if options.rainbow_boxes else "grey")))
        #creates left large hitbox
        rect = pygame.Rect((0, 0), (self.line_spacing*1.25, self.grid_size_px))
        self.hitboxes.append(Hitbox(rect, hitbox_type.VERTEX, orientation.VERTICAL, value=-1, color=(colors[next(color_iter)] if options.rainbow_boxes else "grey")))


        for i in range((self.num_cr*2)-1):
            #makes the vertical hitboxes for the vertices and edges, alternating between the two types and coloring them differently for testing purposes
            if i%2 == 0:
                rect = pygame.Rect((self.line_spacing*1.25 + i*self.line_spacing*1/2 - self.line_spacing*self.vertex_hitbox_scale/2, 0), 
                                   (self.line_spacing*1/2 + self.line_spacing*self.vertex_hitbox_scale, self.grid_size_px))
                self.hitboxes.append(Hitbox(rect, hitbox_type.VERTEX, orientation.VERTICAL, value=int(i/2), color=(colors[next(color_iter)] if options.rainbow_boxes else "grey")))
            else:
                rect = pygame.Rect((self.line_spacing*1.25 + i*self.line_spacing*1/2 + self.line_spacing*self.vertex_hitbox_scale/2, 0), 
                                   (self.line_spacing*1/2 - self.line_spacing*self.vertex_hitbox_scale+options.grid_scale, self.grid_size_px))
                self.hitboxes.append(Hitbox(rect, hitbox_type.INSERT, orientation.VERTICAL, value=int(i/2), color=(colors[next(color_iter)] if options.rainbow_boxes else "grey")))
            
            #makes the horizontal hitboxes for the vertices and edges, alternating between the two types and coloring them differently for testing purposes
            
            if i%2 == 0:
                rect = pygame.Rect((0, self.line_spacing*1.25 + i*self.line_spacing*1/2- self.line_spacing*self.vertex_hitbox_scale/2), 
                                   (self.grid_size_px, self.line_spacing*1/2 + self.line_spacing*self.vertex_hitbox_scale))
                self.hitboxes.append(Hitbox(rect, hitbox_type.VERTEX, orientation.HORIZONTAL, value=int(i/2), color=(colors[next(color_iter)] if options.rainbow_boxes else "grey")))
            else:
                rect = pygame.Rect((0, self.line_spacing*1.25 + i*self.line_spacing* 1/2 + self.line_spacing*self.vertex_hitbox_scale/2), 
                                   (self.grid_size_px, self.line_spacing*1/2 - self.line_spacing*self.vertex_hitbox_scale + options.grid_scale))
                self.hitboxes.append(Hitbox(rect, hitbox_type.INSERT, orientation.HORIZONTAL, value=int(i/2), color=(colors[next(color_iter)] if options.rainbow_boxes else "grey")))
        
        #creates a right large hitbox
        rect = pygame.Rect((self.grid_size_px - self.line_spacing*1.25, 0), (self.line_spacing*1.25, self.grid_size_px))
        self.hitboxes.append(Hitbox(rect, hitbox_type.VERTEX, orientation.VERTICAL, value=self.num_cr, color=(colors[next(color_iter)] if options.rainbow_boxes else "grey")))
        #creates a bottom large hitbox
        rect = pygame.Rect((0, self.grid_size_px - self.line_spacing*1.25), (self.grid_size_px, self.line_spacing*1.25))
        self.hitboxes.append(Hitbox(rect, hitbox_type.VERTEX, orientation.HORIZONTAL, value=self.num_cr, color=(colors[next(color_iter)] if options.rainbow_boxes else "grey")))


        edge_width = int((self.line_spacing//4)*(options.vertex_scale_min+self.vertex_scale_increase))
        for edge in grid.get_all_edges():
            hitbox = Edge_Hitbox(edge)
            e_hitboxes = []
            v1, v2 = edge.vertex1, edge.vertex2
            x1, y1 = self.line_spacing*(v1.x+1.5), self.line_spacing*(v1.y+1.5)
            x2, y2 = self.line_spacing*(v2.x+1.5), self.line_spacing*(v2.y+1.5)
            edge_len = math.dist((x1,y1),(x2,y2))
            edge_box_count = math.ceil((1/options.edge_hitbox_scaling)*(edge_len/edge_width))+1
            edge_dir_x = (x2-x1)/edge_box_count
            edge_dir_y = (y2-y1)/edge_box_count
            for i in range(edge_box_count):
                rect = pygame.Rect((x1+((-0.5*options.edge_hitbox_scaling)*edge_width)+edge_dir_x*i,y1+((-0.5*options.edge_hitbox_scaling)*edge_width)+edge_dir_y*i),
                                   (options.edge_hitbox_scaling*edge_width, options.edge_hitbox_scaling*edge_width))
                e_hitboxes.append(Hitbox(rect, hitbox_type.EDGE, color = options.edge_hitbox_color))
            hitbox.hitboxes = e_hitboxes
            self.edge_hitboxes.append(hitbox)
        
        for vertex in grid.get_all_vertices():
            x, y = vertex.x, vertex.y
            width = (self.line_spacing/4)*(vertex.scale+self.vertex_scale_increase)*options.vertex_hitbox_scale
            rect = pygame.Rect((self.line_spacing*(x+1.5)-(width/2),self.line_spacing*(y+1.5)-(width/2)),
                    (width,width))
            self.vertex_hitboxes.append(Hitbox(rect, hitbox_type.VERTEX, color=options.vertex_hitbox_color))

    

gr = d_grid(grid.Grid(options.start_dim,options.start_dim))




def display_grid(gr: d_grid, partial = False):
    dis_grid = pygame.Surface.copy(gr.region_surface)
    pos = pygame.mouse.get_pos()
    if not partial:
        for hitbox in gr.hitboxes:
            if hitbox.orientation == orientation.HORIZONTAL:
                #various options for displaying the hitboxes for testing purposes
                if options.show_hitboxes == "Full" or (options.show_xy_hitbox_on_hover and hitbox.collide_rect.collidepoint(pos)):
                    pygame.draw.rect(dis_grid, hitbox.color, hitbox.rect)
                elif options.show_hitboxes == "Small":
                    pygame.draw.rect(dis_grid, hitbox.color, hitbox.rect.scale_by(1,0.5))
            else:
                #various options for displaying the hitboxes for testing purposes
                if options.show_hitboxes == "Full" or (options.show_xy_hitbox_on_hover and hitbox.collide_rect.collidepoint(pos)):
                    pygame.draw.rect(dis_grid, hitbox.color, hitbox.rect)
                elif options.show_hitboxes == "Small":
                    pygame.draw.rect(dis_grid, hitbox.color, hitbox.rect.scale_by(0.5,1))

    if options.show_grid_lines and not partial:
        for i in range(gr.num_lines):
            pygame.draw.line(dis_grid, "black", ((int(gr.line_spacing*int(i)+gr.line_spacing*0.5)), 0), (int(gr.line_spacing*int(i)+gr.line_spacing*0.5), int(gr.grid_size_px)), width=options.grid_scale)
            pygame.draw.line(dis_grid, "black", (0, int(gr.line_spacing*int(i)+gr.line_spacing*0.5)), (int(gr.grid_size_px), int(gr.line_spacing*int(i)+gr.line_spacing*0.5)), width=options.grid_scale)
   
    if state.creating_edge:
        x1, y1 = gr.line_spacing*(state.edge_start.x+1.5), gr.line_spacing*(state.edge_start.y+1.5)
        x2, y2 = tuple(map(lambda x: x * options.grid_scale, pos))
        edge_width = int(options.edge_width*(gr.line_spacing//4)*(options.vertex_scale_min+gr.vertex_scale_increase))
        pygame.draw.line(dis_grid, color=(options.edge_color if state.color_index == 9 else options.edge_vertex_color_set[state.color_index]), start_pos=(x1,y1), end_pos=(x2,y2), width=edge_width)

    for edge in gr.grid.edges:
        v1,  v2 = edge.vertex1, edge.vertex2
        x1, y1 = gr.line_spacing*(v1.x+1.5), gr.line_spacing*(v1.y+1.5)
        x2, y2 = gr.line_spacing*(v2.x+1.5), gr.line_spacing*(v2.y+1.5)
        edge_width = int(options.edge_width*(gr.line_spacing//4)*(options.vertex_scale_min+gr.vertex_scale_increase))
        pygame.draw.line(dis_grid, color=edge.color, start_pos=(x1,y1), end_pos=(x2,y2), width=edge_width)

    for vertex in gr.grid.get_all_vertices():
        if (vertex is not None) and (not vertex.ghost or options.show_ghost_vertex):
            x, y = vertex.x, vertex.y
            pygame.draw.circle(dis_grid,color=vertex.color,center=(gr.line_spacing*(x+1.5), gr.line_spacing*(y+1.5)),radius=(gr.line_spacing/4)*(vertex.scale+gr.vertex_scale_increase), width=vertex.width)
            if not vertex.ghost:
                pygame.draw.circle(dis_grid,color=options.vertex_ring_color,center=(gr.line_spacing*(x+1.5), gr.line_spacing*(y+1.5)),radius=(gr.line_spacing/4)*(vertex.scale+gr.vertex_scale_increase), width=int((gr.line_spacing/4)*(vertex.scale+gr.vertex_scale_increase)*0.2))

    for edge_hitbox in gr.edge_hitboxes:
        for hitbox in edge_hitbox.hitboxes:
            if options.show_hitbox_on_hover and hitbox.collide_rect.collidepoint(pos):
                pygame.draw.rect(dis_grid, hitbox.color, hitbox.rect)
    for hitbox in gr.vertex_hitboxes:
        if options.show_hitbox_on_hover and hitbox.collide_rect.collidepoint(pos):
             pygame.draw.rect(dis_grid, hitbox.color, hitbox.rect)


    if options.show_mouse_pos == True and not partial: 
        font = pygame.font.SysFont(None, 24*options.grid_scale)
        img = font.render(str(get_mouse_grid_pos(gr)), True, "black")
        dis_grid.blit(img, tuple(map(lambda x: x * options.grid_scale, pos)))
    screen.blit(pygame.transform.smoothscale_by(dis_grid,1/options.grid_scale))
    return dis_grid
    #pygame.gfxdraw.textured_polygon(screen, [(0,0),(0,screen_height),(screen_height,screen_height),(screen_height,0)], dis_grid,0,0)

# def collides_edge_or_vertex(hitbox):
#     if hitbox.rect.collidelist(gr.vertex_hitboxes) != -1:
#         return True
#     for edge_hitbox in gr.edge_hitboxes:
#         if hitbox.rect.collidelist(edge_hitbox.color_hitboxes) != -1:
#             return True
#     return False


# def visit_hitbox(hitbox,visited):
#     visited.add(hitbox)
#     hitbox.color = pygame.colordict.THECOLORS["green"]
#     for box in hitbox.adjacent:
#         if box not in visited and not collides_edge_or_vertex(box):
#             visit_hitbox(box,visited)
# def color_area():
#     pos = pygame.mouse.get_pos()

#     w,h = gr.color_hitboxes.shape
#     c_x = -1
#     c_y = -1
#     for x in range(w):
#         for y in range(h):
#             if gr.color_hitboxes[y][x].collide_rect.collidepoint(pos):
#                 gr.color_hitboxes[y][x].color= options.edge_hitbox_color
#                 c_x = x
#                 c_y = y
#                 break
#         if c_x != -1:
#             break
#     if c_x == -1:
#         return
#     visited = set()
#     queue = []
#     queue.append(gr.color_hitboxes[c_y,c_x])
#     while len(queue) > 0:
#         box = queue.pop(len(queue)-1)
#         visited.add(box)
#         box.color = pygame.colordict.THECOLORS["green"]
#         for b in box.adjacent:
#             if b not in visited and not collides_edge_or_vertex(box):
#                 queue.append(b)


class Colorfill:
    def __init__(self, color_from, color_to, pos):
        self.color_from = color_from
        self.color_to = color_to
        self.visited = set()
        self.queue = deque([])
        self.queue.appendleft(pos)


def color_area(event = None):
    dis_grid = display_grid(gr,True)
    grid_display = pygame.PixelArray(dis_grid)
    region = pygame.PixelArray(gr.region_surface)
    if not state.filling_color:
        pos = pygame.mouse.get_pos()
        pos_screen = (options.grid_scale*pos[0],options.grid_scale*pos[1])
        color_from = grid_display[options.grid_scale*pos[0]][options.grid_scale*pos[1]]
        print(color_from)
        color_to = options.region_color_set[state.color_index]
        state.color_fill = Colorfill(color_from,color_to, pos_screen)
        state.filling_color = True
    cycles = 0
    while len(state.color_fill.queue) > 0:
        px = state.color_fill.queue.pop()
        x,y = px
        state.color_fill.visited.add(px)
        region[x][y] = state.color_fill.color_to
        if x > 0:
            if (grid_display[x-1][y] == state.color_fill.color_from) and ((x-1,y) not in state.color_fill.visited):
                state.color_fill.queue.append((x-1,y))
        if x < grid_display.shape[0]-1:
            if (grid_display[x+1][y] == state.color_fill.color_from) and ((x+1,y) not in state.color_fill.visited):
                state.color_fill.queue.append((x+1,y))
        if y > 0:
            if (grid_display[x][y-1] == state.color_fill.color_from) and ((x,y-1) not in state.color_fill.visited):
                state.color_fill.queue.append((x,y-1))
        if y < grid_display.shape[0]-1:
            if (grid_display[x][y+1] == state.color_fill.color_from) and ((x,y+1) not in state.color_fill.visited):
                state.color_fill.queue.append((x,y+1))
        cycles +=1
        if cycles >= state.color_max_cycles:
            pygame.PixelArray.close(grid_display)
            pygame.PixelArray.close(region)
            fps = clock.get_fps()
            print(fps)
            if fps < options.target_fps:
                state.color_max_cycles -= state.color_max_cycles*options.color_cycles_mod
            else:
                state.color_max_cycles += state.color_max_cycles*options.color_cycles_mod
            return
    pygame.PixelArray.close(grid_display)
    pygame.PixelArray.close(region)
    state.filling_color = False
    #screen.blit(pygame.transform.smoothscale_by(dis_grid,1/options.grid_scale))
    
def create_vertex_func(event=None, ghost = False):

    if not state.can_input and not state.creating_edge:
        return
    state.can_input = False
    mouse_grid_pos = get_mouse_grid_pos(gr)
    if mouse_grid_pos != (None, None):
        (x,x_t), (y,y_t) = mouse_grid_pos
        if x_t != hitbox_type.VERTEX:
            gr.grid.add_col(x)
            x+=1
            gr.update_grid(gr.grid)
        if y_t != hitbox_type.VERTEX:
            gr.grid.add_row(y)
            y+=1
            gr.update_grid(gr.grid)

        if gr.grid.get_vertex(x,y) is not None and not gr.grid.get_vertex(x,y).ghost:
            print("vertex already exists at", mouse_grid_pos)
            return
        print(f"create vertex at {mouse_grid_pos}")
        if ghost:
            print("ghost vertex")
        gr.grid.add_vertex(x,y,ghost=ghost, 
                              color=options.ghost_color if ghost else (options.vertex_color if state.color_index == 9 else options.edge_vertex_color_set[state.color_index]),
                              width=options.ghost_width if ghost else options.vertex_width,
                              scale=options.ghost_scale if ghost else options.vertex_scale_min)
        gr.grid.trim()
        gr.update_grid(gr.grid)
            

def create_ghost_vertex_func(event=None):
    if state.can_input and state.creating_edge:
        create_edge_func(ghost=True)
    create_vertex_func(event, ghost=True)

def create_edge_func(event=None, ghost = False):
    pos = get_mouse_grid_pos()
    if pos is (None, None):
        return
    ((mx, xt), (my, yt)) = pos
    if xt is hitbox_type.INSERT and yt is hitbox_type.INSERT:
        return
    vert:grid.Vertex = gr.grid.get_vertex(mx, my)
    if vert is not None:
        if not state.creating_edge:
            state.creating_edge = True
            state.edge_start = vert
        else:
            if vert == state.edge_start:
                return
            else:
                state.creating_edge = False
                gr.grid.add_edge(state.edge_start, vert, (options.edge if state.color_index == 9 else options.edge_vertex_color_set[state.color_index]))
                gr.update_grid(gr.grid)
            


def delete_vertex_func(event=None):
    if not state.can_input and not state.creating_edge:
        return
    ((mx, xt), (my, yt)) = get_mouse_grid_pos()
    if xt is hitbox_type.INSERT and yt is hitbox_type.INSERT:
        return
    vert:grid.Vertex = gr.grid.get_vertex(mx, my)
    if vert is not None:
        gr.grid.remove_vertex(mx, my)
        if not vert.ghost:
            create_ghost_vertex_func()
        gr.grid.trim()
        gr.update_grid(gr.grid)


def cancel_edge_func(event=None):
    print("cancel")
    if state.creating_edge:
        state.creating_edge = False
        state.edge_start = None
        return

def delete_edge_func(event=None):
    if not state.can_input:
        return
    if state.creating_edge:
        create_edge_func()
        create_edge_func()
    else:
        hit_edges = set()
        pos = pygame.mouse.get_pos()
        for edge_hitbox in gr.edge_hitboxes:
            for hitbox in edge_hitbox.hitboxes:
                if hitbox.collide_rect.collidepoint(pos):
                    hit_edges.add(edge_hitbox.edge)
                    gr.edge_hitboxes.remove(edge_hitbox)
                    break
        for edge in hit_edges:
            gr.grid.remove_edge(edge)

def restart_func(event=None):
    print("restart")
    gr.__init__(grid.Grid(3,3))

def ghost_toggle_func(event=None):
    options.show_ghost_vertex = not options.show_ghost_vertex

def grid_lines_toggle_func(event=None):
    options.show_grid_lines = not options.show_grid_lines

def toggle_paint_func(event=None):
    pass
#     if state.paint_area:
#         state.paint_area = False
#         return
#     state.paint_area = True
#     #gr.generate_color_hitboxes()

def set_1_func(event=None):
    state.color_index = 1
def set_2_func(event=None):
    state.color_index = 2
def set_3_func(event=None):
    state.color_index = 3
def set_4_func(event=None):
    state.color_index = 4
def set_5_func(event=None):
    state.color_index = 5
def set_6_func(event=None):
    state.color_index = 6
def set_7_func(event=None):
    state.color_index = 7
def set_8_func(event=None):
    state.color_index = 8
def set_9_func(event=None):
    state.color_index = 9
def set_0_func(event=None):
    state.color_index = 0
def paint_vertex_edge_func(event=None):
    pos = pygame.mouse.get_pos()

    for vertex_hitbox in gr.vertex_hitboxes:
        if vertex_hitbox.collide_rect.collidepoint(pos):
            ((mx, xt), (my, yt)) = get_mouse_grid_pos()
            if xt is hitbox_type.INSERT and yt is hitbox_type.INSERT:
                break
            vert:grid.Vertex = gr.grid.get_vertex(mx, my)
            if (vert is not None) and (not vert.ghost):
                vert.color = (options.vertex_color if state.color_index == 9 else options.edge_vertex_color_set[state.color_index])
                return

    for edge_hitbox in gr.edge_hitboxes:
        for hitbox in edge_hitbox.hitboxes:
            if hitbox.collide_rect.collidepoint(pos):
                ed = edge_hitbox.edge
                ed.color = (options.vertex_color if state.color_index == 9 else options.edge_vertex_color_set[state.color_index])
                return
    
def toggle_hitbox_hover_func(Event = None):
    options.show_hitbox_on_hover = not options.show_hitbox_on_hover


def get_mouse_grid_pos(grid: d_grid = gr):
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
        if hitbox.collide_rect.collidepoint(pos):
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



#pygame.event.set_blocked(pygame.MOUSEMOTION)
bindings, used_mods = create_bindings()
    
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    dt = clock.tick(60) / 1000.0
    state.can_input = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEMOTION:
            state.update = True
        if not state.filling_color:
            check_bindings(event)
        #print(event)
        manager.process_events(event)
    if state.filling_color:
        color_area()
    clock.get_fps()
    display_grid(gr)
    manager.update(dt)
    manager.draw_ui(screen)
    # flip() the display to put your work on screen
    #if state.update:
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    



pygame.quit()