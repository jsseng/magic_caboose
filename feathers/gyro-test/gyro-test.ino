// Basic demo for accelerometer readings from Adafruit MPU6050

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

#define ACCEL_FLAG 0xA1

Adafruit_MPU6050 mpu;

void setup(void) {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
  // while (!Serial)
  //   delay(10); // will pause Zero, Leonardo, etc until serial console opens

  // Serial.println("Adafruit MPU6050 test!");

  // // Try to initialize!
  // if (!mpu.begin()) {
  //   Serial.println("Failed to find MPU6050 chip");
  //   while (1) {
  //     delay(10);
  //   }
  // }
  // Serial.println("MPU6050 Found!");

  // mpu.setAccelerometerRange(MPU6050_RANGE_4_G);
  // mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  // mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  init_accel_gyro();
  delay(100);
}

void loop() {
  // sensors_event_t a, g, temp;
  // mpu.getEvent(&a, &g, &temp);

  // /* Print out the values */
  // Serial.print("Acceleration X: ");
  // Serial.print(a.acceleration.x);
  // Serial.print(", Y: ");
  // Serial.print(a.acceleration.y);
  // Serial.print(", Z: ");
  // Serial.print(a.acceleration.z);
  // Serial.println(" m/s^2");

  // Serial.print("Acceleration X %: ");
  // Serial.print(convert_accel_range(a.acceleration.x));
  // Serial.print(", Y %: ");
  // Serial.print(convert_accel_range(a.acceleration.y));
  // Serial.print(", Z %: ");
  // Serial.print(convert_accel_range(a.acceleration.z));
  // Serial.println();

  // Serial.print("Rotation X: ");
  // Serial.print(g.gyro.x);
  // Serial.print(", Y: ");
  // Serial.print(g.gyro.y);
  // Serial.print(", Z: ");
  // Serial.print(g.gyro.z);
  // Serial.println(" rad/s");

  // Serial.print("Temperature: ");
  // Serial.print(temp.temperature);
  // Serial.println(" degC");

  // Serial.println("");
  // delay(500);

  send_accel_gyro_periodically();
  // delay(500);
}

void init_accel_gyro() {
  // Try to initialize!
  if (!mpu.begin()) {
    // Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }
  // Serial.println("MPU6050 Found!");

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

  // customPrint("Acceleration X: ");
  // customPrint(packet[0]);
  // customPrint(", Y: ");
  // customPrint(packet[1]);
  // customPrint(", Z: ");
  // customPrint(packet[2]);
  // customPrintln();

  // rf69.send(packet, 7);
  // if (WIRED_MODE) {
  Serial.write(packet, 7);
  // }
}

void send_accel_gyro_periodically() {
  const uint32_t send_period_ms = 200; // 10Hz => 100ms
  static unsigned long last_sent_time = 0;

  if (millis() - last_sent_time > send_period_ms) {
    send_accel_gyro();
    last_sent_time = millis();
  }
}

void Blink(byte pin, byte delay_ms, byte loops) {
  while (loops--) {
    digitalWrite(pin, HIGH);
    delay(delay_ms);
    digitalWrite(pin, LOW);
    delay(delay_ms);
  }
}