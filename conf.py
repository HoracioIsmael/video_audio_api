import os

class Config:
    STATIC_FOLDER = os.path.join(os.getcwd(), 'static', 'videos')

    IMAGEMAGICK_BINARY = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
