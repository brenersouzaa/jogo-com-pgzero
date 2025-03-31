# Importando as bibliotecas necessárias
import pgzrun
import random
from pygame import Rect
from pgzero.actor import Actor
from pgzero.keyboard import keyboard, keys
from pgzero.clock import clock
from pgzero import music
import pgzero.screen
screen: pgzero.screen.Screen

# Configurações globais do jogo
WIDTH = 800
HEIGHT = 600  #
TITLE = "Galaxy Invasion"  # Título que escolho para o jogo
music_enabled = True  # Controle para ativar/desativar a música

# Variáveis de estado do jogo
game_state = "menu"  # Estados possíveis: "menu", "playing", "game_over"
enemy_spawn_delay = 300  # Intervalo para spawn de inimigos
frames_elapsed = 0  # Contador de frames para controle de eventos

########## Classe do Jogador ##########


class Player:
    def __init__(self):
        self.actor = Actor("alien-yellow-front", (WIDTH // 2, HEIGHT - 100))
        self.vy = 0  # Velocidade vertical
        self.speed = 4  # Velocidade horizontal
        self.direction = "right"  # Direção inicial
        self.walk_frames = ["alien-yellow-walk-1",
                            "alien-yellow-walk-2"]  # Animação de caminhada
        self.idle_frames = ["alien-yellow-swim-1"]  # Animação de inatividade
        self.current_frame = 0  # Quadro atual da animação
        self.frame_counter = 0  # Contador para alternar quadros
        self.is_hit = False  # Indica se o jogador foi atingido

    def update(self):
        # Atualiza o estado do jogador
        if self.is_hit:  # Se o jogador foi atingido, ele cai lentamente
            self.vy += 0.2
            self.actor.y += self.vy
            if self.actor.y > HEIGHT:  # Se sair da tela, o jogo termina
                game_over()
            return

        self.vy += 0.3  # Gravidade
        self.actor.y += self.vy
        if self.actor.y > HEIGHT or self.actor.y < 0:  # Verifica se o jogador caiu ou bateu no teto
            self.trigger_death()

        landed = False
        for block in blocks:
            # Verifica colisão com blocos
            block_rect = Rect(block.x - 60, block.y - 20, 120, 40)
            if self.actor.colliderect(block_rect) and self.actor.y + self.actor.height // 2 <= block_rect.y + 10:
                self.actor.y = block_rect.y - self.actor.height // 2
                self.vy = 0
                landed = True
                break

        if not landed:
            self.vy += 0.3  # Aumenta a gravidade se não estiver pousado

        for enemy in enemies:
            # Ajusta a lógica para verificar colisão apenas com o corpo do personagem
            if self.actor.colliderect(enemy.actor) and abs(self.actor.y - enemy.actor.y) < self.actor.height // 2:
                self.trigger_death()

        self.animate()  # Atualiza a animação do jogador

    def trigger_death(self):
        # Executa a animação de morte do jogador
        if not self.is_hit:
            self.is_hit = True
            self.actor.image = "alien-yellow-over"  # Muda para a imagem de derrota
            clock.schedule_unique(lambda: setattr(self, "vy", 2), 0.5)

    def move_left(self):
        # Move o jogador para a esquerda
        if self.actor.x > 0:
            self.actor.x -= self.speed
        self.direction = "left"
        self.actor.flip_x = True

    def move_right(self):
        # Move o jogador para a direita
        if self.actor.x < WIDTH:
            self.actor.x += self.speed
        self.direction = "right"
        self.actor.flip_x = False

    def jump(self):
        # Faz o jogador pular
        self.vy = -5

    def animate(self):
        # Atualiza a animação do jogador
        self.frame_counter += 1
        if self.frame_counter >= 10:
            self.current_frame = (self.current_frame +
                                  1) % len(self.walk_frames)
            if self.direction == "right":
                self.actor.image = self.walk_frames[self.current_frame]
            elif self.direction == "left":
                self.actor.image = self.walk_frames[self.current_frame]
                self.actor.flip_x = True
            else:
                self.actor.image = self.idle_frames[0]
            self.frame_counter = 0

########## Classe do Inimigo ##########


class Enemy:
    def __init__(self, x, y):
        # Inicializa o inimigo em uma posição aleatória
        self.actor = Actor("fly", (x, y))
        self.direction = random.choice([-1, 1])  # Direção inicial aleatória
        self.speed = random.randint(1, 2)  # Velocidade reduzida para 1 ou 2
        self.patrol_range = random.randint(
            100, WIDTH - 100)  # Alcance de patrulha
        self.start_x = x
        self.walk_frames = ["fly", "fly-move"]  # Animação do inimigo
        self.current_frame = 0
        self.frame_counter = 0

    def update(self):
        # Atualiza a posição do inimigo
        self.actor.x += self.direction * self.speed
        if self.actor.x <= 0 or self.actor.x >= WIDTH or abs(self.actor.x - self.start_x) > self.patrol_range:
            self.direction *= -1  # Inverte a direção ao atingir os limites
        self.animate()

    def animate(self):
        # Atualiza a animação do inimigo
        self.frame_counter += 1
        if self.frame_counter >= 10:
            self.current_frame = (self.current_frame +
                                  1) % len(self.walk_frames)
            self.actor.image = self.walk_frames[self.current_frame]
            self.frame_counter = 0


# Blocos do cenário
blocks = [Actor("block-small", (random.randint(50, WIDTH - 50),
                random.randint(300, HEIGHT - 50))) for _ in range(5)]
enemies = []
player = Player()

########## Funções de Desenho ##########


def draw():
    screen.clear()
    screen.blit("background", (0, 0))  # Desenha o fundo
    if game_state == "menu":
        draw_menu()
    elif game_state == "playing":
        draw_game()
    elif game_state == "game_over":
        draw_game_over()


def draw_menu():
    # Desenha o menu principal
    screen.draw.text("Galaxy Invasion", center=(
        WIDTH // 2, 100), fontsize=50, color="black")
    screen.draw.filled_rect(Rect((300, 200, 200, 50)), "gray")
    screen.draw.text("Play", center=(400, 225), fontsize=30, color="black")
    screen.draw.filled_rect(Rect((300, 300, 200, 50)), "gray")
    screen.draw.text("Exit", center=(400, 325), fontsize=30, color="black")
    screen.draw.filled_rect(Rect((300, 400, 200, 50)), "gray")
    screen.draw.text(f"Music: {'On' if music_enabled else 'Off'}", center=(
        400, 425), fontsize=30, color="black")


def draw_game():
    # Desenha o jogo em andamento
    player.actor.draw()
    for block in blocks:
        block.draw()
    for enemy in enemies:
        enemy.actor.draw()


def draw_game_over():
    # Desenha a tela de game over
    screen.draw.text("Game Over", center=(
        WIDTH // 2, 100), fontsize=50, color="red")
    player.actor.draw()
    screen.draw.filled_rect(Rect((300, 400, 200, 50)), "gray")
    screen.draw.text("Return to Menu", center=(
        400, 425), fontsize=30, color="black")

########## Funções de Atualização ##########


def update():
    global frames_elapsed
    if game_state == "playing":
        frames_elapsed += 1
        player.update()
        update_blocks()
        if frames_elapsed > enemy_spawn_delay:
            update_enemies()
        handle_player_movement()


def update_blocks():
    # Atualiza os blocos do cenário
    global blocks
    for block in blocks:
        block.y -= 1  # Diminui a velocidade com que os blocos sobem
    blocks = [block for block in blocks if block.y + 40 > 0]

    # Garante que sempre haja pelo menos 4 blocos na tela
    while len(blocks) < 4:
        new_block_x = random.randint(60, WIDTH - 60)
        new_block_y = HEIGHT + 80
        blocks.append(Actor("block-small", (new_block_x, new_block_y)))

    # Aumenta a chance de surgimento de blocos (de 50% para 70%)
    if random.randint(1, 100) <= 70:
        new_block_x = random.randint(60, WIDTH - 60)
        new_block_y = HEIGHT + 80
        if all(abs(new_block_x - block.x) > 100 for block in blocks):  # Mantém espaçamento horizontal
            blocks.append(Actor("block-small", (new_block_x, new_block_y)))


def update_enemies():
    # Atualiza os inimigos
    global enemies
    for enemy in enemies:
        enemy.update()
    enemies = [enemy for enemy in enemies if 0 <= enemy.actor.x <= WIDTH]
    if len(enemies) == 0:  # Garante que apenas 1 inimigo esteja presente
        new_enemy_x = random.randint(0, WIDTH)
        new_enemy_y = random.randint(50, HEIGHT - 150)
        enemies.append(Enemy(new_enemy_x, new_enemy_y))

########## Funções de Controle ##########


def on_key_down(key):
    if key == keys.SPACE:
        player.jump()


def on_key_up(key):
    if key == keys.LEFT or key == keys.RIGHT:
        player.direction = "idle"


def handle_player_movement():
    # Corrigido o uso de "e" para "and"
    if keyboard.left and not keyboard.right:
        player.move_left()
    elif keyboard.right and not keyboard.left:
        player.move_right()
    else:
        player.direction = "idle"


def on_mouse_down(pos):
    global game_state, music_enabled
    if game_state == "menu":
        if Rect((300, 200, 200, 50)).collidepoint(pos):
            start_game()
        elif Rect((300, 300, 200, 50)).collidepoint(pos):
            exit()
        elif Rect((300, 400, 200, 50)).collidepoint(pos):
            music_enabled = not music_enabled
            if music_enabled:
                music.play("music.wav")
            else:
                music.stop()
    elif game_state == "game_over":
        if Rect((300, 400, 200, 50)).collidepoint(pos):
            game_state = "menu"

########## Funções de Inicialização ##########


def start_game():
    global game_state, frames_elapsed, enemies
    game_state = "playing"
    frames_elapsed = 0
    enemies = []
    reset_game()
    if music_enabled:
        music.play("music.wav")


def reset_game():
    global blocks, enemies
    blocks = []
    y_position = HEIGHT
    for _ in range(3):
        x_position = random.randint(60, WIDTH - 60)
        blocks.append(Actor("block-small", (x_position, y_position)))
        y_position -= 150

    first_block = blocks[0]
    player.actor.pos = (first_block.x, first_block.y -
                        first_block.height // 2 - player.actor.height // 2)
    player.vy = 0
    player.is_hit = False
    player.actor.image = "alien-yellow-front"
    enemies = []


def game_over():
    global game_state
    game_state = "game_over"
    player.vy = 0
    music.stop()


pgzrun.go()
