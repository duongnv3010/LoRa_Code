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

def send_message(message):
    packet_size = 5  # Kích thước mỗi gói tin (tùy ý điều chỉnh)
    total_packets = len(message) // packet_size + (1 if len(message) % packet_size > 0 else 0)
    packet_counter = 0

    while True:
        for i in range(total_packets):
            start = i * packet_size
            end = start + packet_size
            packet = message[start:end]

            # Gửi thông tin gói
            ser.write(f'PACKET {i+1}/{total_packets}\n'.encode())
            time.sleep(1)  # Giảm thời gian chờ giữa các gói tin

            # Gửi gói tin dữ liệu
            ser.write(packet.encode())
            print(f'Sent packet {i+1}/{total_packets}: {packet}')
            
            time.sleep(2)  # Giảm thời gian chờ giữa các gói tin

        packet_counter += 1
        print(f'Cycle {packet_counter}: Message sent completely.')
        time.sleep(1)  # Chờ 1 giây trước khi gửi lại

# Gửi thông điệp liên tục
try:
    send_message("Hom nay la ngay 27 thang 9 nam 2024")
except KeyboardInterrupt:
    print("Transmission stopped by user.")

# Dọn dẹp GPIO khi dừng chương trình
GPIO.cleanup()
