from contextlib import redirect_stderr
from turtle import speed
import arcade
import math
import random

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
SCREEN_TITLE = "space shooter"

PLAYER_SCALE = 0.3
PLAYER_SPEED = 5
PLAYER_TURN_SPEED = 3
PLAYER_SHOOT_COOLDOWN = 0.2


BULLET_SPEED = 10
BULLET_SCALE = 0.8

ENEMY_SPAWN_RATE = 1
ENEMY_SPEED_MAX = 3
ENEMY_SPEED_MIN = 3
ENEMY_SCALE = 0.3

ENEMY_TYPES = ["normal", "shooter"]
ENEMY_SHOOT_COOLDOWN = 2.0
ENEMY_BULLET_SPEED = 5
ENEMY_BULLET_COLOR = arcade.color.RED

PARTICLE_COUNT = 5
PARTICLE_SPEED = 3
PARTICLE_FADE_RATE = 8


class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.type = power_type
        self.radius = 20
        self.speed_y = -1

        if power_type == "rapid_fire":
            self.color = arcade.color.CYAN
        elif power_type == "shield":   
            self.color = arcade.color.BLUE
        else:
            self.color = arcade.color.GREEN

    def update(self):
        self.y += self.speed_y

    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.radius, self.color)
        if self.type == "rapid_fire":
            arcade.draw_text("⚡", self.x - 6, self.y - 6, arcade.color.WHITE, 12)
        elif self.type == "shield":
            arcade.draw_text("❤️", self.x - 6, self.y - 6, arcade.color.WHITE, 12)
        else:
            arcade.draw_text("💛", self.x - 6, self.y - 6, arcade.color.WHITE, 12)                   
    

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.uniform(2, 6)
        self.color = random.choice([
             arcade.color.YELLOW,
             arcade.color.ORANGE,
             arcade.color.RED
        ])
        self.speed_x = random.uniform(-PARTICLE_SPEED, PARTICLE_SPEED)
        self.speed_y = random.uniform(-PARTICLE_SPEED, PARTICLE_SPEED)
        self.alpha = 255

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.alpha -= PARTICLE_FADE_RATE
        return self.alpha > 0

    def draw(self):
        r, g, b, _ = self.color 
        color_with_alpha = (r, g, b, int(self.alpha))
        
        arcade.draw_circle_filled(
            center_x=self.x,
            center_y=self.y,
            radius=self.size,
            color=color_with_alpha
        )    


class EnemyBullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = ENEMY_BULLET_SPEED
        self.radius = 6
        self.color = ENEMY_BULLET_COLOR

    def update(self):
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed

    def draw (self):
        arcade.draw_circle_filled(
            self.x, self.y, self.radius, arcade.color.YELLOW
        )    

class Enemy:
    def __init__(self):
        side = random.choice(["top", "right", "bottom", "left"])
        if side == "top":
            self.x = random.uniform(0, SCREEN_WIDTH)
            self.y = SCREEN_HEIGHT + 20
        elif side == "right":
            self.x = SCREEN_WIDTH + 20
            self.y = random.uniform(0, SCREEN_HEIGHT)
        elif side == "bottom":
            self.x = random.uniform(0, SCREEN_WIDTH)
            self.y = -20
        else:
            self.x = -20
            self.y = random.uniform(0, SCREEN_HEIGHT)

        self.enemy_type = random.choice(ENEMY_TYPES)   
        self.speed = random.uniform(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)
        self.angle = 0
        self.radius = 40 * ENEMY_SCALE
        self.health = 3
        self.max_health = 3
        self.shoot_cooldown = 0


    def draw(self):

        if self.enemy_type == "shooter":
            color = arcade.color.RED
        else:
            color = arcade.color.BLUE

        arcade.draw_triangle_filled(
            self.x + math.cos(math.radians(self.angle)) * self.radius * 2,
            self.y + math.sin(math.radians(self.angle)) * self.radius * 2,
            self.x + math.cos(math.radians(self.angle + 140)) * self.radius,
            self.y + math.sin(math.radians(self.angle + 140)) * self.radius,
            self.x + math.cos(math.radians(self.angle - 140)) * self.radius,
            self.y + math.sin(math.radians(self.angle - 140)) * self.radius,
            color

        )

    def take_damage(self):
        self.health -= 1
        return self.health <= 0
    
    def update(self, player_x, player_y, delta_time):
        dx = player_x - self.x
        dy = player_y - self.y
        self.angle = math.degrees(math.atan2(dy, dx))

        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed

        if self.enemy_type == "shooter":
            self.shoot_cooldown -= delta_time

    def shoot(self):
        if self.enemy_type == "shooter" and self.shoot_cooldown <= 0:
            bullet_x = self.x + \
                math.cos(math.radians(self.angle)) * self.radius
            bullet_y = self.y + \
                math.sin(math.radians(self.angle)) * self.radius
            self.shoot_cooldown = ENEMY_SHOOT_COOLDOWN
            return EnemyBullet(bullet_x, bullet_y, self.angle)
        return None

    def draw_health_bar(self):
        if self.health < self.max_health:
            bar_width = 40
            bar_height = 5
            health_percentage = self.health / self.max_health
            health_width = health_percentage * bar_width

            bar_x = self.x
            bar_y = self.y + self.radius + 30

            arcade.draw_rect_filled(
                arcade.XYWH(bar_x, bar_y, bar_width, bar_height), arcade.color.RED
            )
            arcade.draw_rect_filled(
                arcade.XYWH(bar_x - (bar_width - health_width) / 2, bar_y,
                                         health_width, bar_height), arcade.color.GREEN)
            arcade.draw_rect_outline(
                arcade.XYWH(bar_x, bar_y, bar_width, bar_height), arcade.color.WHITE,
                border_width=1
            )
            
    def is_off_screen(self):
        return (self.x < -50 or self.x > SCREEN_WIDTH + 50 or
                self.y < -50 or self.y > SCREEN_HEIGHT + 50)  

class BossBullet:
    def __init__(self, x, y, angle, is_big=False):
        self.x = x
        self.y = y
        self.angle = angle
        self.is_big = is_big
        self.speed = 7
        self.damage = 999 if is_big else 30

        if is_big:
            self.radius = 12
            self.color = arcade.color.YELLOW
        else:
            self.radius = 6
            self.color = arcade.color.ORANGE_RED

    def update(self):
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed

    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.radius, self.color)

    def is_off_screen(self):
        return(self.x < 0 or self.x > SCREEN_WIDTH or
               self.y < 0 or self.y > SCREEN_HEIGHT)
    


class Boss:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2 + random.uniform(-200, 200)
        self.y = SCREEN_HEIGHT + 100

        self.speed = 2
        self.angle = 0
        self.radius = 150 * ENEMY_SCALE * 3
        self.health = 100
        self.max_health = 100

        self.normal_shoot_cooldown = 0
        self.big_shoot_cooldown = 0
        self.damage_flash_timer = 0
        self.flashing = False

        self.color = arcade.color.ORANGE

    def take_damage(self):
        self.health -= 1
        self.damage_flash_timer = 0.3
        self.flashing = True
        return self.health <= 0
    
    def update(self, player_x, player_y, delta_time):
        dx = player_x - self.x
        dy = player_y - self.y
        self.angle = math.degrees(math.atan2(dy, dx))

        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed

        self.normal_shoot_cooldown -= delta_time
        self.big_shoot_cooldown -= delta_time

        if self.flashing:
           self.damage_flash_timer -= delta_time
           if self.damage_flash_timer <= 0:
               self.flashing = False

    def shoot_normal(self):
        if self.normal_shoot_cooldown <= 0:
            bullet_x = self.x + \
                math.cos(math.radians(self.angle)) * self.radius
            bullet_y = self.y + \
                math.sin(math.radians(self.angle)) * self.radius
            self.normal_shoot_cooldown = 1.5
            return BossBullet(bullet_x, bullet_y, self.angle, is_big=False)
        return None
    
    def shoot_big(self):
        if self.big_shoot_cooldown <= 0:
            bullet_x = self.x + \
                math.cos(math.radians(self.angle)) * self.radius
            bullet_y = self.y + \
                math.sin(math.radians(self.angle)) * self.radius
            self.big_shoot_cooldown = 8.0
            return BossBullet(bullet_x, bullet_y, self.angle, is_big=True)
        return None

    def draw(self):
        if self.flashing:
            draw_color = arcade.color.WHITE
        else:
            draw_color = self.color

        points = [
            (self.x + math.cos(math.radians(self.angle)) * self.radius * 1.5,
             self.y + math.sin(math.radians(self.angle)) * self.radius * 1.5),
            (self.x + math.cos(math.radians(self.angle + 90)) * self.radius,
             self.y + math.sin(math.radians(self.angle + 90)) * self.radius),
            (self.x + math.cos(math.radians(self.angle + 180)) * self.radius * 1.5,
             self.y + math.sin(math.radians(self.angle + 180)) * self.radius * 1.5),
            (self.x + math.cos(math.radians(self.angle + 270)) * self.radius,
             self.y + math.sin(math.radians(self.angle + 270)) * self.radius)
        ]
        arcade.draw_polygon_filled(points, draw_color)

    def draw_health_bar(self):
        bar_width = 200
        bar_height = 15
        health_percentage = self.health / self.max_health
        health_width = health_percentage * bar_width

        bar_x = self.x
        bar_y = self.y + self.radius + 40

        arcade.draw_rect_filled(
            arcade.XYWH(bar_x, bar_y, bar_width, bar_height), arcade.color.RED)

        if health_percentage > 0.7:
            health_color = arcade.color.GREEN
        elif health_percentage > 0.4:
            health_color = arcade.color.YELLOW
        else:
            health_color = arcade.color.RED

        arcade.draw_rect_filled(
            arcade.XYWH(bar_x - (bar_width - health_width) / 2, bar_y, health_width, bar_height), health_color
        )

        arcade.draw_rect_outline(
            arcade.XYWH(bar_x, bar_y, bar_width, bar_height), arcade.color.WHITE, 2
        )

        arcade.draw_text(f"BOSS HP: {self.health}/{self.max_health}",
                        bar_x - 80, bar_y + 25, arcade.color.WHITE, 12)
        
    def is_off_screen(self):
        return (self.x < -100 or self.x > SCREEN_WIDTH + 100 or
                self.y <-100 or self.y > SCREEN_HEIGHT + 100)

class Bullet:
    def __init__(self,x,y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = BULLET_SPEED
        self.radius = 5 * BULLET_SCALE

    def update(self):
            self.x += math.cos(math.radians(self.angle)) * self.speed
            self.y += math.sin(math.radians(self.angle)) * self.speed

    def draw(self):
        arcade.draw_circle_filled(
            self.x, self.y, self.radius, arcade.color.YELLOW)
        
    def is_off_screen(self):
        return (self.x < 0 or self.x > SCREEN_WIDTH or
                self.y < 0 or self.y > SCREEN_HEIGHT)
    

class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH,SCREEN_HEIGHT,SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)

        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT // 2
        self.player_angle = 0
        self.player_radius = 150 * PLAYER_SCALE

        self.boss = None
        self.boss_bullets = []
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.shoot_cooldown = 0
        self.enemy_spawn_timer = 0
        self.health = 100
        self.game_over = False
        self.score = 0

        self.keys_pressed = set()
        self.powerups = []
        self.rapid_fire_timer = 0

    def on_draw(self):
        self.clear()
        if self.game_over:
            arcade.draw_text("GAME OVER - Press 'R' to Restart", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.color.RED, 30, anchor_x="center")
            return
        
        if self.boss:
            self.boss.draw()
            self.boss.draw_health_bar()
        for bigbullet in self.boss_bullets:
            bigbullet.draw()
        
        for enemy in self.enemies:
            enemy.draw()
            enemy.draw_health_bar()

        arcade.draw_triangle_filled(
           self.player_x + 
           math.cos(math.radians(self.player_angle)) * 
           self.player_radius * 1.5,
           self.player_y + 
           math.sin(math.radians(self.player_angle)) * 
           self.player_radius * 1.5,
           self.player_x + 
           math.cos(math.radians(self.player_angle + 150)) * 
           self.player_radius,
           self.player_y + 
           math.sin(math.radians(self.player_angle + 150)) * 
           self.player_radius,
           self.player_x + 
           math.cos(math.radians(self.player_angle - 150)) * 
           self.player_radius,
           self.player_y + 
           math.sin(math.radians(self.player_angle - 150)) * 
           self.player_radius,
           arcade.color.WHITE
        )

        for bullet in self.bullets:
            bullet.draw()
        for enemybullet in self.enemy_bullets:
            enemybullet.draw()

        for powerup in self.powerups:
            powerup.draw()

        arcade.draw_text(f"Score: {self.score} Health: {self.health}", 10, 10, arcade.color.WHITE, 16)    
            


    def on_update(self, delta_time):
        self.shoot_cooldown -= delta_time

        self.enemy_spawn_timer -= delta_time

        if arcade.key.SPACE in self.keys_pressed:
            self.shoot()

        if self.enemy_spawn_timer <= 0:
            self.enemies.append(Enemy())
            self.enemy_spawn_timer = ENEMY_SPAWN_RATE    

        if arcade.key.W in self.keys_pressed:
            self.player_y += PLAYER_SPEED
        if arcade.key.S in self.keys_pressed:
            self.player_y -= PLAYER_SPEED
        if arcade.key.A in self.keys_pressed:
            self.player_x -= PLAYER_SPEED
        if arcade.key.D in self.keys_pressed:
            self.player_x += PLAYER_SPEED    

        self.player_x = max(self.player_radius, min(
            SCREEN_WIDTH - self.player_radius, self.player_x))
        self.player_y = max(self.player_radius, min(
            SCREEN_HEIGHT - self.player_radius, self.player_y))
        
        #player bullet update
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
        
        #enemy bullet update
        for enemybullet in self.enemy_bullets[:]:
            enemybullet.update()
            dist = math.hypot(enemybullet.x - self.player_x, enemybullet.y - self.player_y)
            if dist < 15:
                self.health -= 10
                if enemybullet in self.enemy_bullets: self.enemy_bullets.remove(enemybullet)
            elif enemybullet.x < 0 or enemybullet.x > SCREEN_WIDTH: self.enemy_bullets.remove(enemybullet)            
        
        # Enemy update and shooting
        for enemy in self.enemies[:]:
            enemy.update(self.player_x, self.player_y, delta_time)
            
            enemybullet = enemy.shoot()
            if enemybullet: 
                self.enemy_bullets.append(enemybullet)

            # Player vs Enemy collision
            distance = math.hypot(enemy.x - self.player_x, enemy.y - self.player_y)

            if distance < enemy.radius + self.player_radius:
                self.health -= 10
                self.enemies.remove(enemy)
                if self.health <= 0:
                    self.game_over = True

            elif enemy.is_off_screen():
                self.enemies.remove(enemy)

        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                distance = math.hypot(bullet.x - enemy.x, bullet.y - enemy.y)

                if distance < bullet.radius + enemy.radius:
                    #Enemy called remove ki jagha pe take_damage() call kia he
                    if enemy.take_damage():
                        self.enemies.remove(enemy)
                        self.score += 10

                        # Spawn powerup logic
                    if random.random() < 0.2: # 20% chance
                        power_type = random.choice(["rapid_fire", "shield", "health"])
                        self.powerups.append(PowerUp(enemy.x, enemy.y, power_type))

                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break          
        if self.score >= 210 and self.boss is None:
            self.boss = Boss()

        if self.boss:
            self.boss.update(self.player_x, self.player_y, delta_time)

            # Boss bullets
            normalbullet = self.boss.shoot_normal()
            if normalbullet: self.enemy_bullets.append(normalbullet)

            bigbullet = self.boss.shoot_big()
            if bigbullet : self.enemy_bullets.append(bigbullet)
        
        # boss ke sath bullet collison (isse if ke andar rakha he kiu ki crash na ho)
        if self.boss:
            for bullet in self.bullets[:]:
              distance = math.hypot(bullet.x - self.boss.x, bullet.y - self.boss.y)
              
              if distance < self.boss.radius:
                if self.boss.take_damage():
                    self.boss = None #boss is dead
                    self.score += 500
                
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                break

        # Powerup update and collision
        for powerup in self.powerups[:]:
            powerup.update()
            
            # Remove if off screen
            if powerup.y < -50:
                self.powerups.remove(powerup)
                continue

            # Player collision
            distance = math.hypot(powerup.x - self.player_x, powerup.y - self.player_y)
            if distance < powerup.radius + self.player_radius:
                if powerup.type == "rapid_fire":
                    self.rapid_fire_timer = 5.0 # 5 seconds of rapid fire
                elif powerup.type == "shield":
                    self.health = min(100, self.health + 20) # Simple shield: heal 20
                elif powerup.type == "health":
                    self.health = min(100, self.health + 50) # Heal 50
                
                self.powerups.remove(powerup)

        # Handle rapid fire timer
        if self.rapid_fire_timer > 0:
            self.rapid_fire_timer -= delta_time

    def shoot(self):
        if self.shoot_cooldown <= 0:
            bullet_x = self.player_x + \
                math.cos(math.radians(self.player_angle)) * self.player_radius
            bullet_y = self.player_y + \
                math.sin(math.radians(self.player_angle)) * self.player_radius
            self.bullets.append(Bullet(bullet_x, bullet_y, self.player_angle))
            
            # Apply rapid fire effect
            cooldown = PLAYER_SHOOT_COOLDOWN
            if self.rapid_fire_timer > 0:
                cooldown /= 4 # 4x faster firing speed
            
            self.shoot_cooldown = cooldown
        
    def on_key_press(self, symbol, modifiers):
        self.keys_pressed.add(symbol)

        if symbol == arcade.key.R and self.game_over:
            self.restart_game()

    def on_key_release(self, symbol, modifiers):
        if symbol in self.keys_pressed:
            self.keys_pressed.remove(symbol)

    def on_mouse_motion(self, x, y, dx, dy):
        dx = x - self.player_x
        dy = y - self.player_y
        self.player_angle = math.degrees(math.atan2(dy,dx))

    def on_mouse_pressed(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
         self.shoot()

    def restart_game(self):
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT // 2
        self.player_angle = 0
        self.bullets.clear()
        self.enemy_bullets.clear()
        self.enemies.clear()
        self.score = 0
        self.health = 100
        self.game_over = False



    
        


def main():
    window = GameWindow()
    arcade.run()


if __name__ == "__main__":
    main()


