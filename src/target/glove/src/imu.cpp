#include "imu.h"

void Imu::begin(){
    
    if (!imu.init())
    {
        Serial.println("MPU6500 does not respond");
    }
    else
    {
        Serial.println("MPU6500 is connected");
    }

    cali_load();

    imu.enableGyrDLPF();
    imu.setGyrDLPF(MPU6500_DLPF_6);
    imu.setSampleRateDivider(5);
    imu.setGyrRange(MPU6500_GYRO_RANGE_2000);
    imu.setAccRange(MPU6500_ACC_RANGE_16G);
    imu.enableAccDLPF(true);
    imu.setAccDLPF(MPU6500_DLPF_6);

    delay(200);
}

void Imu::cali_load(){
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


void Imu::cali_save()
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
    // ESP.restart();
}

void Imu::calculate_attitude(float dt)
{
    // 1. 归一化加速度计数据
    float norm = sqrt(ax * ax + ay * ay + az * az);
    if (norm < 1e-6)
    {
        pitch = roll = yaw = 0.0f;
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
    pitch = (1.0f - BETA) * pitch_gyro + BETA * pitch_acc;
    roll = (1.0f - BETA) * roll_gyro + BETA * roll_acc;
    yaw = yaw_gyro; // 无校正，仅积分

    // 5. 转换为角度制输出
    pitch = pitch * 180.0f / PI;
    roll = roll * 180.0f / PI;
    yaw = yaw * 180.0f / PI;
}

void Imu::update(){
    float dt = millis() - last_time;
    last_time = millis();
    xyzFloat acc = imu.getGValues();
    xyzFloat gyr = imu.getGyrValues();
    float temp = imu.getTemperature();
    float resultantG = imu.getResultantG(acc);
    
    ax = acc.x;
    ay = acc.y;
    az = acc.z;

    // 转换为 rad/s
    gx = gyr.x * 0.0174533f; 
    gy = gyr.y * 0.0174533f;
    gz = gyr.z * 0.0174533f;

    calculate_attitude(dt / 1000.0000f);
}
