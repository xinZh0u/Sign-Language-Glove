#include "MPU6500_WE.h"
#include <Wire.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <glove.h>
#include <imu.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <EEPROM.h>

// 设备类型对应的ID
#define DEV_TYPE_CENTER 0
#define DEV_TYPE_L_BIG 1
#define DEV_TYPE_L_SMALL 2
#define DEV_TYPE_L_GLOVE 3
#define DEV_TYPE_R_BIG 4
#define DEV_TYPE_R_SMALL 5
#define DEV_TYPE_R_GLOVE 6

#define DEV_TYPE DEV_TYPE_R_GLOVE

uint16_t glove_pins[FINGER_NUM][FINGER_JOINT_NUM] = {39,35,33,34,26,36,27,25,4,2};

// 设备类型配置
#if DEV_TYPE == DEV_TYPE_L_GLOVE
#define IS_GLOVE
Glove glove = Glove(glove_pins,HAND_LEFT);
#define DEVICE_NAME "Glove_Left"
#elif DEV_TYPE == DEV_TYPE_R_GLOVE
#define IS_GLOVE
Glove glove = Glove(glove_pins,HAND_RIGHT);
#define DEVICE_NAME "Glove_Right"
#else
#define IS_TRACKER
#endif

#define SERVICE_UUID "df1413de-2317-4dca-8b04-551ccc2f399b"
#define CHARACTERISTIC_UUID "df1413de-2317-4dca-8b04-551ccc2f399b"

// 引脚定义
#define BTN_PIN 32

Imu imu = Imu();

// 数据包格式
typedef struct
{
    uint8_t id;
    uint8_t btn;
    float pitch,yaw,roll;
    float fingers[FINGER_NUM][FINGER_JOINT_NUM];
} Pak;

Pak pak = {0};

unsigned char regadd;
char registeradress[5];
unsigned char registerdata[] = {33};

BLECharacteristic *pCharacteristic;
bool deviceConnected = false;

// 蓝牙事件回调
class MyServerCallbacks : public BLEServerCallbacks
{
    void onConnect(BLEServer *pServer)
    {
        deviceConnected = true;
        Serial.println("设备已连接");
    }
    void onDisconnect(BLEServer *pServer)
    {
        deviceConnected = false;
        Serial.println("设备已断开");
        pServer->startAdvertising(); // 重新广播
    }
};

// 蓝牙初始化
void ble_init()
{
    BLEDevice::init(DEVICE_NAME);
    BLEServer *pServer = BLEDevice::createServer();
    pServer->setCallbacks(new MyServerCallbacks());

    // 创建服务与特征
    BLEService *pService = pServer->createService(SERVICE_UUID);
    pCharacteristic = pService->createCharacteristic(
        CHARACTERISTIC_UUID,
        BLECharacteristic::PROPERTY_READ |
            BLECharacteristic::PROPERTY_WRITE |
            BLECharacteristic::PROPERTY_NOTIFY);
    pCharacteristic->addDescriptor(new BLE2902());
    // pCharacteristic->setCallbacks(new RxCallbacks());

    pService->start();

    // 开始广播
    BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->addServiceUUID(SERVICE_UUID);
    pAdvertising->start();
    Serial.println("BLE广播已启动");
}

// 蓝牙发送数据包
void send_data(uint8_t * data,size_t size)
{
    pCharacteristic->setValue(data,size);
    pCharacteristic->notify();
}

/*********************主程序**************************/
float last_time;
void setup()
{
    Serial.begin(115200);
    pinMode(BTN_PIN, INPUT_PULLUP);
    Wire.begin(21, 22);
    ble_init();
    imu.begin();
}

float press_time = 0;
void loop()
{
    float dt = millis() - last_time;
    if(dt>=50){
        last_time = millis();
        imu.update();
        pak.pitch = imu.pitch;
        pak.yaw = imu.yaw;
        pak.roll = imu.roll;

        glove.update();
        memcpy(pak.fingers,glove.angles,sizeof(pak.fingers)); 
        Serial.printf("%4.2f %4.2f %4.2f\n",imu.pitch,imu.yaw,imu.roll);
        send_data((uint8_t*)&pak,sizeof(pak));
    }
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
                imu.cali_save();
                press_time = 0;
            }
            else
            {
                pak.btn = 1;
                send_data((uint8_t*)&pak,sizeof(pak));
            }
        }
    }
    else
    {
        pak.btn = 0;
        press_time = 0;
    }
}
