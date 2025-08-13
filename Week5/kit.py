from dronekit import connect
from datetime import datetime
import time
import math

# Connect to the vehicle using TCP
vehicle = connect('tcp:127.0.0.1:5762', wait_ready=True)
print("Connection established")

try:
    while True:
        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # GPS and altitude (relative to home)
        gps = vehicle.gps_0
        location = vehicle.location.global_relative_frame
        altitude = location.alt

        # Attitude (orientation)
        attitude = vehicle.attitude
        pitch = attitude.pitch
        roll = attitude.roll
        yaw = attitude.yaw

        # Velocity vector (x, y, z in m/s)
        velocity = vehicle.velocity  # [vx, vy, vz]

        # Mode and arming status
        flight_mode = vehicle.mode.name
        armed_status = vehicle.armed

        # Mavlink last heartbeat time
        heartbeat_timestamp = vehicle.last_heartbeat

        # Print all telemetry data
        print(f"{timestamp}")
        print(f"P: {math.degrees(pitch):.2f}°, R: {math.degrees(roll):.2f}°, Y: {math.degrees(yaw):.2f}°")
        print(f"Altitude: {altitude:.2f} m")
        print(f"Velocity → Vx: {velocity[0]:.2f} m/s, Vy: {velocity[1]:.2f} m/s, Vz: {velocity[2]:.2f} m/s")
        print(f"Flight Mode: {flight_mode}")
        print(f"Arm Status: {'Armed' if armed_status else 'Disarmed'}")
        print(f"Last Mavlink Heartbeat: {heartbeat_timestamp:.2f} seconds ago")
        print("==========================")

        time.sleep(3)

except KeyboardInterrupt:
    print("Loop interrupted by user.")

finally:
    vehicle.close()
    print("Connection closed.")
