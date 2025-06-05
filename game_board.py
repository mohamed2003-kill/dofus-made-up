from typing import Dict, Optional, Tuple, List
from models import Character

class GameBoard:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid: Dict[Tuple[int, int], Optional[Character]] = {}
        self.obstacles: set = set()

    def is_valid_position(self, position: Tuple[int, int]) -> bool:
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height

    def is_occupied(self, position: Tuple[int, int]) -> bool:
        return position in self.grid or position in self.obstacles

    def add_character(self, character: Character, position: Tuple[int, int]) -> bool:
        if not self.is_valid_position(position) or self.is_occupied(position):
            return False
        self.grid[position] = character
        return True

    def remove_character(self, position: Tuple[int, int]) -> Optional[Character]:
        return self.grid.pop(position, None)

    def get_character_at(self, position: Tuple[int, int]) -> Optional[Character]:
        return self.grid.get(position)

    def add_obstacle(self, position: Tuple[int, int]) -> bool:
        if not self.is_valid_position(position) or self.is_occupied(position):
            return False
        self.obstacles.add(position)
        return True

    def remove_obstacle(self, position: Tuple[int, int]) -> bool:
        if position in self.obstacles:
            self.obstacles.remove(position)
            return True
        return False

    def get_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Find a path between two points using A* pathfinding"""
        if not self.is_valid_position(start) or not self.is_valid_position(end):
            return []
        
        if start == end:
            return [start]
            
        # A* pathfinding algorithm
        def heuristic(pos):
            return abs(pos[0] - end[0]) + abs(pos[1] - end[1])
            
        open_set = {start}
        closed_set = set()
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start)}
        
        while open_set:
            current = min(open_set, key=lambda pos: f_score.get(pos, float('inf')))
            
            if current == end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]
                
            open_set.remove(current)
            closed_set.add(current)
            
            # Check all adjacent squares
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                if not self.is_valid_position(neighbor):
                    continue
                    
                if neighbor in closed_set:
                    continue
                    
                if self.is_occupied(neighbor) and neighbor != end:
                    continue
                    
                tentative_g = g_score[current] + 1
                
                if neighbor not in open_set:
                    open_set.add(neighbor)
                elif tentative_g >= g_score.get(neighbor, float('inf')):
                    continue
                    
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor)
        
        return []  # No path found

    def get_movable_positions(self, position: Tuple[int, int], movement_points: int) -> List[Tuple[int, int]]:
        """Get all positions that can be reached with given movement points"""
        if not self.is_valid_position(position):
            return []
            
        positions = []
        for x in range(max(0, position[0] - movement_points), 
                      min(self.width, position[0] + movement_points + 1)):
            for y in range(max(0, position[1] - movement_points),
                         min(self.height, position[1] + movement_points + 1)):
                if (x, y) != position and not self.is_occupied((x, y)):
                    manhattan_dist = abs(x - position[0]) + abs(y - position[1])
                    if manhattan_dist <= movement_points:
                        positions.append((x, y))
        return positions
