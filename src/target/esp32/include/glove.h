#include <Arduino.h>
#include <EEPROM.h>

#define CALIBRATE_DATA_ADDR 0 

typedef enum{
    HAND_STATE_PALM = 0,
    HAND_STATE_FIST,
}HAND_STATE_T;

typedef enum{
    FINGER_THUMB = 0 ,
    FINGER_INDEX,
    FINGER_MIDDLE,
    FINGER_RING,
    FINGER_LITTLE,
    FINGER_NUM
}FINGER_T;

class Glove
{
public:
    float angles[FINGER_NUM];
    Glove(uint16_t thumbPin,uint16_t indexPin,uint16_t middlePin,uint16_t ringPin,uint16_t littlePin);
    float * getAngles();
    void calibrate(FINGER_T finger,HAND_STATE_T state);
    void saveCalibrate();
    void loadCalibrate();
private:
    typedef struct 
    {
        uint16_t pin;
        uint16_t data;
        uint16_t calibratePlam = 4095;
        uint16_t calibrateFist = 0;
        float angle;
    }Finger;
    Finger fingers[FINGER_NUM];
};
