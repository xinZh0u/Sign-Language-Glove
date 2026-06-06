#ifndef _GLOVE_H_
#define _GLOVE_H_

#include <Arduino.h>

#define FINGER_JOINT_NUM    2
#define ANGLE_RANGE             333.3
#define ANGLE_OFFSET             333.3/2 + 20
#define ANGLE_DIR                   1

typedef enum{
    HAND_LEFT,
    HAND_RIGHT
}hand_e;

typedef enum{
    FINGER_THUMB,
    FINGER_INDEX,
    FINGER_MIDDLE,
    FINGER_RING,
    FINGER_LITTLE,
    FINGER_NUM
}finger_e;

class Glove{
public:
    Glove(uint16_t pins[][FINGER_JOINT_NUM],hand_e hand);
    void update();
    float angles[FINGER_NUM][FINGER_JOINT_NUM];
private:
    uint16_t gpios[FINGER_NUM][FINGER_JOINT_NUM];
};

#endif
