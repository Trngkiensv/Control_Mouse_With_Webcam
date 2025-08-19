import tisgrabber as ic

# Khởi tạo thư viện
ic.InitLibrary(0)

# Lấy số lượng thiết bị
device_count = ic.IC_GetDeviceCount()

# Lấy tên các camera
for i in range(device_count):
    device_name = ic.IC_GetDevice(i).decode('utf-8')
    print(f"Camera {i}: {device_name}")

# Giải phóng thư viện
ic.CloseLibrary()