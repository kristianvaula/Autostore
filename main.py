#!/usr/bin/env pybricks-micropython
# Importerer nødvendige bibliotek 
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor, InfraredSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, DataLog
from pybricks.robotics import DriveBase

# ***** INNIT *****
ev3 = EV3Brick()

# ***** MOTORS & SENSORS *****
# Erklærer alle motorer og sensorer 
left_motor = Motor(Port.C)
right_motor = Motor(Port.D)
lifter_motor = Motor(Port.B)
left_line_sensor = ColorSensor(Port.S3)
right_line_sensor = ColorSensor(Port.S4)

# ***** KONSTANTER *****
# BLACK & WHITE er målinger for lysrefleksjon på strek og gulv, er bestemt ved å observere verdiene til sensor
BLACK = 4
WHITE =22
# Fart for robot, løftemotor
DRIVE_SPEED = 100
LIFTER_SPEED = 300
# Andre kostanter
LIFT_POS = 1000
ROBOT_LENGTH = 110
WHEEL_DIAMETER = 55
TOLERANCE = 10
GAIN = 3
# Grenser for å bestemme hva som er tilnærmet strek 
TRIGGER = (BLACK * 2 + TOLERANCE)
HALFTRIGGER = BLACK + TOLERANCE


# ***** ROBOT *****
robot = DriveBase(left_motor, right_motor, WHEEL_DIAMETER, axle_track=90)
robot.settings(DRIVE_SPEED)

# ***** VARIABLER *****
start_angle = deviation = turn_rate = columns_driven = rows_driven = COLUMNS = ROWS = 0

# ***** BOOLS *****
run = False        #Om robot-kjørefunksjon skal gå eller ikke 
product = False    #Om robot har produkt i gaffel
check = True       #Bool for å forhindre løkke å kjøre videre før roboten er ferdig med funksjoner

# ***** CLIENT-FUNCTIONS *****
def stringToLocation(input):    #Konverterer stringinput til koordinater som roboten skal til
    list = input.split(",")
    global COLUMNS,ROWS
    COLUMNS = int(list[0])
    ROWS = int(list[1])

def waitForJob():               #Venter på neste jobb fra serveren
    while not run:
        print("<getJob>")
        INPUT = input()
        stringToLocation(INPUT) 
        wait(1000)
        if len(INPUT) > 1:
            global run
            run = True

#ROBOT-FUNCTIONS
def follow_line(i):             #Følger linje 
    deviation = left_line_sensor.reflection() - right_line_sensor.reflection()  #Forskjell på måling er hvor mye robot skal svinge
    turn_rate = GAIN * deviation                                                #Multipliseres med en gain konstant
    robot.drive(DRIVE_SPEED*i,turn_rate)                                        #Kjører med retning og svingrate

def skip_intersection():             #PASSERER ET KRYSS 
    while (left_line_sensor.reflection() + right_line_sensor.reflection()) < (TRIGGER): # Kjører til forbi krysset
        robot.drive(DRIVE_SPEED,0)
        wait(10)

def turn_function(Angle,Straight):      #SVINGE FUNKSJON - angle PARAMETER -> 90 // 180, straight PARAMETER -> 80 // 0
    if product: 
        turn_sensor = left_line_sensor    #og lese med motsatt sensor 
        turn_direction = -1               #Har robot produkt skal den svinge motsatt vei
    else: 
        turn_sensor = right_line_sensor
        turn_direction = 1

    robot.straight(Straight)               #Kjører avstand mellom sensor og hjul frem 
    wait(10)
    robot.turn((Angle - 45)*turn_direction)#Visst f.eks 90 graders sving: svinger 90-45 grader først
    while (turn_sensor.reflection() > HALFTRIGGER):    #Svinger til sensor finner strek
        robot.drive(0,70*turn_direction)
        wait(10)

def pick(): # FUNKSJON FOR Å PLUKKE OPP PRODUKT 
    start_angle = right_motor.angle()     #Logger hvor mange grader robotens hjul har gjort til nå
    while (left_line_sensor.reflection()+right_line_sensor.reflection()) > (TRIGGER) :
        follow_line(0.5)                  #Følger linje frem til kryss under reol
        wait(10)
    stop_angle = right_motor.angle() - start_angle  #Logger hvor mange grader robotens hjul har gjort i mellomtiden
    robot.stop()
    lift(-1)                                        #Løfter
    distance =  stop_angle * (3.14 * WHEEL_DIAMETER / 360) #Regner ut hvor langt roboten må rygge for å komme tilbake til der den svinget
    robot.straight(-distance)
    turn_function(90,0)                                     #Rygger og svinger tilbake til linje
    global product,check
    product = check = True

def lift(direction):        #Beveger gafflene i en gitt retning
    wait(1000)
    lifter_motor.run_angle(LIFTER_SPEED,direction*LIFT_POS,then=Stop.HOLD,wait=True)
    wait(1000)  

def park_n_drop():          #Droppe av produkt og parkerer
    while (left_line_sensor.reflection()+right_line_sensor.reflection()) > (TRIGGER):   #Finner linje
        follow_line(1)
        wait(10)
    robot.stop()                #Stopper
    lift(1)                     #Senker gaffelen
    global product
    product = False
    robot.straight(-120)        #Rygger
    turn_function(180,0)        #Snur seg 
    while (left_line_sensor.reflection()+right_line_sensor.reflection()) > (TRIGGER):       #Kjører til linje igjen
        follow_line(1)
        wait(10)
    turn_function(90,80)                                                                    #Svinger
    robot.stop()                                                                            #Stoppe 


#RUN 
while True: # Overodnet løkke for å kunne vente på nye oppdrag. 
    if run:
        while run and check:  #Løkke for å utføre oppdrag 
            follow_line(1)
            
            if(left_line_sensor.reflection()+right_line_sensor.reflection()) < (TRIGGER):   #Visst begge sensorer ser svart 
           
                if(columns_driven < COLUMNS): #dersom kolloner er mindre enn det som skal kjøres
                    skip_intersection()
                    columns_driven = columns_driven + 1 

                elif (columns_driven == COLUMNS): #dersom kolloner er lik det som skal kjøres
                    turn_function(Angle=90,Straight=80)
                    columns_driven = columns_driven + 1 

                elif (rows_driven < ROWS): #dersom rader er mindre enn det som skal kjøres
                    skip_intersection()
                    rows_driven = rows_driven + 1 

                elif(rows_driven==ROWS): #dersom rader er lik det som skal kjøres
                    turn_function(Angle=90,Straight=80)
                    rows_driven = rows_driven + 1
                    if product: columns_driven = 0
                
            elif columns_driven == (COLUMNS + 1) and rows_driven == (ROWS + 1):
                if not product:
                    check = False
                    pick()
                    
                elif product: 
                    run = False
                    park_n_drop()
                rows_driven = 0
            wait(10)
            
    else:
        rows_driven = columns_driven = 0
        waitForJob()
