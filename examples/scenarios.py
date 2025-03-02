#!/usr/bin/env python3

#  Copyright 2024-2025 ContactSim Contributors
#  SPDX-License-Identifier: Apache-2.0
#

# This file contains scenarios that exercise the contactsim module.

# Incude the LOCAL contact sim, not the published module (You won't do this in your own files once we publish a module!)
import sys
sys.path.append("..")

import arguably
import numpy as np
import pandas as pd

# import contactsim.contactsim as contactsim
from contactsim.contactsim import generateActors,Simulation


# Declare general defaults now

actorCount = 30
# stepSizeSeconds = 0.1
# simDurationSeconds = 120
stepSizeSeconds = 5
simDurationSeconds = 1200
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



# Now specify explicit scenarios as functions



@arguably.command
def baselineFixedTxPower(meanPower=13):
    """
    This function runs a simulation with each phone TxPower set to a fixed value of 13 dBm

    Args:
        meanPower: int Mean txpower (defaults to 13)
    """

    # Generate our initial actors
    actors = generateActors(actorCount, meanSpeed, txPowerMethod="fixed", meanTxPower=meanPower)

    # calculate actors to introduce each time step
    extraActorsCount = newActorsPerTimeStep * maxSteps
    extraActors = generateActors(extraActorsCount, meanSpeed, txPowerMethod="fixed", meanTxPower=meanPower)

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
    if (meanPower != 13):
        df.to_csv(f"./output/sim-baselineFixedTxPower{meanPower}.csv", index=False) #, float_format='%.3f')
    else:
        df.to_csv("./output/sim-baselineFixedTxPower.csv", index=False) #, float_format='%.3f')



@arguably.command
def baselineGaussianTxPower():
    """
    This function runs a simulation with each phone TxPower set to a gaussian selected from mean=13,sd=4

    Args:
    """
    # Change any standard settings
    simDurationSeconds = 4800
    simDurationSteps = simDurationSeconds / stepSizeSeconds
    maxSteps = int(simDurationSteps)

    # Generate our initial actors
    actors = generateActors(actorCount, meanSpeed, txPowerMethod="gaussian", meanTxPower=13)

    # calculate actors to introduce each time step
    extraActorsCount = newActorsPerTimeStep * maxSteps
    extraActors = generateActors(extraActorsCount, meanSpeed, txPowerMethod="gaussian", meanTxPower=13)

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
    df.to_csv("./output/sim-baselineGaussianTxPower.csv", index=False) #, float_format='%.3f')



@arguably.command
def higherSensitivity(sensitivity=10):
    """
    This function runs a simulation with each phone TxPower set to a gaussian selected from mean=13,sd=4
    but with receive sensitivity (rxGain) set higher, at 10 instead of 1.5.

    Args:
        sensitivity: int The fixed sensitivity to use (defaults to 10)
    """
    # Change any standard settings
    simDurationSeconds = 4800
    simDurationSteps = simDurationSeconds / stepSizeSeconds
    maxSteps = int(simDurationSteps)

    def rxGainNamer(actorToName):
        rx = actorToName.gainRx
        actorToName.setModel(f"modelGainRx{rx:03d}")

    # Generate our initial actors
    actors = generateActors(actorCount, meanSpeed, txPowerMethod="gaussian", meanTxPower=13,
                            rxSensitivityMethod="fixed", meanRxSensitivity=sensitivity, namer=rxGainNamer)

    # calculate actors to introduce each time step
    extraActorsCount = newActorsPerTimeStep * maxSteps
    extraActors = generateActors(extraActorsCount, meanSpeed, txPowerMethod="gaussian", meanTxPower=13,
                            rxSensitivityMethod="fixed", meanRxSensitivity=sensitivity, namer=rxGainNamer)

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
    if (sensitivity != 10):
        df.to_csv(f"./output/sim-higherSensitivity{sensitivity}.csv", index=False)
    else:
        df.to_csv("./output/sim-higherSensitivity.csv", index=False) #, float_format='%.3f')


@arguably.command
def baselineMeetings():
    """
    This function runs a simulation with each phone TxPower set to a gaussian selected from mean=13,sd=4 with meeting mean duration 5 minutes, sd 1 minute, distance of 1.5m sd 0.3m.

    Args:
    """
    # Change any standard settings
    simDurationSeconds = 960 # was 960
    stepSizeSeconds = 1 # was 0.2
    newActorsPerTimeStep = 1
    simDurationSteps = simDurationSeconds / stepSizeSeconds
    maxSteps = int(simDurationSteps)

    maxRange = 50 # was 15
    meetingMaxRange = 2.3 # was 15

    # Generate our initial actors
    actors = generateActors(actorCount, meanSpeed, txPowerMethod="gaussian", meanTxPower=13)

    # calculate actors to introduce each time step
    extraActorsCount = newActorsPerTimeStep * maxSteps
    extraActors = generateActors(extraActorsCount, meanSpeed, txPowerMethod="gaussian", meanTxPower=13)

    # Run the simulation for 100 seconds at 0.1 second increments (10000 steps)
    sim = Simulation(actors, frequency, maxRange, -simRadius, simRadius,-simRadius,simRadius, 
                     meetingDurationMean = 5*60, meetingDurationSd = 2*60, 
                     meetingDistanceMean = 1.5, meetingDistanceSd = 0.3, 
                     meetingChance = 0.9,
                     meetingMaxRange = meetingMaxRange) 
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
    df.to_csv("./output/sim-baselineMeetings.csv", index=False) #, float_format='%.3f')

    # Now sanity check the meetings output of the simulation
    meetingData = []
    for meeting in sim.meetings:
        meetingData.append((len(meeting.participants),meeting.start,meeting.end))
    meetingDf = pd.DataFrame(meetingData, columns = ['participantCount','startTimeSecs','endTimeSecs'])
    meetingDf['durationSecs'] = meetingDf['endTimeSecs'] - meetingDf['startTimeSecs']
    summary = meetingDf.describe()
    print(summary)



# Expose via a main function with helper text
if __name__ == "__main__":
    arguably.run()