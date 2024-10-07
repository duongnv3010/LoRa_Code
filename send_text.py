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
    packet_size = 10  # Kích thước mỗi gói tin là 10 byte
    message_size = len(message)
    total_packets = len(message) // packet_size + (1 if len(message) % packet_size > 0 else 0)
    
    print(f"Total packets to send: {total_packets}")
    
    start_time = time.time()  # Bắt đầu tính thời gian cho toàn bộ quá trình truyền
    for i in range(total_packets):
        start = i * packet_size
        end = start + packet_size
        packet = message[start:end]

        # Gửi thông tin gói tin
        ser.write(f'PACKET {i+1}/{total_packets}\n'.encode())

        # Gửi dữ liệu gói tin
        ser.write(packet.encode())
        print(f'Sent packet {i+1}/{total_packets}: {packet}')
        
        time.sleep(2)  # Chờ để đảm bảo bên nhận xử lý gói tin

    end_time = time.time()  # Kết thúc tính thời gian
    total_time = end_time - start_time
    print(f"Total transmission time: {total_time:.2f} seconds")
    
    print(f"Message size: {message_size} bytes")
    # Tính tốc độ truyền (bits per second)
    total_data_bits = len(message) * 8  # Số lượng bit được truyền
    transmission_speed = total_data_bits / total_time
    print(f"Transmission speed: {transmission_speed:.2f} bps")

# Gửi thông điệp liên tục
try:
    send_message("Hom nay la ngay 7 thang 10 nam 2024, vay thi ngay mai se la ngay 8 thang 10 nam 2024")
except KeyboardInterrupt:
    print("Transmission stopped by user.")

# Dọn dẹp GPIO khi dừng chương trình
GPIO.cleanup()
