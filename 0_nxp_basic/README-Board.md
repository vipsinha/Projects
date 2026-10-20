# Board serial console

Run these commands in the macOS Terminal.

## Find the board's USB serial port

```sh
ls /dev/cu.*
```

Find the board's device in the output. Use that device path in the command below.

## Connect to the board

```sh
screen /dev/cu.usbmodem58BE0314991 115200
```

If the device path shown on your Mac is different, replace `/dev/cu.usbmodem58BE0314991` with that path before running the command.

## Disconnect

At the board's login prompt, type:

```sh
exit
```

Then quit `screen`: press `Ctrl+A`, release, press `K`, then press `Y` to confirm.

## Flash the board

### Flash setup 
- Download the downloader 
https://github.com/nxp-imx/mfgtools/releases

### Options
If you have a microSD card in the board, I’d start with sd_all, so the factory image on the eMMC stays as a fallback. If not, use emmc_all. Run everything in the Mac terminal, in the folder with uuu_mac_arm.

### Copy image to local folder
scp lima-yocto:/home/vipulsinha.guest/workspace/Projects/0_nxp_basic/frdm-imx93/tmp/deploy/images/imx93frdm/imx-image-full-imx93frdm.rootfs-20261020150602.wic.zst /Users/vipulsinha/Vipul/Study/Nxp/

### Usb port
change the switch to 0001 from 0010

### To check board is avaialble for flash
./uuu_mac_arm -lsusb

### to start the flashing
./uuu_mac_arm -b emmc_all imx-image-full-imx93frdm.rootfs.wic.zst


### How to confirm it’s really your build

- Compare a file on the board with the same file in your build output, for example the kernel.

- On the board:

```
bash
sha256sum /boot/Image*
```

- In the VM:

```
bash
sha256sum ~/workspace/Projects/0_nxp_basic/frdm-imx93/tmp/deploy/images/imx93frdm/Image
```

- If the checksums match, the board is running your build.




