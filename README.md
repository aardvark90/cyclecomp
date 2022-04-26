# cycle computer

 Cycle Computer using micro python, SSD1306 OLED I2C Display and maker pi pico dev board.
 
 Dave Gunning Nov 2021

 I2C display to pi pico pins: VCC 3.3v, SDA - GP4, SCL - GP5.
 
 Input from cycle wheel reed switch to GP1. Switch debounce using CR network.
 Reed switch closes on each wheel rotation and discharges 1uF, causing logic 0 pulse on GP1.
	
