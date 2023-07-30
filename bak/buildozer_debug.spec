[app]

# (str) Title of your application
title = Chicago Card Game

# (str) Package name
package.name = kivychicago

#for AdBuddiz - https://publishers.adbuddiz.com/pub_portal/sdk/kivy#androidmanifest
#vi ~/compile/.buildozer/android/platform/python-for-android/src/templates/AndroidManifest.tmpl.xml
#   <activity android:name="com.purplebrain.adbuddiz.sdk.AdBuddizActivity"
#             android:theme="@android:style/Theme.Translucent" />

#IF USING don't forget we need to download google-play by running ~/.buildozer/android/platform/android-sdk-23/tools/android
#Mark Extra->Google Play Services for download (deselect the rest).

# (str) Package domain (needed for android/ios packaging)
package.domain = net.roadtrip2001

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,png,json,wav,pex,ttf,markup

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
#source.exclude_dirs = tests, bin

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version.regex = __version__ = ['"](.*)['"]
version.filename = %(source.dir)s/main.py

# (str) Application versioning (method 2)
#version = 0.2.2

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = pyjnius,kivy

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivy = ../../kivy

# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png
presplash.filename = %(source.dir)s/images/ChicagoLoadingIcon.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, portrait or all)
orientation = all

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1


#
# Android specific
#

# (list) Permissions
#android.permissions = INTERNET
android.permissions = INTERNET,ACCESS_WIFI_STATE,ACCESS_NETWORK_STATE,com.android.vending.BILLING,org.onepf.openiab.permission.BILLING

# (int) Android API to use
#android.api = 22

# (int) Minimum API required (8 = Android 2.2 devices)
#android.minapi = 8
#http://developer.android.com/about/dashboards/index.html
android.minapi = 16

# (int) Android SDK version to use
#android.sdk = 22

# (str) Android NDK version to use
#android.ndk = 9c

# (bool) Use --private data storage (True) or --dir public storage (False)
#android.private_storage = True
android.private_storage = False

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
#android.p4a_dir =

# (list) python-for-android whitelist
#android.p4a_whitelist =

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.renpy.android.PythonActivity

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add jars that you do not need, since extra jars can slow
# down the build process. Allows wildcards matching, for example:
# OUYA-ODK/libs/*.jar
#android.add_jars = foo.jar,bar.jar,path/to/more/*.jar
android.add_jars = %(source.dir)s/libs/*.jar

# (list) List of Java files to add to the android project (can be java or a
# directory containing the files)
#android.add_src =
android.add_src = Config.java

# (str) python-for-android branch to use, if not master, useful to try
# not yet merged features.
#android.branch = master

# (str) OUYA Console category. Should be one of GAME or APP
# If you leave this blank, OUYA support will not be enabled
#android.ouya.category = GAME

# (str) Filename of OUYA Console icon. It must be a 732x412 png image.
#android.ouya.icon.filename = %(source.dir)s/data/ouya_icon.png

# (str) XML file to include as an intent filters in <activity> tag
#android.manifest.intent_filters =

# (list) Android additionnal libraries to copy into libs/armeabi
#android.add_libs_armeabi = libs/android/*.so
#android.add_libs_armeabi_v7a = libs/android-v7/*.so
#android.add_libs_x86 = libs/android-x86/*.so
#android.add_libs_mips = libs/android-mips/*.so

# (bool) Indicate whether the screen should stay on
# Don't forget to add the WAKE_LOCK permission if you set this to True
#android.wakelock = False

# (list) Android application meta-data to set (key=value format)
#android.meta_data =
android.meta_data = billing_pubkey = _BILLINGKEY_
##ADD IF USING GOOGLE PLAY SERVICES:
#com.google.android.gms.version=@integer/google_play_services_version,
#com.google.android.gms.games.APP_ID=@string/app_id,

# (list) Android library project to add (will be added in the
# project.properties automatically.)
#android.library_references =
#ADD IF USING GOOGLE PLAY SERVICES -- android.library_references = libs/google-play-services_lib/

#
# iOS specific
#

# (str) Name of the certificate to use for signing the debug version
# Get a list of available identities: buildozer ios list_identities
#ios.codesign.debug = "iPhone Developer: <lastname> <firstname> (<hexstring>)"

# (str) Name of the certificate to use for signing the release version
#ios.codesign.release = %(ios.codesign.debug)s


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1


#    -----------------------------------------------------------------------------
#    List as sections
#
#    You can define all the "list" as [section:key].
#    Each line will be considered as a option to the list.
#    Let's take [app] / source.exclude_patterns.
#    Instead of doing:
#
#[app]
#source.exclude_patterns = license,data/audio/*.wav,data/images/original/*
#
#    This can be translated into:
#
#[app:source.exclude_patterns]
#license
#data/audio/*.wav
#data/images/original/*
#


#    -----------------------------------------------------------------------------
#    Profiles
#
#    You can extend section / key with a profile
#    For example, you want to deploy a demo version of your application without
#    HD content. You could first change the title to add "(demo)" in the name
#    and extend the excluded directories to remove the HD content.
#
#[app@demo]
#title = My Application (demo)
#
#[app:source.exclude_patterns@demo]
#images/hd/*
#
#    Then, invoke the command line with the "demo" profile:
#
#buildozer --profile demo android debug
