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
source.include_exts = py,png,jpg,kv,atlas,db

# Version
version = 1.0

# Application requirements
requirements = python3,kivy==2.1.0,requests,pyjnius,android

# Presplash background color
presplash.color = #0099ff

# Icon
#icon.filename = icon.png

# Supported orientations
orientation = portrait

# Android permissions
android.permissions = INTERNET,VIBRATE,WAKE_LOCK

# Android API level
android.api = 31

# Minimum API level
android.minapi = 21

# Android SDK version
android.ndk = 25b

# Android architecture
android.archs = armeabi-v7a

# Android services
#android.services = AlertReceiver:./service.py

# Allow background execution
android.wakelock = True

# Notification support
android.gradle_dependencies = androidx.core:core:1.6.0

[buildozer]

# Log level
log_level = 2

# Display warning if buildozer is run as root
warn_on_root = 1

# Build directory
build_dir = ./.buildozer

# Binary directory  
bin_dir = ./bin
