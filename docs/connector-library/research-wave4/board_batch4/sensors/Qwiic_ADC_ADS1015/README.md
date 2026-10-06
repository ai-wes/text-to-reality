SparkFun Qwiic ADC
========================================

![SparkFun Qwiic 12 Bit ADC - 4 Channel ADS1015](https://cdn.sparkfun.com//assets/parts/1/3/8/5/7/15334-SparkFun_Qwiic_12_Bit_ADC_-_4_Channel__ADS1015_-02.jpg)

[*SparkFun Qwiic 12 Bit ADC - 4 Channel ADS1015 (Sen-15334)*](https://www.sparkfun.com/products/15334)

Qwiic breakout board for the ADS1015 4-channel 12-bit ADC from TI.

A lot of the time you just need to add more analog inputs to solve a problem. It happens. The SparkFun Qwiic 12 Bit ADC can provide four channels of I2C controlled ADC input to your Qwiic enabled project. These channels can be used as single-ended inputs, or in pairs for differential inputs. What makes this even more powerful is that it has a programmable gain amplifier that lets you "zoom in" on a very small change in analog voltage (but will still effect your input range and resolution). Utilizing our handy Qwiic system, no soldering is required to connect it to the rest of your system. However, we still have broken out 0.1"-spaced pins in case you prefer to use a breadboard.

The ADS1015 uses its own internal voltage reference for measurements, but a ground and 3.3V reference are also available on the pin outs for users. This ADC board includes screw pin terminals on the four channels of input, allowing for solderless connection to voltage sources in your setup. It also has an address jumper that lets you choose one of four unique addresses (0x48, 0x49, 0x4A, 0x4B). With this, you can connect up to four of these on the same I2C bus and have sixteen channels of ADC. The maximum resolution of the converter is 12-bits in differential mode and 11-bits for single-ended inputs. Step sizes range from 125μV per count to 3mV per count depending on the full-scale range (FSR) setting.

We have included an onboard 10K trimpot connected to channel A3. This is handy for initial setup testing and can be used as a simple variable input to your project. But don't worry, we added an isolation jumper so you can use channel A3 however you'd like.

Repository Contents
-------------------

* **/Hardware** - Eagle design files (.brd, .sch)
* **/Production** - Production panel files (.brd)

Documentation
--------------
* **[Arduino Library for the ADS1015](https://github.com/sparkfun/SparkFun_ADS1015_Arduino_Library)** - Arduino library for the ADS1015.
* **[Hookup Guide](https://learn.sparkfun.com/tutorials/qwiic-12-bit-adc-hookup-guide)** - Basic hookup guide for the SparkFun Qwiic 12 Bit ADC - 4 Channel ADS1015. Includes hardware overview, software installation instructions and overviews of each example in the arduino library.

License Information
-------------------

This product is _**open source**_! 

Please review the LICENSE.md file for license information. 

If you have any questions or concerns on licensing, please visit the [SparkFun Forum](https://forum.sparkfun.com/index.php) and post a topic. For more general questions related to our qwiic system, please visit this section of the forum: [SparkFun Forums: QWIIC SYSTEMS](https://forum.sparkfun.com/viewforum.php?f=105)

Distributed as-is; no warranty is given.

- Your friends at SparkFun.

