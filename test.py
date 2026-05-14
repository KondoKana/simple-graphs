import pytest
import grid


def test_grid_module_imports():
    assert grid is not None


def test_grid_init():
    g = grid.Grid(5,5)
    print(g.grid)
    assert g.width == 5
    assert g.height == 5
    assert g.grid.shape == (5, 5)

def test_add_vertex():
    g = grid.Grid(3,3)
    g.add_vertex(1,1)
    assert isinstance(g.get_vertex(1,1), grid.Vertex)

def test_add_vertex_out_of_bounds_left():
    g = grid.Grid(3,3)
    g.add_vertex(2,2)
    assert isinstance(g.get_vertex(2,2), grid.Vertex)
    g.add_vertex(-1,1)
    print(g.grid)
    assert g.grid.shape == (3, 4)
    assert isinstance(g.get_vertex(0,1), grid.Vertex)
    assert isinstance(g.get_vertex(3,2), grid.Vertex)

def test_add_multiple_vertex_out_of_bounds_left():
    g = grid.Grid(3,3)
    g.add_vertex(2,2)
    assert isinstance(g.get_vertex(2,2), grid.Vertex)
    g.add_vertex(-2,1)
    print(g.grid)
    assert g.grid.shape == (3, 5)
    assert isinstance(g.get_vertex(0,1), grid.Vertex)
    assert isinstance(g.get_vertex(4,2), grid.Vertex)

def test_add_vertex_out_of_bounds_right():
    g = grid.Grid(3,3)
    g.add_vertex(2,2)
    assert isinstance(g.get_vertex(2,2), grid.Vertex)
    g.add_vertex(3,1)
    print(g.grid)
    assert g.grid.shape == (3, 4)
    assert isinstance(g.get_vertex(3,1), grid.Vertex)
    assert isinstance(g.get_vertex(2,2), grid.Vertex)

def test_add_multiple_vertex_out_of_bounds_right():
    g = grid.Grid(3,3)
    g.add_vertex(2,2)
    assert isinstance(g.get_vertex(2,2), grid.Vertex)
    g.add_vertex(4,1)
    print(g.grid)
    assert g.grid.shape == (3, 5)
    assert isinstance(g.get_vertex(4,1), grid.Vertex)
    assert isinstance(g.get_vertex(2,2), grid.Vertex)

def test_add_vertex_out_of_bounds_up():
    g = grid.Grid(3,3)
    g.add_vertex(2,2)
    assert isinstance(g.get_vertex(2,2), grid.Vertex)
    g.add_vertex(1,-1)
    print(g.grid)
    assert g.grid.shape == (4, 3)
    assert isinstance(g.get_vertex(1,0), grid.Vertex)
    assert isinstance(g.get_vertex(2,3), grid.Vertex)

def test_add_multiple_vertex_out_of_bounds_up():
    g = grid.Grid(3,3)
    g.add_vertex(2,2)
    assert isinstance(g.get_vertex(2,2), grid.Vertex)
    g.add_vertex(1,-2)
    print(g.grid)
    assert g.grid.shape == (5, 3)
    assert isinstance(g.get_vertex(1,0), grid.Vertex)
    assert isinstance(g.get_vertex(2,4), grid.Vertex)

def test_add_vertex_out_of_bounds_down():
    g = grid.Grid(3,3)
    g.add_vertex(2,2)
    assert isinstance(g.get_vertex(2,2), grid.Vertex)
    g.add_vertex(1,3)
    print(g.grid)
    assert g.grid.shape == (4, 3)
    assert isinstance(g.get_vertex(1,3), grid.Vertex)
    assert isinstance(g.get_vertex(2,2), grid.Vertex)

def test_add_multiple_vertex_out_of_bounds_down():
    g = grid.Grid(3,3)
    g.add_vertex(2,2)
    assert isinstance(g.get_vertex(2,2), grid.Vertex)
    g.add_vertex(1,4)
    print(g.grid)
    assert g.grid.shape == (5, 3)
    assert isinstance(g.get_vertex(1,4), grid.Vertex)
    assert isinstance(g.get_vertex(2,2), grid.Vertex)


def test_add_col():
    g = grid.Grid(3,3)
    g.add_vertex(2,2)
    assert isinstance(g.get_vertex(2,2), grid.Vertex)
    print(g.grid)
    g.add_col(1)
    print(g.grid)
    assert g.grid.shape == (3, 4)
    assert isinstance(g.get_vertex(3,2), grid.Vertex)

def test_add_row():
    g = grid.Grid(3,3)
    g.add_vertex(2,2)
    assert isinstance(g.get_vertex(2,2), grid.Vertex)
    print(g.grid)
    g.add_row(1)
    print(g.grid)
    assert g.grid.shape == (4, 3)
    assert isinstance(g.get_vertex(2,3), grid.Vertex)