from sense_emu import SenseHat
import time

# Khởi tạo Sense HAT
sense = SenseHat()

# Màu sắc cho LED
RED = [255, 0, 0]
BLACK = [0, 0, 0]

# Hiển thị chữ "HIEU" trên LED ma trận
def hien_thi_HIEU():
    sense.clear()  # Xóa màn hình
    sense.show_message("HIEU", text_colour=RED, back_colour=BLACK, scroll_speed=0.1)

# Hàm đọc và in dữ liệu cảm biến
def doc_cam_bien():
    # Đọc nhiệt độ, độ ẩm
    nhiet_do = sense.get_temperature()
    do_am = sense.get_humidity()
    
    # Đọc trạng thái joystick
    su_kien = sense.stick.get_events()
    for su_kien_joystick in su_kien:
        if su_kien_joystick.action == "pressed":
            print(f"Joystick: {su_kien_joystick.direction} được nhấn")
    
    # In dữ liệu ra màn hình console
    print(f"Nhiệt độ: {nhiet_do:.1f}°C, Độ ẩm: {do_am:.1f}%")

# Vòng lặp chính
def main():
    while True:
        doc_cam_bien()
        hien_thi_HIEU()
        time.sleep(2)  # Chờ 2 giây trước khi lặp lại

# Chạy chương trình
if __name__ == "__main__":
    main()