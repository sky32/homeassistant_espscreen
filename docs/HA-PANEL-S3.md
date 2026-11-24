# HA Panel (experimental)

A local HA Panel profile for an ESP32-S3 N16R8, a 480 × 320 ST7796 SPI display and FT6336 capacitive touch. This is an experimental profile, not an upstream-supported or hardware-accepted board yet.

## Hardware profile

- ESP32-S3, 16 MB flash, 8 MB octal PSRAM.
- Display: ST7796 over SPI; native panel dimensions 320 × 480, laid out at 480 × 320 with a 90° LVGL rotation.
- Touch: FT6336/FT63x6 at I²C address 0x38, I²C on GPIO6 (SDA) and GPIO7 (SCL), interrupt on GPIO5.
- Display SPI: GPIO13 clock, GPIO12 MOSI, GPIO8 CS, GPIO9 D/C, GPIO10 reset; write-only, no MISO.
- Backlight: PWM on GPIO14 at 44.1 kHz.
- The selected initial profile uses ST7796 BGR ordering, inverted colors and an 80 MHz SPI write clock, matching the known working project configuration.

The 3.5-inch diagonal used for the initial layout density is an estimate; verify the active glass diagonal if precise tile sizing matters. The profile has no camera package.

## Local build and acceptance

Build from the repository checkout with `esphome compile checkout/ha-panel-s3.yaml`, using the Wi-Fi secrets described in [Profiles](PROFILES.md). The installer gets this board's package, components and fonts from the same fork branch configured in `screen_manager/app/ha_panel_source.py`. Push those files to that branch before using the installer. Other boards still use the upstream repository.

For Simplified Chinese, add `LANGUAGE: "zh-Hans"` to the profile's `substitutions` before compiling. The 16 MB
configuration includes a compact glyph subset, not the full Chinese font. The default ESPHome partition table gives
each OTA application slot 7.75 MiB.

The profile is experimental. Verify display colors, orientation, touch corners and drags, and stability on the actual board before promoting it.
