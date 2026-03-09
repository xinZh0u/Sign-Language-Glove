#include "MPU9250_ZX.h"

// //一次积分计算速度
// void MPU9250_ZX::calcSpeed(float deltaT){
//     xyzFloat gVal = getGValues();
//     speed.x += gVal.x*deltaT;
//     speed.y += gVal.y*deltaT;         
//     speed.z += (gVal.z-getResultantG(gVal))*deltaT;
// }

// //二次积分计算位置
// void MPU9250_ZX::calcPos(float deltaT){
//     // xyzFloat a = {0,0,0};
//     // filterAngle.pitch;//y
//     // filterAngle.roll;//x
//     // filterAngle.yaw;//z
//     pos.x += speed.x*deltaT;
//     pos.y += speed.y*deltaT;
//     pos.z += speed.z*deltaT;
// }

// void MPU9250_ZX::calcAll(float deltaT){
//     calcAngleAngle(deltaT);
//     calcSpeed(deltaT);
//     calcPos(deltaT);
// }
