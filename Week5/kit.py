from dronekit import connect, VehicleMode

print("Bağlanılıyor...")
vehicle = connect('udp:127.0.0.1:14550', wait_ready=True)  # <<=== DEĞİŞTİ

print("✅ Bağlantı kuruldu!")
print("Mode:", vehicle.mode.name)
vehicle.close()
