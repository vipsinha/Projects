# traffic-light-classifier

Classifies a cropped image of a vertical traffic light as `red`, `yellow` or `green`, using OpenCV only (no neural network). It resizes the image to 32x32, converts it to HSV, and compares the brightness of the top, middle and bottom bands.

Code blocks marked `zsh` run in the macOS Terminal. Blocks marked `sh` run in the Lima VM or on the board, as noted.

- Recipe: `meta-frdm-apps/recipes-apps/traffic-light-classifier/traffic-light-classifier_1.0.bb`
- Installs: `/usr/bin/traffic-light-classifier`
- Runtime dependencies: `python3-core`, `python3-numpy`, `python3-opencv`
- Reference result on the test set (297 images): accuracy 0.9360, 0 red lights classified as green

## 1. Build

In the Lima VM:

```sh
cd ~/workspace/Projects/0_nxp_basic
source setup-environment frdm-imx93
bitbake traffic-light-classifier
```

## 2. Install on the board

### Option A: include it in the image

Add to `conf/local.conf`, then rebuild and flash the image:

```
IMAGE_INSTALL:append = " traffic-light-classifier"
```

```sh
bitbake imx-image-full
```

Check that it is in the image before flashing:

```sh
grep traffic-light tmp/deploy/images/imx93frdm/imx-image-full-imx93frdm.rootfs.manifest
```

### Option B: install the package without reflashing

In the Lima VM, find the package:

```sh
ls tmp/deploy/deb/all/traffic-light-classifier_*.deb
```

On the Mac, copy it to the board and install it:

```zsh
limactl shell yocto -- cp -L /home/vipulsinha.guest/workspace/Projects/0_nxp_basic/frdm-imx93/tmp/deploy/deb/all/traffic-light-classifier_1.0-r0_all.deb /tmp/lima/
scp /tmp/lima/traffic-light-classifier_1.0-r0_all.deb root@<board-ip>:/tmp/
ssh root@<board-ip> 'dpkg -i /tmp/traffic-light-classifier_1.0-r0_all.deb'
```

## 3. Test on the board

### Check the installation

```sh
which traffic-light-classifier
python3 -c "import cv2, numpy; print(cv2.__version__)"
```

### Measure accuracy

Copy a labelled test set to the board. It needs `red`, `yellow` and `green` subfolders.

```zsh
scp -r <test-folder> root@<board-ip>:/root/tl-test
```

On the board:

```sh
traffic-light-classifier eval /root/tl-test
```

### Classify single images

```sh
traffic-light-classifier image /root/tl-test/red/*.jpg
```

## 4. Live camera

### Check the camera

Connect a USB webcam, then on the board:

```sh
ls /dev/video*
traffic-light-classifier camera --device 0
```

Stop with `Ctrl+C`.

### Find the crop area

The classifier only works on a tightly cropped, upright traffic light, so pass the light's position with `--roi x,y,w,h` (in pixels). Do not type the `<` and `>` characters; use real numbers.

Save one frame on the board:

```sh
python3 -c "import cv2; c=cv2.VideoCapture(0); ok,f=c.read(); print(ok, f.shape); cv2.imwrite('/root/frame.jpg', f)"
```

Copy it to the Mac and open it:

```zsh
scp root@<board-ip>:/root/frame.jpg ~/Downloads/
open ~/Downloads/frame.jpg
```

In Preview, drag a rectangle around the traffic light, then open Tools > Show Inspector to read its position and size.

### Run with the crop area

```sh
traffic-light-classifier camera --device 0 --roi 300,100,60,140
```

It prints a colour about five times per second.

## Usage

```
traffic-light-classifier eval  <dataset_dir>
traffic-light-classifier image <file> [<file>...]
traffic-light-classifier camera [--device 0] [--roi x,y,w,h]
```