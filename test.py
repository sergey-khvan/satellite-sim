import pygame
import math
pygame.init()

WIDTH, HEIGHT =  800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Planet Simulation")

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
DARK_GREY = (80, 78, 81)

FONT = pygame.font.SysFont("comicsans", 16)

class Planet:
	AU = 149.6e6 * 1000
	G = 6.67428e-11
	SCALE = 250 / AU  # 1AU = 100 pixels
	TIMESTEP = 3600*24 # 1 day

	def __init__(self, x, y, radius, color, mass):
		self.x = x
		self.y = y
		self.radius = radius
		self.color = color
		self.mass = mass

		self.orbit = []
		self.sun = False
		self.distance_to = 0

		self.x_vel = 0
		self.y_vel = 0

	def draw(self, win):
		x = self.x * self.SCALE + WIDTH / 2
		y = self.y * self.SCALE + HEIGHT / 2

		if len(self.orbit) > 2:
			updated_points = []
			for point in self.orbit:
				x, y = point
				x = x * self.SCALE + WIDTH / 2
				y = y * self.SCALE + HEIGHT / 2
				updated_points.append((x, y))

			pygame.draw.lines(win, self.color, False, updated_points, 2)

		pygame.draw.circle(win, self.color, (x, y), self.radius)
		
		# if not self.sun:
		# 	distance_text = FONT.render(f"{round(self.distance_to/1000, 1)}km", 1, WHITE)
		# 	win.blit(distance_text, (x - distance_text.get_width()/2, y - distance_text.get_height()/2))

	def attraction(self, other):
		other_x, other_y = other.x, other.y
		distance_x = other_x - self.x
		distance_y = other_y - self.y
		distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

		if other.sun:
			self.distance_to = distance

		force = self.G * self.mass * other.mass / distance**2
		theta = math.atan2(distance_y, distance_x)
		force_x = math.cos(theta) * force
		force_y = math.sin(theta) * force
		return force_x, force_y

	def update_position(self, planets):
		total_fx = total_fy = 0
		for planet in planets:
			if self == planet:
				continue

			fx, fy = self.attraction(planet)
			total_fx += fx
			total_fy += fy

		self.x_vel += total_fx / self.mass * self.TIMESTEP
		self.y_vel += total_fy / self.mass * self.TIMESTEP

		self.x += self.x_vel * self.TIMESTEP
		self.y += self.y_vel * self.TIMESTEP
		self.orbit.append((self.x, self.y))

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
        self.angle += math.radians(1)  # Increment the angle by 1 degree (adjust as needed)
        self.x = self.distance * math.cos(self.angle)
        self.y = self.distance * math.sin(self.angle)

    def draw(self, win):
        planet_x = self.planet.x * Planet.SCALE + WIDTH / 2
        planet_y = self.planet.y * Planet.SCALE + HEIGHT / 2

        x = self.x * Planet.SCALE + planet_x
        y = self.y * Planet.SCALE + planet_y

        pygame.draw.circle(win, self.color, (x, y), self.radius)


def connection(win, satellite1, satellite2):
    planet1_x = satellite1.planet.x * Planet.SCALE + WIDTH / 2
    planet1_y = satellite1.planet.y * Planet.SCALE + HEIGHT / 2

    x1 = satellite1.x * Planet.SCALE + planet1_x
    y1 = satellite1.y * Planet.SCALE + planet1_y

    planet2_x = satellite2.planet.x * Planet.SCALE + WIDTH / 2
    planet2_y = satellite2.planet.y * Planet.SCALE + HEIGHT / 2

    x2 = satellite2.x * Planet.SCALE + planet2_x
    y2 = satellite2.y * Planet.SCALE + planet2_y

    pygame.draw.line(win, (255, 255, 255), (x1, y1), (x2, y2), 2)

	    
def main():
    run = True
    clock = pygame.time.Clock()

    sun = Planet(0, 0, 30, YELLOW, 1.98892 * 10**30)
    sun.sun = True

    earth = Planet(-1 * Planet.AU, 0, 16, BLUE, 5.9742 * 10**24)
    earth.y_vel = 29.783 * 1000 
    moon = Satellite(planet=earth, distance=3e10, radius=5, color=RED)
    moon2 = Satellite(planet=earth, distance=3e10, radius=5, color=BLUE, initial_angle=30)

    mars = Planet(-1.524 * Planet.AU, 0, 12, RED, 6.39 * 10**23)
    mars.y_vel = 24.077 * 1000
    mars_s = Satellite(planet=mars, distance=3e10, radius=5, color=RED)

    planets = [sun, earth, mars]
    satellites = [moon, moon2, mars_s]
    
    selected_satellites = [] 
    while run:
        clock.tick(60)
        WIN.fill((0, 0, 0))

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
        

        for planet in planets:
            planet.update_position(planets)
            planet.draw(WIN)
            
        for satellite in satellites:
            satellite.update_position()
            satellite.draw(WIN)
        
        # Clear the window
        WIN.fill((0, 0, 0))
        
        # Draw connections and satellites
        for planet in planets:
            planet.update_position(planets)
            planet.draw(WIN)
        
        for satellite in satellites:
            satellite.update_position()
            satellite.draw(WIN)
        
        for i in range(len(selected_satellites)):
            for j in range(i + 1, len(selected_satellites)):
                connection(WIN, selected_satellites[i], selected_satellites[j])
        
        
        pygame.display.update()

    pygame.quit()

main()