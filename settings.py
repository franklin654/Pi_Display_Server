from enum import Flag
from PySide6.QtCore import QSettings
from PySide6.QtCore import QDir

settings_file = QDir.homePath() + QDir.separator() + "display_settings.ini"

settings = QSettings(settings_file, QSettings.IniFormat)


class DispMode(Flag):
    TEXT = 1
    IMAGE = 2


display_mode = DispMode.TEXT
display_text = settings.value("display text", "FUCK OFF")
display_image = settings.value("display image", None)


def set_display_mode(value: DispMode):
    settings.setValue("display mode", value)


def set_display_text(value: str):
    settings.setValue("display text", value)


def set_display_image(value: str):
    settings.setValue("display image", value)
