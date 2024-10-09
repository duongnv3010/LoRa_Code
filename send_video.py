import serial
import time
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

# Hàm chia nhỏ file video thành các khối nhỏ


def split_file(file_path, chunk_size):
    with open(file_path, 'rb') as file:
        while chunk := file.read(chunk_size):
            yield chunk

# Hàm gửi dữ liệu qua module LoRa


def send_data_lora(data, ser, packet_num):
    # Gửi gói tin
    ser.write(data)
    time.sleep(2)  # Giữa các gói tin cần có độ trễ nhỏ để không bị quá tải

    # Chờ ACK từ bên nhận
    ack = ser.read(1)
    if ack == b'1':
        print(f"Gói tin {packet_num} đã được gửi thành công!")
        return True
    else:
        print(f"Gói tin {packet_num} không nhận được ACK, gửi lại...")
        return False

# Hàm gửi file video qua LoRa với cơ chế xác nhận


def send_video(file_path, ser):
    file_size = os.path.getsize(file_path)  # Kích thước file
    # Gửi kích thước file trước
    ser.write(file_size.to_bytes(4, byteorder='big'))

    packet_num = 0
    for chunk in split_file(file_path, 100):  # Mỗi khối có kích thước 100 byte
        packet_num += 1
        while not send_data_lora(chunk, ser, packet_num):
            pass  # Gửi lại gói tin nếu không nhận được ACK

    print("Tất cả các gói tin đã được gửi.")


# Thiết lập kết nối serial với module LoRa
# Tùy chỉnh cổng đúng với module LoRa
ser = serial.Serial('/dev/serial0', 9600)

# Gọi hàm cấu hình GPIO và LoRa
setup_lora()

# Gửi file video
video_path = 'video_test.mp4'  # Đường dẫn tới video cần gửi
start_time = time.time()
send_video(video_path, ser)
end_time = time.time()

# Tính toán thời gian và băng thông sử dụng

total_time = end_time - start_time
file_size_byte = os.path.getsize(video_path)
# Kích thước file tính theo bits
file_size_bits = os.path.getsize(video_path) * 8
speed_transmission = file_size_bits / total_time
print(f"Độ lớn của video: {file_size_byte} byte")
print(f"Đã gửi file. Thời gian truyền: {total_time:.2f} giây")
print(f"Tốc độ truyền: {speed_transmission:.2f} bps")

# Dọn dẹp GPIO sau khi hoàn thành
GPIO.cleanup()
