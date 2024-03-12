# Packet design:

To support new buttons, refer to <a href="#button-packet-length-1-byte">Button Packet</a>
You can also add new packets. The most significant bit of the first byte in new packets is 0 for button packet; thus, ensure that you use 1 as the most significant bit of the first byte.

## Battery Packet (length: 5 bytes)
- bytes[0] = 0xA0
- bytes[1:4] = battery voltage 4 byte float

## Button Packet (length: 1 byte)
- bit[7] = 0
- bit[6] = 0/1. 0 for no hold (short click). 1 for hold (long click)
- bit[5:4] = number of clicks button was clicked in a short period. if 00, then button was clicked once. if 11, then button was clicked 4 times
- bits[3:0] = button_idx
  - red button: 0
  - green button: 1
  - new buttons can be added here (16 buttons supported)

Example: green button **double** clicked and released (no hold):
Binary: **0**<span style="color:yellow">0</span><span style="color:orange">01</span> <span style="color:red">0000</span>.




