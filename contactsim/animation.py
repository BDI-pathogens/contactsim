#!/usr/bin/env python3

#  Copyright 2025 ContactSim contributors
#  SPDX-License-Identifier: Apache-2.0
#

# This file contains utility functions to convert simulation data into animations.

import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation

def animateActorsOverTime(actorStateDataFrame, filePath):
    df = actorStateDataFrame

    meetingColors = dict(zip([True,False],["#ff2222","#00ffff"]))

    times = df['time'].unique()

    fig, ax = plt.subplots(figsize=(8, 8))

    # Initialise scatter
    ax.scatter(df['x'][0],df['y'][0])

    def drawFrame(time):
        dff = df[df['time'] == time]

        ax.clear()
        ax.scatter(dff['x'],dff['y'],color=[meetingColors[x] for x in dff['inMeeting']])

        ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
        ax.xaxis.set_ticks_position('top')
        ax.tick_params(axis='x', colors='#777777', labelsize=12)
        
        ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
        ax.yaxis.set_ticks_position('left')
        ax.tick_params(axis='y', colors='#777777', labelsize=12)

        # ax.set_yticks([])
        ax.margins(0, 0.01)
        ax.set_xlim([-200,200])
        ax.set_ylim([-200,200])
        ax.grid(which='major', axis='x', linestyle='-')
        ax.grid(which='major', axis='y', linestyle='-')
        ax.set_axisbelow(True)

        ax.text(0, 1.10, 'Actor movement during simulation',
            transform=ax.transAxes, size=24, weight=120, ha='left')
        ax.text(0,1.06, f"Time: {time}",
            transform=ax.transAxes, size=12, weight=100, ha='left')
        
        plt.box(False)
        # plt.show()

    animator = FuncAnimation(fig, drawFrame, frames = times)
    # plt.show()

    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
    animator.save(filePath, writer=writer)

    # writer = animation.ImageMagickFileWriter()
    # animator.save(filePath, writer=writer)
