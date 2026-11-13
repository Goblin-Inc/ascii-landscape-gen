import os
import shutil
import random
import math
import time

class ASCIIRenderer:
    def __init__(self):
        self.width, self.height = shutil.get_terminal_size((80, 24))
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def generate_smooth_ridge(self, base_height, roughness, frequency):
        """ Генерирует плавный хребет с помощью наложения синусоид """
        ridge = []
        # Случайный сдвиг фазы, чтобы горы каждый раз были разными
        seed1 = random.uniform(0, 100)
        seed2 = random.uniform(0, 100)
        
        for x in range(self.width):
            # Большая плавная волна
            wave1 = math.sin(x * frequency + seed1) * roughness
            # Маленькая волна для детализации скал
            wave2 = math.sin(x * (frequency * 3) + seed2) * (roughness * 0.3)
            
            h = int(base_height + wave1 + wave2)
            # Ограничиваем, чтобы не вылезти за экран
            ridge.append(max(1, min(h, self.height - 2)))
        return ridge

    def draw_landscape(self):
            canvas = [[" " for _ in range(self.width)] for _ in range(self.height)]
            
            # 1. Генерируем звездное небо
            for y in range(self.height // 2): # Звезды только в верхней половине
                for x in range(self.width):
                    if random.random() < 0.03: # 3% шанс спавна звезды
                        canvas[y][x] = random.choice(["*", "."])
                        
            # Рисуем луну в случайном месте на небе
            moon_x = random.randint(5, self.width - 10)
            moon_y = random.randint(2, 4)
            if moon_x < self.width and moon_y < self.height:
                canvas[moon_y][moon_x] = "("
                canvas[moon_y][moon_x+1] = ")"

            # 2. Настройка слоев гор (символ, базовая_высота, амплитуда, частота)
            layers = [
                (".", 14, 3, 0.03),   # Задний план — теперь высоко и плавно
                ("%", 11, 4, 0.07),   # Средний план — чуть пониже
                ("#", 7, 5, 0.12)     # Передний план — уходит вниз, открывая обзор назад
            ]
            
            for fill_char, base_y, roughness, freq in layers:
                ridge = self.generate_smooth_ridge(base_y, roughness, freq)
                
                for x in range(self.width):
                    mountain_height = ridge[x]
                    for y in range(self.height):
                        current_y_from_bottom = self.height - 1 - y
                        
                        if current_y_from_bottom < mountain_height:
                            # Если это самый верхний пиксель горы — делаем красивую кромку
                            if current_y_from_bottom == mountain_height - 1:
                                # Смотрим на соседнюю точку, чтобы понять, куда идет склон
                                next_h = ridge[min(x + 1, self.width - 1)]
                                if next_h > mountain_height:
                                    canvas[y][x] = "/"
                                elif next_h < mountain_height:
                                    canvas[y][x] = "\\"
                                else:
                                    canvas[y][x] = "_"
                            else:
                                canvas[y][x] = fill_char
                                
            return canvas

    def render(self, canvas):
        output = "\n".join("".join(row) for row in canvas)
        print(output, end="")

if __name__ == "__main__":
    renderer = ASCIIRenderer()
    
    # Генерируем один стабильный ландшафт, чтобы горы не прыгали каждую секунду
    canvas_base = renderer.draw_landscape()
    
    # Список для падающих звезд: [[y, x], [y, x]]
    shooting_stars = []
    
    print("Запуск анимации... Для выхода нажмите Ctrl+C")
    time.sleep(1)

    try:
        while True:
            # Обновляем размеры терминала на лету
            renderer.width, renderer.height = shutil.get_terminal_size((80, 24))
            
            # Копируем базовый ландшафт, чтобы не портить оригинал звездами
            frame = [row[:] for row in canvas_base]
            
            # 1. Добавляем динамическое мерцание обычных звезд
            for y in range(renderer.height // 2):
                for x in range(renderer.width):
                    if frame[y][x] == "*":
                        # 20% шанс, что звезда на этом кадре станет тусклой точкой
                        if random.random() < 0.2:
                            frame[y][x] = "."
                    elif frame[y][x] == ".":
                        # И наоборот — тусклая станет яркой
                        if random.random() < 0.05:
                            frame[y][x] = "*"

            # 2. Шанс спавна новой падающей звезды (метеора)
            if random.random() < 0.03 and len(shooting_stars) < 2:
                # Спавним в случайном месте вверху слева
                start_x = random.randint(0, renderer.width // 2)
                start_y = random.randint(1, renderer.height // 4)
                shooting_stars.append([start_y, start_x])

            # 3. Двигаем и рисуем падающие звезды
            active_stars = []
            for star in shooting_stars:
                y, x = star
                if y < renderer.height and x < renderer.width:
                    # Рисуем ядро метеора и его хвост
                    frame[y][x] = "O"
                    if x > 0 and y > 0: frame[y-1][x-1] = "\\"
                    if x > 1 and y > 1: frame[y-2][x-2] = "."
                    
                    # Двигаем по диагонали вниз-вправо
                    active_stars.append([y + 1, x + 2])
            shooting_stars = active_stars

            # Рендерим готовый кадр
            renderer.clear_screen()
            renderer.render(frame)
            
            # Задержка кадра (FPS ~10 кадров в секунду)
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        renderer.clear_screen()
        print("\nАнимация остановлена. Выход.")