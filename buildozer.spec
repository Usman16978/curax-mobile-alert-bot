[app]
title = CuraX Alert Bot
package.name = curaxalertbot
package.domain = com.curax
source.dir = .
source.include_exts = py
version = 1.0

requirements = python3,kivy==2.2.1

orientation = portrait

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.build_tools_version = 33.0.2

[buildozer]
log_level = 2
warn_on_root = 1
