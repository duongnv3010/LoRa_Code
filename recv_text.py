import RPi.GPIO as GPIO
import serial
import time

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

def receive_message():
    total_packets = 0
    received_message = []
    start_time = time.time()  # Bắt đầu tính thời gian khi nhận thông điệp
    
    while True:
        if ser.in_waiting > 0:
            try:
                # Đọc thông tin gói
                line = ser.readline().decode('utf-8').strip()
            except UnicodeDecodeError:
                continue

            if line.startswith('PACKET'):
                packet_info = line.split(' ')[1].split('/')
                current_packet = int(packet_info[0])
                total_packets = int(packet_info[1])
                
                print(f'Receiving packet {current_packet}/{total_packets}')

                # Đọc nội dung gói tin
                packet_data = ser.read(30)  # Đọc tối đa 30 byte
                packet_data = packet_data.decode('ascii', errors='ignore')
                if packet_data:
                    received_message.append(packet_data)

                if current_packet == total_packets:
                    # Ghép các phần của thông điệp lại với nhau
                    full_message = ''.join(received_message)

                    # Ghi thông điệp vào file
                    with open('received_message.txt', 'a') as file:
                        file.write(full_message + '\n')  # Ghi thông điệp vào file
                    print(f'Full message received and written to file: received_message.txt')

                    break  # Kết thúc vòng lặp sau khi nhận toàn bộ thông điệp

# Nhận thông điệp liên tục
try:
    receive_message()
except KeyboardInterrupt:
    print("Reception stopped by user.")

# Dọn dẹp GPIO khi dừng chương trình
GPIO.cleanup()
