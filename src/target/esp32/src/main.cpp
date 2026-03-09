// #include <BLEDevice.h>
// #include <BLEServer.h>
// #include <BLEUtils.h>
// #include <BLE2902.h>
// #include <MPU9250_ZX.h>
// #include <Arduino.h>
// #include <Wire.h>

// // 设备配置
// #define NAME_LEFT     //注释这行名字就是right 
// #ifdef NAME_LEFT 
// #define DEVICE_NAME "Glove_Left"
// #else
// #define DEVICE_NAME "Glove_Right"
// #endif

// #define SERVICE_UUID "df1413de-2317-4dca-8b04-551ccc2f399b"
// #define CHARACTERISTIC_UUID "df1413de-2317-4dca-8b04-551ccc2f399b"

// enum{
//     PAK_POS_X,
//     PAK_POS_Y,
//     PAK_POS_Z,
//     PAK_FINGER_1,
//     PAK_FINGER_2,
//     PAK_FINGER_3,
//     PAK_FINGER_4,
//     PAK_FINGER_5,
//     PAK_NUM
// };

// BLECharacteristic *pCharacteristic;
// bool deviceConnected = false;

// // 蓝牙事件回调
// class MyServerCallbacks: public BLEServerCallbacks {
//     void onConnect(BLEServer* pServer) {
//       deviceConnected = true;
//       Serial.println("设备已连接");
//     }
//     void onDisconnect(BLEServer* pServer) {
//       deviceConnected = false;
//       Serial.println("设备已断开");
//       pServer->startAdvertising(); // 重新广播
//     }
// };

// void flex_init(){
//   pinMode(0,INPUT);
//   pinMode(1,INPUT);
//   pinMode(2,INPUT);
//   pinMode(3,INPUT);
//   pinMode(4,INPUT);
// }

// void ble_init(){
//   // 初始化BLE
//   BLEDevice::init(DEVICE_NAME);
//   BLEServer *pServer = BLEDevice::createServer();
//   pServer->setCallbacks(new MyServerCallbacks());
  
//   // 创建服务与特征
//   BLEService *pService = pServer->createService(SERVICE_UUID);
//   pCharacteristic = pService->createCharacteristic(
//     CHARACTERISTIC_UUID,
//     BLECharacteristic::PROPERTY_READ | 
//     BLECharacteristic::PROPERTY_WRITE | 
//     BLECharacteristic::PROPERTY_NOTIFY
//   );
//   pCharacteristic->addDescriptor(new BLE2902());
//   pService->start();
  
//   // 开始广播
//   BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
//   pAdvertising->addServiceUUID(SERVICE_UUID);
//   pAdvertising->start();
//   Serial.println("BLE广播已启动");
// }

// typedef struct{
//     float data[PAK_NUM];
// }Pak; 

// void send_data(Pak pak){
//     std::string str="";
//     for(int i=0;i<PAK_NUM;i++){
//       str=str+std::to_string(pak.data[i]);
//       if(i!=PAK_NUM-1)str+=',';
//     }
//     Serial.printf("send:%s\n",str.c_str());
//     pCharacteristic->setValue(str);
//     pCharacteristic->notify();
// }

// Pak pak={0};

// #define MPU9250_ADDR 0x68

// MPU9250_ZX myMPU9250 = MPU9250_ZX(MPU9250_ADDR);

// void setup() {
//   flex_init();
//   ble_init();
//   Serial.begin(9600);
//   Wire.setPins(8,9);
//   Wire.begin();
//   if(!myMPU9250.init()){
//     Serial.println("MPU9250 does not respond");
//   }
//   else{
//     Serial.println("MPU9250 is connected");
//   }
//   if(!myMPU9250.initMagnetometer()){
//     Serial.println("Magnetometer does not respond");
//   }
//   else{
//     Serial.println("Magnetometer is connected");
//   }

//   Serial.println("Position you MPU9250 flat and don't move it - calibrating...");
//   delay(1000);
//   myMPU9250.autoOffsets();
//   Serial.println("Done!");
  
//   myMPU9250.enableGyrDLPF();
//   myMPU9250.setGyrDLPF(MPU9250_DLPF_6);
//   myMPU9250.setSampleRateDivider(5);
//   myMPU9250.setGyrRange(MPU9250_GYRO_RANGE_2000);
//   myMPU9250.setAccRange(MPU9250_ACC_RANGE_2G);
//   myMPU9250.enableAccDLPF(true);
//   myMPU9250.setAccDLPF(MPU9250_DLPF_6);
//   myMPU9250.setMagOpMode(AK8963_CONT_MODE_100HZ);
//   delay(200);
// }

// float getPitch(xyzFloat angleVal){
//     float pitch = (atan2(-angleVal.x, sqrt(abs((angleVal.y*angleVal.y + angleVal.z*angleVal.z))))*180.0)/M_PI;
//     return pitch;
// }


// float getRoll(xyzFloat angleVal){
//     float roll = (atan2(angleVal.y, angleVal.z)*180.0)/M_PI;
//     return roll;
// }

// float getYaw(xyzFloat angleVal){
//     float roll = (atan2(angleVal.x, angleVal.y)*180.0)/M_PI;
//     return roll;
// }

// double lastTime = millis();// / 1000;
// void loop(){
//     double timestamp = millis();// / 1000;
//     myMPU9250.calcAll((timestamp-lastTime)/1000);
//     lastTime = timestamp;
//     //xyzFloat speed = myMPU9250.getGValues();
//     xyzDouble speed =  myMPU9250.getSpeed();
//     xyzDouble pos =  myMPU9250.getPos();
//     eulerAngle angle =  myMPU9250.getFliterAngle();
//     //Serial.printf("mpu9250:%f,%f,%f,%f,%f,%f\n",speed.x,speed.y,speed.z,pos.x,pos.y,pos.z);           
//     Serial.printf("mpu9250:%f,%f,%f,%f,%f,%f\n",angle.pitch,angle.roll,myMPU9250.getPitch(),myMPU9250.getRoll(),angle.yaw,(timestamp-lastTime)/1000);
    
//     pak.data[0]=angle.yaw;
//     pak.data[1]=angle.roll;
//     pak.data[2]=angle.pitch;

//     Serial.printf("read:");
//     for(int i=0;i<5;i++){
//       uint16_t data = analogRead(i);
//       Serial.printf("%4d ",data);
//       pak.data[PAK_FINGER_1+i]=90-data*90/4095;
//     }
//     Serial.printf("\n");
//     send_data(pak);
// }

#include "SparkFunMPU9250-DMP.h"

MPU9250_DMP imu;

unsigned char regadd;
char registeradress[5];
unsigned char registerdata[]={33};

//Prorotypes
void printIMUData(void);

void setup() {
  Serial.begin(115200);
  Wire.setPins(8,9);
  Wire.begin();
  // Call imu.begin() to verify communication and initialize
  if (imu.begin() != INV_SUCCESS){
    while (1){
      Serial.printf("Unable to communicate with MPU-9250");
      Serial.printf("Check connections, and try again.\n");
      delay(5000);
      //wait_ms(5000);
    }
  }
    Serial.printf("imu.begin() suceeded\n");
  
    if(imu.dmpBegin(DMP_FEATURE_6X_LP_QUAT | // Enable 6-axis quat
               DMP_FEATURE_GYRO_CAL, // Use gyro calibration
              150)==INV_ERROR){ // Set DMP FIFO rate to 150 Hz
        Serial.printf("imu.dmpBegin have failed\n");//dmpLoad function under it fails which is caused by memcmp(firmware+ii, cur, this_write) (it is located at row 2871 of inv_mpu.c)
              }
    else{
        Serial.printf("imu.dmpBegin() suceeded\n");
    }
    Serial.printf("$GETEU,*\n");
// while(1){
//     if(pc.readable()){
//         Serial.scanf("%s",&registeradress);
//         regadd=(registeradress[0]-48)*100+(registeradress[1]-48)*10+(registeradress[2]-48);
//         mbed_i2c_read(0x68,(unsigned)regadd,1,registerdata);
//         pc.printf("%d is gotten from serial port, data at that register is %d\n",regadd,registerdata[0]);
//     }

//   // Check for new data in the FIFO
//   if (imu.fifoAvailable()){//fifo is not being available
//     led=0;
//     wait_ms(1);
//     led=1;
//     wait_ms(1);
//     // Use dmpUpdateFifo to update the ax, gx, mx, etc. values
//     if ( imu.dmpUpdateFifo() == INV_SUCCESS){
//       // computeEulerAngles can be used -- after updating the
//       // quaternion values -- to estimate roll, pitch, and yaw
//       imu.computeEulerAngles();
//       printIMUData();
//     }
//   }
//   else{
//     led=0;
//   }
// }
//   return 0;
}

void printIMUData(void)
{  
  // After calling dmpUpdateFifo() the ax, gx, mx, etc. values
  // are all updated.
  // Quaternion values are, by default, stored in Q30 long
  // format. calcQuat turns them into a float between -1 and 1
  imu.update(UPDATE_ACCEL | UPDATE_GYRO | UPDATE_COMPASS);
  float q0 = imu.calcQuat(imu.qw);
  float q1 = imu.calcQuat(imu.qx);
  float q2 = imu.calcQuat(imu.qy);
  float q3 = imu.calcQuat(imu.qz);
  float accelX = imu.calcAccel(imu.ax); // accelX is x-axis acceleration in g's
  float accelY = imu.calcAccel(imu.ay); // accelY is y-axis acceleration in g's
  float accelZ = imu.calcAccel(imu.az); // accelZ is z-axis acceleration in g's

  float gyroX = imu.calcGyro(imu.gx); // gyroX is x-axis rotation in dps
  float gyroY = imu.calcGyro(imu.gy); // gyroY is y-axis rotation in dps
  float gyroZ = imu.calcGyro(imu.gz); // gyroZ is z-axis rotation in dps

  float magX = imu.calcMag(imu.mx); // magX is x-axis magnetic field in uT
  float magY = imu.calcMag(imu.my); // magY is y-axis magnetic field in uT
  float magZ = imu.calcMag(imu.mz); // magZ is z-axis magnetic field in uT

  // float G = 0.0;
  // G = sqrt(sq(gyroX) + sq(gyroY) + sq(gyroZ));
  // float aX,aY,aZ;
  // float aG = 0.9778;  //广州重力加速度
  // aX = cos(imu.pitch*PI/180)*cos(imu.yaw*PI/180)*accelX;//-aG*sin(imu.pitch*PI/180));
  // aY = cos(imu.roll*PI/180)*cos(imu.yaw*PI/180)*accelY;//-aG*sin(imu.roll*PI/180));
  // aZ = cos(imu.roll*PI/180)*cos(imu.pitch*PI/180)*accelZ-1;
  //Serial.printf("G:%4.4lf %4.4lf %4.4lf\n",accelX,accelY,accelZ);
  //Serial.printf("G:%4.4lf %4.4lf %4.4lf\n",aX,aY,aZ);
  //Serial.printf("G:%04d %04d %04d              %4d %4d %4d\n",(int)(accelX*1000),(int)(accelY*1000),(int)(accelZ*1000),(int)imu.pitch,(int)imu.roll,(int)imu.yaw);  
  //Serial.printf(":%f,%f,%f\n",imu.roll,imu.pitch,imu.yaw);
  //float G = cos(imu.roll*PI/180.0000f)*cos(imu.pitch*PI/180.0000f)*accelZ;
  //Serial.printf("$,%4.4lf,%4.4lf,%4.4lf,%4.4lf,%4.4lf,%4.4lf,*\n",accelX,accelY,accelZ, imu.yaw,imu.pitch,imu.roll);
  
}

double aX,aY,aZ;
double vX=0,vY=0,vZ=0;
double pX=0,pY=0,pZ=0;

void calc_acc(){
  float accelX = imu.calcAccel(imu.ax); // accelX is x-axis acceleration in g's
  float accelY = imu.calcAccel(imu.ay); // accelY is y-axis acceleration in g's
  float accelZ = imu.calcAccel(imu.az); // accelZ is z-axis acceleration in g's
  float aG = 0.9778;
  double aaX =  cos(imu.pitch*PI/180)*cos(imu.yaw*PI/180)*accelX;
  double aaY =  cos(imu.roll*PI/180)*cos(imu.yaw*PI/180)*accelY;
  double aaZ =  cos(imu.roll*PI/180)*cos(imu.pitch*PI/180)*accelZ;
  //aX = cos(imu.pitch*PI/180)*cos(imu.yaw*PI/180)*(accelX-sin(imu.pitch*PI/180));
  //aY = cos(imu.roll*PI/180)*cos(imu.yaw*PI/180)*(accelY+sin(imu.pitch*PI/180)*sin(imu.roll*PI/180));
  //aZ = cos(imu.roll*PI/180)*cos(imu.pitch*PI/180)*(accelZ-cos(imu.pitch*PI/180)*cos(imu.roll*PI/180));
  aX = cos(imu.pitch*PI/180.0000f)*cos(imu.yaw*PI/180.0000f)*(accelX+aG*sin(imu.pitch*PI/180.0000f));
  aY = cos(imu.roll*PI/180.0000f)*cos(imu.yaw*PI/180.0000f)*(accelY-aG*sin(imu.pitch*PI/180.0000f)*sin(imu.roll*PI/180.0000f));
  aZ = cos(imu.roll*PI/180.0000f)*cos(imu.pitch*PI/180.0000f)*(accelZ+aG*cos(imu.pitch*PI/180.0000f)*cos(imu.roll*PI/180.0000f));

  Serial.printf("%04d %04d %04d %04d %04d %04d\n",(int)(aX*1000),(int)(aY*1000),(int)(aZ*1000),(int)(aaX*1000),(int)(aaY*1000),(int)(aaZ*1000));
} 

void calc_speed(double deltaT){
  vX += deltaT*aX;
  vY += deltaT*aY;
  vZ += deltaT*aZ;
}

void calc_pos(double deltaT){
  pX += deltaT*vX;
  pY += deltaT*vY;
  pZ += deltaT*vZ;
}

void calc_all(double deltaT){
  calc_acc();
  calc_speed(deltaT);
  calc_pos(deltaT);
}

void loop(){
  // Check for new data in the FIFO
  double lastTime = millis();// / 1000;
  double timestamp = millis();// / 1000;
  if (imu.fifoAvailable()){//fifo is not being available
    // Use dmpUpdateFifo to update the ax, gx, mx, etc. values
    if ( imu.dmpUpdateFifo() == INV_SUCCESS){
      // computeEulerAngles can be used -- after updating the
      // quaternion values -- to estimate roll, pitch, and yaw
      imu.computeEulerAngles();
      //printIMUData();
      imu.update(UPDATE_ACCEL | UPDATE_GYRO | UPDATE_COMPASS);
      timestamp = millis();
      calc_all((timestamp-lastTime)/1000.0000f);
      lastTime = timestamp;
    }
  }
}