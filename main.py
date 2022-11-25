import cv2
import RPi.GPIO as GPIO
import serial
ser = serial.Serial("/dev/ttyAMA0", 115200)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

PWM1 = 12
PWM2 = 13
DIR1 = 22
DIR2 = 23
GPIO.setup(PWM1, GPIO.OUT)
GPIO.setup(PWM2, GPIO.OUT)
GPIO.setup(DIR1, GPIO.OUT)
GPIO.setup(DIR2, GPIO.OUT)

motor1 = GPIO.PWM(PWM1, 1000)
motor2 = GPIO.PWM(PWM2, 1000)

motor1.start(10)
motor2.start(10)

GPIO.output(DIR1, GPIO.LOW)
GPIO.output(DIR2, GPIO.LOW)

# 캠 init 설정
video_capture = cv2.VideoCapture(0)
video_capture.set(3, 1280)
video_capture.set(4, 720)


while(True):
    distance = None
    # ------ TFMini Plus Lidar 센서 거리 측정------
    if ser.is_open == False:
        ser.open()
    else:
        count = ser.in_waiting
        if count > 8:
            recv = ser.read(9)
            ser.reset_input_buffer()
            if recv[0] == 0x59 and recv[1] == 0x59:  # python3
                distance = recv[2] + recv[3] * 256
                strength = recv[4] + recv[5] * 256
                ser.reset_input_buffer()
    # ------ TFMini Plus Lidar 센서 거리 측정------

    # 웹캠으로 부터 실시간으로 캡쳐
    ret, frame = video_capture.read()

    # 웹캠으로 받아온 프레임을 리사이징
    crop_img = frame[360:720, 0:1280]

    # 명암 대비를 알아내기 위한 그레이 스케일로 색 변경
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

    # 노이즈 제거를 위해서 가우시안 블러처리
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # 영상의 각각의 이미지를 이진화 하기 위하여 임계값 지정하여 이진화
    ret, thresh = cv2.threshold(blur, 60, 255, cv2.THRESH_BINARY_INV)

    # 영상에 프레임 별로 윤곽선을 찾아냄
    contours, hierarchy = cv2.findContours(
        thresh.copy(), 1, cv2.CHAIN_APPROX_NONE)

    # 윤곽선이 감지 되었을때
    if len(contours) > 0:
        try:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])

            cv2.line(crop_img, (cx, 0), (cx, 720), (255, 0, 0), 1)
            cv2.line(crop_img, (0, cy), (1280, cy), (255, 0, 0), 1)
            cv2.drawContours(crop_img, contours, -1, (0, 255, 0), 1)

            print(cx)
            print(distance)
            if(distance>20):
                if cx >= 700:
                    print("우회전")
                    # TODO: 하단에 라즈베리파이 우회전 모터드라이버 컨트롤 로직 추가
                    motor1.ChangeDutyCycle(13)
                    motor2.ChangeDutyCycle(0)
                if cx < 700 and cx > 400:
                    print("직진")
                    # TODO: 하단에 라즈베리파이 직진 모터드라이버 컨트롤 로직 추가
                    motor1.start(10)
                    motor2.start(10)
                    motor1.ChangeDutyCycle(15 * cx / 1024)
                    motor2.ChangeDutyCycle(15 * (1024 - cx) / 1024)

                if cx <= 400:
                    print("좌회전")
                    # TODO: 하단에 라즈베리파이 좌회전 모터드라이버 컨트롤 로직 추가
                    motor1.ChangeDutyCycle(0)
                    motor2.ChangeDutyCycle(13)
            else:
                motor2.ChangeDutyCycle(0)
                motor2.ChangeDutyCycle(0)


        except:
            print("에러")
    else:
        print("라인을 찾을 수 없음")
        motor1.stop()
        motor2.stop()


    # 영상을 cv2.imshow 함수를 통하여 최종적인 출력을 보여줌
    cv2.imshow('frame', crop_img)

    if cv2.waitKey(1) == 27:
        break

