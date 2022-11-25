
from mesa.time import BaseScheduler, RandomActivation, SimultaneousActivation
from mesa.datacollection import DataCollector
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule, CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa import Agent, Model
from mesa.space import MultiGrid
from os import remove
import numpy as np
import random
from mesa.batchrunner import BatchRunner



#Create a 10x10 grid
#Create 10 cars and 3 traffic lights
#Cars will move randomly
#Traffic lights will be stationary
#Cars will stop at traffic lights and wait for them to turn green
#Simulation will run for 50 steps

class Traffic(Model):
    def __init__(self, width, height, traffic_lights, cars):
        self.width = width
        self.height = height
        self.grid = MultiGrid(width, height, True)
        self.schedule = SimultaneousActivation(self)
        self.running = True
        self.datacollector = DataCollector(
            model_reporters={"Cars": "cars", "Traffic Lights": "traffic_lights"},
            agent_reporters={"Car Position": "car_position", "Traffic Light Position": "traffic_light_position"})
        self.cars = cars
        self.traffic_lights = traffic_lights
        self.create_agents()
        self.datacollector.collect(self)

    def create_agents(self):
        for i in range(self.cars):
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            car = Car("C" + str(i), self, (x, y))
            self.schedule.add(car)
            self.grid.place_agent(car, (x, y))
           

            


        for i in range(self.traffic_lights):
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            traffic_light = TrafficLight("T"+ str(i) , self, (x, y))
            self.schedule.add(traffic_light)
            self.grid.place_agent(traffic_light, (x, y))
            
            

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)

class Car(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.car_position = pos
        self.traffic_light_position = None

    def step(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    #AttributeError: 'Car' object has no attribute 'traffic_light_position'
    def distance(self):
        return self.model.grid.get_distance(self.pos, self.traffic_light_position)

        

class TrafficLight(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.traffic_light_position = pos
        self.car_position = None

    def step(self):
        pass

#Create a 10x10 grid
#Create 10 cars and 3 traffic lights
#Cars will move randomly
#Traffic lights will be stationary
#Cars will stop at traffic lights and wait for them to turn green
#Simulation will run for 50 steps

model = Traffic(10, 10, 3, 10)
for i in range(50):
    model.step()


#Run server for visualization

def traffic_draw(agent):
    if type(agent) is Car:
        portrayal = {"Shape": "circle", "Filled": "true", "r": 0.5, "Layer": 0, "Color": "green"}
    elif type(agent) is TrafficLight:
        portrayal = {"Shape": "circle", "Filled": "true", "r": 0.5, "Layer": 0, "Color": "red"}
    return portrayal

#Create chart for visualization of cars and traffic lights

chart = ChartModule([{"Label": "Cars", "Color": "Green"}, {"Label": "Traffic Lights", "Color": "Red"}])

#Create server for visualization

server = ModularServer(Traffic, [CanvasGrid(traffic_draw, 10, 10), chart], "Traffic", {"width": 10, "height": 10, "traffic_lights": 3, "cars": 10})
server.port = 8521
server.launch()
