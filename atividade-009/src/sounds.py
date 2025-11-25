from pathlib import Path
import pygame as pg

BASE_PATH = Path(__file__).resolve().parent

SOUNDS_PATH = BASE_PATH.parent / "sounds"


def init_mixer() -> None:
    """Initialize the mixer if it is not initialized yet."""
    if not pg.mixer.get_init():
        pg.mixer.init()


def load_sound(filename: str, volume: float = 1.0) -> pg.mixer.Sound:
    """Load a sound from the global sounds folder and set volume."""
    sound_path = SOUNDS_PATH / filename
    sound = pg.mixer.Sound(sound_path)
    sound.set_volume(volume)
    return sound


# Init mixer and load all sounds
init_mixer()

SHOT = load_sound("fire.wav", volume=0.6)
BREAK_LARGE = load_sound("bangLarge.wav", volume=0.9)
BREAK_MEDIUM = load_sound("bangMedium.wav", volume=0.8)
FLY_BIG = load_sound("flyBig.wav", volume=0.4)
FLY_SMALL = load_sound("flySmall.wav", volume=0.4)
