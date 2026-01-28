[app]

# Application title
title = CuraX Alert Bot

# Package name
package.name = curaxalertbot

# Package domain
package.domain = com.curax

# Source code directory
source.dir = .

# Source files
source.include_exts = py,png,jpg,kv,atlas

# Version
version = 1.0

# Application requirements
# sqlite3 is built-in to Python, requests needs urllib3
requirements = python3,kivy==2.2.1,pyjnius==1.4.2,certifi,urllib3,charset-normalizer,idna,requests

# Presplash background color
presplash.color = #0099ff

# Supported orientations
orientation = portrait

# Android permissions
android.permissions = INTERNET,VIBRATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Android API level
android.api = 31

# Minimum API level
android.minapi = 21

# Android SDK version
android.ndk = 25b

# Android architecture
android.archs = armeabi-v7a

[buildozer]

# Log level
log_level = 2

# Display warning if buildozer is run as root
warn_on_root = 1
