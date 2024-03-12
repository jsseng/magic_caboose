/**
 * @brief Interface for big button. builtin debouncing
 * @author Christian Honein
 */
#ifndef BUTTON_H
#define BUTTON_H

// clicks with 200ms are counted as multiple clicks
// example: two clicks with 200ms count as double clicks
#define MULTICLICK_WAIT_DUR 140
// maximum number of multiple clicks. for now support up to triple click
#define MAX_MULTICLICK 3
#define DEBOUNCE_DUR 10
#define LONG_PRESS_DUR 2000

typedef enum {
  WAIT_FOR_BUTTON_DOWN,
  BUTTON_DOWN_DEBOUNCE,
  BUTTON_UP_DEBOUNCE,
  WAIT_FOR_BUTTON_UP,
  WAIT_FOR_DEBOUNCE
} button_state_t;

typedef struct {
  bool clicked = false;
  bool hold = false;
  unsigned char num_clicks;
} button_status_t;

/**
 * @brief A button which support multiple clicks, debouncing and hold
 */
struct Button {
private:
  uint32_t pin;
  unsigned long down_time = 0;  // time button was clicked down
  unsigned long up_time = 0;    // time button was released up
  unsigned char num_clicks = 0; // num times button was clicked
  button_state_t state = WAIT_FOR_BUTTON_DOWN;

public:
  button_status_t status;
  Button(uint32_t pin) {
    this->pin = pin;
    pinMode(pin, INPUT_PULLUP);
  }

  bool is_clicked() { return !digitalRead(pin); }

  /**
   * @brief Button state machine
   *
   * @return uint8_t returns 0 if no click. > 0 if there is click. Value
   * returned is number of times button was clicked
   */
  void update() {
    status.clicked = false;

    switch (state) {
    case WAIT_FOR_BUTTON_DOWN:
      // multiclick support
      if (num_clicks > 0 && millis() - up_time > MULTICLICK_WAIT_DUR ||
          num_clicks == MAX_MULTICLICK) {
        // there are clicks and no click was detected in MULTICLICK_WAIT_DUR or
        // num_clicks == MAX_MULTICLICK
        // so report click
        status.num_clicks = num_clicks;
        status.hold = false;
        status.clicked = true;
        num_clicks = 0;
      }
      if (!digitalRead(pin)) { // button down
        // button clicked
        state = BUTTON_DOWN_DEBOUNCE;
        down_time = millis();
      }
      break;

    case BUTTON_DOWN_DEBOUNCE:
      if (millis() - down_time > DEBOUNCE_DUR) {
        // after 10 ms check if button still clicked
        if (!digitalRead(pin)) {
          // button still down. register click
          state = WAIT_FOR_BUTTON_UP;
          num_clicks += 1;
          // return 1;
        } else {
          // false button down. ignore click
          state = WAIT_FOR_BUTTON_DOWN;
        }
      }
      break;

    case WAIT_FOR_BUTTON_UP:
      // long press support
      if (num_clicks > 0 && millis() - down_time > LONG_PRESS_DUR) {
        // report long press even before button up
        status.hold = true;
        status.num_clicks = num_clicks;
        status.clicked = true;
        num_clicks = 0;
      }
      if (digitalRead(pin)) { // button up
        state = BUTTON_UP_DEBOUNCE;
        up_time = millis();
      }
      break;

    case BUTTON_UP_DEBOUNCE:
      if (millis() - up_time > DEBOUNCE_DUR) {
        if (digitalRead(pin)) { // button up
          state = WAIT_FOR_BUTTON_DOWN;
        } else {
          // false up. go back to WAIT_FOR_BUTTON_UP
          state = WAIT_FOR_BUTTON_UP;
        }
      }
      break;

    default:
      state = WAIT_FOR_BUTTON_DOWN;
      break;
    }
  }
};

#endif
