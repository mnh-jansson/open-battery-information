*
 * ═══════════════════════════════════════════════════════════════════
 * Open Battery Information - Standalone OLED Edition
 * ═══════════════════════════════════════════════════════════════════
 *
 * Copyright (c) 2026 Massimo Biagi - Standalone OLED Edition
 * Copyright (c) 2024 Martin Jansson - Open Battery Information
 *
 * ── LICENSE (MIT) ──────────────────────────────────────────────────
 *
 * This project is based on "Open Battery Information" by
 * Martin Jansson (https://github.com/mnh-jansson/open-battery-information)
 * and is released under the same MIT License.
 *
 * Permission is hereby granted, free of charge, to any person
 * obtaining a copy of this software and associated documentation
 * files (the "Software"), to deal in the Software without
 * restriction, including without limitation the rights to use,
 * copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following
 * conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 * OTHER DEALINGS IN THE SOFTWARE.
 *
 * ── ATTRIBUTION ────────────────────────────────────────────────────
 *
 * Original project : Open Battery Information (OBI)
 * Original author  : Martin Jansson (mnh-jansson)
 * Original license : MIT
 * Original repo    : github.com/mnh-jansson/open-battery-information
 *
 * Standalone OLED adaptation by Massimo Biagi:
 *   - Removed PC/Python dependency
 *   - Added OLED display interface (SSD1306 128x32)
 *   - Added 2-button navigation
 *   - Added circuit protection (Zener + series resistor)
 *   - Ported OneWire protocol from serial bridge to direct calls
 *
 * ═══════════════════════════════════════════════════════════════════
 *
 * BILL OF MATERIALS (BOM)
 * ═══════════════════════════════════════════════════════════════════
 *
 *  Qty  Component                  Value / Model       Notes
 *  ---  -------------------------  ------------------  ---------------
 *   1   Arduino Nano               ATmega328P          Clone OK (CH340)
 *   1   OLED Display               SSD1306 128x32 I2C  0.91" module
 *   2   Push button                Momentary, NO       Tactile switch
 *   1   Resistor (OneWire pullup)  4.7 kOhm 1/4W      Yellow-Violet-Red
 *   1   Resistor (Enable pullup)   4.7 kOhm 1/4W      Yellow-Violet-Red
 *   1   Resistor (OneWire series)  100 Ohm 1/4W        Brown-Black-Brown
 *   1   Zener diode (protection)   5.1V 1W             1N4733A
 *   1   Makita battery connector   LXT 18V             From dead tool
 *   -   Hookup wire, solder, USB-C cable for power
 *
 * ═══════════════════════════════════════════════════════════════════
 *
 * CIRCUIT SCHEMATIC
 * ═══════════════════════════════════════════════════════════════════
 *
 *                        +5V                           MAKITA LXT
 *                         |                          BATTERY CONN.
 *                         |                         .-----------.
 *                        [4.7k]  R_pullup           | VBAT+ (X) | DO NOT
 *                         |                         | (18-20V)  | CONNECT!
 *     ARDUINO NANO        |                         |           |
 *    .-----------.        +-------[100R]---+--------o OneWire   |
 *    |        D7 o--------'       R_prot   |        |           |
 *    |           |                     Zener|5.1V    |           |
 *    |        D8 o--------[4.7k]-----------+--------o Enable    |
 *    |           |                         |        |           |
 *    |       GND o-------------------------+--------o VBAT-     |
 *    |           |                                  '-----------'
 *    |           |
 *    |    A4/SDA o--------o SDA  .--------.
 *    |    A5/SCL o--------o SCL  |  OLED  |
 *    |       +5V o--------o VCC  | 128x32 |
 *    |       GND o--------o GND  '--------'
 *    |           |
 *    |        D2 o--------+
 *    |           |       BTN_A  [A] Next / Back(long)
 *    |           |        |
 *    |        D3 o-----+  |
 *    |           |    BTN_B |   [B] OK / Execute
 *    '-----------'     |  |
 *                      +--+---- GND
 *
 *    Zener detail (1N4733A):
 *
 *        Signal ---+--- Cathode |< Anode --- GND
 *                  |      (band side)
 *              Band/stripe on cathode side
 *              goes TOWARDS the signal line,
 *              plain side goes to GND.
 *
 *    Protection explained:
 *      - R_prot (100R): limits current if fault occurs
 *      - Zener (5.1V): clamps overvoltage from battery
 *      - R_pullup (4.7k): standard OneWire pull-up
 *      - If 18V reaches data line: Zener clamps to 5.1V,
 *        100R limits current to safe level, Nano is protected
 *
 * ═══════════════════════════════════════════════════════════════════
 *
 * PIN SUMMARY
 * ═══════════════════════════════════════════════════════════════════
 *
 *   Pin   Function         Connection
 *   ----  ---------------  ------------------------------------------
 *   D2    BTN_A input      Button to GND (internal pull-up)
 *   D3    BTN_B input      Button to GND (internal pull-up)
 *   D7    OneWire data     100R -> junction -> 4.7k to 5V, Zener to GND
 *   D8    Battery enable   4.7k pull-up to battery Enable pin
 *   A4    I2C SDA          OLED display
 *   A5    I2C SCL          OLED display
 *   5V    Power out        OLED VCC, pull-up resistors
 *   GND   Ground           Common ground for all components
 *
 * Required library: SSD1306Ascii by Bill Greiman
 *   (install from Arduino Library Manager)
 *
 * Required files in sketch folder:
 *   OneWire2.h, OneWire2.cpp, util/ folder
 *   (from ArduinoOBI/lib/OneWire/)
 *
 * ═══════════════════════════════════════════════════════════════════
 */

#include <Wire.h>
#include "SSD1306Ascii.h"
#include "SSD1306AsciiWire.h"
#include "OneWire2.h"

// ═══════════════════════════════════════════════════════════
// PIN CONFIGURATION
// ═══════════════════════════════════════════════════════════
#define ONEWIRE_PIN   7
#define ENABLE_PIN    8
#define BTN_A         2    // NEXT (short) / BACK (long)
#define BTN_B         3    // OK / EXECUTE

// ═══════════════════════════════════════════════════════════
// OLED CONFIGURATION
// ═══════════════════════════════════════════════════════════
#define OLED_ADDR     0x3C

// ═══════════════════════════════════════════════════════════
// BUTTON TIMING
// ═══════════════════════════════════════════════════════════
#define LONG_PRESS_MS  800
#define DEBOUNCE_MS    80

// ═══════════════════════════════════════════════════════════
//
//  LANGUAGE / LABELS
//
//  All user-visible strings are defined here.
//  To translate, just change the strings below.
//
// ═══════════════════════════════════════════════════════════

// -- Splash screen --
#define L_SPLASH_TITLE    "  OBI-1"
#define L_SPLASH_LINE1    "  Makita LXT Battery"
#define L_SPLASH_LINE2    "     Standalone"

// -- Status messages --
#define L_WORKING         " Reading..."
#define L_RESULT          "=== RESULT ==="
#define L_NO_BATTERY      "No battery!"
#define L_UNSUPPORTED     "Unsupported!"
#define L_F0513_LIMITED   "F0513 limited"
#define L_READ_FAILED     "Read failed!"
#define L_READ_FIRST      "Read first!"
#define L_LEDS_ON         "LEDs ON"
#define L_LEDS_OFF        "LEDs OFF"
#define L_ERRORS_CLEARED  "Errors cleared!"
#define L_IN_DEVELOPMENT  "In development!"
#define L_BTN_OK          "[B] OK"

// -- Menu items --
const char mi0[] PROGMEM = "Read Battery";
const char mi1[] PROGMEM = "LED ON";
const char mi2[] PROGMEM = "LED OFF";
const char mi3[] PROGMEM = "Clear Errors";
const char mi4[] PROGMEM = "Reset Msg";
const char* const menuItems[] PROGMEM = {mi0, mi1, mi2, mi3, mi4};
#define MENU_COUNT 5

// -- Menu footer --
#define L_MENU_HEADER     "=== MENU "
#define L_MENU_LOCKED     "[A]Next (Read 1st!)"
#define L_MENU_NORMAL     "[A]Next  [B]Execute"

// -- Data screen footer --
#define L_DATA_FOOTER     "[A]Next [A+]Menu"

// -- Parameter names (displayed on data screens) --
const char pn0[]  PROGMEM = "Model";
const char pn1[]  PROGMEM = "Charges";
const char pn2[]  PROGMEM = "State";
const char pn3[]  PROGMEM = "Status";
const char pn4[]  PROGMEM = "Pack V";
const char pn5[]  PROGMEM = "Cell 1";
const char pn6[]  PROGMEM = "Cell 2";
const char pn7[]  PROGMEM = "Cell 3";
const char pn8[]  PROGMEM = "Cell 4";
const char pn9[]  PROGMEM = "Cell 5";
const char pn10[] PROGMEM = "V Diff";
const char pn11[] PROGMEM = "Temp 1";
const char pn12[] PROGMEM = "Temp 2";
const char pn13[] PROGMEM = "ROM ID";
const char pn14[] PROGMEM = "Mfg Date";
const char pn15[] PROGMEM = "Capacity";
const char pn16[] PROGMEM = "Type";
const char pn17[] PROGMEM = "Msg";
const char* const paramNames[] PROGMEM = {
  pn0, pn1, pn2, pn3, pn4, pn5, pn6, pn7, pn8,
  pn9, pn10, pn11, pn12, pn13, pn14, pn15, pn16, pn17
};
#define MAX_PARAMS 18

// ═══════════════════════════════════════════════════════════
//
//  END OF LANGUAGE SECTION
//
// ═══════════════════════════════════════════════════════════

// -- Hardware instances --
SSD1306AsciiWire oled;
OneWire makita(ONEWIRE_PIN);

// -- Button enum --
enum Button : uint8_t { BTN_NONE, BTN_NEXT, BTN_OK, BTN_BACK };

// -- Application state --
enum AppState : uint8_t {
  STATE_MENU,
  STATE_SHOW_DATA,
  STATE_SHOW_MSG,
};

AppState appState = STATE_MENU;
int8_t   menuSel = 0;
int8_t   scrollOffset = 0;

// -- Battery data storage --
char paramValues[MAX_PARAMS][14];
bool batteryPresent  = false;
bool cmdVerF0513     = false;
bool buttonsEnabled  = false;
char statusMsg[28]   = "";

// -- PROGMEM string buffer --
char pgmBuf[16];

// ═══════════════════════════════════════════════════════════
// UTILITY FUNCTIONS
// ═══════════════════════════════════════════════════════════

// Read a string from a PROGMEM table into pgmBuf
void readPgm(const char* const* table, uint8_t idx) {
  strncpy_P(pgmBuf, (char*)pgm_read_word(&table[idx]), 15);
  pgmBuf[15] = '\0';
}

// Swap upper and lower nibbles of a byte
// Used by Makita protocol for certain data fields
byte nibbleSwap(byte b) {
  return ((b & 0xF0) >> 4) | ((b & 0x0F) << 4);
}

// Check if all bytes in buffer are 0xFF (invalid response)
bool isAllFF(byte *b, uint8_t len) {
  for (uint8_t i = 0; i < len; i++)
    if (b[i] != 0xFF) return false;
  return true;
}

// Clear all stored battery parameter values
void clearAllData() {
  for (uint8_t i = 0; i < MAX_PARAMS; i++)
    paramValues[i][0] = '\0';
  batteryPresent = false;
  cmdVerF0513 = false;
  buttonsEnabled = false;
}

// ═══════════════════════════════════════════════════════════
// BUTTON INPUT
//
// At startup, checks if pins are HIGH (pull-up working).
// If a pin is stuck LOW at boot, it's disabled.
//
//   BTN_A short press = BTN_NEXT
//   BTN_A long press  = BTN_BACK
//   BTN_B any press   = BTN_OK
// ═══════════════════════════════════════════════════════════

unsigned long bootTime = 0;
bool btnA_ok = false;  // true if BTN_A pull-up works
bool btnB_ok = false;  // true if BTN_B pull-up works

// Check pin is genuinely pressed: must be LOW 3 times
bool pinIsPressed(uint8_t pin) {
  if (digitalRead(pin) != LOW) return false;
  delay(30);
  if (digitalRead(pin) != LOW) return false;
  delay(30);
  if (digitalRead(pin) != LOW) return false;
  return true;
}

Button readButton() {
  // Ignore all input for 3 seconds after boot
  if (millis() - bootTime < 3000) return BTN_NONE;

  // -- Button A: NEXT (short) or BACK (long) --
  if (btnA_ok && pinIsPressed(BTN_A)) {
    unsigned long t0 = millis();
    while (digitalRead(BTN_A) == LOW) {
      if (millis() - t0 >= LONG_PRESS_MS) {
        while (digitalRead(BTN_A) == LOW) delay(10);
        delay(DEBOUNCE_MS);
        return BTN_BACK;
      }
      delay(10);
    }
    delay(DEBOUNCE_MS);
    return BTN_NEXT;
  }

  // -- Button B: always OK --
  if (btnB_ok && pinIsPressed(BTN_B)) {
    while (digitalRead(BTN_B) == LOW) delay(10);
    delay(DEBOUNCE_MS);
    return BTN_OK;
  }

  return BTN_NONE;
}

// Validate pull-ups at startup
void initButtons() {
  pinMode(BTN_A, INPUT_PULLUP);
  pinMode(BTN_B, INPUT_PULLUP);
  delay(100);  // Let pull-ups stabilize

  btnA_ok = (digitalRead(BTN_A) == HIGH);
  btnB_ok = (digitalRead(BTN_B) == HIGH);
}

// ═══════════════════════════════════════════════════════════
// ONEWIRE COMMUNICATION
//
// These functions are ported from ArduinoOBI/src/main.cpp.
// They perform the same OneWire sequences that the original
// Arduino bridge firmware executed when receiving commands
// from the Python application via USB serial.
// ═══════════════════════════════════════════════════════════

// Enable / disable battery power (RTS pin)
void enableBatt()  { digitalWrite(ENABLE_PIN, HIGH); delay(400); }
void disableBatt() { digitalWrite(ENABLE_PIN, LOW); }

// OneWire command with Read ROM (0x33) prefix
// Reads 8-byte ROM ID, then sends cmd, then reads rsp_len bytes
void ow_cmd_33(byte *cmd, uint8_t cmd_len, byte *rsp, uint8_t rsp_len) {
  makita.reset();
  delayMicroseconds(400);
  makita.write(0x33, 0);
  for (uint8_t i = 0; i < 8; i++) {
    delayMicroseconds(90);
    rsp[i] = makita.read();
  }
  for (uint8_t i = 0; i < cmd_len; i++) {
    delayMicroseconds(90);
    makita.write(cmd[i], 0);
  }
  for (uint8_t i = 8; i < (uint8_t)(rsp_len + 8); i++) {
    delayMicroseconds(90);
    rsp[i] = makita.read();
  }
}

// OneWire command with Skip ROM (0xCC) prefix
// Sends cmd bytes, then reads rsp_len bytes
void ow_cmd_cc(byte *cmd, uint8_t cmd_len, byte *rsp, uint8_t rsp_len) {
  makita.reset();
  delayMicroseconds(400);
  makita.write(0xcc, 0);
  for (uint8_t i = 0; i < cmd_len; i++) {
    delayMicroseconds(90);
    makita.write(cmd[i], 0);
  }
  for (uint8_t i = 0; i < rsp_len; i++) {
    delayMicroseconds(90);
    rsp[i] = makita.read();
  }
}

// ═══════════════════════════════════════════════════════════
// BATTERY COMMANDS
//
// Each function documents the original Python command format
// and how the Arduino OBI bridge decoded it.
// ═══════════════════════════════════════════════════════════

// --- Read battery message (ROM ID, charge count, state, etc.) ---
// Python: READ_MSG_CMD = [0x01, 0x02, 0x28, 0x33, 0xAA, 0x00]
// buf[0..7]=ROM, buf[8..47]=message, Python response[N] = buf[N-2]
bool readBatteryMessage() {
  byte cmd[] = {0xAA, 0x00};
  byte buf[48];
  memset(buf, 0xFF, sizeof(buf));
  enableBatt();
  ow_cmd_33(cmd, 2, buf, 40);
  disableBatt();
  if (isAllFF(buf + 8, 32)) return false;

  snprintf(paramValues[13], 14, "%02X%02X%02X%02X",
           buf[0], buf[1], buf[2], buf[3]);
  snprintf(paramValues[14], 14, "%02d/%02d/20%02d",
           buf[2], buf[1], buf[0]);

  byte ns34 = nibbleSwap(buf[34]);
  byte ns35 = nibbleSwap(buf[35]);
  uint16_t cc = (((uint16_t)ns34 << 8) | ns35) & 0x0FFF;
  snprintf(paramValues[1], 14, "%u", cc);

  strcpy(paramValues[2], (buf[28] & 0x0F) ? "LOCKED" : "UNLOCKED");
  snprintf(paramValues[3], 14, "0x%02X", buf[27]);

  float cap = nibbleSwap(buf[24]) / 10.0;
  dtostrf(cap, 3, 1, paramValues[15]);
  strcat(paramValues[15], "Ah");

  snprintf(paramValues[16], 14, "%d", nibbleSwap(buf[19]));
  strcpy(paramValues[17], "OK");
  return true;
}

// --- Read model (standard) ---
// Python: MODEL_CMD = [0x01, 0x02, 0x10, 0xCC, 0xDC, 0x0C]
// Model string = first 7 bytes of response as ASCII
bool readModel() {
  byte cmd[] = {0xDC, 0x0C};
  byte rsp[16];
  memset(rsp, 0xFF, sizeof(rsp));
  enableBatt();
  ow_cmd_cc(cmd, 2, rsp, 16);
  disableBatt();
  if (isAllFF(rsp, 7)) return false;
  for (uint8_t i = 0; i < 7; i++)
    if (rsp[i] < 0x20 || rsp[i] > 0x7E) return false;
  memcpy(paramValues[0], rsp, 7);
  paramValues[0][7] = '\0';
  cmdVerF0513 = false;
  buttonsEnabled = true;
  return true;
}

// --- Read model (F0513 variant) ---
// Python: F0513_MODEL_CMD = [0x01, 0x00, 0x02, 0x31]
// Special case 0x31 in main.cpp: testmode, read 2 bytes, clear
bool readModelF0513() {
  byte dummy[2];
  enableBatt();
  makita.reset(); delayMicroseconds(400);
  makita.write(0xcc, 0); delayMicroseconds(90);
  makita.write(0x99, 0); delay(400);
  makita.reset(); delayMicroseconds(400);
  makita.write(0x31, 0); delayMicroseconds(90);
  byte rsp3 = makita.read(); delayMicroseconds(90);
  byte rsp2 = makita.read(); delayMicroseconds(90);
  byte clr[] = {0xF0, 0x00};
  ow_cmd_cc(clr, 2, dummy, 0);
  disableBatt();
  if (rsp2 == 0xFF && rsp3 == 0xFF) return false;
  snprintf(paramValues[0], 14, "BL%X%X", rsp2, rsp3);
  cmdVerF0513 = true;
  buttonsEnabled = true;
  return true;
}

// --- Read live data (standard) ---
// Python: READ_DATA_REQUEST = [0x01, 0x04, 0x1D, 0xCC, 0xD7, 0x00, 0x00, 0xFF]
// Voltages: little-endian uint16 / 1000, temps: / 100
bool readDataStd() {
  byte cmd[] = {0xD7, 0x00, 0x00, 0xFF};
  byte buf[29];
  memset(buf, 0xFF, sizeof(buf));
  enableBatt();
  ow_cmd_cc(cmd, 4, buf, 29);
  disableBatt();
  if (isAllFF(buf, 20)) return false;

  float v[5];
  float vPack = (uint16_t)(buf[0] | (buf[1] << 8)) / 1000.0;
  for (uint8_t i = 0; i < 5; i++)
    v[i] = (uint16_t)(buf[2 + i * 2] | (buf[3 + i * 2] << 8)) / 1000.0;
  float vMin = v[0], vMax = v[0];
  for (uint8_t i = 1; i < 5; i++) {
    if (v[i] < vMin) vMin = v[i];
    if (v[i] > vMax) vMax = v[i];
  }
  dtostrf(vPack, 4, 2, paramValues[4]); strcat(paramValues[4], "V");
  for (uint8_t i = 0; i < 5; i++) {
    dtostrf(v[i], 4, 3, paramValues[5 + i]); strcat(paramValues[5 + i], "V");
  }
  dtostrf(vMax - vMin, 4, 3, paramValues[10]); strcat(paramValues[10], "V");
  dtostrf((uint16_t)(buf[14] | (buf[15] << 8)) / 100.0, 4, 1, paramValues[11]);
  strcat(paramValues[11], "C");
  dtostrf((uint16_t)(buf[16] | (buf[17] << 8)) / 100.0, 4, 1, paramValues[12]);
  strcat(paramValues[12], "C");
  return true;
}

// --- Read live data (F0513 variant) ---
// Individual cell voltage commands + temperature
bool readDataF0513() {
  byte rsp[2]; float v[5];
  enableBatt();
  byte clr[] = {0xF0, 0x00};
  ow_cmd_cc(clr, 2, rsp, 0); delay(100);
  ow_cmd_cc(clr, 2, rsp, 0); delay(100);
  for (uint8_t c = 0; c < 5; c++) {
    byte vc[] = {(byte)(0x31 + c)};
    memset(rsp, 0xFF, 2);
    ow_cmd_cc(vc, 1, rsp, 2);
    v[c] = (uint16_t)(rsp[0] | (rsp[1] << 8)) / 1000.0;
    delay(50);
  }
  byte tc[] = {0x52};
  memset(rsp, 0xFF, 2);
  ow_cmd_cc(tc, 1, rsp, 2);
  float t1 = (uint16_t)(rsp[0] | (rsp[1] << 8)) / 100.0;
  disableBatt();

  float vPack = 0, vMin = v[0], vMax = v[0];
  for (uint8_t i = 0; i < 5; i++) {
    vPack += v[i];
    if (v[i] < vMin) vMin = v[i];
    if (v[i] > vMax) vMax = v[i];
  }
  dtostrf(vPack, 4, 2, paramValues[4]); strcat(paramValues[4], "V");
  for (uint8_t i = 0; i < 5; i++) {
    dtostrf(v[i], 4, 3, paramValues[5 + i]); strcat(paramValues[5 + i], "V");
  }
  dtostrf(vMax - vMin, 4, 3, paramValues[10]); strcat(paramValues[10], "V");
  dtostrf(t1, 4, 1, paramValues[11]); strcat(paramValues[11], "C");
  paramValues[12][0] = '\0';
  return true;
}

// --- Full battery read: model + message + live data ---
// Combines the three steps into a single operation
bool readBatteryFull() {
  clearAllData();

  // Step 1: Read message (ROM ID, charge count, state, etc.)
  if (!readBatteryMessage()) return false;
  batteryPresent = true;

  // Step 2: Read model (try standard first, then F0513)
  if (!readModel()) {
    if (!readModelF0513()) return false;
  }
  buttonsEnabled = true;

  // Step 3: Read live data (voltages, temperatures)
  if (cmdVerF0513)
    readDataF0513();
  else
    readDataStd();

  return true;
}

// --- LED test ON ---
// Python: TESTMODE_CMD + LEDS_ON_CMD (both via 0x33)
void ledsOn() {
  byte rsp[17]; enableBatt();
  byte t[] = {0xD9, 0x96, 0xA5};
  ow_cmd_33(t, 3, rsp, 9); delay(100);
  byte l[] = {0xDA, 0x31};
  ow_cmd_33(l, 2, rsp, 9); disableBatt();
}

// --- LED test OFF ---
// Standard uses 0x33 testmode, F0513 uses 0xCC testmode
void ledsOff() {
  byte rsp[17]; enableBatt();
  if (cmdVerF0513) {
    byte t[] = {0x99}; ow_cmd_cc(t, 1, rsp, 0);
  } else {
    byte t[] = {0xD9, 0x96, 0xA5}; ow_cmd_33(t, 3, rsp, 9);
  }
  delay(100);
  byte l[] = {0xDA, 0x34};
  ow_cmd_33(l, 2, rsp, 9); disableBatt();
}

// --- Clear BMS errors ---
// Python: TESTMODE_CMD + RESET_ERROR_CMD (both via 0x33)
void clearErrors() {
  byte rsp[17]; enableBatt();
  byte t[] = {0xD9, 0x96, 0xA5};
  ow_cmd_33(t, 3, rsp, 9); delay(100);
  byte r[] = {0xDA, 0x04};
  ow_cmd_33(r, 2, rsp, 9); disableBatt();
}

// ═══════════════════════════════════════════════════════════
// DISPLAY FUNCTIONS
//
// Layout for 128x32 (4 text rows at 1X, 2 rows at 2X):
//   Row 0 (1X): header / context info
//   Row 1-2 (2X): main content, large and readable
//   Row 3 (1X): button instructions
// ═══════════════════════════════════════════════════════════

void showSplash() {
  oled.clear();
  oled.set2X();
  oled.println(F(L_SPLASH_TITLE));
  oled.set1X();
  oled.println(F(L_SPLASH_LINE1));
  oled.println(F(L_SPLASH_LINE2));
  delay(2000);
}

void showWorking() {
  oled.clear();
  oled.println();
  oled.set2X();
  oled.println(F(L_WORKING));
  oled.set1X();
}

void showStatus(const char* msg) {
  oled.clear();
  oled.set1X();
  oled.println(F(L_RESULT));
  oled.set2X();
  oled.println(msg);
  oled.set1X();
  oled.print(F(L_BTN_OK));
}

void drawMenu() {
  oled.clear();
  oled.set1X();

  // Header: === MENU 1/5 ===
  oled.print(F(L_MENU_HEADER));
  oled.print(menuSel + 1);
  oled.print(F("/"));
  oled.print(MENU_COUNT);
  oled.println(F(" ==="));

  // Current item displayed large
  oled.set2X();
  readPgm(menuItems, menuSel);
  oled.println(pgmBuf);

  // Footer with button hints
  oled.set1X();
  if (!buttonsEnabled && menuSel >= 1 && menuSel <= 3)
    oled.print(F(L_MENU_LOCKED));
  else
    oled.print(F(L_MENU_NORMAL));
}

void drawDataScreen() {
  int8_t total = MAX_PARAMS;

  // Cyclic scrolling
  if (scrollOffset >= total) scrollOffset = 0;
  if (scrollOffset < 0) scrollOffset = total - 1;

  int8_t pIdx = scrollOffset;

  oled.clear();
  oled.set1X();

  // Header: parameter name + position counter
  readPgm(paramNames, pIdx);
  oled.print(pgmBuf);
  char counter[6];
  snprintf(counter, 6, "%d/%d", scrollOffset + 1, total);
  uint8_t nameLen = strlen(pgmBuf);
  uint8_t cLen = strlen(counter);
  int8_t pad = 21 - nameLen - cLen;
  for (int8_t i = 0; i < pad; i++) oled.print(' ');
  oled.println(counter);

  // Value displayed large
  oled.set2X();
  if (paramValues[pIdx][0] != '\0')
    oled.println(paramValues[pIdx]);
  else
    oled.println(F("---"));

  // Footer
  oled.set1X();
  oled.print(F(L_DATA_FOOTER));
}

// ═══════════════════════════════════════════════════════════
// MENU ACTIONS
// ═══════════════════════════════════════════════════════════

void execAction(int8_t item) {
  showWorking();

  switch (item) {

    case 0: {
      // Read Battery: reads model + message + live data in one go
      if (!readBatteryFull()) {
        strcpy_P(statusMsg, PSTR(L_NO_BATTERY));
        appState = STATE_SHOW_MSG;
        return;
      }
      scrollOffset = 0;
      appState = STATE_SHOW_DATA;
      break;
    }

    case 1: case 2: case 3: {
      // LED ON / LED OFF / Clear Errors
      if (!buttonsEnabled) {
        strcpy_P(statusMsg, PSTR(L_READ_FIRST));
        appState = STATE_SHOW_MSG;
        return;
      }
      if (item == 1)       ledsOn();
      else if (item == 2)  ledsOff();
      else                 clearErrors();

      strcpy_P(statusMsg, item == 1 ? PSTR(L_LEDS_ON) :
                           item == 2 ? PSTR(L_LEDS_OFF) :
                                       PSTR(L_ERRORS_CLEARED));
      appState = STATE_SHOW_MSG;
      break;
    }

    case 4: {
      // Reset Message (not yet implemented)
      strcpy_P(statusMsg, PSTR(L_IN_DEVELOPMENT));
      appState = STATE_SHOW_MSG;
      break;
    }
  }
}

// ═══════════════════════════════════════════════════════════
// SETUP
// ═══════════════════════════════════════════════════════════

void setup() {
  initButtons();
  pinMode(ENABLE_PIN, OUTPUT);
  digitalWrite(ENABLE_PIN, LOW);

  Wire.begin();
  Wire.setClock(400000L);

  oled.begin(&Adafruit128x32, OLED_ADDR);
  oled.setFont(Adafruit5x7);
  oled.clear();

  clearAllData();
  showSplash();

  // Show button status briefly (debug)
  oled.clear();
  oled.set1X();
  oled.print(F("BTN A(D"));
  oled.print(BTN_A);
  oled.print(F("): "));
  oled.println(btnA_ok ? F("OK") : F("STUCK LOW!"));
  oled.print(F("BTN B(D"));
  oled.print(BTN_B);
  oled.print(F("): "));
  oled.println(btnB_ok ? F("OK") : F("STUCK LOW!"));
  if (!btnA_ok || !btnB_ok) {
    oled.println(F("Check wiring!"));
  }
  delay(2000);

  bootTime = millis();
  appState = STATE_MENU;
  drawMenu();
}

// ═══════════════════════════════════════════════════════════
// MAIN LOOP
//
// Navigation:
//   MENU:    [A]=next item  [B]=execute  [A+]=nothing
//   DATA:    [A]=next param [B]=nothing  [A+]=back to menu
//   MSG:     [A]/[B]=back to menu
// ═══════════════════════════════════════════════════════════

void loop() {
  delay(10);  // Prevent CPU spinning, reduce noise sensitivity
  Button btn = readButton();
  if (btn == BTN_NONE) return;

  switch (appState) {

    case STATE_MENU:
      if (btn == BTN_NEXT) {
        menuSel = (menuSel + 1) % MENU_COUNT;
        drawMenu();
      }
      else if (btn == BTN_OK) {
        execAction(menuSel);
        if (appState == STATE_SHOW_MSG)  showStatus(statusMsg);
        else if (appState == STATE_SHOW_DATA) drawDataScreen();
      }
      break;

    case STATE_SHOW_DATA:
      if (btn == BTN_NEXT) {
        scrollOffset++;
        drawDataScreen();
      }
      else if (btn == BTN_BACK) {
        scrollOffset = 0;
        appState = STATE_MENU;
        drawMenu();
      }
      break;

    case STATE_SHOW_MSG:
      if (btn == BTN_NEXT || btn == BTN_OK || btn == BTN_BACK) {
        appState = STATE_MENU;
        drawMenu();
      }
      break;
  }
}
