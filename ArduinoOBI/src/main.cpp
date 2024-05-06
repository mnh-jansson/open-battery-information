#include <Arduino.h>
#include "OneWire2.h"

OneWire makita(6);

void cmd_and_read_33(byte *cmd, uint8_t cmd_len, byte *rsp, uint8_t rsp_len) {
	int i;
	makita.reset();
	delayMicroseconds(400);
	makita.write(0x33,0);

	for (i=0; i < 8; i++) {
		delayMicroseconds(90);   
		rsp[i] = makita.read(); 
	}

	for (i=0; i < cmd_len; i++) {
		delayMicroseconds(90);
		makita.write(cmd[i],0);
	}

	for (i=8; i < rsp_len + 8; i++) {
		delayMicroseconds(90);   
		rsp[i] = makita.read(); 
	}
}

void cmd_and_read_cc(byte *cmd, uint8_t cmd_len, byte *rsp, uint8_t rsp_len) {
	int i;
	makita.reset();
	delayMicroseconds(400);
	makita.write(0xcc,0);

	for (i=0; i < cmd_len; i++) {
		delayMicroseconds(90);
		makita.write(cmd[i],0);
	}

	for (i=0; i < rsp_len; i++) {
		delayMicroseconds(90);   
		rsp[i] = makita.read(); 
	}
}


void setup() {
	Serial.begin (9600);
	pinMode(8, OUTPUT);
	pinMode(2, OUTPUT);

}

void send_usb(byte *rsp, byte rsp_len) {
    for (int i; i < rsp_len; i++) {
        Serial.write(rsp[i]);
    }
}

void read_usb() {
    if (Serial.available() > 4) {
        byte start = Serial.read();
        byte cmd;
        byte len;
        byte data[255];
        byte rsp[255];
        byte rsp_len;

        if (start == 0x01) {
            len = Serial.read();
            rsp_len = Serial.read();
            cmd = Serial.read();

            for (int i = 0; i < len; i++) {
				while (Serial.available() < 1) {

				}
                data[i] = Serial.read();
            }
        }
        else {
            return;
        }
        /* Set RTS */
    	digitalWrite(8, HIGH);
	    delay(400);

        switch(cmd) {
            case 0x33:
            cmd_and_read_33(data, len, &rsp[2], rsp_len);
			rsp[0] = 0x02;
            break;
            case 0xCC:
            cmd_and_read_cc(data, len, &rsp[2], rsp_len);
			rsp[0] = 0x03;
            break;
            default:
            break;
        }
        rsp[1] = rsp_len;
        send_usb(rsp, rsp_len + 2);

        digitalWrite(8, LOW);
    }
}

void loop() {
    read_usb();
}
