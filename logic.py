import pygame
import tkinter as tk
from skyfield.api import load
from astroquery.jplhorizons import Horizons
import math
import numpy as np
from datetime import datetime, timedelta
import time 
import csv

def start_sim(sim_str, end_date):
    pygame.init()

    WHITE = (255, 255, 255)
    YELLOW = (255, 255, 0)
    BLUE = (100, 149, 237)
    RED = (188, 39, 50)
    DARK_GREY = (80, 78, 81)
    SCALE = 200
    FONT = pygame.font.SysFont("comicsans", 16)



    WIDTH, HEIGHT =  800, 800
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Planet Simulation")



    def scale_x(x):
        return x * SCALE + WIDTH/2

    def scale_y(y):
        return y * SCALE + HEIGHT/2
    #region classes
    class Planet:
        def __init__(self, id:int, radius, color):
            self.radius = radius
            self.color = color
            self.planet_id = id
            self.x = 0
            self.y = 0
            
            self.xyz = [0,0,0]
            # self.vxyz = [0,0,0]
            self.surface = []
            for angle in range(0, 360, 10):
                x = self.x + self.radius * math.cos(math.radians(angle))
                y = self.y + self.radius * math.sin(math.radians(angle))
                self.surface.append((scale_x(x), scale_y(y)))
            self.orbit = []
        
        # def update_surface(self):
        #     x = (self.x * SCALE + WIDTH/2)**2 
        #     y = (self.y * SCALE + HEIGHT/2)**2
        #     coordinate = 
            
        def update_position(self, time):
            obj = Horizons(id=self.planet_id, location="@sun", epochs=time.tt).vectors()
            self.xyz = [np.double(obj[xi]) for xi in ['x', 'y', 'z']]
            # self.vxyz = [np.double(obj[vxi]) for vxi in ['vx', 'vy', 'vz']]
            self.x, self.y = self.xyz[0], self.xyz[1]
            self.orbit.append((self.x, self.y))
            
            self.surface = []
            for angle in range(0, 360, 10):
                x = self.x + self.radius * math.cos(math.radians(angle))
                y = self.y + self.radius * math.sin(math.radians(angle))
                self.surface.append((scale_x(x), scale_y(y)))
            
        def draw(self, win):
            x_1 = scale_x(self.x)
            y_1 = scale_y(self.y)
            
            if len(self.orbit) > 2:
                updated_points = []
                for point in self.orbit:
                    x, y = point
                    x = scale_x(x)
                    y = scale_y(y)
                    updated_points.append((x, y))

                pygame.draw.lines(win, self.color, False, updated_points, 2)
            
            pygame.draw.circle(win, self.color, (x_1, y_1), self.radius)
                

    class Satellite:
        def __init__(self, planet, distance, radius, color, initial_angle=0):
            self.planet = planet
            self.distance = distance
            self.radius = radius
            self.color = color
            self.angle = initial_angle
            self.x = 0
            self.y = 0

        def update_position(self):
            self.angle += math.radians(10)  # Increment the angle by 1 degree (adjust as needed)
            self.x = self.distance * math.cos(self.angle)
            self.y = self.distance * math.sin(self.angle)

        def draw(self, win):
            planet_x = scale_x(self.planet.x)
            planet_y = scale_y(self.planet.y)

            x = self.x  + planet_x
            y = self.y  + planet_y

            pygame.draw.circle(win, self.color, (x, y), self.radius)


    def connection(win, satellite1, satellite2):
        planet1_x = scale_x(satellite1.planet.x)
        planet1_y = scale_y(satellite1.planet.y )

        x1 = satellite1.x  + planet1_x
        y1 = satellite1.y  + planet1_y

        planet2_x = scale_x(satellite2.planet.x) 
        planet2_y = scale_y(satellite2.planet.y )

        x2 = satellite2.x + planet2_x
        y2 = satellite2.y + planet2_y

        pygame.draw.line(win, WHITE, (x1, y1), (x2, y2), 2)
        
        return Connection(x1,y1,x2,y2)
            
    class Connection:
        
        def __init__(self,x1,y1,x2,y2):
            self.x1 = x1
            self.x2 = x2
            self.y1 = y1
            self.y2 = y2
    #endregion

    def write_dates(message, date):
        with open('data.csv', 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([message, date])
            


    def main(sim_str, end_date):
        run = True    
        # sim_str = "2018-01-01"
        # end_date = "2020-02-20" 
        ts = load.timescale()
        date_obj = datetime.strptime(sim_str, '%Y-%m-%d')
        t = ts.tt(date_obj.year, date_obj.month, date_obj.day, 0, 0, 0)
        date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        endtime = ts.tt(date_obj.year, date_obj.month, date_obj.day, 0, 0, 0)
        
        sun = Planet(id=10, radius=20, color=YELLOW)
        earth = Planet(id=399, radius = 16, color=BLUE)
        mars = Planet(id=499, radius =12, color = RED)
        planets = [earth, mars]
        
        moon = Satellite(planet=earth, distance=30, radius=5, color=RED)
        moon2 = Satellite(planet=earth, distance=30, radius=5, color=BLUE, initial_angle=30)
        mars_s = Satellite(planet=mars, distance=30, radius=5, color=RED)

        satellites = [moon, moon2, mars_s]
        selected_satellites = []
        connections = []
        while t.tt < endtime.tt and run:
            WIN.fill((0, 0, 0))
            
            sun.draw(WIN)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if a satellite was clicked, and toggle its selection
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    for satellite in satellites:
                        planet_x = satellite.planet.x * Planet.SCALE + WIDTH / 2
                        planet_y = satellite.planet.y * Planet.SCALE + HEIGHT / 2
                        x = satellite.x * Planet.SCALE + planet_x
                        y = satellite.y * Planet.SCALE + planet_y
                        distance = math.sqrt((x - mouse_x)**2 + (y - mouse_y)**2)
                        if distance < satellite.radius * Planet.SCALE:
                            if satellite in selected_satellites:
                                selected_satellites.remove(satellite)
                            else:
                                selected_satellites.append(satellite)
                elif event.type == pygame.KEYDOWN:
                    # Check if keys corresponding to satellite names are pressed
                    key = event.key
                    if key == pygame.K_1:
                        selected_satellites.append(moon)
                    elif key == pygame.K_2:
                        selected_satellites.append(moon2)
                    elif key == pygame.K_3:
                        selected_satellites.append(mars_s)
                    elif key == pygame.K_c:
                        selected_satellites.clear()  # Clear selected satellites
                    elif key == pygame.K_n:
                        write_dates("No Signal", date_str)
                    elif key == pygame.K_y:
                        write_dates("Signal Present", date_str)
            
            for planet in planets:
                planet.update_position(time=t)
                planet.draw(WIN)
            
            for satellite in satellites:
                satellite.update_position()
                satellite.draw(WIN)
            
            for i in range(len(selected_satellites)):
                for j in range(i + 1, len(selected_satellites)):
                    connections.append(connection(WIN, selected_satellites[i], selected_satellites[j]))
            
            # for line in connections:
            #     if (
            #         ((scale_x(sun.x) + sun.radius >= line.x1
            #         and scale_x(sun.x) + sun.radius <= line.x2) 
            #          or (scale_x(sun.x) - sun.radius >= line.x1
            #         and scale_x(sun.x) - sun.radius <= line.x2))
            #         and scale_y(sun.y) >= min(line.y1, line.y2)
            #         and scale_y(sun.y) <= max(line.y1, line.y2)
            #     ):
            #         print("Touch!")
            
            # Date on the screen
            formated_time = t.tt - 2443144.5
            date_obj = datetime(1977, 1, 1) + timedelta(days=formated_time)
            date_str = date_obj.strftime("%d-%m-%Y")
            
            text_surface = FONT.render(date_str, True, WHITE)
            text_rect = text_surface.get_rect()

            # Set the position of the rectangular object
            text_rect.center = (100, 30)
            WIN.blit(text_surface, text_rect)
            pygame.display.update()
            time.sleep(0.03)
            t += timedelta(days=1)
            
    main(sim_str,end_date)
    pygame.quit()
    

root = tk.Tk()
root.title("Planets Simulator")
root.minsize(400, 300)

# Create two input fields
format_label = tk.Label(root, text="Insert the date in format 'year-month-day'")
format_label.pack()
input1_label = tk.Label(root, text="Start date:")
input1_label.pack()
input1_entry = tk.Entry(root)
input1_entry.pack()

input2_label = tk.Label(root, text="End date:")
input2_label.pack()
input2_entry = tk.Entry(root)
input2_entry.pack()

# Create a button that compiles the function with the two inputs
compile_button = tk.Button(root, text="Simulate", command=lambda: start_sim(input1_entry.get(), input2_entry.get()))
compile_button.pack()

root.mainloop()
