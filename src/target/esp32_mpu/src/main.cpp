#include <Arduino.h>
#include "MPU9250.h"
extern "C"
{
#include "MahonyAHRS.h"
}
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <glove.h>

#define MPU9250_ADDR 0x68

// 设备配置
#define NAME_LEFT // 注释这行名字就是right
#ifdef NAME_LEFT
#define DEVICE_NAME "Glove_Left"
Glove myglove = Glove(0, 4, 3, 2, 1);
#else
#define DEVICE_NAME "Glove_Right"
Glove myglove = Glove(0, 1, 2, 3, 4);
#endif

#define CAL_PLAM_PIN 5
#define CAL_FIST_PIN 6

#define SERVICE_UUID "df1413de-2317-4dca-8b04-551ccc2f399b"
#define CHARACTERISTIC_UUID "df1413de-2317-4dca-8b04-551ccc2f399b"

MPU9250 mpu;

// 数据包格式
enum
{
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
void send_data(Pak pak)
{
    std::string str = "";
    for (int i = 0; i < PAK_NUM; i++)
    {
        str = str + std::to_string(pak.data[i]);
        if (i != PAK_NUM - 1)
            str += ',';
    }
    // Serial.printf("send:%s\n",str.c_str());
    pCharacteristic->setValue(str);
    pCharacteristic->notify();
}

typedef struct
{
    float time;

    float ax, ay, az;

    float ogx = 2.836123, ogy = -2.999731, ogz = -2.268440;
    int sum = 0;
    float gx, gy, gz;
    float gwx = 0, gwy = 0, gwz = 0;

    float mx, my, mz;

    float sax, say, saz;
    float pit = 0, ro = 0, ya = 0;
    float pitch = 0, roll = 0, yaw = 0;

    float accX = 0, accY = 0, accZ = 0;
    float avX = 0, avY = 0, avZ = 0;
    float apX = 0, apY = 0, apZ = 0;
} IMU_DATA;

IMU_DATA imu_data;

void imu_init()
{
    MPU9250Setting setting;
    setting.accel_fs_sel = ACCEL_FS_SEL::A16G;
    setting.gyro_fs_sel = GYRO_FS_SEL::G2000DPS;
    setting.mag_output_bits = MAG_OUTPUT_BITS::M16BITS;
    setting.fifo_sample_rate = FIFO_SAMPLE_RATE::SMPL_200HZ;
    setting.gyro_fchoice = 0x03;
    setting.gyro_dlpf_cfg = GYRO_DLPF_CFG::DLPF_41HZ;
    setting.accel_fchoice = 0x01;
    setting.accel_dlpf_cfg = ACCEL_DLPF_CFG::DLPF_45HZ;

    if (!mpu.setup(0x68, setting)) {  // change to your own address
        while (1) {
            Serial.println("MPU connection failed. Please check your connection with `connection_check` example.");
            delay(5000);
        }
    }
    delay(1000);
}

void setup()
{
    Serial.begin(115200);
    pinMode(CAL_PLAM_PIN, INPUT_PULLUP);
    pinMode(CAL_FIST_PIN, INPUT_PULLUP);
    ble_init();
    Wire.setPins(8, 9);
    Wire.begin();

    myglove.loadCalibrate();
    imu_init();
}

void bodyToNavigationFrame(IMU_DATA *data)
{
    // 将角度转换为弧度
    // float roll_rad = data->roll * M_PI / 180.0f;
    // float pitch_rad = data->pitch * M_PI / 180.0f;
    // float yaw_rad = data->yaw * M_PI / 180.0f;

    // 计算旋转矩阵（Z-Y-X顺序，即先横滚，再俯仰，最后偏航）
    float cr = cosf(data->roll);  // cos(roll)
    float sr = sinf(data->roll);  // sin(roll)
    float cp = cosf(data->pitch); // cos(pitch)
    float sp = sinf(data->pitch); // sin(pitch)
    float cy = cosf(data->yaw);   // cos(yaw)
    float sy = sinf(data->yaw);   // sin(yaw)

    // 旋转矩阵 R = R_z(yaw) * R_y(pitch) * R_x(roll)
    // 但实际计算时，我们使用 R^T（逆矩阵）来转换向量
    // 因为 v_nav = R^T * v_body
    float R11 = cp * cy;
    float R12 = cp * sy;
    float R13 = -sp;

    float R21 = sr * sp * cy - cr * sy;
    float R22 = sr * sp * sy + cr * cy;
    float R23 = sr * cp;

    float R31 = cr * sp * cy + sr * sy;
    float R32 = cr * sp * sy - sr * cy;
    float R33 = cr * cp;

    // 计算绝对坐标系下的加速度
    data->accX = R11 * data->sax + R12 * data->say + R13 * data->saz;
    data->accY = R21 * data->sax + R22 * data->say + R23 * data->saz;
    data->accZ = R31 * data->sax + R32 * data->say + R33 * data->saz;
}

// 去除重力影响
void remove_gravity(IMU_DATA *data)
{
    // 将角度转换为弧度
    // float roll_rad = euler_angle.roll * M_PI / 180.0f;
    // float pitch_rad = euler_angle.pitch * M_PI / 180.0f;

    // 计算重力在载体坐标系下的分量
    float gx = sin(data->pitch);
    float gy = -sin(data->roll) * cos(data->pitch);
    float gz = cos(data->roll) * cos(data->pitch);

    data->sax = data->ax;
    data->say = data->ay;
    data->saz = data->az;

    // 去除重力分量
    data->sax += gx;
    data->say += gy;
    data->saz -= gz; // 减去重力加速度(1g)
}

void attitude_estimation(IMU_DATA *data)
{
    static float roll_acc, pitch_acc;
    static float gyro_roll, gyro_pitch, gyro_yaw;

    // 计算加速度计测量的角度
    roll_acc = atan2f(data->ay, data->az) * 180.0f / M_PI;
    pitch_acc = atan2f(-data->ax, sqrtf(data->ay * data->ay + data->az * data->az)) * 180.0f / M_PI;

    float dt = imu_data.time;

    data->gwx += data->gx * dt;
    data->gwy += data->gy * dt;
    data->gwz += data->gz * dt;

    // 计算陀螺仪积分角度
    gyro_roll = data->roll * 180 / M_PI + data->gwx * dt;
    gyro_pitch = data->pitch * 180 / M_PI + data->gwy * dt;
    gyro_yaw = data->yaw * 180 / M_PI + data->gwz * dt;

    // Serial.printf(":%f,%f,%f,%f\n",gyro_pitch,gyro_roll,gyro_yaw,dt);
    //  互补滤波融合
    float alpha = 0.98f;
    data->roll = alpha * gyro_roll + (1 - alpha) * roll_acc;
    data->pitch = alpha * gyro_pitch + (1 - alpha) * pitch_acc;
    data->yaw = gyro_yaw; // 简化处理，实际应融合磁力计数据

    data->pitch = data->pitch * M_PI / 180;
    data->roll = data->roll * M_PI / 180;
    data->yaw = data->yaw * M_PI / 180;
}

void calc_v(IMU_DATA *data)
{
    float dt = imu_data.time;
    data->avX += data->accX * dt;
    data->avY += data->accY * dt;
    data->avZ += data->accZ * dt;
}

void calc_acc()
{
    imu_data.pitch = mpu.getPitch();
    imu_data.yaw = mpu.getYaw();
    imu_data.roll = mpu.getRoll();

    Serial.printf(":%f,%f,%f\n",imu_data.pitch,imu_data.yaw,imu_data.roll);

    // 移除重力分量
    remove_gravity(&imu_data);

    // 计算绝对坐标系加速度
    bodyToNavigationFrame(&imu_data);

    calc_v(&imu_data);

    // Serial.printf(":%f,%f,%f,%f,%f,%f,%f\n",imu_data.sax,imu_data.say,imu_data.saz,
    //   imu_data.avX,imu_data.avY,imu_data.avZ,0.00f);
    imu_data.ogx += imu_data.gx;
    imu_data.ogy += imu_data.gy;
    imu_data.ogz += imu_data.gz;
    imu_data.sum++;
    // Serial.printf(":%f,%f,%f\n",imu_data.ogx/imu_data.sum,imu_data.ogy/imu_data.sum,imu_data.ogz/imu_data.sum);
    // Serial.printf(":%f,%f,%f\n",imu_data.gx,imu_data.gy,imu_data.gz);

    // Serial.printf(":%f,%f,%f,%f,%f\n",imu_data.pitch,imu_data.yaw,imu_data.roll,0.0000f,imu_data.time);

    // Serial.printf(":%f,%f,%f\n",imu_data.gx,imu_data.gy,imu_data.gz);
    // Serial.printf(":%f,%f,%f,%f\n",imu_data.accX,imu_data.accY,imu_data.accZ,0.000f);
}

void loop()
{
    double lastTime = millis();
    double timestamp = millis();
    if(mpu.update()){
        timestamp = millis();
        imu_data.time = (timestamp - lastTime) / 1000.0000f;
        calc_acc();

        // 打包数据并且发送
        pak.data[PAK_TIME] = timestamp / 1000.0000f;
        // pak.data[PAK_YAW] = imu.yaw;
        // pak.data[PAK_ROLL] = imu.roll;
        // pak.data[PAK_PITCH] = imu.pitch;

        float *angles = myglove.getAngles();
        pak.data[PAK_FINGER_THUMB] = angles[0];
        pak.data[PAK_FINGER_INDEX] = angles[1];
        pak.data[PAK_FINGER_MIDDLE] = angles[2];
        pak.data[PAK_FINGER_RING] = angles[3];
        pak.data[PAK_FINGER_LITTLE] = angles[4];
        send_data(pak);
        lastTime = timestamp;
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

// #include <Arduino.h>
// #include "MPU9250.h"

// MPU9250 mpu;

// void setup() {
//     Serial.begin(115200);
//     Wire.begin(8,9,100000);
//     delay(500);

//     MPU9250Setting setting;
//     setting.accel_fs_sel = ACCEL_FS_SEL::A16G;
//     setting.gyro_fs_sel = GYRO_FS_SEL::G2000DPS;
//     setting.mag_output_bits = MAG_OUTPUT_BITS::M16BITS;
//     setting.fifo_sample_rate = FIFO_SAMPLE_RATE::SMPL_200HZ;
//     setting.gyro_fchoice = 0x03;
//     setting.gyro_dlpf_cfg = GYRO_DLPF_CFG::DLPF_41HZ;
//     setting.accel_fchoice = 0x01;
//     setting.accel_dlpf_cfg = ACCEL_DLPF_CFG::DLPF_45HZ;

//     if (!mpu.setup(0x68, setting)) {  // change to your own address
//         while (1) {
//             Serial.println("MPU connection failed. Please check your connection with `connection_check` example.");
//             delay(5000);
//         }
//     }
// }

// void print_roll_pitch_yaw() {
//     Serial.printf(":%f,%f,%f\n",mpu.getPitch(),mpu.getYaw(),mpu.getRoll());
// }
// void loop() {
//     if (mpu.update()) {
//         static uint32_t prev_ms = millis();
//         if (millis() > prev_ms + 25) {
//             print_roll_pitch_yaw();
//             prev_ms = millis();
//         }
//     }
// }

