name: APK Yigish
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: APK yaratish
        uses: ArtemSBulgakov/buildozer-action@v1
        with:
          command: buildozer android debug
          buildozer_version: master
      - name: APK yuklash
        uses: actions/upload-artifact@v4
        with:
          name: ODTI-Energiya-APK
          path: bin/*.apk
