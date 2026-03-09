// #include <Arduino.h>
// #include <BLEDevice.h>
// #include <BLEServer.h>
// #include <BLEUtils.h>
// #include <BLE2902.h>

// // 设备配置
// #define SERVICE_UUID "b4250400-1102-11e9-8f0b-362b9e155667"
// #define CHARACTERISTIC_UUID "b4250401-1102-11e9-8f0b-362b9e155667"

// class BTSerial{
// public:
//     BTSerial::BTSerial(std::string name,std::string passwd);
// private:
//     std::string name;
//     std::string passwd;
// };


// BTSerial::BTSerial(std::string name,std::string passwd)
// :name(name),passwd(passwd)
// {
//     // 初始化BLE
//     BLEDevice::init(name);
//     BLEServer *pServer = BLEDevice::createServer();
//     pServer->setCallbacks(new MyServerCallbacks());
  
//     // 创建服务与特征
//     BLEService *pService = pServer->createService(SERVICE_UUID);
//     pCharacteristic = pService->createCharacteristic(
//     CHARACTERISTIC_UUID,
//     BLECharacteristic::PROPERTY_READ | 
//     BLECharacteristic::PROPERTY_WRITE | 
//     BLECharacteristic::PROPERTY_NOTIFY
//     );
//     pCharacteristic->addDescriptor(new BLE2902());
//     pService->start();
// }



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

// void setup() {
//   Serial.begin(115200);
  
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

// void loop() {
//   // 接收串口数据并转发到BLE
//   if (Serial.available()) {
//     String data = Serial.readStringUntil('\n');
//     pCharacteristic->setValue(data.c_str());
//     pCharacteristic->notify();
//     Serial.println("发送: " + data);
//   }
  
//   // 接收BLE数据并转发到串口
//   // if (deviceConnected && pCharacteristic->getValueLength() > 0) {
//   //   String received = pCharacteristic->getValue();
//   //   Serial.println("接收: " + received);
//   //   pCharacteristic->setValue(""); // 清空缓存
//   // }
//   delay(10);
// }
