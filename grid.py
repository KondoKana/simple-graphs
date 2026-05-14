
import numpy as np

class Grid:
    """Vertex and edge grid that expands when given indexes out of bounds by 1"""

    def __init__(self, width=3, height=3):
        """Initialize the grid with the given dimensions.
        Args:
            width (int): Initial number of columns.
            height (int): Initial number of rows.
        """
        self.width = width
        self.height = height
        self.grid = np.full((height, width), None)
        self.edges = []

    """Add a vertex at the specified coordinates, expanding the grid if necessary."""
    def add_vertex(self, x, y, ghost=False):
        # if not (-1 <= x <= self.width and -1 <= y <= self.height):
        #     raise ValueError("Coordinates out of bounds")
        while x <= -1:
            new_col = np.full((self.height, 1), None)
            self.grid = np.append(new_col,self.grid, axis=1)
            self.width += 1
            x+=1
        while self.width <= x:
            new_col = np.full((self.height, 1), None)
            self.grid = np.append(self.grid,new_col, axis=1)
            self.width += 1
        while y <= -1:
            new_row = np.full((1, self.width), None)
            self.grid = np.append(new_row,self.grid, axis=0)
            self.height += 1
            y+=1
        while self.height <= y:
            new_row = np.full((1, self.width), None)
            self.grid = np.append(self.grid,new_row, axis=0)
            self.height += 1
        vert = Vertex(ghost=ghost)
        self.grid[y][x] = vert #switched x and y because of how numpy arrays are indexed
    
    def add_col(self,x):
        new_col = np.full(self.height, None)
        self.grid = np.insert(self.grid,x,new_col, axis=1)
        self.width += 1
    
    def add_row(self,y):
        new_row = np.full(self.width, None)
        self.grid = np.insert(self.grid,y,new_row, axis=0)
        self.height += 1

    def get_vertex(self, x, y):
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError("Coordinates out of bounds")
        return self.grid[y][x]
    
    def get_all_vertices(self):
        vertices = []
        for row in range(self.height):
            for col in range(self.width):
                cell = self.grid[row][col]
                if isinstance(cell, Vertex):
                    vertices.append(cell.set_coordinates(col, row))
        return vertices

    def add_edge(self, x1, y1, x2, y2, color=(0,0,0)):
        vertex1 = self.get_vertex(x1, y1)
        vertex2 = self.get_vertex(x2, y2)
        if vertex1 is None or vertex2 is None:
            raise ValueError("Both incident vertices must exist")
        edge = Edge(vertex1, vertex2, color)
        self.edges.append(edge)
        return edge

    def get_all_edges(self):
        vertex_coords = {}
        for row in range(self.height):
            for col in range(self.width):
                cell = self.grid[row][col]
                if isinstance(cell, Vertex):
                    vertex_coords[cell] = (col, row)

        edges = []
        for edge in self.edges:
            edges.append({
                "edge": edge,
                "vertex1": vertex_coords.get(edge.vertex1),
                "vertex2": vertex_coords.get(edge.vertex2),
            })
        return edges

    def __print__(self):
        for row in self.grid:
            print(" ".join([str(cell) for cell in row]))


class Vertex:
    def __init__(self, ghost=False, color = (0,0,0)):
        self.ghost = ghost
        self.color = color
    def __print__(self):
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