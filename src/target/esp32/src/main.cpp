#include "MPU6500_WE.h"
#include <Wire.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <glove.h>

// 设备类型对应的ID
#define DEV_TYPE_CENTER 0
#define DEV_TYPE_L_BIG 1
#define DEV_TYPE_L_SMALL 2
#define DEV_TYPE_L_GLOVE 3
#define DEV_TYPE_R_BIG 4
#define DEV_TYPE_R_SMALL 5
#define DEV_TYPE_R_GLOVE 6

#define DEV_TYPE DEV_TYPE_L_BIG

// 设备类型配置
#if DEV_TYPE == DEV_TYPE_L_GLOVE
#define IS_GLOVE
Glove myglove = Glove(0, 4, 3, 2, 1);
#elif DEV_TYPE == DEV_TYPE_R_GLOVE
#define IS_GLOVE
Glove myglove = Glove(0, 1, 2, 3, 4);
#else
#define IS_TRACKER
#endif

// 引脚定义
#define CAL_PLAM_PIN 5
#define CAL_FIST_PIN 6
#define BTN_PIN 21

// Wi-Fi 配置
#define ssid "Oneplus 11"
#define password "19226782798"
#define remoteIP "10.42.0.1" // 目标IP
#define remotePort 4321      // 目标端口
#define localPort 1234       // 本地端口
// 陀螺仪
#define MPU6500_ADDR 0x68
MPU6500_WE imu = MPU6500_WE(MPU6500_ADDR);

WiFiUDP Udp;

// 数据包格式
enum
{
    PAK_DEV,
    PAK_BTN,
    PAK_ROLL,
    PAK_PITCH,
    PAK_YAW,
#ifdef IS_GLOVE
    PAK_FINGER_THUMB,
    PAK_FINGER_INDEX,
    PAK_FINGER_MIDDLE,
    PAK_FINGER_RING,
    PAK_FINGER_LITTLE,
#endif
    PAK_NUM
};

typedef struct
{
    float data[PAK_NUM];
} Pak;

Pak pak = {0};

/*********************WIFI**************************/
void wifi_init()
{
    WiFi.mode(WIFI_STA);
    WiFi.disconnect();
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
    Udp.beginPacket(remoteIP, remotePort); // 配置远端ip地址和端口
    Udp.print(message);
    // Udp.write((uint8_t *)message, (uint8_t)(strlen(message) + 1)); // 把数据写入发送缓冲区
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

void send_pak()
{
    std::string message = "";
    for (int i = 0; i < PAK_NUM; i++)
    {
        message = message + std::to_string(pak.data[i]);
        if (i != PAK_NUM - 1)
            message += ',';
    }
    Serial.println(message.c_str());
    // send_message(message.c_str());
}

/*********************IMU**************************/
#define IMU_CALI_ADDR 100
void imu_cali_load()
{
    // EEPROM中获取校准数据
    float data[6];
    EEPROM.begin(4096);
    for (int i = 0; i < 6; i++)
    {
        data[i] = EEPROM.readFloat(IMU_CALI_ADDR + i * sizeof(float));
    }

    // 获取偏移
    xyzFloat acc, gyr;
    acc.x = data[0];
    acc.y = data[1];
    acc.z = data[2];
    gyr.x = data[3];
    gyr.y = data[4];
    gyr.z = data[5];
    imu.setAccOffsets(acc);
    imu.setGyrOffsets(gyr);
}

void imu_cali_save()
{
    // 自动校准(校准需要重启后才生效)
    Serial.println("Position you MPU6500 flat and don't move it - calibrating...");
    delay(5000);
    imu.autoOffsets();

    // 填充数据
    xyzFloat acc, gyr;
    acc = imu.getAccOffsets();
    gyr = imu.getGyrOffsets();
    float data[6];
    data[0] = acc.x;
    data[1] = acc.y;
    data[2] = acc.z;
    data[3] = gyr.x;
    data[4] = gyr.y;
    data[5] = gyr.z;

    // 写入数据
    EEPROM.begin(4096);
    for (int i = 0; i < 6; i++)
    {
        EEPROM.writeFloat(IMU_CALI_ADDR + i * sizeof(float), data[i]);
    }
    EEPROM.commit();

    // 重启使校准生效
    ESP.restart();
}

void imu_init()
{

    if (!imu.init())
    {
        Serial.println("MPU6500 does not respond");
    }
    else
    {
        Serial.println("MPU6500 is connected");
    }

    imu_cali_load();

    imu.enableGyrDLPF();
    imu.setGyrDLPF(MPU6500_DLPF_6);
    imu.setSampleRateDivider(5);
    imu.setGyrRange(MPU6500_GYRO_RANGE_2000);
    imu.setAccRange(MPU6500_ACC_RANGE_16G);
    imu.enableAccDLPF(true);
    imu.setAccDLPF(MPU6500_DLPF_6);

    delay(200);
}

#define BETA 0.1
float pitch, yaw, roll;
void calculate_attitude(float ax, float ay, float az,
                        float gx, float gy, float gz,
                        float dt, float *pitch, float *roll, float *yaw)
{
    // 1. 归一化加速度计数据
    float norm = sqrt(ax * ax + ay * ay + az * az);
    if (norm < 1e-6)
    {
        *pitch = *roll = *yaw = 0.0f;
        return;
    }
    ax /= norm;
    ay /= norm;
    az /= norm;

    // 2. 计算初始俯仰和横滚（基于重力向量）
    float pitch_acc = atan2f(ay, az);
    float roll_acc = atan2f(-ax, sqrt(ay * ay + az * az));

    // 3. 陀螺仪积分（单位：弧度/秒 → 弧度）
    static float pitch_gyro = 0.0f, roll_gyro = 0.0f, yaw_gyro = 0.0f;
    pitch_gyro += gx * dt;
    roll_gyro += gy * dt;
    yaw_gyro += gz * dt;

    // 4. 互补滤波融合：加速度计校正俯仰/横滚，陀螺仪主导偏航
    // 注意：偏航角无法由加速度计校正，需磁力计，此处仅做陀螺积分（有漂移）
    *pitch = (1.0f - BETA) * pitch_gyro + BETA * pitch_acc;
    *roll = (1.0f - BETA) * roll_gyro + BETA * roll_acc;
    *yaw = yaw_gyro; // 无校正，仅积分

    // 5. 转换为角度制输出
    *pitch = *pitch * 180.0f / PI;
    *roll = *roll * 180.0f / PI;
    *yaw = *yaw * 180.0f / PI;
}

/*********************主程序**************************/
float last_time;

void setup()
{
    Serial.begin(115200);
    pinMode(CAL_PLAM_PIN, INPUT_PULLUP);
    pinMode(CAL_FIST_PIN, INPUT_PULLUP);
    pinMode(BTN_PIN, INPUT_PULLUP);
    Wire.begin(8, 9);
    // wifi_init();

#ifdef IS_GLOVE
    myglove.loadCalibrate();
#endif

    imu_init();
    pak.data[PAK_DEV] = DEV_TYPE;
    last_time = millis();
}

float press_time = 0;

void loop()
{
    float dt = millis() - last_time;
    if (dt >= 50)
    {
        last_time = millis();
        xyzFloat acc = imu.getGValues();
        xyzFloat gyr = imu.getGyrValues();
        float temp = imu.getTemperature();
        float resultantG = imu.getResultantG(acc);

        // 将单位转换为标准单位
        gyr.x *= 0.0174533f; // 转换为 rad/s
        gyr.y *= 0.0174533f;
        gyr.z *= 0.0174533f;

        calculate_attitude(acc.x, acc.y, acc.z, gyr.x, gyr.y, gyr.z, dt / 1000.0000f, &pitch, &roll, &yaw);

        pak.data[PAK_PITCH] = pitch;
        pak.data[PAK_ROLL] = roll;
        pak.data[PAK_YAW] = yaw;

#ifdef IS_GLOVE
        float *angles = myglove.getAngles();
        pak.data[PAK_FINGER_THUMB] = angles[0];
        pak.data[PAK_FINGER_INDEX] = angles[1];
        pak.data[PAK_FINGER_MIDDLE] = angles[2];
        pak.data[PAK_FINGER_RING] = angles[3];
        pak.data[PAK_FINGER_LITTLE] = angles[4];
#endif

        send_pak();
    }

#ifdef IS_GLOVE
    // 手指张开校准
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

    // 手指握拳校准
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
#endif
#ifdef IS_TRACKER
    // 检测按键按下
    if (digitalRead(BTN_PIN) == LOW)
    {
        delay(20);
        if (digitalRead(BTN_PIN) == LOW)
        {
            if (press_time <= 0)
            {
                press_time = millis();
            }
            if (millis() - press_time >= 500)
            {
                imu_cali_save();
                press_time = 0;
            }
            else
            {
                pak.data[PAK_BTN] = 1;
                send_pak();
            }
        }
    }
    else
    {
        pak.data[PAK_BTN] = 0;
        press_time = 0;
    }
#endif
}
