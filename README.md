# STM32-Servo-Control-Panel-with-ESP32-CAM-Live-Monitoring

A real-time embedded control and monitoring project that combines an STM32F103C8T6, servo motor, Python GUI, and ESP32-CAM.

The system allows the user to control the servo motor from a desktop graphical interface while simultaneously viewing a live video stream of the hardware setup inside the same control panel.

The Python application communicates with the STM32 through UART, while the ESP32-CAM provides an MJPEG live stream over Wi-Fi.
This project combines:

Python GUI + STM32 + UART + DMA + PWM + ESP32-CAM + Wi-Fi + Live Video into a single control and monitoring system.

It was built as a hands-on project to explore the integration of embedded hardware, desktop software, serial communication, networking, and real-time visual feedback.

📌 Project Overview

This project creates a small remote-control and monitoring system for a servo motor.

The user interacts with a Python GUI that provides:

🔐 Password-based access
🎛️ Servo position control
📹 Live camera monitoring
🔌 Serial communication with the STM32

🧩 System Architecture:


The project contains three main subsystems.

1. Python Control Panel

The Python application is the user interface.

It is responsible for:

User
 │
 ├── Password
 │
 ├── 0° button
 │
 ├── 90° button
 │
 └── 180° button
       │
       ▼
     UART

At the same time, the application receives the camera stream:

ESP32-CAM
    │
    │ Wi-Fi
    ▼
HTTP MJPEG Stream
    │
    ▼
Python
    │
    ▼
JPEG Frame
    │
    ▼
Pillow
    │
    ▼
Tkinter Label

This allows the user to control the hardware and observe it from the same window.

2. STM32 Servo Controller

The STM32 receives commands through USART1.

UART is configured as:

Baud Rate : 9600
Data      : 8 bits
Parity    : None
Stop Bits : 1

The STM32 receives data into:

char data[20];

using:

HAL_UART_Receive_DMA(&huart1, (uint8_t *)data, 20);

This allows the UART peripheral to transfer received bytes directly into memory using DMA.

3. ESP32-CAM

The ESP32-CAM provides the live video stream through an HTTP MJPEG endpoint:

http://<ESP32-CAM-IP>:81/stream

The Python program connects to the stream using:

requests.get(
    "http://<ESP32-CAM-IP>:81/stream",
    stream=True
)

The incoming stream consists of a sequence of JPEG frames.

The Python application extracts each frame and displays it in the Tkinter interface.

🔐 Password Protection

Before the control buttons become available, the user must enter a password.

The Python application checks the entered password:

p = self.e1.get()

if p == "eli2026":

When the password is correct, the application:

Opens the serial connection.
Sends the right command.
Creates the servo-control buttons.
Starts the camera stream.

If the password is incorrect, the application sends:

wrong\r

to the STM32.

The STM32 then activates an LED for approximately 500 ms.

Incorrect Password
       │
       ▼
Python
       │
       │ "wrong\r"
       ▼
STM32
       │
       ▼
LED ON
       │
     500 ms
       │
       ▼
LED OFF

Security note: The password in this project is hard-coded in the Python source code and should be considered a demonstration feature, not a secure authentication mechanism. A production implementation should avoid storing credentials directly in source code and should use proper authentication and access control.

🎛️ Servo Control

Three buttons are provided in the GUI:



Each button sends a different command to the STM32.

0°

Python sends:

sefr degree\r

STM32 interprets this command as:

__HAL_TIM_SET_COMPARE(
    &htim1,
    TIM_CHANNEL_1,
    1000
);

Result:

PWM = 1000 µs
90°

Python sends:

navad degree\r

STM32 sets:

__HAL_TIM_SET_COMPARE(
    &htim1,
    TIM_CHANNEL_1,
    1500
);

Result:

PWM = 1500 µs
180°

Python sends:

sad degree\r

STM32 sets:

__HAL_TIM_SET_COMPARE(
    &htim1,
    TIM_CHANNEL_1,
    2000
);

Result:

PWM = 2000 µs
📐 Servo PWM

TIM1 is configured with:

Prescaler = 7
Period    = 19999

With the project's 8 MHz HSE clock:

8 MHz / (7 + 1)
      = 1 MHz

Therefore:

1 timer tick = 1 µs

The timer period becomes:

19999 + 1
= 20000 µs
= 20 ms

Therefore the PWM frequency is:

1 / 20 ms
= 50 Hz

The servo commands therefore use:

1000 µs → approximately 0°
1500 µs → approximately 90°
2000 µs → approximately 180°

The exact physical angle depends on the specific servo and its calibration.

🔄 UART Command Protocol

The communication between Python and STM32 is intentionally simple.

Python Command	STM32 Action
right\r	Correct password
wrong\r	Incorrect password
sefr degree\r	Servo → 0°
navad degree\r	Servo → 90°
sad degree\r	Servo → 180°

The STM32 searches the received buffer using:

strstr(data, "sefr degree\r")

and similar conditions for the other commands.

This allows the microcontroller to identify the command contained in the received UART data.

⚡ UART + DMA

The STM32 uses DMA for UART reception:

HAL_UART_Receive_DMA(
    &huart1,
    (uint8_t *)data,
    20
);

The basic communication flow is:

Python
   │
   │ UART
   │ 9600 baud
   ▼
USART1
   │
   ▼
DMA
   │
   ▼
data[20]
   │
   ▼
strstr()
   │
   ▼
Command Detection
   │
   ▼
Servo / LED Action

After processing a command, the receive DMA is stopped, the buffer is cleared, and DMA reception is started again.

This project therefore also demonstrates a practical example of peripheral-to-memory data transfer using DMA.

📹 Live Video Streaming

One of the main features of this project is the live camera view.

The ESP32-CAM sends an MJPEG stream consisting of JPEG frames.

The Python application receives chunks of the HTTP response:

self.chunks = result.iter_content(
    chunk_size=8192
)

The chunks are stored in a byte buffer:

self.buffer += chunks

The program then searches for the HTTP header boundary:

position = self.buffer.find(
    b"\r\n\r\n"
)

After locating the header, it searches for:

Content-Length:

The value tells the program how many bytes belong to the current JPEG frame.

Conceptually:

HTTP/MJPEG Stream

The JPEG data is extracted using:

image_data = BytesIO(part1)
image = Image.open(image_data)

Pillow converts the JPEG data into an image object.

It is then converted into a Tkinter-compatible image:

photo = ImageTk.PhotoImage(image)

Finally, the GUI is updated:

self.txt20.config(
    image=self.img
)
🧵 Threading and Tkinter

The camera request is started in a separate Python thread:

thread1 = threading.Thread(
    target=self.camera_request
)

thread1.start()

The purpose is to prevent the HTTP streaming operation from blocking the main GUI startup.

After the camera connection is established, the frame-processing loop uses Tkinter's:

self.root.after()

to schedule subsequent processing.

The project therefore combines:

Python Thread
      │
      ▼
Camera HTTP Stream
      │
      ▼
JPEG Buffer
      │
      ▼
Tkinter after()
      │
      ▼
GUI Update

Note: Tkinter is generally safest when widget updates happen on the main GUI thread. A future improvement would be to separate camera acquisition from GUI updates using a thread-safe queue, with the main Tkinter thread responsible for displaying frames.

🖥️ Python GUI

The control panel is created using Tkinter:

self.root = Tk()

The window size is:

660 × 500

The title is:

Servo Motor Control Panel

The GUI contains:

Password section
Please Enter your password to access the panel

             [ password ]

          [ check password ]
Live camera section

The ESP32-CAM video is displayed in a Tkinter Label.

Servo controls
[ 0 degree ]    [ 90 degree ]    [ 180 degree ]

This provides a simple interface for controlling the physical servo while monitoring the hardware visually.

🔌 Hardware Communication

The Python application uses PySerial:

serial.Serial("COM13", 9600)

The communication path is:

Windows PC
    │
    │ USB / UART
    ▼
USB-to-TTL Adapter
    │
    │ 9600 baud
    ▼
STM32 USART1
    │
    ▼
TIM1 PWM
    │
    ▼
Servo

The actual COM port may be different on another computer.

For example:

COM3
COM5
COM13

depending on the connected USB-to-TTL adapter.

🔌 Suggested Hardware Connections
STM32 ↔ UART Adapter
USB-to-TTL          STM32

TX   ─────────────► RX
RX   ◄───────────── TX
GND  ────────────── GND

The UART voltage levels must be appropriate for the STM32.

Servo
STM32 TIM1 PWM ────► Servo Signal

External Supply ───► Servo VCC
GND ───────────────► Servo GND

The STM32 and external servo supply must share a common ground.

⚠️ Do not power a servo directly from an insufficient USB/UART adapter or from a GPIO pin. Use an appropriate external power supply capable of supplying the servo's current.

📡 ESP32-CAM Configuration:

The ESP32-CAM configuration is provided in the CameraConfig.ino file by using Arduino IDE and libraries.

The CameraConfig.ino file contains the network configuration, including the Wi-Fi credentials and the camera's network settings.

After uploading the CameraConfig.ino code to the ESP32-CAM, the camera obtains an IP address on the network.

The Python application then connects to the camera's MJPEG stream using:

http://:81/stream

For example:

http://192.168.137.60:81/stream

If the ESP32-CAM receives a different IP address, update the stream URL in the Python code accordingly.

📊 How to Run:

1. Prepare the hardware

Connect:

STM32F103C8T6
Servo motor
UART/USB-to-TTL adapter
ESP32-CAM
LCD
External servo power supply

Make sure the STM32 firmware has already been programmed.

2. Configure the ESP32-CAM

Connect the ESP32-CAM to the same local network as the computer.

Find its IP address and update the Python code:

requests.get(
    "http://<ESP32-CAM-IP>:81/stream",
    stream=True
)

For example:

http://192.168.137.60:81/stream

The IP address may be different on another network.

3. Configure the serial port

Update:

serial.Serial("COM13", 9600)

with the COM port assigned to your USB-to-TTL adapter.

4. Start the Python application

Run:

python main.py

The control panel should appear.

5. Enter the password

Enter the configured password.

If authentication succeeds:

Servo buttons appear.
The serial connection is opened.
The STM32 receives the right command.
The ESP32-CAM live stream starts.
6. Control the servo

Use:

[ 0 degree ]
[ 90 degree ]
[ 180 degree ]

while observing the physical hardware through the live camera feed.

🖥️📽️YouTube video link:https://youtu.be/qHD8jX5M3lg
