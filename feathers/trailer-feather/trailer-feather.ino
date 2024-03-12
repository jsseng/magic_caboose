#include <RH_RF69.h>
#include <SPI.h>

#define RF69_FREQ 915.0

// First 3 here are boards w/radio BUILT-IN. Boards using FeatherWing follow.
#define RFM69_CS 8
#define RFM69_INT 3
#define RFM69_RST 4
#define LED 13

#define BATTERY_FLAG 0xA0

#define DEBUG 0

// Singleton instance of the radio driver
RH_RF69 rf69(RFM69_CS, RFM69_INT);

int16_t packetnum = 0; // packet counter, we increment per xmission

void setup() {
  Serial.begin(115200);
  // while (!Serial)
  //   delay(1); // Wait for Serial Console (comment out line if no computer)

  pinMode(LED, OUTPUT);
  pinMode(RFM69_RST, OUTPUT);
  digitalWrite(RFM69_RST, LOW);

#ifdef DEBUG
  Serial.println("Feather RFM69 TX Test!");
  Serial.println();
#endif

  // manual reset
  digitalWrite(RFM69_RST, HIGH);
  delay(10);
  digitalWrite(RFM69_RST, LOW);
  delay(10);

  if (!rf69.init()) {
#ifdef DEBUG
    Serial.println("RFM69 radio init failed");
#endif
    while (1)
      ;
  }
  Serial.println("RFM69 radio init OK!");
  // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM (for
  // low power module) No encryption
  if (!rf69.setFrequency(RF69_FREQ)) {
#ifdef DEBUG
    Serial.println("setFrequency failed");
#endif
  }

  // If you are using a high power RF69 eg RFM69HW, you *must* set a Tx power
  // with the ishighpowermodule flag set like this:
  rf69.setTxPower(
      14, true); // range from 14-20 for power, 2nd arg must be true for 69HCW

// The encryption key has to be the same as the one in the server
//   uint8_t key[] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
//                    0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08};
//   rf69.setEncryptionKey(key);
#ifdef DEBUG
  Serial.print("RFM69 radio @");
  Serial.print((int)RF69_FREQ);
  Serial.println(" MHz");
#endif
}

/**
 * @brief Reads in from rf69. if multiple bytes, take last byte only
 *
 * @return uint8_t flag. if no flag, return 0
 */
void *processRfm69Data() {
  if (rf69.available()) {
    static char buff[RH_RF69_MAX_MESSAGE_LEN];
    uint8_t len = sizeof(buff);
    if (rf69.recv((uint8_t *)buff, &len) && len > 0) {
      Serial.write(buff, len);
      Blink(LED, 50, 1);
    }
  }
  return NULL;
}

void loop() {
  static char buff[RH_RF69_MAX_MESSAGE_LEN];
  //   delay(1000); // Wait 1 second between transmits, could also 'sleep' here!

  if (Serial.available()) {
    // read in buff. keep byte available for null byte
    size_t bytesRead = Serial.readBytes(buff, RH_RF69_MAX_MESSAGE_LEN - 1);
    buff[bytesRead++] = '\0';
    rf69.send((uint8_t *)buff, bytesRead + 1);
    rf69.waitPacketSent();
  }
  // Now wait for a reply
  processRfm69Data();
}

void Blink(byte pin, byte delay_ms, byte loops) {
  while (loops--) {
    digitalWrite(pin, HIGH);
    delay(delay_ms);
    digitalWrite(pin, LOW);
    delay(delay_ms);
  }
}
