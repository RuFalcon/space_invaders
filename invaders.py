import pygame
import random
import math # Понадобится для коллизий

# --- Инициализация Pygame ---
pygame.init()
pygame.mixer.init() # Для звуков (если будут)

# --- Константы ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# --- Настройки экрана ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Космические Захватчики") # Переведено

# --- Загрузка ресурсов (замените пути или используйте фигуры) ---
try:
    # Попробуйте загрузить изображения. Если нет, будут ошибки,
    # которые мы пока проигнорируем и будем рисовать фигуры.
    player_img = pygame.image.load('player.png').convert_alpha() # Пример пути
    enemy_img = pygame.image.load('enemy.png').convert_alpha()   # Пример пути
    bullet_img = pygame.image.load('bullet.png').convert_alpha() # Пример пути
    # Масштабирование изображений (если нужно)
    player_img = pygame.transform.scale(player_img, (50, 40))
    enemy_img = pygame.transform.scale(enemy_img, (40, 30))
    bullet_img = pygame.transform.scale(bullet_img, (5, 15))
    images_loaded = True
except pygame.error as e:
    print(f"Не удалось загрузить изображения: {e}. Будут использоваться фигуры.")
    images_loaded = False

# Звуки (примеры)
# shoot_sound = pygame.mixer.Sound('laser.wav')
# explosion_sound = pygame.mixer.Sound('explosion.wav')

# --- Игрок ---
player_width = 50
player_height = 40
player_x = SCREEN_WIDTH // 2 - player_width // 2
player_y = SCREEN_HEIGHT - player_height - 10
player_speed = 5
player_rect = pygame.Rect(player_x, player_y, player_width, player_height) # Rect для коллизий

# --- Пуля игрока ---
bullet_width = 5
bullet_height = 15
bullet_speed = 10
bullet_state = "ready" # "ready" - можно стрелять, "fired" - пуля летит
player_bullet_rect = pygame.Rect(0, 0, bullet_width, bullet_height) # Инициализируем вне экрана

# --- Враги ---
enemy_width = 40
enemy_height = 30
enemy_speed_x = 1 # Скорость по горизонтали
enemy_speed_y = 15 # На сколько спускаются вниз
enemies = []
num_enemies_rows = 5
num_enemies_cols = 10
enemy_start_x = 50
enemy_start_y = 50
enemy_spacing_x = 60
enemy_spacing_y = 40

# Создаем врагов
for row in range(num_enemies_rows):
    for col in range(num_enemies_cols):
        enemy_x = enemy_start_x + col * enemy_spacing_x
        enemy_y = enemy_start_y + row * enemy_spacing_y
        enemy_rect = pygame.Rect(enemy_x, enemy_y, enemy_width, enemy_height)
        enemies.append(enemy_rect) # Добавляем Rect врага в список

# Направление движения врагов (1 = вправо, -1 = влево)
enemy_direction = 1

# --- Пули врагов ---
enemy_bullets = []
enemy_bullet_width = 5
enemy_bullet_height = 10
enemy_bullet_speed = 7
enemy_shoot_chance = 0.05 # Шанс выстрела врага в каждом кадре (уменьшить для сложности)

# --- Счет и Жизни ---
score = 0
lives = 3
font = pygame.font.Font(None, 36) # Стандартный шрифт Pygame

# --- Игровой цикл ---
running = True
game_over = False
game_won = False # Флаг для победы
clock = pygame.time.Clock()

def draw_player(x, y):
    if images_loaded:
        screen.blit(player_img, (x, y))
    else:
        pygame.draw.rect(screen, GREEN, player_rect) # Рисуем зеленый квадрат

def draw_enemy(rect):
    if images_loaded:
        screen.blit(enemy_img, (rect.x, rect.y))
    else:
        pygame.draw.rect(screen, RED, rect) # Рисуем красный квадрат

def draw_bullet(rect):
    if images_loaded and bullet_state == "fired": # Только если стреляли
         # Центрируем изображение пули относительно Rect
        img_rect = bullet_img.get_rect(center=rect.center)
        screen.blit(bullet_img, img_rect.topleft)
    elif bullet_state == "fired": # Если изображений нет, но стреляли
        pygame.draw.rect(screen, WHITE, rect) # Рисуем белый прямоугольник

def draw_enemy_bullet(rect):
     # Для пуль врагов можно тоже использовать изображение или цвет
    pygame.draw.rect(screen, RED, rect)

def show_score_lives():
    score_text = font.render(f"Счет: {score}", True, WHITE) # Переведено
    lives_text = font.render(f"Жизни: {lives}", True, WHITE) # Переведено
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 10, 10))

def show_game_over():
    game_over_font = pygame.font.Font(None, 72)
    game_over_text = game_over_font.render("ИГРА ОКОНЧЕНА", True, RED) # Переведено
    text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)) # Немного поднимем
    screen.blit(game_over_text, text_rect)
    restart_font = pygame.font.Font(None, 36)
    restart_text = restart_font.render("Нажмите R или ПРОБЕЛ для рестарта", True, WHITE)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
    screen.blit(restart_text, restart_rect)

def is_collision(obj1_rect, obj2_rect):
    return obj1_rect.colliderect(obj2_rect)

def show_victory_screen():
    victory_font = pygame.font.Font(None, 72)
    victory_text = victory_font.render("ПОБЕДА!", True, GREEN) # Сообщение о победе
    text_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
    screen.blit(victory_text, text_rect)
    restart_font = pygame.font.Font(None, 36)
    restart_text = restart_font.render("Нажмите R или ПРОБЕЛ для рестарта", True, WHITE)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
    screen.blit(restart_text, restart_rect)

# -------- Основной Цикл Игры -----------
while running:
    # --- Обработка событий ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Нажатие клавиш
        if event.type == pygame.KEYDOWN:
            if not game_over and not game_won: # Управляем только если игра не окончена и не выиграна
                if event.key == pygame.K_SPACE and bullet_state == "ready":
                    # Стреляем (пуля появляется над центром игрока)
                    player_bullet_rect.centerx = player_rect.centerx
                    player_bullet_rect.bottom = player_rect.top
                    bullet_state = "fired"
                    # if shoot_sound: shoot_sound.play() # Воспроизвести звук выстрела

            # Рестарт по клавише R или ПРОБЕЛ, если игра окончена
            # Рестарт по клавише R или ПРОБЕЛ, если игра окончена или выиграна
            if (game_over or game_won) and (event.key == pygame.K_r or event.key == pygame.K_SPACE):
                # Сброс всех переменных к начальным значениям
                score = 0
                lives = 3
                player_rect.x = SCREEN_WIDTH // 2 - player_width // 2
                player_rect.y = SCREEN_HEIGHT - player_height - 10
                enemies.clear()
                enemy_bullets.clear()
                bullet_state = "ready"
                enemy_direction = 1
                for row in range(num_enemies_rows):
                    for col in range(num_enemies_cols):
                        enemy_x = enemy_start_x + col * enemy_spacing_x
                        enemy_y = enemy_start_y + row * enemy_spacing_y
                        enemy_rect = pygame.Rect(enemy_x, enemy_y, enemy_width, enemy_height)
                        enemies.append(enemy_rect)
                game_over = False
                game_won = False # Сбрасываем флаг победы при рестарте


    # Если игра окончена или выиграна, показываем соответствующий экран и пропускаем логику
    if game_over or game_won:
        # --- Отрисовка конца игры / победы ---
        screen.fill(BLACK)
        show_score_lives()
        if game_over:
            show_game_over()
        elif game_won:
            show_victory_screen()
        pygame.display.flip() # Обновляем экран
        clock.tick(60) # Ограничиваем FPS
        continue # Переходим к следующей итерации цикла

    # --- Логика Игры ---

    # -- Движение игрока --
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_rect.left > 0:
        player_rect.x -= player_speed
    if keys[pygame.K_RIGHT] and player_rect.right < SCREEN_WIDTH:
        player_rect.x += player_speed

    # -- Движение пули игрока --
    if bullet_state == "fired":
        player_bullet_rect.y -= bullet_speed
        # Если пуля улетела за экран
        if player_bullet_rect.bottom < 0:
            bullet_state = "ready"

    # -- Движение врагов --
    move_down = False
    for enemy in enemies:
        enemy.x += enemy_speed_x * enemy_direction
        # Проверка выхода за границы экрана
        if enemy.right > SCREEN_WIDTH or enemy.left < 0:
            move_down = True # Ставим флаг, что нужно двигаться вниз

    # Если нужно двигаться вниз
    if move_down:
        enemy_direction *= -1 # Меняем направление
        for enemy in enemies:
            enemy.y += enemy_speed_y # Сдвигаем всех врагов вниз
            enemy.x += enemy_speed_x * enemy_direction # Корректируем позицию после смены направления

    # -- Стрельба врагов --
    # Выбираем случайного врага для выстрела
    if enemies and random.random() < enemy_shoot_chance: # Стреляем только если есть враги
        shooter = random.choice(enemies)
        enemy_bullet_rect = pygame.Rect(shooter.centerx - enemy_bullet_width // 2,
                                        shooter.bottom,
                                        enemy_bullet_width,
                                        enemy_bullet_height)
        enemy_bullets.append(enemy_bullet_rect)

    # -- Движение пуль врагов --
    bullets_to_remove = [] # Список для пуль, которые нужно удалить
    for i, bullet in enumerate(enemy_bullets):
        bullet.y += enemy_bullet_speed
        if bullet.top > SCREEN_HEIGHT:
            bullets_to_remove.append(i) # Добавляем индекс для удаления

    # Удаляем пули, вышедшие за экран (в обратном порядке, чтобы не сбить индексы)
    for index in sorted(bullets_to_remove, reverse=True):
        del enemy_bullets[index]


    # -- Проверка коллизий --

    # 1. Пуля игрока с врагами
    enemies_to_remove = []
    if bullet_state == "fired":
        for i, enemy in enumerate(enemies):
            if is_collision(player_bullet_rect, enemy):
                # if explosion_sound: explosion_sound.play() # Звук взрыва
                score += 10 # Добавляем очки
                enemies_to_remove.append(i) # Добавляем индекс врага для удаления
                bullet_state = "ready" # Сбрасываем пулю
                player_bullet_rect.y = -100 # Убираем ее с экрана до следующего выстрела
                break # Пуля может сбить только одного врага за раз

    # Удаляем сбитых врагов (в обратном порядке)
    for index in sorted(enemies_to_remove, reverse=True):
        del enemies[index]

    # 2. Пули врагов с игроком
    bullets_to_remove.clear() # Очищаем список для удаления пуль
    for i, bullet in enumerate(enemy_bullets):
        if is_collision(bullet, player_rect):
            lives -= 1
            bullets_to_remove.append(i) # Добавляем индекс пули для удаления
            # Можно добавить эффект мигания или временной неуязвимости
            if lives <= 0:
                game_over = True
                # Можно добавить звук проигрыша
            break # Одна пуля - одно попадание за кадр

    # Удаляем попавшие пули врагов (в обратном порядке)
    for index in sorted(bullets_to_remove, reverse=True):
        del enemy_bullets[index]


    # 3. Враги с игроком (или достижение низа)
    for enemy in enemies:
        if is_collision(enemy, player_rect) or enemy.bottom >= player_rect.top:
            lives = 0 # Мгновенный проигрыш
            game_over = True
            break # Достаточно одного столкновения

    # Проверка победы (если врагов не осталось)
    if not enemies and not game_over and not game_won: # Проверяем, что еще не выиграли
        game_won = True # Устанавливаем флаг победы
        # Звук победы? pygame.mixer.Sound('victory.wav').play()


    # --- Отрисовка ---
    screen.fill(BLACK) # Очищаем экран (фон)

    draw_player(player_rect.x, player_rect.y)
    for enemy in enemies:
        draw_enemy(enemy)
    draw_bullet(player_bullet_rect) # Рисуем пулю игрока
    for bullet in enemy_bullets:
        draw_enemy_bullet(bullet) # Рисуем пули врагов

    show_score_lives() # Показываем счет и жизни

    # --- Обновление экрана ---
    pygame.display.flip() # Показываем нарисованное

    # --- Контроль FPS ---
    clock.tick(60) # Ограничиваем до 60 кадров в секунду

# --- Завершение Pygame ---
pygame.quit()
