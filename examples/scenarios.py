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
from contactsim.animation import animateActorsOverTime

import matplotlib.pyplot as plt

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
def baselineFixedTxPower(meanPower=13,*,animate=False):
    """
    This function runs a simulation with each phone TxPower set to a fixed value of 13 dBm

    Args:
        meanPower: int Mean txpower (defaults to 13)
        animate: [-a] Boolean Whether to show a movement animation (Defaults to False)
    """

    # Generate our initial actors
    actors = generateActors(actorCount, meanSpeed, txPowerMethod="fixed", meanTxPower=meanPower)

    # calculate actors to introduce each time step
    extraActorsCount = newActorsPerTimeStep * maxSteps
    extraActors = generateActors(extraActorsCount, meanSpeed, txPowerMethod="fixed", meanTxPower=meanPower)

    # Run the simulation for 100 seconds at 0.1 second increments (10000 steps)
    sim = Simulation(actors, frequency, maxRange, -simRadius, simRadius,-simRadius,simRadius,recordPositions=animate)
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
        if animate:
            animateActorsOverTime(sim.getActorStatesOverTimeAsDataFrame(),f"./output/sim-baselineFixedTxPower{meanPower}.mp4")
    else:
        df.to_csv("./output/sim-baselineFixedTxPower.csv", index=False) #, float_format='%.3f')
        if animate:
            animateActorsOverTime(sim.getActorStatesOverTimeAsDataFrame(),"./output/sim-baselineFixedTxPower.mp4")




@arguably.command
def baselineGaussianTxPower(*,animate=False):
    """
    This function runs a simulation with each phone TxPower set to a gaussian selected from mean=13,sd=4

    Args:
        animate: [-a] Whether to generate an animate (Default: False)
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
    sim = Simulation(actors, frequency, maxRange, -simRadius, simRadius,-simRadius,simRadius,recordPositions=animate)
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
    if animate:
        animateActorsOverTime(sim.getActorStatesOverTimeAsDataFrame(),"./output/sim-baselineGaussianTxPower.mp4")



@arguably.command
def higherRxGain(rxGain=10,*,animate=False):
    """
    This function runs a simulation with each phone TxPower set to a gaussian selected from mean=13,sd=4
    but with receive gain (rxGain) set higher, at 10 instead of 1.5.

    Args:
        rxGain: int The fixed rxGain to use (defaults to 10)
        animate: [-a] Whether to generate an animate (Default: False)
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
                            rxGainMethod="fixed", meanRxGain=rxGain, namer=rxGainNamer)

    # calculate actors to introduce each time step
    extraActorsCount = newActorsPerTimeStep * maxSteps
    extraActors = generateActors(extraActorsCount, meanSpeed, txPowerMethod="gaussian", meanTxPower=13,
                            rxGainMethod="fixed", meanRxGain=rxGain, namer=rxGainNamer)

    # Run the simulation for 100 seconds at 0.1 second increments (10000 steps)
    sim = Simulation(actors, frequency, maxRange, -simRadius, simRadius,-simRadius,simRadius,recordPositions=animate)
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
    if (rxGain != 10):
        df.to_csv(f"./output/sim-higherRxGain{rxGain}.csv", index=False)
        if animate:
            animateActorsOverTime(sim.getActorStatesOverTimeAsDataFrame(),f"./output/sim-higherRxGain{rxGain}.mp4")
    else:
        df.to_csv("./output/sim-higherRxGain.csv", index=False) #, float_format='%.3f')
        if animate:
            animateActorsOverTime(sim.getActorStatesOverTimeAsDataFrame(),"./output/sim-higherRxGain.mp4")

def runSensitivitySim(sensitivity = None, meetings = False):
    print("=============")
    print(f"Running sensitivity simulation with sensitivity fixed at: {sensitivity}, with meetings?: {meetings}")
    print("=============")
    simDurationSeconds = 960 #960 # was 960
    stepSizeSeconds = 1 # was 0.2
    newActorsPerTimeStep = 1
    simDurationSteps = simDurationSeconds / stepSizeSeconds
    maxSteps = int(simDurationSteps)

    maxRange = 50 # was 15
    meetingMaxRange = 2.3 # was 15

    sensitivityMethod = "None" # This IS a string
    rxSens = -96
    if sensitivity != None:
        sensitivityMethod = "fixed"
        rxSens = sensitivity

    # Generate our initial actors
    # actors = generateActors(actorCount, meanSpeed, txPowerMethod="gaussian", meanTxPower=13)
    actors = generateActors(newActorsPerTimeStep, meanSpeed, txPowerMethod="gaussian", meanTxPower=13, rxSensitivityMethod = sensitivityMethod, meanRxSensitivity=rxSens)

    # calculate actors to introduce each time step
    extraActorsCount = newActorsPerTimeStep * maxSteps
    extraActors = generateActors(extraActorsCount, meanSpeed, txPowerMethod="gaussian", meanTxPower=13, rxSensitivityMethod = sensitivityMethod, meanRxSensitivity=rxSens)

    # Run the simulation for 100 seconds at 0.1 second increments (10000 steps)
    if meetings:
        sim = Simulation(actors, frequency, maxRange, -simRadius, simRadius,-simRadius,simRadius, 
                        meetingDurationMean = 5*60, meetingDurationSd = 2*60, 
                        meetingDistanceMean = 1.5, meetingDistanceSd = 0.3, 
                        meetingChance = 0.9,
                        meetingMaxRange = meetingMaxRange) 
    else:
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
    df['sensitivity'] = sensitivity # set this so we can merge on return
    print(df)
    print("=============")
    print(f"Completed sensitivity simulation with sensitivity fixed at: {sensitivity}, with meetings?: {meetings}")
    print("=============")

    return df


@arguably.command
def baselineSensitivity(*, withMeetings = False):
    """
    This function runs several simulations with a mix of transmitters and fixed sensitivity settings for all chips to see the effect.
    
    Args:
        withMeetings: [-m] bool Whether to allow meetings (default: False)
    """

    # noneDf = runSensitivitySim(None) # produces the same result as -120 so I've disabled it
    veryGoodDf = runSensitivitySim(-120, meetings=withMeetings)
    goodDf = runSensitivitySim(-100, meetings=withMeetings)
    okDf = runSensitivitySim(-95, meetings=withMeetings)
    poorDf = runSensitivitySim(-90, meetings=withMeetings)
    veryPoorDf = runSensitivitySim(-80, meetings=withMeetings)
    # noneDf['sensitivity'] = -999

    df = pd.concat([veryGoodDf,goodDf,okDf,poorDf,veryPoorDf]) #noneDf,
    
    addOn = ""
    if withMeetings:
        addOn = "-with-meetings"
    
    # The below takes time because of the use of float_format to make the time look sensible
    df.to_csv(f"./output/sim-baselinesensitivity{addOn}.csv", index=False) #, float_format='%.3f')

    # Normalise contact charts
    df['rss'] = np.asarray(df['receiverPower'],int)
    mdf = df.groupby(['sensitivity','rss'], as_index=False).agg(count=('rss','count'))
    aggdf = mdf.groupby(['sensitivity'], as_index=False).agg(total=('count','sum'))
    mdf = pd.merge(left=mdf,right=aggdf,on='sensitivity')
    mdf['prop'] = mdf['count'] / mdf['total']

    # charts
    fig, (ax) = plt.subplots(1, 1, layout="constrained", figsize=(8,6), sharey=True)
    for (sensitivity),data in mdf.groupby(['sensitivity']):
        ax.plot(data['rss'], data['prop'], label=sensitivity[0], marker='o', linestyle='-')

    ax.set_xlabel("RSS")
    ax.set_ylabel("Proportion")
    ax.set_ylim(bottom=0)
    ax.set_xlim(left=-120,right=0)
    titleAddOn = "Without meetings"
    if withMeetings:
        titleAddOn = "With meetings"
    ax.set_title(f"Contact distribution\nLow to high sensitivity receivers\n{titleAddOn}")
    ax.legend(loc="upper right")


    fig.savefig(f"./output/sim-baseline-sensitivity{addOn}.png", bbox_inches='tight', pad_inches=0.1)

    plt.close()


@arguably.command
def baselineMeetings(*, animate = False):
    """
    This function runs a simulation with each phone TxPower set to a gaussian selected from mean=13,sd=4 with meeting mean duration 5 minutes, sd 1 minute, distance of 1.5m sd 0.3m.

    Args:
        animate: [-a] Whether to generate an animate (Default: False)
    """
    # Change any standard settings
    simDurationSeconds = 320 #960 # was 960
    stepSizeSeconds = 1 # was 0.2
    newActorsPerTimeStep = 1
    simDurationSteps = simDurationSeconds / stepSizeSeconds
    maxSteps = int(simDurationSteps)

    maxRange = 50 # was 15
    meetingMaxRange = 2.3 # was 15

    # Generate our initial actors
    # actors = generateActors(actorCount, meanSpeed, txPowerMethod="gaussian", meanTxPower=13)
    actors = generateActors(newActorsPerTimeStep, meanSpeed, txPowerMethod="gaussian", meanTxPower=13)

    # calculate actors to introduce each time step
    extraActorsCount = newActorsPerTimeStep * maxSteps
    extraActors = generateActors(extraActorsCount, meanSpeed, txPowerMethod="gaussian", meanTxPower=13)

    # Run the simulation for 100 seconds at 0.1 second increments (10000 steps)
    sim = Simulation(actors, frequency, maxRange, -simRadius, simRadius,-simRadius,simRadius, 
                     meetingDurationMean = 5*60, meetingDurationSd = 2*60, 
                     meetingDistanceMean = 1.5, meetingDistanceSd = 0.3, 
                     meetingChance = 0.9,
                     meetingMaxRange = meetingMaxRange,
                     recordPositions=animate) 
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
    if animate:
        animateActorsOverTime(sim.getActorStatesOverTimeAsDataFrame(),"./output/sim-baselineMeetings.mp4")

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