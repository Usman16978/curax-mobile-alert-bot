[app]
title = CuraX Alert Bot
package.name = curaxalertbot
package.domain = com.curax
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

requirements = python3,kivy==2.2.1,pyjnius==1.4.2,requests,certifi,urllib3,charset-normalizer,idna

orientation = portrait
presplash.color = #0099ff

android.permissions = INTERNET,VIBRATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
