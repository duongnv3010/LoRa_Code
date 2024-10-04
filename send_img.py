import RPi.GPIO as GPIO
import serial
import time

# Cấu hình GPIO cho các chân M0, M1
M0_PIN = 23
M1_PIN = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(M0_PIN, GPIO.OUT)
GPIO.setup(M1_PIN, GPIO.OUT)

# Đặt module ở chế độ truyền
GPIO.output(M0_PIN, GPIO.LOW)
GPIO.output(M1_PIN, GPIO.LOW)

# Cấu hình cổng serial
ser = serial.Serial("/dev/serial0", 9600, timeout=1)

# Đọc ảnh và chia thành các gói nhỏ
def send_image(image_path):
    with open(image_path, 'rb') as f:
        image_data = f.read()

    packet_size = 50  # Kích thước mỗi gói tin
    total_packets = len(image_data) // packet_size + (1 if len(image_data) % packet_size > 0 else 0)
    print(f'Total packets to send: {total_packets}')

    for i in range(total_packets):
        start = i * packet_size
        end = start + packet_size
        packet = image_data[start:end]

        # Gửi thông tin gói
        ser.write(f'PACKET {i + 1}/{total_packets}\n'.encode())
        time.sleep(0.1)  # Giảm thời gian chờ giữa các gói tin

        # Gửi gói tin
        ser.write(packet)

        # Chờ xác nhận từ bên nhận
        ack = ser.readline().decode('ascii', errors='ignore').strip()
        if ack == f'ACK {i + 1}':
            print(f'Packet {i + 1} acknowledged')
        else:
            print(f'Packet {i + 1} not acknowledged, resending...')
            ser.write(packet)  # Gửi lại nếu không nhận được xác nhận

        time.sleep(2)  # Tạm dừng giữa các gói tin

    print('Image sent successfully!')

# Truyền ảnh
send_image('logo.png')

# Dọn dẹp GPIO
GPIO.cleanup()
