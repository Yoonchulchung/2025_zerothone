# 2025_zerothone

2025.03.29 단국대학교에서 진행한 Zerothon 참가 코드 입니다.
제로톤은 단국대학교에서 개최한 해커톤으로 2인 이상의 팀원이 모여서 3박 4일간 프로젝트를 기획하고 개발하는 해커톤입니다.

__팀명__ : 지구촌 유물들

__팀원__ : 고민준, 서동우, 정윤철


2개의 라즈베리파이4와 4개의 서버모터를 이용하여 인공지능으로 사람의 얼굴을 인식하고 서보모터를 통해 책상을 숨기고 보여줍니다.

### 설명
- AI Server는 Resnett10 + SSD 를 이용하여 사용자의 얼굴을 인식하여 좌표 값을 보내주는 서버입니다. 
- RasberryPi Camera는 라즈베리파이4와 연결된 카메라가 이미지를 MJPEG 데이터로 받아서 비트로 변환 후 AI Server로 전송합니다.
- RasberryPi Hardware는 라즈베리파이4와 연결된 4개의 서보모터를 제어하여 카메라의 상하좌우를 제어하고, 2개의 서보머터를 제어하여 책상을 제어합니다.

```
├── AI_Server
│   ├── models
│   ├── opencv
│   │   └── build
│   │       └── install.sh
│   ├── Readme.md
│   └── resnet_server.py
├── LICENSE
├── RasPI_Camera
│   ├── detect_adc.py
│   ├── get_data_from_AI_Server.py
│   ├── init_RasPI_Camera.py
│   ├── Readme.md
│   ├── run.sh
│   └── send_camera_to_AI_Server.py
├── RasPI_HW
│   ├── AI_tracking.py
│   ├── pi1_main.py
│   ├── Readme.md
│   ├── servo_move
│   │   ├── servo_close.py
│   │   ├── servo_down.py
│   │   ├── servo_open.py
│   │   └── servo_up.py
│   ├── table_initial.py
│   ├── table_mode.py
│   ├── table_mode.txt
│   └── table_setting.py
├── README.md
└── requirements.txt
```

RasberryPi Hardware는 라즈베리파이4와 연결된 수광 센서를 통해 입력이 들어오면, 인터럽트를 통해 시스템을 ON/OFF를 할 수 있도록 설계되어 있습니다.
전력 효율을 높이기 위해 Thread를 통해 인터럽트 신호에 따라 시스템이 동작되도록 설계되어 있습니다.

AI Server는 Flask를 활용하여 인공지능 서버를 구축하였습니다. ONNX를 통해 모델을 로드하는 과정을 단축시켰습니다.
