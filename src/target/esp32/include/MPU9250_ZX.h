#include "SparkFunMPU9250-DMP.h"
#include <cmath>     

// //对MPU9250_DMP进行二次封装,实现角度解算和位置解算
// //目前手中的mpu9250没有磁力计
class MPU9250_ZX : public MPU9250_DMP{
    public:
        double x=0,y=0,z=0;

        void calc_(float deltaT);
    private:    
};

