# DroneKit Telemetry Logger

This Python script connects to a drone (real or simulated) via **DroneKit** and retrieves live telemetry data such as:

- **GPS position & altitude** (relative to home)
- **Attitude** (Pitch, Roll, Yaw in degrees)
- **Velocity vector** (Vx, Vy, Vz in m/s)
- **Flight mode** & arming status
- **MAVLink last heartbeat time**

Data is printed to the console every **3 seconds** until the user interrupts.

## 🚀 Usage

1. Install dependencies:
   ```bash
   pip install dronekit pymavlink
