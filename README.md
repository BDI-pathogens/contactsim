# Python Bluetooth contact simulation

This simulation uses the Friis formula and the mean Bluetooth advertisement frequency
to estimate an expected Receiver Signal Strength power (RxPower or Pr) for given distances.

This is done to create a reference 'background' set of signal strength readings for
comparison to the England and Wales (or any other) Bluetooth contact strength dataset.

## Why is this needed?

Many manufacturers use their own formulae to estimate signal strength based on power strength at the antenna of
a receiver. This does not take into account any digital information recorded in the transmission (such as TxPower in Bluetooth packets).

There was a need to simulate what distribution of receiver power would be received from a 'perfect device' with no interference, and to
see if this is affected by the population of others devices' transmission powers, or by static meetings between their human owners at
a small range of meeting distances.

ContactSim was created by Adam Fowler at the Pandemic Sciences Institute (PSI, https://www.psi.ox.ac.uk/ ) to generate this reference data.

## Method

We expect single devices to detect others up to 50m in radius. We therefore create a 
'world' which is circular of 200m radius. We generate 'agents' with phones
and place them at random around the circular world, then choose an angle and speed for
them to traverse. (max 180 degree - tangent to the circle). We then measure their progress every 1/10th
of a second and generate an expected signal strength estimate for every pair wise set of contacts in
the range of interest (50m radius).

## Simulation Limitations

Currently the simulation has the following limitations:-

- Uses a single frequency for the Bluetooth simulation, not the three frequencies actually used by Bluetooth
- Meetings are pairwise, with meetings only possible between 2 actors that are NOT YET in a meeting
- Does not yet use a Link Budget calculation to limit whether the signal would have actually been received in real life - uses a fixed meetingMaxRange value instead
- The generateActors function sets all actor speed to a static speed (meanSpeed) rather than selecting from a distribution

## Repository limitations

We're missing the current features in this repository:-

- We have not set up the DCO Bot in GitHub to ensure signing of all commits
- We have not implemented tests
- We have not built and published this as a module to PyPi
- Whilst documentation is present in the code files, it has not been converted to friendly HTML
- No developer or user HTML documentation is yet provided

## Installing prerequisities

Install the following prerequisites:-

```sh
pip install arguably numpy pandas scipy matplotlib
```

## Running the simulator

There are built in scenarios in scenarios.py. You can get a list of these by running the file:-

```sh
cd examples
python scenarios.py
```

To run a specific example, such as a full simulation, run one of the commands:-

```sh
cd examples
python scenarios.py baselinefixedtxpower
```

Note: Although the function names use capital letters, the command line commands are lowercase only.

Each command will, by default, generate output into the ./output folder.

## Sample data

Output from all of the commands in `./examples/scenarios.py` can be found in the `./samples` folder.

The meetings baseline file is not provided as it is 500MB in size! You can generate that yourself within 10 minutes using the following command:-

```sh
cd examples
mkdir output
python scenarios.py baselinemeetings
```

## Output data format

The generated output CSV is in the `./output` folder. The format includes the following columns in the first row:-

- time - Time in seconds (NOT simulation ticks) that the detection occurred
- receiverId - The unique string identifier of the receiver
- transmitterId -The unique string identifier of the transmitter
- receiverPower - The detected receiver power (full actual physica formula derived power, NOT RSSI yet). NOT corrected for TxPower.
- receiverDeviceModel - String name of the receiver device model
- transmitterDeviceModel - String name of the

## Copyright and Licensing

Copyright 2024-2025 ContactSim Contributors. 

Code is licensed under the Apache-2.0 license. See the `LICENSE` file for details.

The data in the samples folder is made available under the Open Data Attribution 1.0 license (ODB-by-1.0): https://opendatacommons.org/licenses/by/1-0/

The documentation is available under the CC-BY International 4.0 license (CC-BY-4.0): https://creativecommons.org/licenses/by/4.0/ 