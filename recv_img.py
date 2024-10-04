import RPi.GPIO as GPIO
import serial
import time

# Tắt cảnh báo GPIO
GPIO.setwarnings(False)

# Cấu hình GPIO cho các chân M0, M1
M0_PIN = 23
M1_PIN = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(M0_PIN, GPIO.OUT)
GPIO.setup(M1_PIN, GPIO.OUT)

# Đặt module ở chế độ nhận
GPIO.output(M0_PIN, GPIO.LOW)
GPIO.output(M1_PIN, GPIO.LOW)

# Cấu hình cổng serial
ser = serial.Serial("/dev/serial0", 9600, timeout=1)

# Bộ đệm để lưu ảnh nhận
received_image = bytearray()
expected_total_packets = None
received_packets = 0

# Hàm kiểm tra ảnh có nhận đủ gói không
def check_received_image():
    global received_packets, expected_total_packets
    if received_packets == expected_total_packets:
        print("Received all packets!")
        with open('received_image.png', 'wb') as f:
            f.write(received_image)
        print("Image saved as 'received_image.png'")
    else:
        print(f"Received {received_packets}/{expected_total_packets} packets. Missing packets!")

# Nhận dữ liệu
while True:
    if ser.in_waiting > 0:
        try:
            # Đọc thông tin gói
            line = ser.readline().decode('ascii', errors='ignore').strip()
        except UnicodeDecodeError:
            continue

        if line.startswith('PACKET'):
            packet_info = line.split(' ')[1].split('/')
            current_packet = int(packet_info[0])
            expected_total_packets = int(packet_info[1])
            print(f'Receiving packet {current_packet}/{expected_total_packets}')

            # Đọc dữ liệu gói tin
            packet_data = ser.read(50)  # Đọc đúng 50 byte từ cổng serial
            received_image.extend(packet_data)  # Thêm vào bộ đệm
            received_packets += 1

            # Gửi xác nhận (ACK) cho bên gửi
            ser.write(f'ACK {current_packet}\n'.encode())

            # Kiểm tra xem đã nhận đủ gói chưa
            if received_packets == expected_total_packets:
                check_received_image()
                break  # Kết thúc vòng lặp sau khi nhận đủ

# Dọn dẹp GPIO
GPIO.cleanup()
