from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional, Set, Tuple

Pos = Tuple[int, int]  # (row, col)
Grid = List[List[str]]


EXAMPLE_MAP_1 = """
##########
#S.......#
#..##.##.#
#...#...G#
##########
""".strip("\n")

EXAMPLE_MAP_2 = """
############
#S.....#...#
###.##.#.#.#
#...#..#...#
#.###..###G#
#..........#
############
""".strip("\n")


def parse_grid(text: str) -> Tuple[Grid, Pos, Pos]:
    """
    Convert a multiline string map into a grid plus start and goal positions.

    Map legend:
    '#' wall
    '.' floor
    'S' start (exactly one)
    'G' goal (exactly one)
    """
    lines = [line for line in text.splitlines() if line]
    if not lines:
        raise ValueError("Grid text is empty")

    width = len(lines[0])
    if any(len(line) != width for line in lines):
        raise ValueError("Grid must be rectangular")

    grid: Grid = []
    start: Optional[Pos] = None
    goal: Optional[Pos] = None

    valid = {"#", ".", "S", "G"}
    for r, line in enumerate(lines):
        row: List[str] = []
        for c, ch in enumerate(line):
            if ch not in valid:
                raise ValueError(f"Invalid grid character: {ch!r}")
            if ch == "S":
                if start is not None:
                    raise ValueError("Grid must contain exactly one start 'S'")
                start = (r, c)
            elif ch == "G":
                if goal is not None:
                    raise ValueError("Grid must contain exactly one goal 'G'")
                goal = (r, c)
            row.append(ch)
        grid.append(row)

    if start is None or goal is None:
        raise ValueError("Grid must contain exactly one 'S' and one 'G'")

    return grid, start, goal


def neighbors(grid: Grid, node: Pos) -> List[Pos]:
    """Return valid 4-direction neighbors that are not walls."""
    r, c = node
    h = len(grid)
    w = len(grid[0])
    out: List[Pos] = []
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < h and 0 <= nc < w and grid[nr][nc] != "#":
            out.append((nr, nc))
    return out


def reconstruct_path(parent: Dict[Pos, Pos], start: Pos, goal: Pos) -> Optional[List[Pos]]:
    """Reconstruct path from start->goal using parent pointers. Return None if goal unreachable."""
    if start == goal:
        return [start]
    if goal not in parent:
        return None

    path = [goal]
    cur = goal
    while cur != start:
        cur = parent[cur]
        path.append(cur)
    path.reverse()
    return path


def bfs_path(grid: Grid, start: Pos, goal: Pos) -> Tuple[Optional[List[Pos]], Set[Pos]]:
    """
    Queue-based BFS.
    Return (path, visited).
    - path is a list of positions from start to goal (inclusive), or None.
    - visited contains all explored/seen nodes.
    """
    q: deque[Pos] = deque([start])
    visited: Set[Pos] = {start}
    parent: Dict[Pos, Pos] = {}

    while q:
        cur = q.popleft()
        if cur == goal:
            return reconstruct_path(parent, start, goal), visited

        for nxt in neighbors(grid, cur):
            if nxt in visited:
                continue
            visited.add(nxt)  # mark when enqueued
            parent[nxt] = cur
            q.append(nxt)

    return None, visited


def dfs_path(grid: Grid, start: Pos, goal: Pos) -> Tuple[Optional[List[Pos]], Set[Pos]]:
    """
    Stack-based DFS (iterative, no recursion).
    Return (path, visited).
    """
    stack: List[Pos] = [start]
    visited: Set[Pos] = {start}
    parent: Dict[Pos, Pos] = {}

    while stack:
        cur = stack.pop()
        if cur == goal:
            return reconstruct_path(parent, start, goal), visited

        for nxt in reversed(neighbors(grid, cur)):
            if nxt in visited:
                continue
            visited.add(nxt)  # mark when pushed
            parent[nxt] = cur
            stack.append(nxt)

    return None, visited


def render(grid: Grid, path: Optional[List[Pos]] = None, visited: Optional[Set[Pos]] = None) -> str:
    """
    Render the grid as text.
    Overlay rules (recommended):
    - path tiles shown as '*'
    - visited tiles shown as '·' (middle dot) or '+'
    - preserve 'S' and 'G'
    """
    path_set = set(path or [])
    visited_set = visited or set()

    out_rows: List[str] = []
    for r, row in enumerate(grid):
        chars: List[str] = []
        for c, ch in enumerate(row):
            pos = (r, c)
            if ch in {"S", "G"}:
                chars.append(ch)
            elif pos in path_set:
                chars.append("*")
            elif pos in visited_set and ch == ".":
                chars.append("·")
            else:
                chars.append(ch)
        out_rows.append("".join(chars))
    return "\n".join(out_rows)


def run_one(label: str, grid_text: str) -> None:
    grid, start, goal = parse_grid(grid_text)

    print("=" * 60)
    print(label)
    print("- Raw map")
    print(render(grid))

    path_bfs, visited_bfs = bfs_path(grid, start, goal)
    print("\n- BFS")
    print(f"found={path_bfs is not None} path_len={(len(path_bfs) if path_bfs else None)} visited={len(visited_bfs)}")
    print(render(grid, path=path_bfs, visited=visited_bfs))

    path_dfs, visited_dfs = dfs_path(grid, start, goal)
    print("\n- DFS")
    print(f"found={path_dfs is not None} path_len={(len(path_dfs) if path_dfs else None)} visited={len(visited_dfs)}")
    print(render(grid, path=path_dfs, visited=visited_dfs))


def main() -> None:
    run_one("Example Map 1", EXAMPLE_MAP_1)
    run_one("Example Map 2", EXAMPLE_MAP_2)


if __name__ == "__main__":
    main()
