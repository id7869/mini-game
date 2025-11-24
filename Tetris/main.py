import pygame
import random
import sys

# 初始化 pygame
pygame.init()

# 常量设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 200

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)

# 方块形状定义
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]]   # L
]

# 方块颜色
SHAPE_COLORS = [CYAN, YELLOW, MAGENTA, GREEN, RED, BLUE, ORANGE]

class Tetromino:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.shape_idx = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.shape_idx]
        self.color = SHAPE_COLORS[self.shape_idx]
        self.rotation = 0

    def rotate(self):
        # 转置矩阵实现旋转
        rows = len(self.shape)
        cols = len(self.shape[0])
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]
        
        for r in range(rows):
            for c in range(cols):
                rotated[c][rows - 1 - r] = self.shape[r][c]
        
        return rotated

class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("simhei", 24)
        self.small_font = pygame.font.SysFont("simhei", 18)
        
        self.reset_game()
        
    def reset_game(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.base_fall_speed = 0.5  # 基础下降速度(秒)
        self.fall_speed = self.base_fall_speed  # 当前下降速度
        self.fall_time = 0
        self.speed_level = 1  # 速度等级(1-10)
        
    def new_piece(self):
        return Tetromino(GRID_WIDTH // 2 - 1, 0)
        
    def valid_position(self, piece, x, y, shape=None):
        shape_to_check = shape if shape else piece.shape
        
        for r, row in enumerate(shape_to_check):
            for c, cell in enumerate(row):
                if cell:
                    pos_x, pos_y = x + c, y + r
                    # 检查边界
                    if pos_x < 0 or pos_x >= GRID_WIDTH or pos_y >= GRID_HEIGHT:
                        return False
                    # 检查是否与已放置的方块重叠
                    if pos_y >= 0 and self.grid[pos_y][pos_x]:
                        return False
        return True
        
    def merge_piece(self):
        for r, row in enumerate(self.current_piece.shape):
            for c, cell in enumerate(row):
                if cell:
                    pos_y = self.current_piece.y + r
                    pos_x = self.current_piece.x + c
                    if pos_y >= 0:  # 只合并可见区域内的方块
                        self.grid[pos_y][pos_x] = self.current_piece.color
                        
    def clear_lines(self):
        lines_to_clear = []
        for r in range(GRID_HEIGHT):
            if all(self.grid[r]):
                lines_to_clear.append(r)
                
        for line in lines_to_clear:
            del self.grid[line]
            self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            
        # 更新分数
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            self.score += [100, 300, 500, 800][min(len(lines_to_clear) - 1, 3)] * self.level
            self.level = self.lines_cleared // 10 + 1
            # 不再根据等级自动调整速度
            
        return len(lines_to_clear)
        
    def adjust_speed(self, delta):
        """调整下降速度"""
        self.speed_level = max(1, min(10, self.speed_level + delta))
        # 速度计算：基础速度 * (11 - 速度等级) / 10
        # 速度等级越高，下降速度越快
        self.fall_speed = self.base_fall_speed * (11 - self.speed_level) / 10
        # 确保最小速度
        self.fall_speed = max(0.05, self.fall_speed)
        
    def move(self, dx, dy):
        if not self.game_over:
            if self.valid_position(self.current_piece, self.current_piece.x + dx, self.current_piece.y + dy):
                self.current_piece.x += dx
                self.current_piece.y += dy
                return True
        return False
        
    def rotate_piece(self):
        if not self.game_over:
            rotated_shape = self.current_piece.rotate()
            if self.valid_position(self.current_piece, self.current_piece.x, self.current_piece.y, rotated_shape):
                self.current_piece.shape = rotated_shape
                return True
        return False
        
    def drop(self):
        if not self.game_over:
            while self.move(0, 1):
                pass
            self.lock_piece()
            
    def lock_piece(self):
        self.merge_piece()
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        
        # 检查游戏结束
        if not self.valid_position(self.current_piece, self.current_piece.x, self.current_piece.y):
            self.game_over = True
            
    def draw_grid(self):
        # 绘制游戏区域背景
        game_area = pygame.Rect(0, 0, GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE)
        pygame.draw.rect(self.screen, DARK_GRAY, game_area)
        
        # 绘制网格线
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(self.screen, GRAY, (x * GRID_SIZE, 0), (x * GRID_SIZE, GRID_HEIGHT * GRID_SIZE))
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, GRAY, (0, y * GRID_SIZE), (GRID_WIDTH * GRID_SIZE, y * GRID_SIZE))
            
        # 绘制已放置的方块
        for r in range(GRID_HEIGHT):
            for c in range(GRID_WIDTH):
                if self.grid[r][c]:
                    pygame.draw.rect(self.screen, self.grid[r][c], 
                                    (c * GRID_SIZE, r * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                    pygame.draw.rect(self.screen, WHITE, 
                                    (c * GRID_SIZE, r * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)
                    
        # 绘制当前方块
        if not self.game_over:
            for r, row in enumerate(self.current_piece.shape):
                for c, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen, self.current_piece.color, 
                                        ((self.current_piece.x + c) * GRID_SIZE, 
                                         (self.current_piece.y + r) * GRID_SIZE, 
                                         GRID_SIZE, GRID_SIZE))
                        pygame.draw.rect(self.screen, WHITE, 
                                        ((self.current_piece.x + c) * GRID_SIZE, 
                                         (self.current_piece.y + r) * GRID_SIZE, 
                                         GRID_SIZE, GRID_SIZE), 1)
                        
    def draw_sidebar(self):
        # 侧边栏背景
        sidebar = pygame.Rect(GRID_WIDTH * GRID_SIZE, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, BLACK, sidebar)
        
        # 显示分数
        score_text = self.font.render(f"分数: {self.score}", True, WHITE)
        self.screen.blit(score_text, (GRID_WIDTH * GRID_SIZE + 20, 50))
        
        # 显示等级
        level_text = self.font.render(f"等级: {self.level}", True, WHITE)
        self.screen.blit(level_text, (GRID_WIDTH * GRID_SIZE + 20, 100))
        
        # 显示消除行数
        lines_text = self.font.render(f"行数: {self.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, (GRID_WIDTH * GRID_SIZE + 20, 150))
        
        # 显示速度等级
        speed_text = self.font.render(f"速度: {self.speed_level}", True, WHITE)
        self.screen.blit(speed_text, (GRID_WIDTH * GRID_SIZE + 20, 180))
        
        # 显示下一个方块
        next_text = self.font.render("下一个:", True, WHITE)
        self.screen.blit(next_text, (GRID_WIDTH * GRID_SIZE + 20, 230))
        
        # 绘制下一个方块预览
        preview_x = GRID_WIDTH * GRID_SIZE + 50
        preview_y = 280
        for r, row in enumerate(self.next_piece.shape):
            for c, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, self.next_piece.color, 
                                    (preview_x + c * GRID_SIZE, 
                                     preview_y + r * GRID_SIZE, 
                                     GRID_SIZE, GRID_SIZE))
                    pygame.draw.rect(self.screen, WHITE, 
                                    (preview_x + c * GRID_SIZE, 
                                     preview_y + r * GRID_SIZE, 
                                     GRID_SIZE, GRID_SIZE), 1)
                    
        # 显示控制说明
        controls = [
            "控制说明:",
            "← → : 移动",
            "↑ : 旋转",
            "↓ : 软降",
            "空格 : 硬降",
            "+/- : 调节速度"
        ]
        
        for i, text in enumerate(controls):
            control_text = self.small_font.render(text, True, WHITE)
            self.screen.blit(control_text, (GRID_WIDTH * GRID_SIZE + 20, 380 + i * 30))
            
        # 显示游戏结束信息
        if self.game_over:
            game_over_text = self.font.render("游戏结束!", True, RED)
            self.screen.blit(game_over_text, (GRID_WIDTH * GRID_SIZE + 20, SCREEN_HEIGHT - 100))
            
    def run(self):
        last_time = pygame.time.get_ticks()
        
        while True:
            # 确保事件队列被处理
            pygame.event.pump()
            
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - last_time) / 1000.0  # 转换为秒
            last_time = current_time
            
            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.KEYDOWN:
                    # 速度调节控制
                    if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.adjust_speed(1)  # 增加速度等级
                    elif event.key == pygame.K_MINUS:
                        self.adjust_speed(-1)  # 减少速度等级
                        
                    if not self.game_over:
                        if event.key == pygame.K_LEFT:
                            self.move(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.move(1, 0)
                        elif event.key == pygame.K_DOWN:
                            self.move(0, 1)
                        elif event.key == pygame.K_UP:
                            self.rotate_piece()
                        elif event.key == pygame.K_SPACE:
                            self.drop()
                            
            # 自然下落
            if not self.game_over:
                self.fall_time += delta_time
                if self.fall_time >= self.fall_speed:
                    if not self.move(0, 1):
                        self.lock_piece()
                    self.fall_time = 0
                    
            # 绘制
            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_sidebar()
            
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = TetrisGame()
    game.run()
