#include "glove.h"


Glove::Glove(uint16_t thumbPin,uint16_t indexPin,
    uint16_t middlePin,uint16_t ringPin,uint16_t littlePin){
    fingers[FINGER_THUMB].pin=thumbPin;
    fingers[FINGER_INDEX].pin=indexPin;
    fingers[FINGER_MIDDLE].pin=middlePin;
    fingers[FINGER_RING].pin=ringPin;
    fingers[FINGER_LITTLE].pin=littlePin;
    pinMode(thumbPin,INPUT);
    pinMode(indexPin,INPUT);
    pinMode(middlePin,INPUT);
    pinMode(ringPin,INPUT);
    pinMode(littlePin,INPUT);
}

void Glove::calibrate(FINGER_T finger,HAND_STATE_T state){
    if(finger>=FINGER_NUM||finger<0)return;
    getAngles();
    Finger * fing = &fingers[finger];
    if(state == HAND_STATE_PALM){
        fing->calibratePlam = fing->data; 
    }
    else if(state == HAND_STATE_FIST){
        fing->calibrateFist = fing->data; 
    }
}

float * Glove::getAngles(){
    for(int i=0;i<FINGER_NUM;i++){
        Finger * fin = &fingers[i]; 
        fin->data = analogRead(fin->pin);
        Serial.printf("%4d ",fin->data);
        float maxAngle = 90;
        if(fin->data>fin->calibratePlam){
            fin->angle = 0;
        }
        else if(fin->data<fin->calibrateFist){
            fin->angle = maxAngle;
        }
        else{
            fin->angle = (1-(float)(fin->data-fin->calibrateFist)/(float)(fin->calibratePlam-fin->calibrateFist))*maxAngle;
        }
        angles[i]=fin->angle;
    }

    Serial.printf("\n");
    return angles;
}
void Glove::loadCalibrate(){
//初始化EEPROM,并读取校准信息
    EEPROM.begin(4096); 
    for(int i=0;i<5;i++){
        uint8_t high = EEPROM.read(CALIBRATE_DATA_ADDR+i*4);
        uint8_t low  = EEPROM.read(CALIBRATE_DATA_ADDR+i*4+1);
        uint16_t data = ((uint16_t)high << 8) | (uint16_t)low;
        this->fingers[i].calibratePlam = data;
        Serial.printf("plam:%d\n",data);
        
        high = EEPROM.read(CALIBRATE_DATA_ADDR+i*4+2);
        low  = EEPROM.read(CALIBRATE_DATA_ADDR+i*4+3);
        data = ((uint16_t)high << 8) | (uint16_t)low;
        this->fingers[i].calibrateFist = data;
        Serial.printf("fist:%d\n",data);
    }
}

void Glove::saveCalibrate(){
    EEPROM.begin(4096); 
    for(int i=0;i<5;i++){
        uint8_t high = (uint8_t)(this->fingers[i].calibratePlam >> 8);
        uint8_t low  = (uint8_t)(this->fingers[i].calibratePlam & 0xFF);
        uint16_t d = ((uint16_t)high << 8) | (uint16_t)low;
        Serial.printf("data(%d):%x %x %d %d\n",i,high,low,this->fingers[i].calibratePlam,d);
        EEPROM.write(CALIBRATE_DATA_ADDR+i*4,high);
        EEPROM.write(CALIBRATE_DATA_ADDR+i*4+1,low);

        high = (uint8_t)(this->fingers[i].calibrateFist >> 8);
        low  = (uint8_t)(this->fingers[i].calibrateFist & 0xFF);
        d = ((uint16_t)high << 8) | (uint16_t)low;
        Serial.printf("data(%d):%x %x %d %d\n",i,high,low,this->fingers[i].calibrateFist,d);
        EEPROM.write(CALIBRATE_DATA_ADDR+i*4+2,high);
        EEPROM.write(CALIBRATE_DATA_ADDR+i*4+3,low);
    }
    EEPROM.commit();
}