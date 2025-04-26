import usb
import fastcrc
import enum

class AttrHook(enum.IntEnum):
    """
    Can be used as user-data for customs event handling. So instead of using a string that says "mini2_brightness_hook" or whatever, you can use these
    """
    Brightness = 0x00
    Contrast = 0x01
    Scene = 0x02

class CommandClasses(enum.Enum):
    """
    Most Commands will use 0x10, but some, like zoom and shutter use 0x01
    """
    Basic = b'\x10'
    SPECIAL = b'\x01'


class CommandIndex(enum.Enum):
    ShutterSettings = b'\x02'
    ColorVideo = b'\x03'
    ImageSettings = b'\x04'
    ImageFormat = b'\x10'
    Calibration = b'\x11'
    ShutterSet = b'\x0f'
    Zoom = b'1'


class SubCommand(enum.Enum):
    """
    Some of these values are duplicates, because I couldn't come up with a better naming scheme...
    """
    EdgeEnhancement = b'N'
    Gamma = b'M'
    TNR = b'L'
    SNR = b'K'
    Contrast = b'J'
    Brightness = b'G'
    DetailEnhancement = b'E'
    PseudoColor = b'E'
    SceneMode = b'B'
    PointZoom = b'Q'
    Zoom = b'B'
    YuvFormat = b'M'
    ImageSource = b'E'
    ShutterSet = b'E'
    DetectorFPS = b'D'
    SaveVideoFormat = b'I'
    AnalogVideo = b'J'
    DigitalVideo = b'F'
    ParameterSave = b'Q'
    ParameterRestore = b'R'
    BurnProtection = b'K'
    AutoShutter = b'A'
    Flip = b'C'
    ShutterCalibration = b'C'
    BackgroundCorrection = b'R'
    ModuleSleep = b'H'


class SceneMode(enum.IntEnum):
    LowHighlight = 0x00
    LinearStretch = 0x01
    LowContrast = 0x02
    GeneralMode = 0x03
    HighContrast = 0x04
    Highlight = 0x05
    Outline = 0x09

class PseudoColor(enum.IntEnum):
    WhiteHot = 0x0
    Sepia = 0x1
    Ironbow = 0x2
    Rainbow = 0x3
    Night = 0x4
    Aurora = 0x5
    RedHot = 0x6
    Jungle = 0x7
    Medical = 0x8
    BlackHot = 0x9
    GoldenRed = 0xA

class FlipMode(enum.IntEnum):
    No_Flip = 0x00
    X_Flip = 0x01
    Y_Flip = 0x02
    XY_Flip = 0x03

class ImageSource(enum.IntEnum):
    IR = 0x00
    KBC = 0x01
    TNR = 0x02
    SNR = 0x03
    DDE = 0x04
    YUV = 0x05

class DigitalVideoFormat(enum.IntEnum):
    UsbProgressive = 0x00
    DvpProgressive = 0x01
    Bt656Progressive = 0x02
    bt656Interlaced = 0x12
    MipiProgressive = 0x03

class DigitalFrameRate(enum.IntEnum):
    """
    30/60 for 384core and 640core
    25/50 for 256core
    """
    Hz30 = 0x1e
    Hz60 = 0x3c
    Hz25 = 0x19
    Hz50 = 0x32
    Hz_NA = 0x0

class AnalogVideoFormat(enum.IntEnum):
    NTSC = 0x00
    PAL = 0x01

class YuvFormat(enum.IntEnum):
    UYVY = 0x0
    VYUY = 0x1
    YUYV = 0x2
    YVYU = 0x3

class Mini2:
    def __init__(self):
        for vendor, product in (
                (0x3474, 0x43c1), # IDs for 256core
                (0x3474, 0x43d1), # IDs for 384core (?)
                (0x3474, 0x43e1), # IDs for 640core
        ):
            self.dev = usb.core.find(idVendor=vendor, idProduct=product)
            if self.dev is not None:
                break
        if self.dev is None:
            raise RuntimeError("No Mini2 camera was found!")

    def write_command(self, command_class, command_index, sub_command, parameter_1, parameter_2):
        out_list = [command_class, command_index, sub_command, b'\x00', parameter_1, parameter_2, b'\x00\x00', b'\x00\x00']

        out_bytes = b""
        for item in out_list:
            if type(item) != bytes:
                out_bytes += item.value
            else:
                out_bytes += item

        assert len(out_bytes) == 16

        crc = fastcrc.crc16.xmodem(out_bytes)

        out_bytes += crc.to_bytes(2)[1].to_bytes(1) + crc.to_bytes(2)[0].to_bytes(1)

        try:
            self.dev.ctrl_transfer(bmRequestType=0x41, bRequest=32, wValue=0x0000, wIndex=0x0000,
                                   data_or_wLength=out_bytes)
        except usb.core.USBError:
            pass

    @staticmethod
    def parameter_value(value: int):
        """
        Used for basic commands that take a small value range. Turns 0x01 into 0x01_00_00_00 because parameters are always 4bytes and little endian
        """
        assert type(value) == int

        return value.to_bytes(4, "little")

    def set_brightness(self, value: int):
        assert type(value) == int and 0 <= value <= 100
        self.write_command(CommandClasses.Basic, CommandIndex.ImageSettings, SubCommand.Brightness, self.parameter_value(int(value)), self.parameter_value(0))

    def set_contrast(self, value: int):
        assert type(value) == int and 0 <= value <= 100
        self.write_command(CommandClasses.Basic, CommandIndex.ImageSettings, SubCommand.Contrast, self.parameter_value(int(value)), self.parameter_value(0))

    def set_scene(self, scene: SceneMode):
        self.write_command(CommandClasses.Basic, CommandIndex.ImageSettings, SubCommand.SceneMode, self.parameter_value(int(scene)), self.parameter_value(0))

    def set_pseudo_color(self, pseudo_color: PseudoColor):
        self.write_command(CommandClasses.Basic, CommandIndex.ColorVideo, SubCommand.PseudoColor, b'\x00' + pseudo_color.to_bytes(1) + b'\x00\x00', self.parameter_value(0))

    def set_flip(self, flip: FlipMode):
        self.write_command(CommandClasses.Basic, CommandIndex.ImageFormat, SubCommand.Flip, self.parameter_value(int(flip)), self.parameter_value(0))

    def set_edge_enhancement(self, gear: int):
        assert type(gear) == int and 0 <= gear <= 2

        self.write_command(CommandClasses.Basic, CommandIndex.ImageSettings, SubCommand.EdgeEnhancement, self.parameter_value(int(gear)), self.parameter_value(0))

    def set_detail_enhancement(self, gear: int):
        assert type(gear) == int and 0 <= gear <= 100
        self.write_command(CommandClasses.Basic, CommandIndex.ImageSettings, SubCommand.DetailEnhancement,
                           self.parameter_value(int(gear)), self.parameter_value(0))

    def set_snr(self, gear: int):
        assert type(gear) == int and 0 <= gear <= 100
        self.write_command(CommandClasses.Basic, CommandIndex.ImageSettings, SubCommand.SNR,
                           self.parameter_value(int(gear)), self.parameter_value(0))

    def set_tnr(self, gear: int):
        assert 0 <= gear <= 100
        self.write_command(CommandClasses.Basic, CommandIndex.ImageSettings, SubCommand.TNR,
                           self.parameter_value(int(gear)), self.parameter_value(0))

    def set_gamma(self, gear: int):
        assert type(gear) == int and 0 <= gear <= 100


    def set_image_source(self, image_source: ImageSource):
        self.write_command(CommandClasses.Basic, CommandIndex.ImageFormat, SubCommand.ImageSource, self.parameter_value(int(image_source)), self.parameter_value(0))

    def set_shutter_position(self, closed_open: int):
        """
        0 for Closed
        1 for Open
        """
        assert type(closed_open) == int and 0 <= closed_open <= 1
        self.write_command(CommandClasses.Basic, CommandIndex.ShutterSet, SubCommand.ShutterSet, self.parameter_value(closed_open), self.parameter_value(0))

    def do_shutter_calibration(self):
        self.write_command(CommandClasses.Basic, CommandIndex.ShutterSettings, SubCommand.ShutterCalibration, self.parameter_value(0), self.parameter_value(0))

    def do_background_correction(self):
        self.write_command(CommandClasses.SPECIAL, CommandIndex.ImageFormat, SubCommand.BackgroundCorrection, self.parameter_value(0), self.parameter_value(0))

    def set_auto_shutter_switch(self, off_on: int):
        """
        0 for Off
        1 for On
        """
        assert type(off_on) == int and 0 <= off_on <= 1
        self.write_command(CommandClasses.Basic, CommandIndex.ShutterSettings, SubCommand.AutoShutter, self.parameter_value(off_on), self.parameter_value(0))

    def set_burn_protection(self, off_on: int):
        assert type(off_on) == int and 0 <= off_on <= 1
        self.write_command(CommandClasses.Basic, CommandIndex.ColorVideo, SubCommand.BurnProtection, self.parameter_value(off_on), self.parameter_value(0))

    def set_sleep(self, wake_up_or_sleep):
        """
        0 for wake_up
        1 for sleep
        """
        assert type(wake_up_or_sleep) == int and 0 <= wake_up_or_sleep <= 1
        self.write_command(CommandClasses.Basic, CommandIndex.ImageFormat, SubCommand.ModuleSleep, self.parameter_value(wake_up_or_sleep), self.parameter_value(0))

    def save_parameters(self):
        """
        This will save some parameter, but not all. For example zoom is not saved, so anytime the module boots, the zoom will be 1x
        """
        self.write_command(CommandClasses.Basic, CommandIndex.ImageFormat, SubCommand.ParameterSave, self.parameter_value(0), self.parameter_value(0))

    def restore_parameters(self):
        """
        Resets the saved parameters back to default, I wouldn't recommend using this unless you know what you're doing, as this might result in loosing video feed.
        In the event that you already did mess up, use the windows software from Hdaniee to properly restore them, if using the commands in this wrapper isn't working.
        """
        self.write_command(CommandClasses.Basic, CommandIndex.ImageFormat, SubCommand.ParameterRestore,
                           self.parameter_value(0), self.parameter_value(0))

    def set_digital_video_format(self, off_on: int, digital_video_format: DigitalVideoFormat, digital_video_fps: DigitalFrameRate):
        """
        0 for disabled
        1 for digital video output enabled
        """
        assert type(off_on) == int and 0 <= off_on <= 1
        self.write_command(CommandClasses.Basic, CommandIndex.ImageFormat, SubCommand.DigitalVideo,
                           off_on.to_bytes(1) + digital_video_format.to_bytes(1) + digital_video_fps.to_bytes(1) + b'\x00', self.parameter_value(0))

    def set_analog_video_format(self, off_on: int, analog_video_format: AnalogVideoFormat):
        """
        1 for digital video output enabled
        0 for disabled
        :return:
        """
        assert type(off_on) == int and 0 <= off_on <= 1
        assert analog_video_format == AnalogVideoFormat.NTSC if off_on == 0 else True
        self.write_command(CommandClasses.Basic, CommandIndex.ImageFormat, SubCommand.AnalogVideo, off_on.to_bytes(1) + analog_video_format.to_bytes(1) + b'\x00\x00', self.parameter_value(0))

    def save_digital_video_format(self):
        self.write_command(CommandClasses.Basic, CommandIndex.ImageFormat, SubCommand.SaveVideoFormat, self.parameter_value(0), self.parameter_value(0))

    def set_detector_frame_rate(self, detector_frame_rate: DigitalFrameRate):
        self.write_command(CommandClasses.Basic, CommandIndex.ImageFormat, SubCommand.DetectorFPS, self.parameter_value(int(detector_frame_rate)), self.parameter_value(0))

    def set_yuv_format(self, yuv_format: YuvFormat):
        self.write_command(CommandClasses.Basic, CommandIndex.ColorVideo, SubCommand.YuvFormat, self.parameter_value(int(yuv_format)), self.parameter_value(0))

    def set_zoom_centre(self, zoom_level: int):
        assert 10 <= zoom_level <= 80 # 1x zoom to 8x zoom allowed
        self.write_command(CommandClasses.SPECIAL, CommandIndex.Zoom, SubCommand.Zoom, b'\x00' + zoom_level.to_bytes(1) + b'\x00\x00', self.parameter_value(0))

    def set_zoom_on_point(self, zoom_level: int, x: int, y: int):
        assert 10 <= zoom_level <= 80  # 1x zoom to 8x zoom allowed
        self.write_command(CommandClasses.SPECIAL, CommandIndex.Zoom, SubCommand.PointZoom, b'\x00' + zoom_level.to_bytes(1) + b'\x00\x00', x.to_bytes(2, "little") + y.to_bytes(2, "little"))



if __name__ == '__main__':
    mini = Mini2()

