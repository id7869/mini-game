# Greedy Snake - 贪吃蛇游戏
import pygame
import random
import sys

# 初始化Pygame
pygame.init()

# 游戏配置
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CELL_SIZE = 20
CELL_NUMBER_X = WINDOW_WIDTH // CELL_SIZE
CELL_NUMBER_Y = WINDOW_HEIGHT // CELL_SIZE

# 颜色定义
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
DARK_GREEN = (0, 200, 0)
GRAY = (128, 128, 128)

class Snake:
    def __init__(self):
        # 初始蛇身位置（3个方块）
        self.body = [pygame.Vector2(5, 10), pygame.Vector2(4, 10), pygame.Vector2(3, 10)]
        self.direction = pygame.Vector2(1, 0)  # 初始向右移动
        self.new_block = False
        
    def draw_snake(self, screen):
        for index, block in enumerate(self.body):
            x_pos = int(block.x * CELL_SIZE)
            y_pos = int(block.y * CELL_SIZE)
            block_rect = pygame.Rect(x_pos, y_pos, CELL_SIZE, CELL_SIZE)
            
            # 蛇头使用不同颜色
            if index == 0:
                pygame.draw.rect(screen, DARK_GREEN, block_rect)
            else:
                pygame.draw.rect(screen, GREEN, block_rect)
    
    def move_snake(self):
        if self.new_block:
            # 如果吃到食物，不删除尾部，实现增长
            body_copy = self.body[:]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]
            self.new_block = False
        else:
            # 正常移动，删除尾部，添加新头部
            body_copy = self.body[:-1]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]
    
    def add_block(self):
        self.new_block = True
    
    def check_collision(self):
        # 检查是否撞墙
        if not 0 <= self.body[0].x < CELL_NUMBER_X or not 0 <= self.body[0].y < CELL_NUMBER_Y:
            return True
        
        # 检查是否撞到自己
        for block in self.body[1:]:
            if block == self.body[0]:
                return True
        
        return False

class Food:
    def __init__(self):
        self.randomize()
    
    def draw_food(self, screen):
        food_rect = pygame.Rect(int(self.pos.x * CELL_SIZE), int(self.pos.y * CELL_SIZE), CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, RED, food_rect)
    
    def randomize(self):
        self.x = random.randint(0, CELL_NUMBER_X - 1)
        self.y = random.randint(0, CELL_NUMBER_Y - 1)
        self.pos = pygame.Vector2(self.x, self.y)

class SpeedSlider:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.knob_radius = 10
        self.min_value = 1
        self.max_value = 10
        self.value = 5  # 默认速度
        self.dragging = False
        
    def draw(self, screen):
        # 绘制滑块轨道
        pygame.draw.rect(screen, GRAY, self.rect)
        
        # 计算滑块位置
        knob_x = self.rect.x + (self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width
        knob_y = self.rect.centery
        
        # 绘制滑块
        pygame.draw.circle(screen, BLUE, (int(knob_x), int(knob_y)), self.knob_radius)
        
        # 绘制标签
        font = pygame.font.Font(None, 24)
        text = font.render("Speed: " + str(self.value), True, WHITE)
        screen.blit(text, (self.rect.x, self.rect.y - 30))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                mouse_pos = pygame.mouse.get_pos()
                knob_x = self.rect.x + (self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width
                knob_y = self.rect.centery
                knob_rect = pygame.Rect(knob_x - self.knob_radius, knob_y - self.knob_radius, 
                                        self.knob_radius * 2, self.knob_radius * 2)
                
                if knob_rect.collidepoint(mouse_pos):
                    self.dragging = True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # 左键释放
                self.dragging = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x, _ = pygame.mouse.get_pos()
                # 限制滑块在轨道范围内
                mouse_x = max(self.rect.left, min(mouse_x, self.rect.right))
                
                # 计算新的值
                relative_x = (mouse_x - self.rect.x) / self.rect.width
                self.value = self.min_value + relative_x * (self.max_value - self.min_value)
                self.value = max(self.min_value, min(self.max_value, self.value))

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.speed_slider = SpeedSlider(50, WINDOW_HEIGHT - 50, 200, 10)
        self.game_over = False
    
    def update(self):
        if not self.game_over:
            self.snake.move_snake()
            self.check_collision()
            self.check_fail()
    
    def draw_elements(self, screen):
        self.food.draw_food(screen)
        self.snake.draw_snake(screen)
        self.draw_score(screen)
        self.speed_slider.draw(screen)
    
    def check_collision(self):
        # 检查蛇是否吃到食物
        if self.food.pos == self.snake.body[0]:
            self.food.randomize()
            self.snake.add_block()
            self.score += 10
            
            # 确保食物不会出现在蛇身上
            for block in self.snake.body[1:]:
                if block == self.food.pos:
                    self.food.randomize()
    
    def check_fail(self):
        # 检查游戏结束条件
        if self.snake.check_collision():
            self.game_over = True
    
    def draw_score(self, screen):
        font = pygame.font.Font(None, 36)
        score_text = "Score: " + str(self.score)
        score_surface = font.render(score_text, True, WHITE)
        score_rect = score_surface.get_rect(center=(WINDOW_WIDTH // 2, 30))
        screen.blit(score_surface, score_rect)
        
        if self.game_over:
            game_over_font = pygame.font.Font(None, 72)
            game_over_text = game_over_font.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(game_over_text, game_over_rect)
            
            restart_font = pygame.font.Font(None, 36)
            restart_text = restart_font.render("Press SPACE to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
            screen.blit(restart_text, restart_rect)
    
    def reset_game(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.game_over = False

def main():
    # 创建游戏窗口
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Greedy Snake')
    clock = pygame.time.Clock()
    
    # 创建游戏实例
    game = Game()
    
    # 设置游戏更新事件
    SCREEN_UPDATE = pygame.USEREVENT
    pygame.time.set_timer(SCREEN_UPDATE, 150)  # 初始更新间隔
    
    # 主游戏循环
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == SCREEN_UPDATE and not game.game_over:
                game.update()
            
            if event.type == pygame.KEYDOWN:
                if not game.game_over:
                    # 控制蛇的方向
                    if event.key == pygame.K_UP:
                        if game.snake.direction.y != 1:  # 不能直接向下转
                            game.snake.direction = pygame.Vector2(0, -1)
                    if event.key == pygame.K_DOWN:
                        if game.snake.direction.y != -1:  # 不能直接向上转
                            game.snake.direction = pygame.Vector2(0, 1)
                    if event.key == pygame.K_RIGHT:
                        if game.snake.direction.x != -1:  # 不能直接向左转
                            game.snake.direction = pygame.Vector2(1, 0)
                    if event.key == pygame.K_LEFT:
                        if game.snake.direction.x != 1:  # 不能直接向右转
                            game.snake.direction = pygame.Vector2(-1, 0)
                else:
                    # 游戏结束后按空格键重新开始
                    if event.key == pygame.K_SPACE:
                        game.reset_game()
            
            # 处理速度滑块事件
            game.speed_slider.handle_event(event)
            
            # 根据速度滑块值调整游戏速度
            pygame.time.set_timer(SCREEN_UPDATE, 200 - int(game.speed_slider.value) * 15)
        
        # 填充背景
        screen.fill(BLACK)
        
        # 绘制游戏元素
        game.draw_elements(screen)
        
        # 更新显示
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()