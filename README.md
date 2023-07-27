# seamless-tile-inpainting
An [automatic1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui) extension for making tiles seamless using inpainting. It was designed to use [Stable Diffusion's official inpainting model](https://huggingface.co/stabilityai/stable-diffusion-2-inpainting/blob/main/512-inpainting-ema.ckpt) at 512x512 resolution, but it should work fine with other inpainting models.

## Example
![Example image](example-image.png)

## How to install

**Option #1:** Clone this repo into the automatic1111 "extensions" folder.

**Option #2 *(COMING SOON)*:** Run automatic1111, install "Seamless Tile Inpainting" from the Extensions tab, then reset UI.

## How to use
1. Run [automatic1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui) and make sure your selected model is [512-inpainting-ema.ckpt](https://huggingface.co/stabilityai/stable-diffusion-2-inpainting/blob/main/512-inpainting-ema.ckpt) (or choose another inpainting model)
2. Go to "img2img", upload the image you want to make seamless, and then select "Seamless Tile Inpainting" from the scripts dropdown menu
3. Adjust the script settings described below, and then generate images. (Also, I recommend setting denoising strength to 1.)

### Settings

**Tiling Direction:** Select "horizontal only" if your tiles will only be seamless along the x-axis, like floor or ceiling tiles. Select "vertical only" if your tiles will only be seamless along the y-axis, like wall or ladder tiles. You can also choose "both directions" to make tiles that are seamless in both directions (although "*seam* ***less***" might be a more appropriate phrase for this option, because there are still very minor seams when choosing "both directions").

**Masked area width (px):** Determines how large the area modified by inpainting should be. On the edges of the final image, the size of the modified area will appear to be half of this value (that's because this number represents the total size of the mask when both edges are placed next to each other).

**Split sides again after inpainting?:** If checked, the center area of the final image will appear the same as before. If unchecked, the center area will be where the modified seam appears. Both options will result in a seamless tile image you can use, but uncheck this if you want to easily confirm the modification looks right.

## How is this different from the "Asymmetric Tiling" extension?
This is an original script of mine, not a fork. But there are two main differences between what this script does and what [asymmetric-tiling-sd-webui](https://github.com/tjm35/asymmetric-tiling-sd-webui) (created by [tjim35](https://github.com/tjm35)) does:

1. This script preserves the majority of the original image, and only modifies the edges that will connect to other tiles. Asymmetric Tiling doesn't preserve an original image, it's used either for text-to-image generations OR it modifies every part of the image in image-to-image generations.
2. This script uses inpainting by splitting the original image in two halves, switching the sides, and then inpainting along the seams in between (and optionally switching the halves back again afterwards). I honestly don't know how Asymmetric Tiling works, but it doesn't work this way because it doesn't generate the same results.

## Credits

Created by brick2face
