#include "glove.h"

//uint16_t pins[FINGER_NUM][FINGER_JOINT_NUM] = {39,35,33,34,26,36,27,25,4,2};

Glove::Glove(uint16_t pins[][FINGER_JOINT_NUM],hand_e hand){
    for(int i=0;i<FINGER_NUM;i++){
        for(int j=0;j<FINGER_JOINT_NUM;j++){
            hand == HAND_RIGHT ? gpios[i][j] = pins[i][j] : gpios[i][j] = pins[FINGER_NUM-1-i][j];    
            pinMode(gpios[i][j],INPUT);
        }
    }
}

void Glove::update(){
   float val;
    for(int i=0;i<FINGER_NUM;i++){
        for(int j=0;j<FINGER_JOINT_NUM;j++){
            val = analogRead(gpios[i][j]);
            angles[i][j] = ANGLE_DIR * (val * ANGLE_RANGE/4095 - ANGLE_OFFSET);

        }
    }
}