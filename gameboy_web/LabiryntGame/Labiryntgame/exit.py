class Exit:
    def __init__(self, maze):
        self.x, self.y = self.find_exit_position(maze)

    def find_exit_position(self, maze):
        for y in range(len(maze) - 1, -1, -1):
            for x in range(len(maze[0]) - 1, -1, -1):
                if maze[y][x] == 0:
                    return x, y
        return 1, 1  