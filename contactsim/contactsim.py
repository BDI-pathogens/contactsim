#!/usr/bin/env python3

#  Copyright 2024-2025 ContactSim contributors
#  SPDX-License-Identifier: Apache-2.0
#

# This file contains the classes, and a sample app, for the 
# contact simulation

import math
import numpy as np
import pandas as pd

import scipy.stats as stats
import random

class Actor:
    """
    The Actor class represents a person moving in an environment. (More correctly, a mobile device at a consistent location on that person)
    """
    def __init__(self, id, powerTransmitter, gainTransmitter, gainReceiver, deviceModel="model001"):
        """
        Creates a new Actor instance.
        
        Args:
            id:                 str Unique identifier for this Actor
            powerTransmitter:   int This device's Transmisstion Power (TxPower) in dBm (0+)
            gainTransmitter:    int This device's Transmitter Gain (TxGain) in dBm (0+)
            deviceModel:        str The identifier for this model of device (allows analysis across multiple instances)
        """
        self.id = id
        self.powerTx = powerTransmitter # dBm
        self.gainTx = gainTransmitter # dBm
        self.gainRx = gainReceiver # dBm
        self.x = 0 # m
        self.y = 0 # m
        self.angle = 0 # radians
        self.speed = 0 # m/s
        self.included = True
        self.deviceModel = deviceModel
        # Power Receiver is calculated for each actor based on Distance using Friis formula

    def setModel(self,newModel):
        """
        Sets the device model
        
        Args:
            newModel:   str The model name
        """
        self.deviceModel = newModel

    def setPosition(self, newX, newY):
        """
        Sets the 2D position of this device on the simulation grid.

        Args:
            newX:   float x position in the simulation
            newY:   float y position in the simulation
        """
        self.x = newX
        self.y = newY

    def setVelocity(self, newAngleRadians, newSpeed):
        """
        Sets the velocity (speed and direction) of this actor in the sim.

        Args:
            newAngleRadians:    float Direction in radians (not degrees)
            newSpeed:           float Speed in metres per second
        """
        self.angle = newAngleRadians
        self.speed = newSpeed
        # Calculate xDiff and yDiff for a more performant updatePosition function
        self.xComponent = math.cos(self.angle) * self.speed
        self.yComponent = math.sin(self.angle) * self.speed

    def updatePosition(self, secondsElapsed):
        """
        Asks this Actor to update its own position given time elapsed (and its internal state of previous position and velocity).

        Args:
            secondsElapsed: float Seconds elapsed in the simulation since last movement.
        """
        # North is 0 radians (x left to right, y bottom to top, noth upwards/topwards)
        yDiff = self.xComponent * secondsElapsed
        xDiff = self.yComponent * secondsElapsed
        self.x = self.x + xDiff
        self.y = self.y + yDiff
        # return (self.x, self.y)

    # WARNING: Ensure distance > wavelength
    def powerReceiver(self, wavelength, distance, otherPowerTransmitter, otherGainTransmitter):
        """
        Requests a calculation of the 'receive power' for this device (NOT RSSI, strictly speaking) given another transmitting devices txPower and txGain, distance, and wavelength.

        Uses the Friis formula to calculate the expected receiver power. Does not correct for TxPower and does not shape the resultant power into RSSI between 0 and -100/-127)

        Args:
            wavelength:             float Wavelength in Hertz (NOT MHz)
            distance:               float Distance between actors (Transmitter and Receiver) in metres
            otherPowerTransmitter:  float Observed transmitter's Transmission Power (TxPower) in dBm
            otherGainTransmitter:   float Observed transmittier's Transmitter Gain (TxGain) in dBm

        Returns:
            receiverPower:          float Calculated Receiver Power in dBm
        """
        # prioritising readability over raw performance
        # TODO Ensure distance is not <= wavelength (Restriction of Friis formula)
        operand = wavelength / (4 * math.pi * distance)
        return self.gainRx + otherPowerTransmitter + otherGainTransmitter + (20 * math.log10(operand)) # dBm




class Meeting:
    """
    Represents a meeting of 2 or more Actors for a fixed duration. Assumes actors do not move when meeting.
    """
    def __init__(self, startedAtTick, endedAtTick, participantIds):
        """
        Creates a Meeting

        Args:
            startedAtTick:  int The number of 'ticks' in the simulation that past until the meeting started
            endedAtTick:    int The number of 'ticks' in the simulation that past until the meeting ended (NOT the meeting duration)
            participantIds: []str The unique identifiers of the participants in this meeting
        """
        self.start = startedAtTick
        self.end = endedAtTick
        self.participants = participantIds

    def stillMeeting(self, tickNow):
        """
        Determines if the participants are still meeting at the given tick time index in the simulation.
        
        Args:
            tickNow:            int The number of 'ticks' in the simulation that past until now

        Returns:
            areStillMeeting:    boolean True if the meeting is still in progress (Or has exactly just started or just ended)
        """
        return tickNow >= self.start and tickNow <= self.end
    
    def hasParticipant(self, participantId):
        """
        Enquires as to whether the given participantId is present in the meeting (no matter the time index)

        Args:
            participantId:      str The participant's unique string ID in the simulation

        Returns:
            participantPresent: boolean True is the given participantId is present in this meeting (no matter the time index)
        """
        return participantId in self.participants
    
    def duration(self):
        """
        Returns the duration of the meeting in simulation time ticks (NOT seconds)

        Returns:
            meetingDurationTicks:   int The duration of the meeting in simulation time ticks (NOT seconds)
        """
        return self.end - self.start




class Simulation:
    """
    Controller class that manages the overall simulation. The main class you will work with in ContactSim.

    For an example, look at the `examples` folder, or execute this module directly. Output is generated in the `./output` folder.
    """
    def __init__(self, actors, frequency, maxEffectRange, minX, maxX, minY, maxY, meetingDurationMean = 0, meetingDurationSd = 0, meetingDistanceMean = 0, meetingDistanceSd = 0, meetingChance = 0, meetingMaxRange = 3):
        """
        Creates a simulation instance.

        The simulation occurs within a 2D simulation space of interest measured in metres. Think of it like recording wildlife within a 200m square of observation.

        If meeting chance is greater than 0, then the simulation allows meetings of Actors for a time selected from a Gaussian distribution with the requires mean and standard devices in seconds.

        Meetings are only considered within a particular maximum range of human standing positions. A meeting effectively stops these actors from moving at all, maintaining this distance as their meeting distance.
        This is why meeting chance is used - to select the chance for each tick of the simulation, whilst these actors are within the meetingMaxRange, that they will stop at their current distance and meet. Thus the
        chance that they will meet is actually a Bernoulli distribution, with P(have met yet) = meetingChance.

        For examples, see the `examples` folder in the Git repository.

        Limitations in this current version:-
        - Uses a single frequency for the Bluetooth simulation, not the three frequencies actually used by Bluetooth
        - Meetings are pairwise, with meetings only possible between 2 actors that are NOT YET in a meeting
        - Does not yet use a Link Budget calculation to limit whether the signal would have actually been received in real life - uses a fixed meetingMaxRange value instead

        Args:
            actors:                 []Actor An array of Actor objects present at the start of this simulation
            frequency:              float The frequency in Hertz to use in this simulation (NOT Mhz)
            maxEffectRange:         float A hard coded maximum possible detection range in metres (limits infinite range calculations - reduces overall data recorded to that which matters most). Does not effect meeting range
            minX:                   float The simulation square's minimum x value to consider actors within. In metres.
            maxX:                   float The simulation square's maximum x value to consider actors within. In metres.
            minY:                   float The simulation square's minimum y value to consider actors within. In metres.
            maxY:                   float The simulation square's maximum y value to consider actors within. In metres.
            meetingDurationMean:    float (default 0) The mean meeting duration in seconds.
            meetingDurationSd:      float (default 0) The standard deviation of the meeting duration.
            meetingDistanceMean:    float (default 0) The mean meeting distance in metres.
            meetingDistanceSd:      float (default 0) The standard deviation of the meeting distance.
            meetingChange:          float (default 0 - disables meetings) The probability that a meeting will occur at each tick of the simulation, if distance <= meeting distance selected from the distance duration.
            meetingMaxRange:        float (default 3m) The maximum range a human to human meeting can occur, in metres. Does not effect maxEffectRange (which is instead the transmission detection distance).
        """
        self.actors = actors
        self.radioFrequency = frequency
        self.maxRange = maxEffectRange
        c = 2999100 # speed of light at sea level through air in m/s
        self.c = c
        wavelength = c / frequency
        self.wavelength = wavelength # do this conversion once for speed. Use wavelength from now on
        self.time = 0 # seconds
        self.readings = [] # (timeSecond,idReceiver,idTransmitter,powerReceiver)
        self.minX = minX
        self.minY = minY
        self.maxX = maxX
        self.maxY = maxY
        self.meetings = []
        self.meetingDurationMean = meetingDurationMean
        self.meetingDurationSd = meetingDurationSd
        self.meetingDistanceMean = meetingDistanceMean
        self.meetingDistanceSd = meetingDistanceSd
        self.meetingChance = meetingChance
        self.meetingMaxRange = meetingMaxRange

    def addActor(self, newActor):
        """
        Adds an additional actor to the simulation. Useful for adding new actors part way through a simulation.
        
        Args:
            actor:  Actor The new actor instance to add
        """
        self.actors.append(newActor)

    def isInMeeting(self, participantId, tickNow):
        """
        Returns whether the given participant is in a meeting at the specified time (in ticks of the simulation, not seconds)

        Args:
            participantId:  str The unique participant identifier
            tickNow:        int The time within the simulation (in simulation ticks, not seconds)

        Returns:
            isInMeeting:    boolean If the participant is in a meeting
        """
        # TODO use a data structure that makes this much quicker for lookups
        for meeting in self.meetings:
            if meeting.hasParticipant(participantId):
                if meeting.stillMeeting(tickNow):
                    return True
        return False
    
    def getMeeting(self, participantIds):
        """
        Searches for the meeting instance including all of the given participant IDs

        Args:
            participantIds: []str Array of participant unique IDs

        Returns:
            meeting:        Meeting|None Meeting instance or None if none match
        """
        for meeting in self.meetings:
            if sorted(meeting.participants) == sorted(participantIds):
                return meeting
        return None

    def step(self, secondsElapsed):
        """
        Progresses the simulation by a single 'tick' of the given number of seconds.
        
        Args:
            secondsElapsed: float The number of seconds to progress in this tick of the simulation.
        """
        # Increment internal clock
        self.time += secondsElapsed
        # Move each actor 1 step
        remainingActors = []
        for actor in self.actors:
            if actor.included:
                if not self.isInMeeting(actor.id, self.time):
                    actor.updatePosition(secondsElapsed)
                    # Remove them from consideration if out of the effective area (our simulation circle - using a bounding box for now for computational ease)
                    if (actor.x < self.minX) or (actor.x > self.maxX) or (actor.y < self.minY) or actor.y > self.maxY:
                        actor.included = False
                    else:
                        remainingActors.append(actor)
                else:
                    # Keep the ones who are in meetings!
                    remainingActors.append(actor)

        # remainingActors = []
        # for actor in self.actors:
        #     if actor.included:
        #         remainingActors.append(actor)
        self.actors = remainingActors

        # Determine which are inside the area of effect
        for rxIdx,actorRx in enumerate(self.actors):
            for _,actorTx in enumerate(self.actors,start=rxIdx + 1):
                if (actorRx.id != actorTx.id): # and actorRx.included and actorTx.included and 
                    # Calculate mutual distance
                    range = math.sqrt(math.pow(actorRx.x - actorTx.x, 2) + math.pow(actorRx.y - actorTx.y, 2))

                    # Now filtered ones already in meetings
                    # if not self.isInMeeting(actorRx.id,self.time) and not self.isInMeeting(actorTx.id,self.time): # This is computationally expensive


                    # Check meetings are supported
                    if (self.meetingDurationMean > 0) and (range <= self.meetingMaxRange):
                        # Determine if our actors are newly within a meeting
                        # If we have ever met, ignore (we can only meet one)
                        meeting = self.getMeeting([actorRx.id,actorTx.id])
                        if None == meeting:
                            if range <= (self.meetingDistanceMean + (2 * self.meetingDistanceSd)): # minimises compute usage
                                # calculate if we have met yet
                                rnd = random.random()
                                cdf = stats.norm.cdf(x = range, loc = self.meetingDistanceMean, scale = self.meetingDistanceSd) # was 1.0 - 
                                if (rnd * self.meetingChance) > cdf :
                                    # Have met
                                    endTime = int(self.time + stats.norm.rvs(loc = self.meetingDurationMean, scale = self.meetingDurationSd))
                                    if endTime < self.time + 1:
                                        endTime = self.time + 1
                                    self.meetings.append(Meeting(self.time,endTime, [actorRx.id,actorTx.id]))
                                    print(f"Participant {actorRx.id} and {actorTx.id} have met at {self.time} at range {range} with probability {rnd} * { self.meetingChance} > {cdf} for {endTime-self.time}s")
                                else:
                                    # Have not met yet
                                    pass

                    # Ensure distance >= wavelength (Friis formula restriction)
                    if (range <= self.maxRange) and (range >= self.wavelength):
                        # Calculate Free Space Path Loss and Link Budget
                        # fspl = (20 * math.log10(range)) + (20 * math.log10(self.radioFrequency)) + (20 * math.log10((4 * math.pi) / self.c)) # Could save this constant really...
                        # linkBudget = actorTx.powerTx + actorTx.gainTx - fspl - actorRx.gainRx - 1.5 # assume minimal mobile phone receiver power (sensitivity)
                        # maxRange = math.pow(10, linkBudget - actorTx.powerTx + 1.5 - fspl / (20 * math.log(self.radioFrequency)))
                        # print(maxRange)

                        # # Only record the value if the receiver is actually capable of receiving the transmission
                        # if range <= maxRange:

                            # Calculate mutual powerReceiver
                            powerRx = actorRx.powerReceiver(self.wavelength,range,actorTx.powerTx,actorTx.gainTx)

                            # Save value into data store
                            self.readings.append((self.time, actorRx.id, actorTx.id, powerRx, actorRx.deviceModel, actorTx.deviceModel))


def txPowerNamer(actorToName):
    """
    A utility function to name new actors' device model names based on their TxPower. Used by generateActors(). Not intended to be called directly.
    """
    txPower = actorToName.powerTx
    actorToName.setModel(f"model{txPower:03d}")

def noneNamer(actorToName):
    """
    The default none-namer actor device name modeller
    """
    pass

def generateActors(actorCount, meanSpeed, txPowerMethod="fixed", meanTxPower=13, txGainMethod="fixed",meanTxGain=1.5, rxSensitivityMethod="fixed",meanRxSensitivity=1.5, namer = txPowerNamer):
    """
    Utility function to generate a set of actors given some boundary parameters.

    By default, selects txPower, txGain, rxSensitivity (aka rxPower) from a fixed value, but can be set to 'gaussian' to select from a Gaussian (Normal) distribution instead.

    Limitations:
    - Sets all actor speed to a static speed (meanSpeed) rather than selecting from a distribution

    Args:
        actorCount:             int The number of actors to generate
        meanSpeed:              float Mean speed in metres per second (actor speed is fixed for now at this speed)
        txPowerMethod:          str (default: 'fixed') The method used to select each actor's TxPower. Can be 'gaussian'.
        meanTxPower:            float (default: 13) The mean TxPower to select the TxPower from
        txGainMethod:           str (default: 'fixed') The method used to select each actor's TxGain. Can be 'gaussian'.
        meanTxGain:             float (default 1.5) The mean TxGain to select the TxGain from
        rxSensitivityMethod:    str (default: 'fixed') The method used to select each actor's RxSensitivity (aka RxPower). Can be 'gaussian'.
        meanRxSensitivity:      float (default 1.5) The mean RxPower / sensitivity to select the RxPower from
        namer:                  function(Actor) (default txPowerNamer()) The device model namer function

    Returns:
        actorArray:             []Actor An array of Actor instances you can then add to a simulation
    """
    actors = []
    rng = np.random.default_rng()
    facePositionAngles = rng.uniform(0,2.0 * math.pi, actorCount)
    directionAngleDiffs = rng.uniform(0, math.pi, actorCount)

    for i in range(actorCount):
        # Calculate position from the centre of a 200m radius circle
        x = 200.0 * math.sin(facePositionAngles[i])
        y = 200.0 * math.cos(facePositionAngles[i])
        # Calculate direction based on opposite of angle, plus 90 degrees, minus directionAngleDiffs
        angle = facePositionAngles[i] + (1.5*math.pi) - directionAngleDiffs[i]
        speed = meanSpeed # For now, one single speed
        # meanTxPower = 13 # Class 1 BLE is < 20 dBm
        
        # Two choices: Fixed or Gaussian
        txPower = meanTxPower
        txGain = meanTxGain
        rxSensitivity = meanRxSensitivity
        
        if txPowerMethod == "gaussian":
            txPower = rng.normal(meanTxPower, 4)
            if txPower < 0.0:
                txPower = 0.0
            # regularise txPower to an integer
            txPower = int(math.floor(txPower))

        if txGainMethod == "gaussian":
            txGain = rng.normal(meanTxGain, 2)
            if txGain < 0.0:
                txGain = 0.0
            # regularise txGain to an approx power accurate to 0.5 dBm
            txGain = math.floor(txGain*2)/2 # Normalise to nearest 0.5 dBm
        
        if rxSensitivityMethod == "gaussian":
            rxSensitivity = rng.normal(meanRxSensitivity, 2)
            if rxSensitivity < 0.0:
                rxSensitivity = 0.0
            # regularise rxSensitivity to an approx power accurate to 0.5 dBm
            rxSensitivity = math.floor(rxSensitivity*2)/2 # Normalise to nearest 0.5 dBm

        # Create a device model name from this txPower
        # deviceModel = f"model{txPower:03d}"
        newActor = Actor(i + 1, txPower, txGain, rxSensitivity)
        newActor.setPosition(x,y)
        newActor.setVelocity(angle,speed)
        namer(newActor)
        actors.append(newActor)


    return actors

# Example application:-
if __name__ == "__main__":

    actorCount = 30
    stepSizeSeconds = 0.1
    simDurationSeconds = 120
    simRadius = 200
    newActorsPerTimeStep = 2

    simDurationSteps = simDurationSeconds / stepSizeSeconds
    maxSteps = int(simDurationSteps)

    # Create a set of actors and their initial positions
    maxRange = 15 # m max range to bother calculating Receiver power
    frequency = ((2402 + 2426 + 2480) / 3.0) * 1000000 # Bluetooth mean ADVERTISING frequency
    actors = []

    meanSpeed = (3 * 1.60934 * 1000) / (60 * 60) # 3 mph into m/s ~= 1.341m/s

    # set random seed for reproducibility
    np.random.seed(19680801)
    # Generate our initial actors
    actors = generateActors(actorCount, meanSpeed)

    # calculate actors to introduce each time step
    extraActorsCount = newActorsPerTimeStep * maxSteps
    extraActors = generateActors(extraActorsCount, meanSpeed)

    # Run the simulation for 100 seconds at 0.1 second increments (10000 steps)
    sim = Simulation(actors, frequency, maxRange, -simRadius, simRadius,-simRadius,simRadius)
    for i in range(maxSteps):
        print(f"Simulation step {i + 1}, with actor count: {len(sim.actors)}")
        # Add extra actors
        for newActorI in range(newActorsPerTimeStep):
            sim.addActor(extraActors[(i * newActorsPerTimeStep) + newActorI])
        sim.step(stepSizeSeconds)
    # Save the output data
    data = sim.readings
    df = pd.DataFrame(data, columns = ['time','receiverId','transmitterId','receiverPower','receiverDeviceModel','transmitterDeviceModel'])
    print(df)

    # The below takes time because of the use of float_format to make the time look sensible
    df.to_csv("./output/sim-output.csv", index=False) #, float_format='%.3f')