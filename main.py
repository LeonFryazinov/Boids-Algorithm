import pygame
import math
import random
import time

#https://vanhunteradams.com/Pico/Animal_Movement/Boids-algorithm.html Massive help


#all vectors and coordinates are expressed as tuples, so doing equations between tuples would be very useful for finding distance between two points

def sum_tuple(a:tuple,b:tuple):
    return (a[0]+b[0],a[1]+b[1])


def sub_tuple(a:tuple,b:tuple):
    return (a[0]-b[0],a[1]-b[1])

def mult_tuple(a:tuple,b:float):
    return (a[0]*b,a[1]*b)




def normalize(vect:tuple): #without changing the direction, scales the magnitude of a vector to 1
    mod = math.sqrt(vect[0]**2+vect[1]**2)
    x = vect[0]/mod
    y = vect[1]/mod
    #print("basically one") if math.sqrt(x**2+y**2) - 1 < 0.1 else print(math.sqrt(x**2+y**2) - 1)  (debug)
    return (x,y)

def find_dist(diff): # finds a distance of a vector, by using pythagoras.
    
    return math.sqrt(diff[0]**2+diff[1]**2)

def calculate_triangle(pos,vel,scale): #calculates the verticies of a triangle that the boids use as a "sprite"
    ang = math.atan2(vel[1],vel[0]) # calculates the direction the boid is facing using trig

    # to figure out the maths behind the point drawing, i used this graphing calculator, where a is the direction, and s is the scale
    # https://www.desmos.com/calculator/qnk8ixnxuq

    p1 = (pos[0]+(scale*math.cos(ang)),(scale*math.sin(ang)+pos[1])) # point 1, if the direction is due north (90 degrees or Pi/2 rad) then this vertex is [scale] pixels away from the origin
    p2 = (pos[0]+(scale*(math.cos(ang-(3*math.pi)/4))),((scale*math.sin(ang-(3*math.pi)/4))+pos[1])) #point 2, a point like p1, but if it was rotated around the center 135 deg (3pi/4 rad) clockwise
    p3 = (pos[0]+(scale*(math.cos(ang+(3*math.pi)/4))),((scale*math.sin(ang+(3*math.pi)/4))+pos[1])) #point 3, a point like p1, but if it was rotated around the center 135 deg (3pi/4 rad) anticlockwise

    points = [p1,p2,p3] #list of points
    return points
    
def rand_pos(bounds): # creates a random position within an area, defined by a rectangle where top left is (0,0) and bottom right is (bounds.x,bounds.y)
    return (random.randint(0,bounds[0]),random.randint(0,bounds[1]))

class Obst: # evil circle, pushes boids away
    def __init__(self,pos,radius) -> None:
        self.pos = pos
        self.radius = radius




class Boid: # boid object
    def __init__(self,pos,init_vel,range,screen_size) -> None: #initialises a boid
        self.pos = pos
        self.velocity = init_vel
        self.range = range
        self.top_speed = find_dist(init_vel)
        self.sep = 1
        self.col = (random.randint(100,255),random.randint(100,255),random.randint(100,255))
        self.screen_size = screen_size

    def get_pos(self): #unused getter function that returns a boids position
        return self.pos
    
    def move(self):
        norm = normalize(self.velocity)
        self.velocity = mult_tuple(norm,self.top_speed) #makes sure that  no matter how i scale a vector, a boid always moves at top speed
            

        self.pos = sum_tuple(self.pos,self.velocity) # adds the velocity to the position every frame.
        
        #code that moves the boid to the other side of the screen
        if self.pos[0] > self.screen_size[0]:
            self.pos = sum_tuple(self.pos,(-self.screen_size[0],0))
        if self.pos[0] < 0:
            self.pos = sum_tuple(self.pos,(self.screen_size[0],0))
        if self.pos[1] > self.screen_size[1]:
            self.pos = sum_tuple(self.pos,(0,-self.screen_size[1]))
        if self.pos[1] < 0:
            self.pos = sum_tuple(self.pos,(0,self.screen_size[1]))
    
    def boids_in_range(self,boid_list): #returns a list of boids in range. 
        #this was added to optimise as I had this block of code in every algorithm function, causing unneeded resource use
        near_boids = []
        for boid in boid_list:
            if boid != self:
                
                other_pos = boid.pos
                diff_vect = sub_tuple(other_pos,self.pos)
                dist = find_dist(diff_vect)
                if dist < self.range:
                    near_boids.append(boid)
        return near_boids
                    

    def separation(self,boid_list,obst_list):
        #boids algorithm involves 3 steps, the first step is separation, makes sure that the boids dont hit each other. (my model is not tuned well, they hit each other sometimes)
        for boid in boid_list:
            other_pos = boid.pos
            diff_vect = sub_tuple(other_pos,self.pos)
            dist = find_dist(diff_vect)
            
            
            x_added =  -self.sep * (diff_vect[0]/dist) #pushes a boid in the x axis based on how close the boid is, for every boid in range
            y_added =  -self.sep * (diff_vect[1]/dist) #pushes a boid in the y axis based on how close the boid is, for every boid in range
            self.velocity = sum_tuple(self.velocity,(x_added,y_added))
        
        # late addition, the user can add their own "obstacles" that will repel the boids, using simiar logic to boid repelling boid
        for obst in obst_list:
            
            other_pos = obst.pos
            diff_vect = sub_tuple(other_pos,self.pos)
            dist = find_dist(diff_vect)
            
            if dist < self.range:
                x_added =  -self.sep * 3 * (diff_vect[0]/dist)
                y_added =  -self.sep  * 3 * (diff_vect[1]/dist)
                self.velocity = sum_tuple(self.velocity,(x_added,y_added))
        
        
        
        #prototype - tried repelling boids from walls, which didnt work that well

        
        #wall_strength = 0.2
        #if self.screen_size[0] - self.pos[0] < self.range:
        #    self.velocity = sum_tuple(self.velocity,(wall_strength*((self.pos[0] - self.screen_size[0])/self.range),0))
        #if self.pos[0]  < self.range:
        #    self.velocity = sum_tuple(self.velocity,(wall_strength*(self.pos[0]/self.range),0))
        #if self.screen_size[1] - self.pos[1] < self.range:
        #    self.velocity = sum_tuple(self.velocity,(0,wall_strength*((self.pos[1] - self.screen_size[1])/self.range)))
        #if self.pos[1]  < self.range:
        #    self.velocity = sum_tuple(self.velocity,(0,wall_strength*(self.pos[1]/self.range)))





    def alignment(self,boid_list):
        #step 2 in boids algorithm is alignment, which will make the boids want to go into a similar direction to the boids around it
        aver_vel = (0,0)
        
        for boid in boid_list:
            aver_vel = sum_tuple(aver_vel,boid.velocity) #sums all the velocities of the boids around it, to figure out where everyone around the boid is going
            
        
        if len(boid_list)  != 0:
            alignment_factor = 0.3 # if the boid has boids in range, it will find the average velocity, then slightly turn towards it.
            aver_vel = mult_tuple(aver_vel,1/len(boid_list))   # dividing the summed velocities by the amount of velocities added, to get average velocity
            added_vel = mult_tuple(sub_tuple(aver_vel,self.velocity),alignment_factor) 
            self.velocity = sum_tuple(self.velocity,added_vel) # adds a fraction of the average velocity to its own velocity.

    def cohesion(self,boid_list):
        #very similar to step 2, in step 3, the boid is trying to go towards the average position of all the boids around it, kind of looping in on the pack. 
        #step 2 and step 3 look a bit messy and buggy in hindsight, might rework later.
        target_point = (0,0)
        
        for boid in boid_list:       
            target_point = sum_tuple(target_point,boid.pos)
            

        if len(boid_list) != 0:
            #finds average position of all boids in range, then goes towards it
            factor = 0.03
            target_point = mult_tuple(target_point,1/len(boid_list))
            self.velocity = sum_tuple(self.velocity,mult_tuple(sub_tuple(target_point,self.pos),factor))



pygame.init()

screen_size = (1920,1080)

screen = pygame.display.set_mode(screen_size)


boid_amount = 100
boid_list = []

for i in range(boid_amount):
    vel = mult_tuple(normalize((random.randrange(1,25,1)/50,random.randrange(1,25,1)/50)),5)
    boid_list.append(Boid(rand_pos(screen_size),vel,100,screen_size)) # creates 100 identical boids
running = True

#variables resposible for drawing of obstacles. 
mouse_pos = (0,0)
placeable_radius = 10
obst_list = []

allow_obstacles = False #set to true if want option to create obstacles

prev_time = time.time()
while running:
    dt = time.time() - prev_time #delta time for debug
    prev_time = time.time()
    screen.fill((0,0,0)) # clear screen every frame so all boids can be redrawn in new positions, cool effect when this line is removed 

    
    
    
    
    for boid in boid_list:
        near_boids = boid.boids_in_range(boid_list)
        boid.separation(near_boids,obst_list)
        boid.alignment(near_boids)
        boid.cohesion(near_boids)
        boid.move()
        points = calculate_triangle(boid.pos,boid.velocity,7)
        pygame.draw.polygon(screen,boid.col,points)
        #pygame.draw.circle(screen,(255,0,0),(boid.pos),100,1) #debug function, that drew the range at which each boid sees
    #print(boid_list[0].pos) (debug)
    #print(1/dt) #FPS display (debug)
    for event in pygame.event.get():
        #if event.type == pygame.KEYDOWN:    # scrapped idea of changing obstacles radius
            #print(event)
            #if event.scancode == 81: # pressed down
            #    if placeable_radius > 5:
            #        placeable_radius -= 1
            #if event.scancode == 82: # pressed up
            #    if placeable_radius < 50:
            #        placeable_radius += 1

        if allow_obstacles:
            if event.type == pygame.MOUSEBUTTONDOWN:
                #print(event)
                if event.button == 1:
                    obst_pos = event.pos
                    obst_list.append(Obst(obst_pos,10))
                #print(event.button)

            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
        
        if event.type == pygame.QUIT:
            running = False
    
    if allow_obstacles: 
        for obst in obst_list:
            pygame.draw.circle(screen,(255,0,0),obst.pos,10)

        pygame.draw.circle(screen,(255,0,0),mouse_pos,placeable_radius)
    
    
    
    
    pygame.display.update()
    

pygame.quit()