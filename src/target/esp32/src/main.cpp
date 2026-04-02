#include "SparkFunMPU9250-DMP.h"
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <glove.h>

// 设备配置
#define NAME_LEFT     //注释这行名字就是right 
#ifdef NAME_LEFT 
#define DEVICE_NAME "Glove_Left"
Glove myglove = Glove(0,4,3,2,1);
#else
#define DEVICE_NAME "Glove_Right"
Glove myglove = Glove(0,1,2,3,4);
#endif

#define CAL_PLAM_PIN  5
#define CAL_FIST_PIN  6

#define SERVICE_UUID "df1413de-2317-4dca-8b04-551ccc2f399b"
#define CHARACTERISTIC_UUID "df1413de-2317-4dca-8b04-551ccc2f399b"

//数据包格式
enum{
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

typedef struct{
    float data[PAK_NUM];
}Pak; 

Pak pak={0};

MPU9250_DMP imu;

unsigned char regadd;
char registeradress[5];
unsigned char registerdata[]={33};

BLECharacteristic *pCharacteristic;
bool deviceConnected = false;

// 蓝牙事件回调
class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      deviceConnected = true;
      Serial.println("设备已连接");
    }
    void onDisconnect(BLEServer* pServer) {
      deviceConnected = false;
      Serial.println("设备已断开");
      pServer->startAdvertising(); // 重新广播
    }
};
 
// 蓝牙初始化
void ble_init(){
  BLEDevice::init(DEVICE_NAME);
  BLEServer *pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());
  
  // 创建服务与特征
  BLEService *pService = pServer->createService(SERVICE_UUID);
  pCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_READ | 
    BLECharacteristic::PROPERTY_WRITE | 
    BLECharacteristic::PROPERTY_NOTIFY
  );
  pCharacteristic->addDescriptor(new BLE2902());
  //pCharacteristic->setCallbacks(new RxCallbacks());

  pService->start();
  
  // 开始广播
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->start();
  Serial.println("BLE广播已启动");
}


//蓝牙发送数据包
void send_data(Pak pak){
    std::string str="";
    for(int i=0;i<PAK_NUM;i++){
      str=str+std::to_string(pak.data[i]);
      if(i!=PAK_NUM-1)str+=',';
    }
    //Serial.printf("send:%s\n",str.c_str());
    pCharacteristic->setValue(str);
    pCharacteristic->notify();
}

typedef struct {
    float time;

    float ax,ay,az;
    float gx,gy,gz;
    float mx,my,mz;

    float sax,say,saz;
    float pitch=0,roll=0,yaw=0;
    float accX=0,accY=0,accZ=0;
    float avX=0,avY=0,avZ=0;
    float apX=0,apY=0,apZ=0;
}IMU_DATA;

IMU_DATA imu_data;

void setup() {
  Serial.begin(115200);
  pinMode(CAL_PLAM_PIN,INPUT_PULLUP);
  pinMode(CAL_FIST_PIN,INPUT_PULLUP);
  ble_init();
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
    myglove.loadCalibrate();
}


void bodyToNavigationFrame(IMU_DATA * data) {
    // 将角度转换为弧度
    // float roll_rad = data->roll * M_PI / 180.0f;
    // float pitch_rad = data->pitch * M_PI / 180.0f;
    // float yaw_rad = data->yaw * M_PI / 180.0f;

    // 计算旋转矩阵（Z-Y-X顺序，即先横滚，再俯仰，最后偏航）
    float cr = cosf(data->roll);   // cos(roll)
    float sr = sinf(data->roll);   // sin(roll)
    float cp = cosf(data->pitch);  // cos(pitch)
    float sp = sinf(data->pitch);  // sin(pitch)
    float cy = cosf(data->yaw);    // cos(yaw)
    float sy = sinf(data->yaw);    // sin(yaw)

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
void remove_gravity(IMU_DATA * data) {
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
    data->saz += gz;  // 减去重力加速度(1g)
}

void attitude_estimation(IMU_DATA * data) {
    static float roll_acc, pitch_acc;
    static float gyro_roll, gyro_pitch, gyro_yaw;

    // 计算加速度计测量的角度
    roll_acc = atan2f(data->ay,data->az) * 180.0f / M_PI;
    pitch_acc = atan2f(-data->ax, sqrtf(data->ay * data->ay + data->az * data->az)) * 180.0f / M_PI;

    float dt = imu_data.time;
    // 计算陀螺仪积分角度
    gyro_roll = data->roll + data->gx * dt;
    gyro_pitch = data->pitch + data->gy * dt;
    gyro_yaw = data->yaw + data->gz * dt;

    // 互补滤波融合
    float alpha = 0;//0.98f;
    data->roll = alpha * gyro_roll + (1 - alpha) * roll_acc;
    data->pitch = alpha * gyro_pitch + (1 - alpha) * pitch_acc;
    data->yaw = gyro_yaw;  // 简化处理，实际应融合磁力计数据

    data->pitch = data->pitch * M_PI /180;
    data->roll  = data->roll  * M_PI /180;
    data->yaw   = data->yaw   * M_PI /180;
}

void calc_v(IMU_DATA * data){
  float dt = imu_data.time;
  data->avX += data->accX * dt; 
  data->avY += data->accY * dt; 
  data->avZ += data->accZ * dt; 
}

void calc_acc(){
  //imu_data.time = (imu.time-imu_data.time)/1000000.000000f;
  imu_data.ax = imu.calcAccel(imu.ax);
  imu_data.ay = imu.calcAccel(imu.ay); 
  imu_data.az = imu.calcAccel(imu.az); 
  imu_data.gx = imu.calcGyro(imu.gx);
  imu_data.gy = imu.calcGyro(imu.gy);
  imu_data.gz = imu.calcGyro(imu.gz);
  imu_data.mx = imu.calcMag(imu.mx);
  imu_data.my = imu.calcMag(imu.my);
  imu_data.mz = imu.calcMag(imu.mz);

  attitude_estimation(&imu_data);

  //移除重力分量
  remove_gravity(&imu_data);

  //计算绝对坐标系加速度
  bodyToNavigationFrame(&imu_data);

  calc_v(&imu_data);
  
  Serial.printf(":%f,%f,%f,%f,%f,%f,%f\n",imu_data.sax,imu_data.say,imu_data.saz,
    imu_data.avX,imu_data.avY,imu_data.avZ,imu_data.time);

  //Serial.printf(":%f,%f,%f\n",imu_data.pitch,imu_data.roll,imu_data.yaw);

  //Serial.printf(":%f,%f,%f\n",imu_data.gx,imu_data.gy,imu_data.gz);
  //Serial.printf(":%f,%f,%f\n",imu_data.accX,imu_data.accY,imu_data.accZ);
  //Serial.printf("%.3f %.3f %.3f\n",imu_data.accX,imu_data.accY,imu_data.accZ);
} 

void calc_all(double deltaT){
  // calc_acc();
  // calc_speed(imu.time);
  // calc_pos(imu.time);
}

void loop(){
  double lastTime = millis();
  double timestamp = millis();
  if (imu.fifoAvailable()){//fifo is not being available
    // Use dmpUpdateFifo to update the ax, gx, mx, etc. values
    
    if ( imu.dmpUpdateFifo() == INV_SUCCESS){
      imu_data.time = (imu.time-imu_data.time);
      // computeEulerAngles can be used -- after updating the
      // quaternion values -- to estimate roll, pitch, and yaw
      imu.computeEulerAngles();
      //printIMUData();
      imu.update(UPDATE_ACCEL | UPDATE_GYRO | UPDATE_COMPASS);
      timestamp = millis();
      //calc_all((timestamp-lastTime)/1000.0000f);
      calc_acc();
      

      //打包数据并且发送
      pak.data[PAK_TIME]=timestamp/1000.0000f;
      pak.data[PAK_YAW]=imu.yaw;
      pak.data[PAK_ROLL]=imu.roll;
      pak.data[PAK_PITCH]=imu.pitch;
      
      float * angles = myglove.getAngles();
      pak.data[PAK_FINGER_THUMB]  = angles[0];
      pak.data[PAK_FINGER_INDEX]  = angles[1];
      pak.data[PAK_FINGER_MIDDLE] = angles[2];
      pak.data[PAK_FINGER_RING]   = angles[3];
      pak.data[PAK_FINGER_LITTLE] = angles[4];
      send_data(pak);
      //Serial.printf("%f %f %f %f %f\n",angles[0],angles[1],angles[2],angles[3],angles[4]);
      lastTime = timestamp;
    }
  }
  if(digitalRead(CAL_PLAM_PIN)==LOW){
    delay(20);
    if(digitalRead(CAL_PLAM_PIN)==LOW){
      float * angles = myglove.getAngles();
      for(int i=0;i<5;i++){
        myglove.calibrate((FINGER_T)i,HAND_STATE_PALM);
      }
      myglove.saveCalibrate();
      while (digitalRead(CAL_PLAM_PIN)==LOW);
      delay(20);
    }
  }

  if(digitalRead(CAL_FIST_PIN)==LOW){
    delay(20);
    if(digitalRead(CAL_FIST_PIN)==LOW){
      float * angles = myglove.getAngles();
      for(int i=0;i<5;i++){
        myglove.calibrate((FINGER_T)i,HAND_STATE_FIST);
      }
      myglove.saveCalibrate();
      while (digitalRead(CAL_FIST_PIN)==LOW);
      delay(20);
    }
  }

  
}