#include <RH_RF69.h>
#include <SPI.h>

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
// #include "custom_button.h"
#include "custom_button2.h"

#define WIRED_MODE 1

#define customPrintf(...)                                                      \
  if (!WIRED_MODE)                                                             \
  Serial.printf(__VA_ARGS__)
#define customPrintln(...)                                                     \
  if (!WIRED_MODE)                                                             \
  Serial.println(__VA_ARGS__)
#define customPrint(...)                                                       \
  if (!WIRED_MODE)                                                             \
  Serial.print(__VA_ARGS__)

#define RF69_FREQ 915.0

// First 3 here are boards w/radio BUILT-IN. Boards using FeatherWing follow.
#define RFM69_CS 8
#define RFM69_INT 3
#define RFM69_RST 4
#define LED 13

// battery pin
#define VBATPIN A7

#define BATTERY_FLAG 0xA0
#define ACCEL_FLAG 0xA1

#define RED_BUTTON_PACKET 0
#define GREEN_BUTTON_PACKET 1
#define TWO_BUTTON_PACKET 2

#define PACKET_HOLD_BIT_POS 6
#define PACKET_NUM_CLICKS_POS 4

#define BIG_GREEN_BUTTON_PIN 5
#define BIG_RED_BUTTON_PIN 6

#define FAKEGROUNDPIN 12

// Singleton instance of the radio driver
RH_RF69 rf69(RFM69_CS, RFM69_INT);
Adafruit_MPU6050 mpu;

int16_t packetnum = 0; // packet counter, we increment per xmission
Button green_button(BIG_GREEN_BUTTON_PIN);
Button red_button(BIG_RED_BUTTON_PIN);

bool mpu6050_enabled = false;

void setup() {
  Serial.begin(115200);
  // while (!Serial)
  //   delay(100); // Wait for Serial Console (comment out line if no computer)

  pinMode(LED, OUTPUT);
  pinMode(RFM69_RST, OUTPUT);
  digitalWrite(RFM69_RST, LOW);

  pinMode(FAKEGROUNDPIN, OUTPUT);
  digitalWrite(FAKEGROUNDPIN, LOW);

  customPrintln("Feather RFM69 TX Test!");
  customPrintln();

  if (green_button.is_clicked()) {
    Blink(LED_BUILTIN, 50, 2);
    mpu6050_enabled = true;
    init_accel_gyro();
  } else {
    Blink(LED_BUILTIN, 50, 1);
  }

  // manual reset
  digitalWrite(RFM69_RST, HIGH);
  delay(10);
  digitalWrite(RFM69_RST, LOW);
  delay(10);

  if (!rf69.init()) {
    customPrintln("RFM69 radio init failed");
    while (1)
      ;
  }
  customPrintln("RFM69 radio init OK!");
  // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM (for
  // low power module) No encryption
  if (!rf69.setFrequency(RF69_FREQ)) {
    customPrintln("setFrequency failed");
  }

  // If you are using a high power RF69 eg RFM69HW, you *must* set a Tx power
  // with the ishighpowermodule flag set like this:
  rf69.setTxPower(
      14, true); // range from 14-20 for power, 2nd arg must be true for 69HCW

  customPrint("RFM69 radio @");
  customPrint((int)RF69_FREQ);
  customPrintln(" MHz");
}

void loop() {
  static char buff[RH_RF69_MAX_MESSAGE_LEN];
  static unsigned i = 0;

  // alternate turn so that we don't send multiple stuff over rf at same time
  switch (i) {
  case 0:
    sendBatteryPeriodically();
    break;

  case 1:
    handle_two_buttons();
    break;

  case 2:
    send_accel_gyro_periodically();
    break;

  default:
    break;
  }

  i = (i + 1) % 3;

  // Now wait for a reply
  // uint8_t len = sizeof(buff);
  // if (rf69.available()) {
  //   // Should be a reply message for us now
  //   if (rf69.recv((uint8_t *)buff, &len)) {
  //     customPrint("Got a reply: ");
  //     customPrintln((char *)buff);
  //     Blink(LED, 50, 3); // blink LED 3 times, 50ms between blinks
  //   } else {
  //     customPrintln("Receive failed");
  //   }
  // }
}

void Blink(byte pin, byte delay_ms, byte loops) {
  while (loops--) {
    digitalWrite(pin, HIGH);
    delay(delay_ms);
    digitalWrite(pin, LOW);
    delay(delay_ms);
  }
}

void sendFlag(uint8_t flag) {
  rf69.send(&flag, 1);
  if (WIRED_MODE) {
    Serial.write(&flag, 1);
  }
  Blink(LED, 50, 1);
}

void sendBatteryPeriodically() {
  static uint32_t last_sent_time = 0;

  if (millis() - last_sent_time > 30000) {
    sendBattery();
    last_sent_time = millis();
  }
}

void sendBattery() {
  float measuredbat = getBattery();
  uint8_t batteryPacket[1 + sizeof(measuredbat)];
  batteryPacket[0] = BATTERY_FLAG;
  memcpy(batteryPacket + 1, &measuredbat, sizeof(measuredbat));
  rf69.send(batteryPacket, sizeof(batteryPacket));
  if (WIRED_MODE) {
    Serial.write(batteryPacket, sizeof(batteryPacket));
  }
}

float getBattery() {
  float measuredvbat = analogRead(VBATPIN);
  measuredvbat *= 2;    // we divided by 2, so multiply back
  measuredvbat *= 3.3;  // Multiply by 3.3V, our reference voltage
  measuredvbat /= 1024; // convert to voltage
  return measuredvbat;
}

void init_accel_gyro() {
  // Try to initialize!
  if (!mpu.begin()) {
    customPrintln("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }
  customPrintln("MPU6050 Found!");

  mpu.setAccelerometerRange(MPU6050_RANGE_4_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  delay(100);
}

int8_t map_to_int8_t(float num, float max_val) {
  int val = num * 127.0 / max_val;
  if (val > 127) {
    val = 127;
  } else if (val < -128) {
    val = -128;
  }
  return val;
}

void send_accel_gyro() {
  const float max_gravity = 4.0 * SENSORS_GRAVITY_STANDARD;
  uint8_t packet[7];
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  packet[0] = ACCEL_FLAG;
  packet[1] = map_to_int8_t(a.acceleration.y, max_gravity);
  packet[2] = map_to_int8_t(a.acceleration.x, max_gravity);
  packet[3] = map_to_int8_t(a.acceleration.z, max_gravity);
  packet[4] = map_to_int8_t(g.gyro.x, max_gravity);
  packet[5] = map_to_int8_t(g.gyro.z, max_gravity);
  packet[6] = map_to_int8_t(g.gyro.y, max_gravity);

  if (packet[1] == 0 && packet[2] == 0 && packet[3] == 0) {
    Blink(LED_BUILTIN, 50, 2);
    init_accel_gyro();
    return;
  }

  customPrint("Acceleration X: ");
  customPrint(packet[0]);
  customPrint(", Y: ");
  customPrint(packet[1]);
  customPrint(", Z: ");
  customPrint(packet[2]);
  customPrintln();

  rf69.send(packet, 7);
  if (WIRED_MODE) {
    Serial.write(packet, 7);
  }
}

void send_accel_gyro_periodically() {
  if (!mpu6050_enabled) {
    return;
  }
  const uint32_t send_period_ms = 100; // 10Hz => 100ms
  static unsigned long last_sent_time = 0;

  if (millis() - last_sent_time > send_period_ms) {
    send_accel_gyro();
    last_sent_time = millis();
  }
}

typedef enum {
  TWO_BUTTONS_WAIT,
  TWO_BUTTONS_CHECK_FOR_OTHER_HOLD,
} two_buttons_state_t;

void handle_two_buttons() {
  static two_buttons_state_t state = TWO_BUTTONS_WAIT;
  static unsigned long first_long_click;
  static button_status_t original_status;
  static Button *other_button;
  green_button.update();
  red_button.update();

  if (green_button.status.clicked && !green_button.status.hold) {
    sendFlag(0 << PACKET_HOLD_BIT_POS |
             (green_button.status.num_clicks & 0x3) << PACKET_NUM_CLICKS_POS |
             GREEN_BUTTON_PACKET);
    customPrintf("Green click: %d times\n", green_button.status.num_clicks);
  }
  if (red_button.status.clicked && !red_button.status.hold) {
    sendFlag(0 << PACKET_HOLD_BIT_POS |
             (red_button.status.num_clicks & 0x3) << PACKET_NUM_CLICKS_POS |
             RED_BUTTON_PACKET);
    customPrintf("Red click: %d times\n", red_button.status.num_clicks);
  }

  switch (state) {
  case TWO_BUTTONS_WAIT:
    if (green_button.status.clicked && green_button.status.hold) {
      if (red_button.status.clicked && red_button.status.hold) {
        customPrintf("Green click: %d times\n", green_button.status.num_clicks);
        // long click
        // Both buttons long clicked
        sendFlag(1 << PACKET_HOLD_BIT_POS |
                 (green_button.status.num_clicks & 0x3)
                     << PACKET_NUM_CLICKS_POS |
                 TWO_BUTTON_PACKET);
        customPrintf("Both hold: %d times\n", green_button.status.num_clicks);
      } else {
        first_long_click = millis();
        original_status = green_button.status;
        other_button = &red_button;
        state = TWO_BUTTONS_CHECK_FOR_OTHER_HOLD;
        customPrintf("(Green hold): %d times\n",
                     green_button.status.num_clicks);
      }
    } else if (red_button.status.clicked && red_button.status.hold) {
      first_long_click = millis();
      original_status = red_button.status;
      other_button = &green_button;
      state = TWO_BUTTONS_CHECK_FOR_OTHER_HOLD;
      customPrintf("(Red hold): %d times\n", red_button.status.num_clicks);
    }
    break;

  case TWO_BUTTONS_CHECK_FOR_OTHER_HOLD:
    if (millis() - first_long_click > 500) {
      sendFlag(1 << PACKET_HOLD_BIT_POS |
               (original_status.num_clicks & 0x3) << PACKET_NUM_CLICKS_POS |
               (other_button == &red_button ? GREEN_BUTTON_PACKET
                                            : RED_BUTTON_PACKET));
      state = TWO_BUTTONS_WAIT;
      customPrintf("%s hold: %d times\n",
                   other_button == &red_button ? "Green" : "Red",
                   original_status.num_clicks);
    } else if (other_button->status.clicked && other_button->status.hold) {
      sendFlag(1 << PACKET_HOLD_BIT_POS |
               (original_status.num_clicks & 0x3) << PACKET_NUM_CLICKS_POS |
               TWO_BUTTON_PACKET);
      state = TWO_BUTTONS_WAIT;
      customPrintf("Both hold: %d times\n", original_status.num_clicks);
    }
    break;

  default:
    break;
  }
}
