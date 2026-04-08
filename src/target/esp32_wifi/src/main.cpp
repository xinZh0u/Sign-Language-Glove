#include "SparkFunMPU9250-DMP.h"
#include <WiFi.h>
#include <WiFiUdp.h>
#include <glove.h>

#define GLOVE_LEFT_ID 0
#define GLOVE_RIGHT_ID 1

// 设备配置
#define NAME_LEFT // 注释这行名字就是right
#ifdef NAME_LEFT
#define DEVICE_NAME "Glove_Left"
#define GLOVE_ID GLOVE_LEFT_ID
Glove myglove = Glove(0, 4, 3, 2, 1);
#else
#define DEVICE_NAME "Glove_Right"
#define GLOVE_ID GLOVE_RIGHT_ID
Glove myglove = Glove(0, 1, 2, 3, 4);
#endif

#define CAL_PLAM_PIN 5
#define CAL_FIST_PIN 6

// #define SSID "gzx-hotspot"
// #define PASSWORD "" //"19226782798"
// #define TARGET_IP "10.42.0.1"
// #define TARGET_PORT 4321
// unsigned int localUdpPort = 1234;  // 自定义本地监听端口
// unsigned int remoteUdpPort = 4321; // 自定义远程监听端口

// Wi-Fi 配置
const char *ssid = "gzx-hotspot"; // 替换为你的Wi-Fi名称
const char *password = "";        // 替换为你的Wi-Fi密码

unsigned int localPort = 1234;      // 本地监听端口（发送时可不绑定，但建议绑定）
unsigned int remotePort = 4321;     // 目标端口
const char *remoteIP = "10.42.0.1"; // 广播地址或目标IP

WiFiUDP Udp;

// 数据包格式
enum
{
    PAK_ID,
    PAK_TIME,
    PAK_ROLL,
    PAK_PITCH,
    PAK_YAW,
    PAK_FINGER_THUMB,
    PAK_FINGER_INDEX,
    PAK_FINGER_MIDDLE,
    PAK_FINGER_RING,
    PAK_FINGER_LITTLE,
    PAK_NUM
};

typedef struct
{
    float data[PAK_NUM];
} Pak;

Pak pak = {0};

MPU9250_DMP imu;

void wifi_init()
{
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println();
    Serial.print("Connected with IP: ");
    Serial.println(WiFi.localIP());

    // 初始化UDP
    if (Udp.begin(localPort))
    {
        Serial.println("UDP initialized");
    }
    else
    {
        Serial.println("Failed to initialize UDP");
    }
}

// 发送数据包
void send_message(const char *message)
{
    Udp.begin(localPort);
    Udp.beginPacket(remoteIP, remotePort);                       // 配置远端ip地址和端口
    Udp.print(message);
    //Udp.write((uint8_t *)message, (uint8_t)(strlen(message) + 1)); // 把数据写入发送缓冲区
    int result = Udp.endPacket();

    if (result == 1)
    {
        Serial.println("UDP packet sent successfully");
    }
    else
    {
        Serial.println("Failed to send UDP packet");
    }
}

void setup()
{
    Serial.begin(115200);
    pinMode(CAL_PLAM_PIN, INPUT_PULLUP);
    pinMode(CAL_FIST_PIN, INPUT_PULLUP);

    wifi_init();

    Wire.setPins(8, 9);
    Wire.begin();
    // Call imu.begin() to verify communication and initialize
    if (imu.begin() != INV_SUCCESS)
    {
        while (1)
        {
            Serial.printf("Unable to communicate with MPU-9250");
            Serial.printf("Check connections, and try again.\n");
            delay(5000);
        }
    }
    Serial.printf("imu.begin() suceeded\n");

    if (imu.dmpBegin(DMP_FEATURE_6X_LP_QUAT |  // Enable 6-axis quat
                         DMP_FEATURE_GYRO_CAL, // Use gyro calibration
                     150) == INV_ERROR)
    {                                                // Set DMP FIFO rate to 150 Hz
        Serial.printf("imu.dmpBegin have failed\n"); // dmpLoad function under it fails which is caused by memcmp(firmware+ii, cur, this_write) (it is located at row 2871 of inv_mpu.c)
    }
    else
    {
        Serial.printf("imu.dmpBegin() suceeded\n");
    }
    Serial.printf("$GETEU,*\n");
    myglove.loadCalibrate();
}

void loop()
{
    double lastTime = millis();
    double timestamp = millis();
    if (imu.fifoAvailable())
    { // fifo is not being available
        // Use dmpUpdateFifo to update the ax, gx, mx, etc. values

        if (imu.dmpUpdateFifo() == INV_SUCCESS)
        {
            // computeEulerAngles can be used -- after updating the
            // quaternion values -- to estimate roll, pitch, and yaw
            imu.computeEulerAngles();
            // printIMUData();
            imu.update(UPDATE_ACCEL | UPDATE_GYRO | UPDATE_COMPASS);
            // imu_data.time = (imu.time-imu_data.time)/1000000.0000f;

            timestamp = millis();

            // 打包数据并且发送
            pak.data[PAK_ID] = GLOVE_ID;
            pak.data[PAK_TIME] = imu.time / 1000.0000f;
            pak.data[PAK_YAW] = imu.yaw;
            pak.data[PAK_ROLL] = imu.roll;
            pak.data[PAK_PITCH] = imu.pitch;

            float *angles = myglove.getAngles();
            pak.data[PAK_FINGER_THUMB] = angles[0];
            pak.data[PAK_FINGER_INDEX] = angles[1];
            pak.data[PAK_FINGER_MIDDLE] = angles[2];
            pak.data[PAK_FINGER_RING] = angles[3];
            pak.data[PAK_FINGER_LITTLE] = angles[4];

            std::string message = "";
            for (int i = 0; i < PAK_NUM; i++)
            {
                message = message + std::to_string(pak.data[i]);
                if (i != PAK_NUM - 1)
                    message += ',';
            }
            send_message(message.c_str());
            lastTime = timestamp;
        }
    }
    if (digitalRead(CAL_PLAM_PIN) == LOW)
    {
        delay(20);
        if (digitalRead(CAL_PLAM_PIN) == LOW)
        {
            float *angles = myglove.getAngles();
            for (int i = 0; i < 5; i++)
            {
                myglove.calibrate((FINGER_T)i, HAND_STATE_PALM);
            }
            myglove.saveCalibrate();
            while (digitalRead(CAL_PLAM_PIN) == LOW)
                ;
            delay(20);
        }
    }

    if (digitalRead(CAL_FIST_PIN) == LOW)
    {
        delay(20);
        if (digitalRead(CAL_FIST_PIN) == LOW)
        {
            float *angles = myglove.getAngles();
            for (int i = 0; i < 5; i++)
            {
                myglove.calibrate((FINGER_T)i, HAND_STATE_FIST);
            }
            myglove.saveCalibrate();
            while (digitalRead(CAL_FIST_PIN) == LOW)
                ;
            delay(20);
        }
    }
}

// #include <WiFi.h>
// #include <WiFiUdp.h>
// #include <WiFiSTA.h>

// // Wi-Fi 配置
// const char *ssid = "gzx-hotspot"; // 替换为你的Wi-Fi名称
// const char *password = "";        // 替换为你的Wi-Fi密码

// // UDP 配置
// WiFiUDP udp;
// unsigned int localPort = 1234;      // 本地监听端口（发送时可不绑定，但建议绑定）
// unsigned int remotePort = 4321;     // 目标端口
// const char *remoteIP = "10.42.0.1"; // 广播地址或目标IP

// void setup()
// {
//     Serial.begin(115200);

//     // 连接Wi-Fi
//     WiFi.begin(ssid, password);
//     Serial.print("Connecting to WiFi");
//     while (WiFi.status() != WL_CONNECTED)
//     {
//         delay(500);
//         Serial.print(".");
//     }
//     Serial.println();
//     Serial.print("Connected with IP: ");
//     Serial.println(WiFi.localIP());

//     // 初始化UDP
//     if (udp.begin(localPort))
//     {
//         Serial.println("UDP initialized");
//     }
//     else
//     {
//         Serial.println("Failed to initialize UDP");
//     }
// }

// void loop()
// {
//     // 构造要发送的数据
//     String message = "Hello from ESP32 UDP Sender";

//     // 发送UDP数据包
//     udp.beginPacket(remoteIP, remotePort);
//     udp.print(message);
//     int result = udp.endPacket();

//     if (result == 1)
//     {
//         Serial.println("UDP packet sent successfully");
//     }
//     else
//     {
//         Serial.println("Failed to send UDP packet");
//     }
//     delay(100); // 每隔5秒发送一次
// }
