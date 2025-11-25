import math
from random import uniform

import pygame as pg

import config as C
import sounds
from sprites import Asteroid, Ship, UFO
from utils import Vec, rand_edge_pos, rand_unit_vec


class World:
    def __init__(self) -> None:
        # Main sprite groups
        self.ship = Ship(Vec(C.WIDTH / 2, C.HEIGHT / 2))
        self.bullets = pg.sprite.Group()
        self.enemy_bullets = pg.sprite.Group()
        self.asteroids = pg.sprite.Group()
        self.ufos = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group()

        self.all_sprites.add(self.ship)

        # Game state
        self.score = 0
        self.lives = C.START_LIVES
        self.wave = 0
        self.wave_cool = C.WAVE_DELAY
        self.safe = C.SAFE_SPAWN_TIME
        self.ufo_timer = C.UFO_SPAWN_EVERY

        # Start first wave
        self.start_wave()

    # Start a new asteroid wave
    def start_wave(self) -> None:
        self.wave += 1
        count = 3 + self.wave
        for _ in range(count):
            pos = rand_edge_pos()
            while (pos - self.ship.pos).length() < 150:
                pos = rand_edge_pos()
            ang = uniform(0, math.tau)
            speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX)
            vel = Vec(math.cos(ang), math.sin(ang)) * speed
            self.spawn_asteroid(pos, vel, "L")

    # Spawn a new asteroid of a given size
    def spawn_asteroid(self, pos: Vec, vel: Vec, size: str) -> None:
        asteroid = Asteroid(pos, vel, size)
        self.asteroids.add(asteroid)
        self.all_sprites.add(asteroid)

    # Spawn a UFO at a random side, aiming at the player (or center)
    def spawn_ufo(self) -> None:
        small = uniform(0, 1) < 0.5

        y = uniform(0, C.HEIGHT)
        x = 0 if uniform(0, 1) < 0.5 else C.WIDTH

        if self.ship.alive:
            target_pos = self.ship.pos
        else:
            target_pos = Vec(C.WIDTH / 2, C.HEIGHT / 2)

        ufo = UFO(Vec(x, y), small, target_pos)

        self.ufos.add(ufo)
        self.all_sprites.add(ufo)

    # Try to fire a bullet from the ship
    def try_fire(self) -> None:
        if len(self.bullets) >= C.MAX_BULLETS:
            return

        bullet = self.ship.fire()
        if bullet is None:
            return

        self.bullets.add(bullet)
        self.all_sprites.add(bullet)

        sounds.SHOT.play()

    # Teleport the ship to a random position
    def hyperspace(self) -> None:
        if not self.ship.alive:
            return

        self.ship.pos.xy = (
            uniform(0, C.WIDTH),
            uniform(0, C.HEIGHT),
        )
        self.ship.vel.xy = (0, 0)

    # Update world state
    def update(self, dt: float, keys: pg.key.ScancodeWrapper) -> None:
        self.ship.control(keys, dt)
        self.all_sprites.update(dt)

        player_pos = self.ship.pos if self.ship.alive else None
        for ufo in self.ufos:
            bullet = ufo.fire(player_pos)
            if bullet:
                self.enemy_bullets.add(bullet)
                self.all_sprites.add(bullet)

        if self.safe > 0:
            self.safe -= dt
            self.ship.invuln = 0.5
        else:
            self.ship.invuln = max(self.ship.invuln - dt, 0.0)

        self.ufo_timer -= dt
        if self.ufo_timer <= 0:
            self.spawn_ufo()
            self.ufo_timer = C.UFO_SPAWN_EVERY

        self.handle_collisions()

        if not self.asteroids and self.wave_cool <= 0:
            self.start_wave()
            self.wave_cool = C.WAVE_DELAY
        elif not self.asteroids:
            self.wave_cool -= dt

    # Handle all collisions between entities
    def handle_collisions(self) -> None:
        # 1. Player bullets vs asteroids
        hits = pg.sprite.groupcollide(
            self.asteroids,
            self.bullets,
            False,
            True,
            collided=lambda a, b: (a.pos - b.pos).length() < a.r,
        )
        for asteroid, _ in hits.items():
            self.split_asteroid(asteroid)

        # 2. Collisions that kill the player
        if self.ship.invuln <= 0 and self.safe <= 0:
            # Player vs asteroids
            for asteroid in self.asteroids:
                dist = (asteroid.pos - self.ship.pos).length()
                if dist < (asteroid.r + self.ship.r):
                    self.ship_die()
                    break

            # Player vs UFOs
            if self.ship.alive:
                for ufo in self.ufos:
                    dist = (ufo.pos - self.ship.pos).length()
                    if dist < (ufo.r + self.ship.r):
                        self.ship_die()
                        break

            # Player vs enemy bullets
            if self.ship.alive:
                hits = pg.sprite.spritecollide(
                    self.ship,
                    self.enemy_bullets,
                    True,
                    collided=pg.sprite.collide_circle,
                )
                if hits:
                    self.ship_die()

        # 3. Player bullets vs UFOs
        for ufo in list(self.ufos):
            for bullet in list(self.bullets):
                dist = (ufo.pos - bullet.pos).length()
                if dist < (ufo.r + bullet.r):
                    score = (
                        C.UFO_SMALL["score"]
                        if ufo.small
                        else C.UFO_BIG["score"]
                    )
                    self.score += score
                    ufo.kill()
                    bullet.kill()

        # 4. UFOs vs asteroids
        crashes = pg.sprite.groupcollide(
            self.ufos,
            self.asteroids,
            True,
            False,
            collided=lambda u, a: (u.pos - a.pos).length() < (u.r + a.r),
        )

        for ufo, asteroids_hit in crashes.items():
            if hasattr(ufo, "channel") and ufo.channel:
                ufo.channel.stop()

            for asteroid in asteroids_hit:
                self.split_asteroid(asteroid)

    # Split an asteroid into smaller ones and update score
    def split_asteroid(self, asteroid: Asteroid) -> None:
        if asteroid.size == "L":
            sounds.BREAK_LARGE.play()
        else:
            sounds.BREAK_MEDIUM.play()

        self.score += C.AST_SIZES[asteroid.size]["score"]
        split_sizes = C.AST_SIZES[asteroid.size]["split"]

        pos = Vec(asteroid.pos)
        asteroid.kill()

        for size in split_sizes:
            dirv = rand_unit_vec()
            speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX) * 1.2
            self.spawn_asteroid(pos, dirv * speed, size)

    # Handle ship death and respawn / reset
    def ship_die(self) -> None:
        if not self.ship.alive:
            return

        sounds.BREAK_LARGE.play()

        self.lives -= 1
        self.ship.alive = False

        if self.lives >= 0:
            self.ship.pos.xy = (C.WIDTH / 2, C.HEIGHT / 2)
            self.ship.vel.xy = (0, 0)
            self.ship.angle = -90.0
            self.ship.invuln = C.SAFE_SPAWN_TIME
            self.safe = C.SAFE_SPAWN_TIME
            self.ship.alive = True
        else:
            self.__init__()

    # Draw all sprites and HUD
    def draw(self, surf: pg.Surface, font: pg.font.Font) -> None:
        for spr in self.all_sprites:
            spr.draw(surf)

        pg.draw.line(
            surf,
            (60, 60, 60),
            (0, 50),
            (C.WIDTH, 50),
            width=1,
        )

        txt = f"SCORE {self.score:06d}   LIVES {self.lives}   WAVE {self.wave}"
        label = font.render(txt, True, C.WHITE)
        surf.blit(label, (10, 10))
