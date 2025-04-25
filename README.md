# Mini2_USB library
This is a code collection for sending (and in the future reading) data to the Mini2 Thermal Cameras (Commonly sold under the name UV256/384/640)

## Setup
1. Install the requirements found in `requirements.txt`
2. Insure pyusb has a working backend, this isn't super straight forward on windows, but on Linux it usually works out-of-the-box
3. Import the `Mini2` class from `Mini2.py` in your code and create an instance.
4.  Use the methods provided by the `Mini2`-instance to send the desired commands.

## List of methods

- `set_brightness(value: int)`
	-  `value` must be between 0 and 100

- `set_contrast(value: int )`
	- `value` must be between 0 and 100

- `set_scene(scene: SceneMode)`
	- [Scene Modes](#Scene-Modes)

- `set_pseudo_color(pseudo_color: PseudoColor)`
	- [Pseudo Colors](#Pseudo-Colors)
	
- `set_flip(flip: FLipMode)`
	-  [Flip Modes](#Flip-Modes)
	-  Note that image flip doesn't work while zoom is greater than 1.0, and the other way around.

- `set_edge_enhancement(gear: int)`
	- Used to make the lines of the [Outline Scene Mode](#Scene-Modes) thicker. 0 is the default, with fairly thin lines.
	- `gear` must be a value between 0 and 2

- `set_detail_enhancement(gear: int)`
	- Detail enhancment is like a sharpening filter, 0 makes the image looks soft, 100 makes it very sharp.
	- `gear` must be between 0 and 100

- `set_snr(gear: int)`
	- Spatial Noise Reduction.
	- `gear` must be between 0 and 100

- `set_tnr(gear: int)`
	- Temporal Noise Reduction. A value of close to 100 makes a pretty bad ghosting effect. 50 is default
	- `gear` must be between 0 and 100

- `set_gamma(gear: int)`
	- I'm sure this does something, but I'm not sure what.
	- `gear` must be between 0 and 100

- `set_image_source(image_source: ImageSource)`
	- Sets at what stage of image processing you want to read from
	- [Images Sources](#Image-Sources)

- `set_shutter_position(closed_open: int)`
	- `0` for Closed, 1 for Open

- `do_shutter_calibration()`
	- closes the shutter and does calibration for Non-uniformity-correction (NUCing), and then opens the shutter again.

- `do_background_correction()`

- `set_auto_shutter_switch(off_on: int)`
	- `0` for off, `1` for on
	- When enabled this will cause the module to do shutter calibrations automatically instead of having to manually call it.

- `set_burn_protection(off_on: int)`
	- `0` for off, `1` for on
	- Highly recommend to enable. Looking at exterm heat sources like fires, or worse, the sun, can burn pixels on the sensor. Burn protection will detect that you're looking at such a heat source and close the shutter. To open it again, either way for auto shutter, or send another command that will open/cycle the shutter.

- `set_sleep(wake_up_sleep: int)`
	- `0` for wake_up, `1` for sleep
	- After putting the module to sleep it'll only listen for the wake-up call, everything else is ignored.

- `save_parameters()`
	- Saves a bunch of settings like if burn protection is enabled. Note that some settings like zoom aren't saved, so those need to be set again via commands after each boot.

- `restore_parameters()`
	- Resets the saved parameters back to default, I wouldn't recommend using this unless you know what you're doing, as this might result in loosing video feed.
        In the event that you already did mess up, use the windows software from Hdaniee to properly restore them, if using the commands in this wrapper isn't working.
				
- `set_digital_video_format(off_on: int, digital_video_format: DigitalVideoFormat, digital_video_fps: DigitalFrameRate)`
	- `off_on`: `0` for no digital output, `1` for enabled. Note that if you want to disable digital video, you need to send `UsbProgressive` and `Hz_NA` because those are values of `0x0`
	- [Digital Video Formats](#Digital-Video-Formats)
	- Note that sending the command for `bt656Interlaced` doesn't work with the current implementation
	- On Linux I had the issue that by default the FPS of USB video is 25Hz with the 256core, to get 50Hz you need to set both the Detector Refreshrate and the DigitalVideoFormat to 50/60Hz

- `set_analog_video_format(off_on: int, analog_video_format: AnalogVideoFormat)`
	- `off_on`: `0` for no analog output, `1` for enabled. If you want to disable analog video output, send `NTSC` along side the `0`
	- Note that even though you might use a USB board the pins of the 50pin connector are there, so if you make a custom PCB with the connector, you can probably use USB output and analog at the same time, might be usefull when using Computer Vision stuff on FPVs while also using the camera for video link.

- `set_detector_frame_rate(detector_frame_rate: DigitalFrameRate)`
	- [Detector Refresh Rates](#Digital-Frame-Rates)
	- On Linux I had the issue that by default the FPS of USB video is 25Hz with the 256core, to get 50Hz you need to set both the Detector Refreshrate and the DigitalVideoFormat to 50/60Hz

- `set_yuv_format(yuv_format: YuvFormat)`
	- [YUV Formats](#YUV-Formats)
	- Allows you to change the bit order of the YUV format. When using something like OpenCV you can enable auto conversion to RGB888, instead of messing with YUV

- `set_zoom_centre(zoom_level: int)`
	- `zoom_level` must be between `10` and `80`, which correspond to 1x to 8x
	- Note that zoom and flip don't work at the same time

- `set_zoom_on_point(zoom_level: int, x: int, y: int)`
	- `zoom_level` must be between `10` and `80`, which correspond to 1x to 8x
	- X and Y must be values between `0` and the sensor width/height of your modules sensor.
	- Note that zoom and flip don't work at the same time


## Enums
### Scene Modes
- `SceneMode`
	- `LowHighlight`
	- `LinearStretch`
	- `LowContrast`
	- `GeneralMode`
	- `HighContrast`
	- `Highlight`
	- `Outline`
	
### Pseudo Colors
- `PseudoColor`
	- `WhiteHot`
	- `Sepia`
	- `Ironbow`
	- `Rainbow`
	- `Night`
	- `Aurora`
	- `RedHot`
	- `Jungle`
	- `Medical`
	- `BlackHot`
	- `GoldenRed`

### Flip Modes
- `FlipMode`
	- `No_Flip`
	- `X_Flip`
	- `Y_Flip`
	- `XY_Flip`

### Image-Sources
- `ImageSource`
	- `IR` raw detector output
	- `KBC` w/ KB correction
	- `TNR` 
	- `SNR` 
	- `DDE` After streching and detail enhancement
	- `YUV` final output

### Digital Video Formats
- `DigitalVideoFormat`
	- `UsbProgressive` If you're using this lib, you'll probably want this option...
	- `DvpProgressive`
	- `Bt656Progressive`
	- `bt656Interlaced` Value is correct but correctly there is no implementation for sending this command in the right format.
	- `MipiProgressive`

### Digital Frame Rates
- `DigitalFrameRate`
	- `Hz30` 384/640
	- `Hz60` 384/60
	- `Hz25` 256
	- `Hz50` 256
	- `Hz_NA` value of `0x0`, used when disabling digital video

### YUV Formats
- `YuvFormat`
	- `UYVY`
	- `VYUY`
	- `YUYV` I believe this is the default
	- `YVYU`









