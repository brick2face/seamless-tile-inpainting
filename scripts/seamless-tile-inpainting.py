import modules.scripts as scripts
import gradio as gr
import os

from modules import images
from modules.processing import process_images, Processed
from modules.processing import Processed
from modules.shared import opts, cmd_opts, state

from PIL import Image, ImageDraw


class Script(scripts.Script):

# The title of the script. This is what will be displayed in the dropdown menu.
    def title(self):

        return "Seamless Tile Inpainting"


# Determines when the script should be shown in the dropdown menu via the
# returned value. As an example:
# is_img2img is True if the current tab is img2img, and False if it is txt2img.
# Thus, return is_img2img to only show the script on the img2img tab.

    def show(self, is_img2img):

        return is_img2img

# How the script's is displayed in the UI. See https://gradio.app/docs/#components
# for the different UI components you can use and how to create them.
# Most UI components can return a value, such as a boolean for a checkbox.
# The returned values are passed to the run method as parameters.

    def ui(self, is_img2img):
        tile_direction = gr.Dropdown(choices=["horizontal only", "vertical only", "both directions"], value="horizontal only", label="Tiling direction")
        masked_px = gr.Slider(minimum=2.0, maximum=500.0, step=2, value=100,
        label="Masked area width (px)")
        split_again = gr.Checkbox(value=True, label="Split sides again after inpainting?", info="If checked, the modified area will appear around the edges of the image. If unchecked, the modified area will appear in the center of the image.")
        return [tile_direction, masked_px, split_again]



# This is where the additional processing is implemented. The parameters include
# self, the model object "p" (a StableDiffusionProcessing class, see
# processing.py), and the parameters returned by the ui method.
# Custom functions can be defined here, and additional libraries can be imported
# to be used in processing. The return value should be a Processed object, which is
# what is returned by the process_images method.

    def run(self, p, tile_direction, masked_px, split_again):

        my_width, my_height = p.init_images[0].size

        def generate_mask(line_width, direction):
            # Create a new black image
            image = Image.new("RGB", (my_width, my_height), color="black")
            draw = ImageDraw.Draw(image)

            if direction == "horizontal only":
                # Calculate the position and dimensions of the line
                x_start = (my_width - line_width) // 2
                x_end = x_start + line_width - 1
                y_start = 0
                y_end = my_height
                

            elif direction == "vertical only":
                y_start = (my_height - line_width) // 2
                y_end = y_start + line_width - 1
                x_start = 0
                x_end = my_width

            elif direction == "both directions":
                # Calculate the position and dimensions of the line
                x_start = (my_width - line_width) // 2
                x_end = x_start + line_width - 1
                y_start = 0
                y_end = my_height

                # Draw the FIRST white line
                draw.rectangle([(x_start, y_start), (x_end, y_end)], fill="white")

                # Calculate the position and dimensions of the SECOND line
                y_start = (my_height - line_width) // 2
                y_end = y_start + line_width - 1
                x_start = 0
                x_end = my_width

            else:
                raise Exception("Direction variable must be either horizontal, vertical, or both")

            # Draw the white line
            draw.rectangle([(x_start, y_start), (x_end, y_end)], fill="white")

            # Return the image
            return image

        def split_image(image, direction):

            # Get the width and height of the image
            width, height = image.size

            if direction == "horizontal only":
                # Calculate the midpoint
                midpoint = width // 2

                # Split the image into two halves
                left_half = image.crop((0, 0, midpoint, height))
                right_half = image.crop((midpoint, 0, width, height))

                # Return the two halves as separate images
                return left_half, right_half

            elif direction == "vertical only":
                # Calculate the midpoint
                midpoint = height // 2

                # Split the image into two halves
                top_half = image.crop((0, 0, width, midpoint))
                bottom_half = image.crop((0, midpoint, width, height))

                # Return the two halves as separate images
                return top_half, bottom_half
            else:
                raise Exception("Direction variable must be either horizontal, vertical, or both")

        def merge_images(first_half, last_half, direction, flip_sides=False):

            # Get the width and height of the first half (assuming both halves have the same dimensions)
            width, height = first_half.size

            # Create a new image
            merged_image = None

            if direction == "horizontal only":
                # Create a new image with double the width
                merged_image = Image.new("RGB", (width * 2, height))
                height = 0
            elif direction == "vertical only":
                # Create a new image with double the height
                merged_image = Image.new("RGB", (width, height * 2))
                width = 0
            else:
                raise Exception("Direction variable must be either horizontal, vertical, or both")

            # Determine the order in which to paste the halves
            if flip_sides:
                merged_image.paste(last_half, (0, 0))
                merged_image.paste(first_half, (width, height))
            else:
                merged_image.paste(first_half, (0, 0))
                merged_image.paste(last_half, (width, height))

            # Return the merged image
            return merged_image

        if tile_direction == "both directions":

            first_half, last_half = split_image(p.init_images[0], "horizontal only")

            part_A, part_B = split_image(first_half, "vertical only")
            part_C, part_D = split_image(last_half, "vertical only")

            top_half = merge_images(part_B, part_D, "horizontal only", flip_sides=True)
            bottom_half = merge_images(part_A, part_C, "horizontal only", flip_sides=True)

            p.init_images[0] = merge_images(top_half, bottom_half, "vertical only", flip_sides=False)
            p.image_mask = generate_mask(masked_px, tile_direction)
            proc = process_images(p)

            if split_again:
                #If split_again, split the output images and switch their sides.
                for i in range(len(proc.images)):

                    proc_first, proc_last = split_image(proc.images[i], "horizontal only")
                    proc_merged = merge_images(proc_first, proc_last, "horizontal only", flip_sides=True)

                    proc_first, proc_last = split_image(proc_merged, "vertical only")
                    proc_merged = merge_images(proc_first, proc_last, "vertical only", flip_sides=True)

                    proc.images[i] = proc_merged



        else:
            first_side, last_side = split_image(p.init_images[0], tile_direction)

            p.init_images[0] = merge_images(first_side, last_side, tile_direction, flip_sides=True)

            p.image_mask = generate_mask(masked_px, tile_direction)

            proc = process_images(p)

            # Modify processed images after this

            if split_again:
            #If split_again, split the output images and switch their sides.
                for i in range(len(proc.images)):

                    proc_first, proc_last = split_image(proc.images[i], tile_direction)
                    proc.images[i] = merge_images(proc_first, proc_last, tile_direction, flip_sides=True)



        return proc
