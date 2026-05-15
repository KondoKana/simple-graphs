
import numpy as np

class Grid:
    """Vertex and edge grid that expands when given indexes out of bounds by 1"""

    def __init__(self, width=3, height=3, min_dim = 4):
        """Initialize the grid with the given dimensions.
        Args:
            width (int): Initial number of columns.
            height (int): Initial number of rows.
        """
        self.width = width
        self.height = height
        self.grid = np.full((height, width), None)
        self.edges = []
        self.min_dim = min_dim

    def update_vertex_locations(self):
        for row in range(self.height):
            for col in range(self.width):
                cell = self.grid[row][col]
                if isinstance(cell, Vertex):
                    self.grid[row][col] = cell.set_coordinates(col, row)

    def expand(self):
        """Expand the grid by adding a new row and column on each side."""
        new_col = np.full((self.height, 1), None)
        self.grid = np.append(new_col,self.grid, axis=1)
        self.grid = np.append(self.grid, new_col, axis=1)
        self.width += 2
        new_row = np.full((1, self.width), None)
        self.grid = np.append(new_row,self.grid, axis=0)
        self.grid = np.append(self.grid,new_row, axis=0)
        self.height += 2
        self.update_vertex_locations()
    
    def trim(self):
        print("trim")
        # self.trim_tl(min_dim)
        # self.trim_br(min_dim)
        # self.trim_tr(min_dim)
        # self.trim_bl(min_dim)
        if (self.height < self.min_dim) or (self.width< self.min_dim): 
            return
        self.trim_cols()
        self.trim_rows()
        odd_height = self.height%2
        height_added = 0
        #if self.height != self.width and max(self.height, self.width) > min_dim:

        if self.height < self.width and self.width > self.min_dim:
            for i in range(self.width - self.height):
                if i % 2:
                    self.add_row(self.height-1)
                    height_added+=1
                else:
                    self.add_row(-1)
                    height_added+=1
            if not height_added % 2:
                self.add_row(-1)
        
        width_added = 0
        if self.width < self.height and self.height > self.min_dim:
            for i in range(self.height - self.width):
                if i % 2:
                    self.add_col(-1)
                else:
                    self.add_col(self.width-1)
            if not width_added % 2:
                self.add_col(self.width-1)
        self.update_vertex_locations()
        
    
    def trim_cols(self):
        for x in reversed(range(self.width)):
            if all((self.grid[y][x] is None) for y in range(self.height)) and self.width >= self.min_dim:
                self.grid = np.delete(self.grid, x, axis = 1 )
                self.width-=1
    
    def trim_rows(self):
        for y in reversed(range(self.height)):
            if all((self.grid[y][x] is None) for x in range(self.width)) and self.height >= self.min_dim:
                self.grid = np.delete(self.grid, y, axis = 0 )
                self.height -= 1
    

    def trim_tl(self,min_dim):
        min_tl = max(self.width, self.height)
        for x in range(self.width):
            if any(isinstance(self.grid[y][x], Vertex) for y in range(self.height)):
                min_tl = min(min_tl, x)
                print(self.grid)
                break
        for y in range(self.height):
            if any(isinstance(self.grid[y][x], Vertex) for x in range(self.width)):
                min_tl = min(min_tl, y)
                break
        print("min_tl:", min_tl)
        for _ in range(min_tl):
            if self.height >= min_dim and self.width >= min_dim:
                self.grid = self.grid[1:, 1:]
                self.height -= 1
                self.width -= 1
    
    def trim_br(self,min_dim):
        min_br = max(self.width, self.height)
        for x in range(self.width-1, -1, -1):
            if any(isinstance(self.grid[y][x], Vertex) for y in range(self.height)):
                min_br = min(min_br, self.width - 1 - x)
                break
        for y in range(self.height-1, -1, -1):
            if any(isinstance(self.grid[y][x], Vertex) for x in range(self.width)):
                min_br = min(min_br, self.height - 1 - y)
                break
        print("min_br:", min_br)
        for _ in range(min_br):
            if self.height >= min_dim and self.width >= min_dim:
                self.grid = self.grid[:-1, :-1]
                self.height -= 1
                self.width -= 1
    
    def trim_tr(self,min_dim):
        min_tr = max(self.width, self.height)
        for x in range(self.width-1, -1, -1):
            if any(isinstance(self.grid[y][x], Vertex) for y in range(self.height)):
                min_tr = min(min_tr, self.width - 1 - x)
                break
        for y in range(self.height):
            if any(isinstance(self.grid[y][x], Vertex) for x in range(self.width)):
                min_tr = min(min_tr, y)
                break
        print("min_tr:", min_tr)
        for _ in range(min_tr):
            if self.height >= min_dim and self.width >= min_dim:
                self.grid = self.grid[1:, :-1]
                self.height -= 1
                self.width -= 1
    
    def trim_bl(self,min_dim):
        min_bl = max(self.width, self.height)
        for x in range(self.width):
            if any(isinstance(self.grid[y][x], Vertex) for y in range(self.height)):
                min_bl = min(min_bl, x)
                break
        for y in range(self.height-1, -1, -1):
            if any(isinstance(self.grid[y][x], Vertex) for x in range(self.width)):
                min_bl = min(min_bl, self.height - 1 - y)
                break
        print("min_bl:", min_bl)
        for _ in range(min_bl):
            if self.height >= min_dim and self.width >= min_dim:
                self.grid = self.grid[:-1, 1:]
                self.height -= 1
                self.width -= 1

    """Add a vertex at the specified coordinates, expanding the grid if necessary."""
    def add_vertex(self, x, y, ghost=False, color=(0,0,0), width = 0, scale = 1):
        expanded = False
        # if not (-1 <= x <= self.width and -1 <= y <= self.height):
        #     raise ValueError("Coordinates out of bounds")
        while x <= -1 or self.width <= x or y <= -1 or self.height <= y:
            expanded = True
            self.expand()
            y+=1
            x+=1
        vert = Vertex(ghost=ghost, color=color, width=width, scale = scale)
        self.grid[y][x] = vert #switched x and y because of how numpy arrays are indexed
        self.update_vertex_locations()
        return expanded
    



    def add_col(self,x):
        new_col = np.full(self.height, None)
        self.grid = np.insert(self.grid,x+1,new_col, axis=1)
        self.width += 1
        self.update_vertex_locations()
    
    def add_row(self,y):
        new_row = np.full(self.width, None)
        self.grid = np.insert(self.grid,y+1,new_row, axis=0)
        self.height += 1
        self.update_vertex_locations()

    def get_vertex(self, x, y):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None
            print("ValueError: Coordinates out of bounds")
        return self.grid[y][x]
    
    def remove_vertex(self, x, y):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None
            print("ValueError: Coordinates out of bounds")
        vert = self.grid[y][x]
        for edge in self.edges:
            if edge.incident_to(vert):
                self.edges.remove(edge)
        for edge in self.edges:         #do twice be otherwise every other edge isnt removed
            if edge.incident_to(vert):
                self.edges.remove(edge)
        self.grid[y][x] = None
        return self.grid[y][x]

    
    def get_all_vertices(self): 
        vertices = []
        for row in range(self.height):
            for col in range(self.width):
                cell = self.grid[row][col]
                if isinstance(cell, Vertex):
                    vertices.append(cell.set_coordinates(col, row))
        return vertices

    def add_edge(self, v1,  v2, color=(0,0,0)):
        vertex1 = v1
        vertex2 = v2
        if vertex1 is None or vertex2 is None:
            raise ValueError("Both incident vertices must exist")
        edge = Edge(vertex1, vertex2, color)
        self.edges.append(edge)
        return edge

    def remove_edge(self, edge):
        self.edges.remove(edge)

    def get_all_edges(self):
        return self.edges



    def __print__(self):
        for row in self.grid:
            print(" ".join([str(cell) for cell in row]))


class Vertex:
    def __init__(self, ghost=False, color = (0,0,0), width = 0, scale = 1):
        self.ghost = ghost
        self.color = color
        self.width = width
        self.scale = scale
    def __print__(self):
        return "G" if self.ghost else "V"
    def __str__(self):
        return "G" if self.ghost else "V"
    def set_coordinates(self, x, y):
        self.x = x
        self.y = y
        return self

class Edge:
    def __init__(self, vertex1, vertex2, color = (0,0,0)):
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.color = color
    def incident_to(self, vertex: Vertex):
        return (vertex is self.vertex2 or vertex is self.vertex1)