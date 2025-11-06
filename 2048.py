import pygame
import random
import math

pygame.init()

FRAME_RATE = 120

WIDTH, HEIGHT = 800, 800
ROWS = 4
COLS = 4

RECT_HEIGHT = HEIGHT // ROWS
RECT_WIDTH = WIDTH // COLS

OUTLINE_COLOR = (187, 173, 160)
OUTLINE_THICKNESS = 10
BACKGROUND_COLOR = (205, 192, 180)
FONT_COLOR = (119, 110, 101)

FONT = pygame.font.SysFont("comicsans", 60, bold=True)
MOVE_SPEED = 20

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")


class Tile:
    COLORS = [(237, 229, 218),
        (238, 225, 201),
        (243, 178, 122),
        (246, 150, 101),
        (247, 124, 95),
        (247, 95, 59),
        (237, 208, 115),
        (237, 204, 99),
        (236, 202, 80),]
    
    def __init__(self, value, row, col):
        self.value = value 
        self.row = row
        self.col = col
        self.x = col * RECT_WIDTH
        self.y = row * RECT_HEIGHT

    def get_color(self):
        color_index = int(math.log2(self.value) - 1)
        color = self.COLORS[color_index]
        return color

    def draw(self, window):
        color = self.get_color()
        pygame.draw.rect(window, color, (self.x, self.y, RECT_WIDTH, RECT_HEIGHT))

        text = FONT.render(str(self.value), 1, FONT_COLOR)
        window.blit(
            text, 
            (
                self.x + (RECT_WIDTH / 2 - text.get_width() / 2),
                self.y + (RECT_HEIGHT / 2 - text.get_height() /2),
            
            ), 
        )
        


    def set_pos(self, ceil = False):
        if ceil:
            self.row = math.ceil(self.y/RECT_HEIGHT)
            self.col = math.ceil(self.x/RECT_WIDTH)
        
        else: 
            self.row = math.floor(self.y/RECT_HEIGHT)
            self.col = math.floor(self.x/RECT_WIDTH)

    def move(self, delta):
        self.x += delta[0]
        self.y += delta[1]
        

def draw_grid(window):
    for row in range(1, ROWS):
        y = row * RECT_HEIGHT
        pygame.draw.line(window, OUTLINE_COLOR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)
    
    for col in range(1, COLS):
        x = col * RECT_WIDTH
        pygame.draw.line(window, OUTLINE_COLOR, (x, 0), (x, HEIGHT), OUTLINE_THICKNESS)
 

    pygame.draw.rect(window, OUTLINE_COLOR, (0, 0, WIDTH, HEIGHT), OUTLINE_THICKNESS)

def has_moves(tiles):
    # Empty space means you can still play
        if len(tiles) < ROWS * COLS:
            return True

    # Check any equal neighbors
        for r in range(ROWS):
            for c in range(COLS):
                t = tiles.get(f"{r}{c}")
                if not t:
                    continue
                for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < ROWS and 0 <= nc < COLS:
                        n = tiles.get(f"{nr}{nc}")
                        if n and n.value == t.value:
                            return True
        return False
   


def draw(window, tiles):
    window.fill(BACKGROUND_COLOR)
    for tile in tiles.values(): 
        tile.draw(window)
    draw_grid(window)

    pygame.display.update()


def get_random_pos(tiles):
    row = None
    col = None
    while True: 
        row = random.randrange(0, ROWS)
        col = random.randrange(0, COLS)

        if f"{row}{col}" not in tiles: 
            break
    
    return row, col

def move_tiles(window, tiles, clock, direction):
    updated = True
    blocks = set()

    if direction == "left":
        sort_func = lambda x: x.col
        reverse = False
        delta = (-MOVE_SPEED, 0)
        boundary_check = lambda tile: tile.col == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col-1}")
        merge_check = lambda tile, next_tile: tile.x > next_tile.x + MOVE_SPEED
        move_check = lambda tile, next_tile: tile.x > next_tile.x + RECT_WIDTH + MOVE_SPEED
        ceil = True

    elif direction == "right":
        sort_func = lambda x: x.col
        reverse = True
        delta = (MOVE_SPEED, 0)
        boundary_check = lambda tile: tile.col == COLS -1
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col+1}")
        merge_check = lambda tile, next_tile: tile.x < next_tile.x - MOVE_SPEED
        move_check = lambda tile, next_tile: tile.x + RECT_WIDTH + MOVE_SPEED < next_tile.x 
        ceil = False

    elif direction == "up":
        sort_func = lambda x: x.row
        reverse = False
        delta = (0, -MOVE_SPEED)
        boundary_check = lambda tile: tile.row == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row-1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y > next_tile.y + MOVE_SPEED
        move_check = lambda tile, next_tile: tile.y > next_tile.y + RECT_HEIGHT + MOVE_SPEED
        ceil = True
    
    elif direction == "down":
        sort_func = lambda x: x.row
        reverse = True
        delta = (0, MOVE_SPEED)
        boundary_check = lambda tile: tile.row == ROWS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row + 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y < next_tile.y - MOVE_SPEED
        move_check = (lambda tile, next_tile: tile.y + RECT_HEIGHT + MOVE_SPEED < next_tile.y)
        ceil = False
    
 
    while updated: 
        clock.tick(FRAME_RATE)
        updated = False
        sorted_tiles = sorted(tiles.values(), key = sort_func, reverse = reverse)

        for i, tile in enumerate(sorted_tiles):
            if boundary_check(tile):
                continue

            next_tile = get_next_tile(tile)
            if not next_tile:
                tile.move(delta)
            elif tile.value == next_tile.value and tile not in blocks and next_tile not in blocks:
                if merge_check(tile, next_tile):
                    tile.move(delta)
                else: 
                    next_tile.value *= 2
                    sorted_tiles.pop(i)
                    blocks.add(next_tile)
            
            elif move_check(tile, next_tile):
                tile.move(delta)

            else:
                continue

            tile.set_pos(ceil)
            updated = True
        
        update_tiles(window,tiles,sorted_tiles)
    
    return end_move(tiles)

def end_move(tiles):
    # If board is full, either lost or just continue (no spawn)
    if len(tiles) == ROWS * COLS:
        if not has_moves(tiles):
            return "lost"
        return "continue"

    # Otherwise spawn a new tile and keep going
    row, col = get_random_pos(tiles)
    tiles[f"{row}{col}"] = Tile(random.choice([2, 4]), row, col)
    return "continue"

    

    


def update_tiles(window, tiles, sorted_tiles):
    tiles.clear()
    for tile in sorted_tiles:
        tiles[f"{tile.row}{tile.col}"] = tile
    
    draw(window, tiles)


     
def game_over_menu(window):
    # Dark overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    window.blit(overlay, (0, 0))

    title_font = pygame.font.SysFont("comicsans", 80, bold=True)
    btn_font = pygame.font.SysFont("comicsans", 40, bold=True)

    title = title_font.render("Game Over", True, (255, 255, 255))
    window.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 200))

    btn_w, btn_h = 220, 70
    play_rect = pygame.Rect(WIDTH // 2 - btn_w - 20, HEIGHT // 2 - btn_h // 2, btn_w, btn_h)
    quit_rect = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 - btn_h // 2, btn_w, btn_h)

    # Buttons
    pygame.draw.rect(window, (250, 248, 239), play_rect, border_radius=12)
    pygame.draw.rect(window, (250, 248, 239), quit_rect, border_radius=12)

    play_txt = btn_font.render("Play Again", True, (119, 110, 101))
    quit_txt = btn_font.render("Quit", True, (119, 110, 101))
    window.blit(play_txt, (play_rect.centerx - play_txt.get_width() // 2,
                           play_rect.centery - play_txt.get_height() // 2))
    window.blit(quit_txt, (quit_rect.centerx - quit_txt.get_width() // 2,
                           quit_rect.centery - quit_txt.get_height() // 2))

    pygame.display.update()

    # Wait for click/keypress
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_rect.collidepoint(event.pos):
                    return "restart"
                if quit_rect.collidepoint(event.pos):
                    return "quit"
           

def generate_tiles():
    tiles = {}
    for _ in range(2):
        row, col = get_random_pos(tiles)
        tiles[f"{row}{col}"] = Tile(random.randrange(2,5, 2), row, col) #Tile(2, row, col)

    return tiles

def main(window):
    clock = pygame.time.Clock()
    run = True

    tiles = generate_tiles()

    while run: 
        clock.tick(FRAME_RATE) #might not need this

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    result = move_tiles(window,tiles,clock,"left")
                if event.key == pygame.K_RIGHT:
                    result = move_tiles(window,tiles,clock,"right")
                if event.key == pygame.K_UP:
                    result = move_tiles(window,tiles,clock,"up")
                if event.key == pygame.K_DOWN:
                    result = move_tiles(window,tiles,clock,"down")
                
                if result == "lost":
                    choice = game_over_menu(window)
                    if choice == "restart":
                        tiles = generate_tiles()
                        draw(window, tiles)   # refresh immediately
                    else:  # "quit"
                        run = False
                        break
        
        draw(window, tiles)

    pygame.quit()




if __name__ == "__main__":
    main(WINDOW)

