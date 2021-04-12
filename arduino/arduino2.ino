int trig_R = 2;    // TRIG pin
int trig_M = 4;
int trig_L = 6;

int echo_R = 3;    // ECHO pin
int echo_M = 5; 
int echo_L = 7; 

int FWD_L = 8;   // Left motor driver
int RVS_L = 9;   // B=RVS, A=FWD
int PWM_L = 10;

int RVS_R = 12;    // Right motor driver
int FWD_R = 13;
int PWM_R = 11;

int wall=50;

float dist_L, dist_M, dist_R;

void getSensors(){
  // Left sensor
  digitalWrite(trig_L, HIGH);
  delayMicroseconds(60);
  digitalWrite(trig_L, LOW);
  dist_L = 0.017* pulseIn(echo_L, (HIGH));
  
  // Center sensor  
  digitalWrite(trig_M, HIGH);
  delayMicroseconds(60);
  digitalWrite(trig_M, LOW);
  dist_M = 0.017* pulseIn(echo_M, HIGH);

  // Right sensor
  digitalWrite(trig_R, HIGH);
  delayMicroseconds(60);
  digitalWrite(trig_R, LOW);
  dist_R = 0.017* pulseIn(echo_R, HIGH);
}

void writeSensorsSerial(){
  // Left sensor
  Serial.write(highByte(int(dist_L)));
  Serial.write(lowByte(int(dist_L)));
  
  // Center sensor
  Serial.write(highByte(int(dist_M)));
  Serial.write(lowByte(int(dist_M)));
  
  // Right sensor
  Serial.write(highByte(int(dist_R)));
  Serial.write(lowByte(int(dist_R)));
}

void leftDir(char ch){
  if(ch == 'F'){
    digitalWrite(RVS_L, LOW);
    digitalWrite(FWD_L, HIGH);
  }
  else if(ch == 'R'){
    digitalWrite(FWD_L, LOW);
    digitalWrite(RVS_L, HIGH);
  }
  else{
    digitalWrite(FWD_L, LOW);
    digitalWrite(RVS_L, LOW);
  }
}

void rightDir(char ch){
  if(ch == 'F'){
    digitalWrite(RVS_R,LOW);
    digitalWrite(FWD_R,HIGH);
  }
  else if(ch == 'R'){
    digitalWrite(FWD_R,LOW);
    digitalWrite(RVS_R,HIGH);
  }
  else{
    digitalWrite(FWD_R,LOW);
    digitalWrite(RVS_R,LOW);
  }
}

void goForward(){
  rightDir('F');
  leftDir('F');
}

void goBackward(){
  rightDir('R');
  leftDir('R');
}

void stopAll(){
  leftDir('S');
  rightDir('S');
}

void turnLeft(){
  leftDir('R');
  rightDir('F');
  delay(500);
  stopAll();
}

void turnRight(){
  leftDir('F');
  rightDir('R');
  delay(500);
  stopAll();
}

void turnAround(){
  turnRight();
  turnRight();
}

bool checkWall(){
  if(dist_L<wall || dist_M<wall || dist_R<wall){
    return true;
  }
  return false;
}


void chooseDir(){
  if(dist_L>dist_R){
    turnLeft();
  }
  else{
    turnRight();
  }
}

void wander(){
  analogWrite(PWM_L, 50);
  analogWrite(PWM_R, 50);
  while(!Serial.available()){
    getSensors();
    //writeSensorsSerial();
    goForward();
    if(checkWall()){
      stopAll();
      delay(300);
      goBackward();
      delay(300);
      chooseDir();
    }
  }
}

void setup() {
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  pinMode(trig_L, OUTPUT);
  pinMode(trig_M, OUTPUT);
  pinMode(trig_R, OUTPUT);

  pinMode(echo_L, INPUT);
  pinMode(echo_M, INPUT);
  pinMode(echo_R, INPUT);
  
  pinMode(RVS_L, OUTPUT);
  pinMode(FWD_L, OUTPUT);
  pinMode(PWM_L, OUTPUT);

  pinMode(RVS_R, OUTPUT);
  pinMode(FWD_R, OUTPUT);
  pinMode(PWM_R, OUTPUT);

  analogWrite(PWM_L, 50);
  analogWrite(PWM_R, 50);
}

void set_pwm() {

}
void loop() {
    //digitalWrite(LED_BUILTIN, LOW);
    if (Serial.available() >= 2) {
        
        signed char left = Serial.read();   
        signed char right = Serial.read();

        if (right == 100 && left == 100){
          wander()
        } 
        analogWrite(PWM_L, abs(left));
        analogWrite(PWM_R, abs(right));

        if (right == 50) {
            digitalWrite(LED_BUILTIN, HIGH);  
        }
        if (right == 25) {
            digitalWrite(LED_BUILTIN, LOW);
        }
        if (right > 0) {
            rightDir('F');
        } else if (right < 0) {
            rightDir('R');
        } else {
            rightDir('S');
        }
        if (left > 0) {
            leftDir('F');
        } else if (left < 0) {
            leftDir('R');
        } else {
            leftDir('S');
        }
        
    }