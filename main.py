import cv2

# 캠 init 설정
video_capture = cv2.VideoCapture(0)
video_capture.set(3, 1280)
video_capture.set(4, 720)


while(True):
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
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])

            cv2.line(crop_img, (cx, 0), (cx, 720), (255, 0, 0), 1)
            cv2.line(crop_img, (0, cy), (1280, cy), (255, 0, 0), 1)
            cv2.drawContours(crop_img, contours, -1, (0, 255, 0), 1)

            print(cx)
            if cx >= 700:
                print("우회전")
            if cx < 700 and cx > 400:
                print("직진")
            if cx <= 400:
                print("좌회전")
        except:
            print("에러")
    else:
        print("라인을 찾을 수 없음")

    # 영상을 cv2.imshow 함수를 통하여 최종적인 출력을 보여줌
    cv2.imshow('frame', crop_img)

    if cv2.waitKey(1) == 27:
        break
