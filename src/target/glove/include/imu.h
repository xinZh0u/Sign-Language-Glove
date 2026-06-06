#ifndef _IMU_H_
#define _IMU_H_

#include<EEPROM.h>
#include"MPU6500_WE.h"

#define IMU_CALI_ADDR 100
#define BETA 0.1

#define MPU6500_ADDR 0x68

class Imu
{
public:
    //Imu();
    void begin();
    void cali_load();
    void cali_save();
    void update();
    float pitch, yaw, roll;
private:
    MPU6500_WE imu =  MPU6500_WE(MPU6500_ADDR);
    float ax,ay,az;
    float gx,gy,gz;
    float last_time = 0;
    void calculate_attitude(float dt);
};

#endif
