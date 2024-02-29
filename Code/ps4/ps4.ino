#include <PS4Controller.h>
 
void onEvent(){
 
  if(PS4.event.button_up.right){
    Serial.println("right arrow up");
  }
 
  if(PS4.event.button_down.right){
    Serial.println("right arrow down");
  }
 
  if(PS4.event.button_up.left){
    Serial.println("left arrow up");
  }
 
  if(PS4.event.button_down.left){
    Serial.println("left arrow down");
  }
 
  if(PS4.event.button_up.down){
    Serial.println("down arrow up");
  }
 
  if(PS4.event.button_down.down){
    Serial.println("down arrow down");
  }
 
  if(PS4.event.button_up.up){
    Serial.println("up arrow up");
  }
 
  if(PS4.event.button_down.up){
    Serial.println("up arrow down");
  }
 
  if(PS4.event.button_up.r3){
    Serial.println("r3 stick up");
  }
 
  if(PS4.event.button_down.r3){
    Serial.println("r3 stick down");
  }
 
  if(PS4.event.button_up.l3){
    Serial.println("l3 stick up");
  }
 
  if(PS4.event.button_down.l3){
    Serial.println("l3 stick down");
  }
 
  if(PS4.R2Value()){
    printf("R2: %d \n", PS4.R2Value());
  }
 
  if(PS4.L2Value()){
    printf("L2: %d \n", PS4.L2Value());
  }
 
  if(PS4.event.button_up.l1){
    Serial.println("l1 button up");
  }
 
  if(PS4.event.button_down.l1){
    Serial.println("l1 button down");
  }
 
  if(PS4.event.button_up.r2){
    Serial.println("r2 button up");
  }
 
  if(PS4.event.button_down.r2){
    Serial.println("r2 buton down");
  }
 
  if(PS4.event.button_up.r1){
    Serial.println("r1 button up");
  }
 
  if(PS4.event.button_down.r1){
    Serial.println("r1 button down");
  }
 
  if(PS4.event.button_up.touchpad){
    Serial.println("touchpad button up");
  }
 
  if(PS4.event.button_down.touchpad){
    Serial.println("touchpad button down");
  }
 
  if(PS4.event.button_up.options){
    Serial.println("options button up");
  }
 
  if(PS4.event.button_down.options){
    Serial.println("options button down");
  }
 
  if(PS4.event.button_up.share){
    Serial.println("share button up");
  }
 
  if(PS4.event.button_down.share){
    Serial.println("share button down");
  }
 
  if(PS4.event.button_up.ps){
    Serial.println("ps button up");
  }
 
  if(PS4.event.button_down.ps){
    Serial.println("ps button down");
  }
 
  if(PS4.event.button_up.triangle){
    Serial.println("triangle button up");
  }
 
  if(PS4.event.button_down.triangle){
    Serial.println("triangle button down");
  }
 
  if(PS4.event.button_up.circle){
    Serial.println("circle button up");
  }
 
  if(PS4.event.button_down.circle){
    Serial.println("circle button down");
  }
 
  if(PS4.event.button_up.square){
    Serial.println("square button up");
  }
 
  if(PS4.event.button_down.square){
    Serial.println("square button down");
  }
 
  if(PS4.event.button_up.cross){
    Serial.println("cross button up");
  }
 
  if(PS4.event.button_down.cross){
    Serial.println("cross button down");
  }
}
 
void setup()
{
  Serial.begin(115200);
   
  PS4.attach(onEvent);
   
  PS4.begin("d4:6d:6d:fc:54:0d");
  Serial.println("Initialization finished.");
}
 
void loop()
{
  vTaskDelete(NULL);
}