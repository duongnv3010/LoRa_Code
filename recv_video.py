import serial
import os
import RPi.GPIO as GPIO

# Cấu hình GPIO cho chân M0 và M1
M0_PIN = 23
M1_PIN = 24

def setup_lora():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(M0_PIN, GPIO.OUT)
    GPIO.setup(M1_PIN, GPIO.OUT)
    # Đặt cả M0 và M1 ở mức LOW để vào chế độ Normal
    GPIO.output(M0_PIN, GPIO.LOW)
    GPIO.output(M1_PIN, GPIO.LOW)

# Hàm nhận dữ liệu qua module LoRa và ghi vào file
def receive_data_lora(ser, chunk_size):
    return ser.read(chunk_size)

# Hàm nhận file video qua LoRa với cơ chế ACK
def receive_video(output_file, ser):
    # Nhận kích thước file trước (4 byte đầu tiên chứa kích thước file)
    file_size = int.from_bytes(ser.read(4), byteorder='big')
    print(f"Kích thước file nhận: {file_size} bytes")

    with open(output_file, 'wb') as file:
        total_received = 0
        while total_received < file_size:
            # Tính toán lượng dữ liệu còn lại để tránh đọc quá nhiều trong gói cuối
            bytes_to_read = min(100, file_size - total_received)
            data = receive_data_lora(ser, bytes_to_read)  # Nhận từng khối 100 byte (hoặc nhỏ hơn)
            if not data:
                break
            file.write(data)
            total_received += len(data)
            print(f"Đã nhận {total_received}/{file_size} bytes")
            
            # Gửi ACK lại cho bên gửi
            ser.write(b'1')

# Thiết lập kết nối serial với module LoRa
ser = serial.Serial('/dev/serial0', 9600)  # Tùy chỉnh cổng đúng với module LoRa

# Gọi hàm cấu hình GPIO và LoRa
setup_lora()

# Nhận file video
output_video_path = 'received_video.mp4'  # Đường dẫn file lưu trữ video nhận
receive_video(output_video_path, ser)

# Dọn dẹp GPIO sau khi hoàn thành
GPIO.cleanup()
