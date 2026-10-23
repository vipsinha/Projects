# FRDM-IMX93: build, flash and serial console

Code blocks marked `zsh` run in the macOS Terminal. Blocks marked `sh` run in the Lima VM or on the board, as noted.

## 1. Run the build in tmux

Run these commands in the Lima VM. `tmux` keeps the build running if the terminal closes.

### Start a session and build

```sh
tmux new -s build
cd ~/workspace/Projects/0_nxp_basic
source setup-environment frdm-imx93
bitbake imx-image-full
```

### Detach (build keeps running)

Press `Ctrl+B`, release, then press `D`.

### Reattach later

From the Mac, open the VM:

```zsh
limactl shell yocto
```

Then, in the VM:

```sh
tmux attach -t build
```

### Other commands

```sh
tmux ls                      # list sessions
tmux kill-session -t build   # close a session
```

To scroll back through the output: press `Ctrl+B`, then `[`, and use the arrow keys. Press `q` to stop scrolling.

## 2. Transfer files

### Lima VM to Mac

```zsh
limactl copy yocto:/home/vipulsinha.guest/<path-in-vm> /Users/vipulsinha/<mac-folder>/
```

Or with `scp`:

```zsh
scp lima-yocto:/home/vipulsinha.guest/<path-in-vm> /Users/vipulsinha/<mac-folder>/
```

For a symlink (like the short image name), copy the real file through the shared folder `/tmp/lima`:

```zsh
limactl shell yocto -- cp -L /home/vipulsinha.guest/<path-in-vm> /tmp/lima/
mv /tmp/lima/<file> /Users/vipulsinha/<mac-folder>/
```

### Mac to Lima VM

```zsh
limactl copy /Users/vipulsinha/<file> yocto:/home/vipulsinha.guest/<folder-in-vm>/
```

Add `-r` after `copy` to copy a whole folder.

### Mac to board

Find the board's IP on the serial console with `ip addr`, then:

```zsh
scp <file> root@<board-ip>:/root/
```

Use `scp -r` for a folder.

### Board to Mac

```zsh
scp root@<board-ip>:/root/<file> /Users/vipulsinha/<mac-folder>/
```

## 3. Flash the board

### Download the flashing tool

Download `uuu_mac_arm` from https://github.com/nxp-imx/mfgtools/releases, then:

```zsh
chmod +x uuu_mac_arm
```

### Choose a target

- `sd_all`: flash the microSD card. The factory image on the eMMC stays as a fallback.
- `emmc_all`: flash the onboard eMMC.

### Copy the image to the local folder

Copy the **timestamped** file. The short name without the timestamp is only a link.

```zsh
scp lima-yocto:/home/vipulsinha.guest/workspace/Projects/0_nxp_basic/frdm-imx93/tmp/deploy/images/imx93frdm/imx-image-full-imx93frdm.rootfs-20261020150602.wic.zst /Users/vipulsinha/Vipul/Study/Nxp/
```

### Connect the board

1. Unplug power (P1).
2. Change the boot switch to `0001` from `0010`.
3. Connect P2 to the Mac.
4. Plug power (P1) back in.

### Check the board is available

```zsh
./uuu_mac_arm -lsusb
```

The board must be listed as `MX93`.

### Start the flashing

```zsh
sudo ./uuu_mac_arm -b emmc_all imx-image-full-imx93frdm.rootfs-20261020150602.wic.zst
```

Wait for `Success 1 Failure 0`.

### Boot the new image

1. Unplug power (P1).
2. Change the boot switch back to `0010`.
3. Plug power back in.

## 4. Board serial console

### Find the board's USB serial port

```zsh
ls /dev/cu.*
```

Find the board's device in the output. Use that device path in the command below.

### Connect to the board

```zsh
screen /dev/cu.usbmodem58BE0314991 115200
```

If the device path shown on your Mac is different, replace `/dev/cu.usbmodem58BE0314991` with that path.

### Disconnect

At the board's prompt, type:

```sh
exit
```

Then quit `screen`: press `Ctrl+A`, release, press `K`, then press `Y` to confirm.

## 5. Connect the board to Wi-Fi

Run these commands on the board (serial console).

### Load the Wi-Fi driver

```sh
modprobe moal mod_para=nxp/wifi_mod_para.conf
ip link set mlan0 up
```

### Connect to the network

```sh
wpa_passphrase "<wifi-name>" "<wifi-password>" > /etc/wpa.conf
wpa_supplicant -B -i mlan0 -c /etc/wpa.conf
```

The message `rfkill: Cannot open RFKILL control device` is harmless.

### Check the connection and get an IP

```sh
iw dev mlan0 link          # should show "Connected to" and the Wi-Fi name
udhcpc -i mlan0
ip -4 addr show mlan0
```

The `inet 192.168.x.x` address is the board's IP. Use it for `ssh root@<board-ip>` and the `scp` commands in section 3.

The connection does not survive a reboot. Repeat the `modprobe`, `ip link` and `wpa_supplicant` commands, then `udhcpc`, after each boot.

## 6. Confirm it's your build

Compare the kernel checksum on the board and in the build output.

On the board:

```sh
sha256sum /boot/Image*
```

In the Lima VM:

```sh
sha256sum ~/workspace/Projects/0_nxp_basic/frdm-imx93/tmp/deploy/images/imx93frdm/Image
```

If the checksums match, the board is running your build.