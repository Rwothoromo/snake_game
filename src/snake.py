class Snake:
    """
    Represents the snake in the Snake game.

    Attributes:
        positions (list of tuple): List of (x, y) coordinates representing the snake's body.
        direction (tuple): Current direction of the snake's movement as (dx, dy).
        grow_flag (bool): Indicates whether the snake should grow in the next move.
    """

    def __init__(self):
        """
        Initializes the Snake object with default positions, direction, and growth flag.
        """
        self.positions = [(100, 100), (90, 100), (80, 100)]  # Initial snake body
        self.direction = (10, 0)  # Initially moving right
        self.grow_flag = False  # Snake does not grow by default

    def move(self):
        """
        Moves the snake in the current direction. If the grow_flag is set, the snake grows
        by adding a new segment to its body. Otherwise, the tail segment is removed.
        """
        head_x, head_y = self.positions[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])  # Calculate new head position
        self.positions.insert(0, new_head)  # Add new head to the front of the snake
        if not self.grow_flag:
            self.positions.pop()  # Remove the tail if not growing
        else:
            self.grow_flag = False  # Reset grow_flag after growing

    def grow(self):
        """
        Sets the grow_flag to True, indicating that the snake should grow in the next move.
        """
        self.grow_flag = True

    def get_head_position(self):
        """
        Returns the position of the snake's head.

        Returns:
            tuple: (x, y) coordinates of the snake's head.
        """
        return self.positions[0]

    def set_direction(self, new_direction):
        """
        Updates the snake's direction if the new direction is not opposite to the current direction.

        Args:
            new_direction (tuple): The new direction as (dx, dy).
        """
        # Prevent the snake from reversing direction
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction

    def get_positions(self):
        """
        Returns the list of positions representing the snake's body.

        Returns:
            list of tuple: List of (x, y) coordinates of the snake's body.
        """
        return self.positions