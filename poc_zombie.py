"""
Student portion of Zombie Apocalypse mini-project
"""

import random
import poc_grid
import poc_queue
import poc_zombie_gui

# global constants
EMPTY = 0 
FULL = 1
FOUR_WAY = 0
EIGHT_WAY = 1
OBSTACLE = 5
HUMAN = 6
ZOMBIE = 7


class Apocalypse(poc_grid.Grid):
    """
    Class for simulating zombie pursuit of human on grid with
    obstacles
    """

    def __init__(self, grid_height, grid_width, obstacle_list=None, 
                 zombie_list=None, human_list=None):
        """
        Create a simulation of given size with given obstacles,
        humans, and zombies
        """
        poc_grid.Grid.__init__(self, grid_height, grid_width)
        if obstacle_list != None:
            for cell in obstacle_list:
                self.set_full(cell[0], cell[1])
        if zombie_list != None:
            self._zombie_list = list(zombie_list)
        else:
            self._zombie_list = []
        if human_list != None:
            self._human_list = list(human_list)  
        else:
            self._human_list = []
        
    def clear(self):
        """
        Set cells in obstacle grid to be empty
        Reset zombie and human lists to be empty
        """
        poc_grid.Grid.clear(self) 
        self._zombie_list = []
        self._human_list = []
        
    def add_zombie(self, row, col):
        """
        Add zombie to the zombie list
        """
        self._zombie_list.append((row, col))
                
    def num_zombies(self):
        """
        Return number of zombies
        """
        return len(self._zombie_list)       
          
    def zombies(self):
        """
        Generator that yields the zombies in the order they were
        added.
        """
        # replace with an actual generator
        return (zombie for zombie in self._zombie_list)

    def add_human(self, row, col):
        """
        Add human to the human list
        """
        self._human_list.append((row, col))
        
    def num_humans(self):
        """
        Return number of humans
        """
        return len(self._human_list)       
    
    def humans(self):
        """
        Generator that yields the humans in the order they were added.
        """
        # replace with an actual generator
        return (human for human in self._human_list)
        
    def compute_distance_field(self, entity_type):
        """
        Function computes and returns a 2D distance field
        Distance at member of entity_list is zero
        Shortest paths avoid obstacles and use four-way distances
        """
        visited = poc_grid.Grid(self.get_grid_height(), self.get_grid_width())

        initial_val = self.get_grid_height() * self.get_grid_width()
        distance_field =\
            [[initial_val for dummy_row in range(self.get_grid_width())]
             for dummy_col in range(self.get_grid_height())]
 
        boundary = poc_queue.Queue()
        if entity_type == HUMAN:
            entity_list = self.humans()
        else:
            entity_list = self.zombies()
        
        for row, col in entity_list:
            visited.set_full(row, col)
            distance_field[row][col] = 0
            boundary.enqueue((row, col))
       
        while len(boundary) > 0:
            cur_row, cur_col = boundary.dequeue()
            for neigh_row, neigh_col in \
                    visited.four_neighbors(cur_row, cur_col):
                if visited.is_empty(neigh_row, neigh_col):
                    visited.set_full(neigh_row, neigh_col)
                    # only update neighbor distance if its not an obstacle
                    if self.is_empty(neigh_row, neigh_col):
                        distance_field[neigh_row][neigh_col] =\
                        distance_field[cur_row][cur_col] + 1
                        boundary.enqueue((neigh_row, neigh_col))

        return distance_field
    

    def _dists_for_neighs(self, distance_field, neighbors):
        """
        Get the distances from the distance field for each of the
        (row, col) tuples in neighbors
        """
        return (distance_field[row][col] for row, col in neighbors)


    def _find_move(self, distance_field, neighbors, towards=False):
        """
        find next cell to move to based on the neighbors, the distances
        which drive the move and whether to move toward or away

        Returns None if no possible moves
        """
        possible = [neigh for neigh in neighbors if self.is_empty(*neigh)]
        if len(possible) > 0:
            dists = self._dists_for_neighs(distance_field, possible)
            enum_dists = sorted(enumerate(dists), 
                                key=lambda item: item[1], 
                                reverse=(not towards))
            return possible[enum_dists[0][0]]

        else:
            return None


    def move_humans(self, zombie_distance_field):
        """
        Function that moves humans away from zombies, diagonal moves
        are allowed
        """
        for ind in range(len(self._human_list)):
            human = self._human_list[ind]
            neighbors = self.eight_neighbors(*human)
            # we can stay put
            neighbors.append(human)
            move_to = self._find_move(zombie_distance_field,
                                      neighbors,
                                      towards=False)
            if move_to is not None:
                self._human_list[ind] = move_to

    
    def move_zombies(self, human_distance_field):
        """
        Function that moves zombies towards humans, no diagonal moves
        are allowed
        """
        for ind in range(len(self._zombie_list)):
            zombie = self._zombie_list[ind]
            neighbors = self.four_neighbors(*zombie)
            # we can stay put
            neighbors.append(zombie)
            move_to = self._find_move(human_distance_field,
                                      neighbors,
                                      towards=True)
            if move_to is not None:
                self._zombie_list[ind] = move_to


# Start up gui for simulation - You will need to write some code above
# before this will work without errors

# poc_zombie_gui.run_gui(Apocalypse(30, 40))
