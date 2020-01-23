try:
    import Image
    import ImageFilter
except ImportError:
    from PIL import Image, ImageFilter
import argparse
import random as rand
from colorsys import rgb_to_hsv
import imageio, glob
from scipy.io import wavfile
from matplotlib import pyplot as plt
import numpy as np



array = []


black_pixel = (0, 0, 0, 255)
white_pixel = (255, 255, 255, 255)


text = input("iahgiheg: ")

text = text.split("|")


p = argparse.ArgumentParser(description="pixel mangle an image")
p.add_argument("image", help="input image file")
p.add_argument("-i", "--int_function", help="random, threshold, edges, waves, file, file-edges, none", default="threshold")
p.add_argument("-f", "--int_file", help="Image used for defining intervals", default="in.png")
p.add_argument("-t", "--threshold", type=float, help="Pixels darker than this are not sorted, between 0 and 1", default=0.25)
p.add_argument("-u", "--upper_threshold", type=float, help="Pixels darker than this are not sorted, between 0 and 1", default=0.8)
p.add_argument("-c", "--clength", type=int, help="Characteristic length of random intervals", default=50)
p.add_argument("-a", "--angle", type=float, help="Rotate the image by an angle (in degrees) before sorting", default=0)
p.add_argument("-r", "--randomness", type=float, help="What percentage of intervals are NOT sorted", default=0)
p.add_argument("-s", "--sorting_function", help="lightness, intensity, hue, saturation, minimum", default="lightness")
p.add_argument("-anim", "--animation", type=int, help="duration of animation, in frames. Crossfading is not possible yet", default="5")




def initialisePXS(textz):
    argsz = p.parse_args(textz)
    return argsz

__args = initialisePXS(text)






class PixelSort:
    def __init__(self, arguments):
        self.image_input_path = arguments.image
        self.output_image_path = "images/output"
        self.interval_function = self.read_interval_function(arguments.int_function)
        self.interval_file_path = arguments.int_file
        self.bottom_threshold = arguments.threshold
        self.upper_threshold = arguments.upper_threshold
        self.clength = arguments.clength
        self.angle = arguments.angle
        self.randomness = arguments.randomness
        self.sorting_function = self.read_sorting_function(arguments.sorting_function)
        self.anim_length = arguments.animation

    def edge(self, pixels):
        img = Image.open(self.image_input_path)
        img = img.rotate(self.angle, expand=True)
        edges = img.filter(ImageFilter.FIND_EDGES)
        edges = edges.convert('RGBA')
        edge_data = edges.load()

        filter_pixels = []
        edge_pixels = []
        intervals = []

        print("Defining edges...")
        for y in range(img.size[1]):
            filter_pixels.append([])
            for x in range(img.size[0]):
                filter_pixels[y].append(edge_data[x, y])

        print("Thresholding...")
        for y in range(len(pixels)):
            edge_pixels.append([])
            for x in range(len(pixels[0])):
                if self.lightness(filter_pixels[y][x]) < self.bottom_threshold:
                    edge_pixels[y].append(white_pixel)
                else:
                    edge_pixels[y].append(black_pixel)

        print("Cleaning up edges...")
        for y in range(len(pixels) - 1, 1, -1):
            for x in range(len(pixels[0]) - 1, 1, -1):
                if edge_pixels[y][x] == black_pixel and edge_pixels[y][x - 1] == black_pixel:
                    edge_pixels[y][x] = white_pixel

        print("Defining intervals...")
        for y in range(len(pixels)):
            intervals.append([])
            for x in range(len(pixels[0])):
                if edge_pixels[y][x] == black_pixel:
                    intervals[y].append(x)
            intervals[y].append(len(pixels[0]))
        return intervals


    def threshold(self, pixels):
        intervals = []

        print("Defining intervals...")
        for y in range(len(pixels)):
            intervals.append([])
            for x in range(len(pixels[0])):
                if self.lightness(pixels[y][x]) < self.bottom_threshold or self.lightness(pixels[y][x]) > self.upper_threshold:
                    intervals[y].append(x)
            intervals[y].append(len(pixels[0]))
        return intervals

    def random_width(self, clength):
        x = rand.random()
        width = int(clength * (1 - x))
        return width

    def randomz(self, pixels):
        intervals = []

        print("Defining intervals...")
        for y in range(len(pixels)):
            intervals.append([])
            x = 0
            while True:
                width = self.random_width(self.clength)
                x += width
                if x > len(pixels[0]):
                    intervals[y].append(len(pixels[0]))
                    break
                else:
                    intervals[y].append(x)
        return intervals


    def crop_to(self, image_to_crop, reference_image):
        """
        Crops image to the size of a reference image. This function assumes that the relevant image is located in the center
        and you want to crop away equal sizes on both the left and right as well on both the top and bottom.
        :param image_to_crop
        :param reference_image
        :return: image cropped to the size of the reference image
        """
        reference_size = reference_image.size
        current_size = image_to_crop.size
        dx = current_size[0] - reference_size[0]
        dy = current_size[1] - reference_size[1]
        left = dx / 2
        upper = dy / 2
        right = dx / 2 + reference_size[0]
        lower = dy / 2 + reference_size[1]
        return image_to_crop.crop(box=(int(left), int(upper), int(right), int(lower)))

    def waves(self, pixels):
        intervals = []

        print("Defining intervals...")
        for y in range(len(pixels)):
            intervals.append([])
            x = 0
            while True:
                width = self.clength + rand.randint(0, 10)
                x += width
                if x > len(pixels[0]):
                    intervals[y].append(len(pixels[0]))
                    break
                else:
                    intervals[y].append(x)
        return intervals


    def file_mask(self, pixels):
        intervals = []
        file_pixels = []

        img = Image.open(self.interval_file_path)
        img = img.convert('RGBA')
        img = img.rotate(self.angle, expand=True)
        data = img.load()
        for y in range(img.size[1]):
            file_pixels.append([])
            for x in range(img.size[0]):
                file_pixels[y].append(data[x, y])

        print("Cleaning up edges...")
        for y in range(len(pixels) - 1, 1, -1):
            for x in range(len(pixels[0]) - 1, 1, -1):
                if file_pixels[y][x] == black_pixel and file_pixels[y][x - 1] == black_pixel:
                    file_pixels[y][x] = white_pixel

        print("Defining intervals...")
        for y in range(len(pixels)):
            intervals.append([])
            for x in range(len(pixels[0])):
                if file_pixels[y][x] == black_pixel:
                    intervals[y].append(x)
            intervals[y].append(len(pixels[0]))

        return intervals


    def file_edges(self, pixels):
        img = Image.open(self.interval_file_path)
        img = img.rotate(self.angle, expand=True)
        img = img.resize((len(pixels[0]), len(pixels)), Image.ANTIALIAS)
        edges = img.filter(ImageFilter.FIND_EDGES)
        edges = edges.convert('RGBA')
        edge_data = edges.load()

        filter_pixels = []
        edge_pixels = []
        intervals = []

        print("Defining edges...")
        for y in range(img.size[1]):
            filter_pixels.append([])
            for x in range(img.size[0]):
                filter_pixels[y].append(edge_data[x, y])

        print("Thresholding...")
        for y in range(len(pixels)):
            edge_pixels.append([])
            for x in range(len(pixels[0])):
                if self.lightness(filter_pixels[y][x]) < self.bottom_threshold:
                    edge_pixels[y].append(white_pixel)
                else:
                    edge_pixels[y].append(black_pixel)

        print("Cleaning up edges...")
        for y in range(len(pixels) - 1, 1, -1):
            for x in range(len(pixels[0]) - 1, 1, -1):
                if edge_pixels[y][x] == black_pixel and edge_pixels[y][x - 1] == black_pixel:
                    edge_pixels[y][x] = white_pixel

        print("Defining intervals...")
        for y in range(len(pixels)):
            intervals.append([])
            for x in range(len(pixels[0])):
                if edge_pixels[y][x] == black_pixel:
                    intervals[y].append(x)
            intervals[y].append(len(pixels[0]))
        return intervals


    def none(self, pixels):
        intervals = []
        for y in range(len(pixels)):
            intervals.append([len(pixels[y])])
        return intervals


        #hewughuwshgihesiuhsieuhgisuhegiuhsieguhiusge

    def read_interval_function(self, func):
        try:
            return {
                "random": self.randomz,
                "threshold": self.threshold,
                "edges": self.edge,
                "waves": self.waves,
                "file": self.file_mask,
                "file-edges": self.file_edges,
                "none": self.none}[func]
        except KeyError:
            print("[WARNING] Invalid interval function specified, defaulting to 'threshold'.")
            return self.threshold

    def lightness(self, pixel):
        return rgb_to_hsv(pixel[0], pixel[1], pixel[2])[2] / 255.0  # For backwards compatibility with python2


    def intensity(self, pixel):
        return pixel[0] + pixel[1] + pixel[2]


    def hue(self, pixel):
        return rgb_to_hsv(pixel[0], pixel[1], pixel[2])[0] / 255.0

    def saturation(self, pixel):
        return rgb_to_hsv(pixel[0], pixel[1], pixel[2])[1] / 255.0


    def minimum(self, pixel):
        return min(pixel[0], pixel[1], pixel[2])

    def read_sorting_function(self, func):
        try:
            return {
                "lightness": self.lightness,
                "hue": self.hue,
                "intensity": self.intensity,
                "minimum": self.minimum,
                "saturation": self.saturation
                }[func]
        except KeyError:
            print("[WARNING] Invalid sorting function specified, defaulting to 'lightness'.")
            return self.lightness

    def sort_image(self, pixels, intervals):
        sorted_pixels = []
        for y in range(len(pixels)):
            row = []
            x_min = 0
            for x_max in intervals[y]:
                interval = []
                for x in range(x_min, x_max):
                    interval.append(pixels[y][x])
                if rand.randint(0, 100) >= self.randomness:
                    row += self.sort_interval(interval, self.sorting_function)
                else:
                    row += interval
                x_min = x_max
            row.append(pixels[y][0])
            sorted_pixels.append(row)
        return sorted_pixels


    def sort_interval(self, interval, sorting_function):
        return [] if interval == [] else sorted(interval, key=sorting_function)


    def begin_sort(self, filename, inputfile):

        print("Opening image...")
        input_img = Image.open(inputfile)

        print("Converting to RGBA...")
        input_img.convert('RGBA')

        print("Rotating image...")
        if self.angle != 0:
            input_img = input_img.rotate(self.angle, expand=True)

        print("Getting data...")
        data = input_img.load()

        print("Getting pixels...")
        pixels = []
        for y in range(input_img.size[1]):
            pixels.append([])
            for x in range(input_img.size[0]):
                pixels[y].append(data[x, y])

        print("Determining intervals...")
        intervals = self.interval_function(pixels)

        print("Sorting pixels...")
        sorted_pixels = self.sort_image(pixels, intervals)

        print("Placing pixels in output image...")
        output_img = Image.new('RGBA', input_img.size)
        for y in range(output_img.size[1]):
            for x in range(output_img.size[0]):
                output_img.putpixel((x, y), sorted_pixels[y][x])

        if self.angle is not 0:
            print("Rotating output image back to original orientation...")
            output_img = output_img.rotate(-self.angle, expand=True)

            print("Crop image to apropriate size...")
            output_img = self.crop_to(output_img, Image.open(inputfile))




        print("Saving image...")
        output_img.save(filename)

        print("Done!", filename)


    #begin_sort(output_image_path + ".png", image_input_path)




    def turn_to_gif(self, duration, length):
        i = 0
        
        while i < length:
            self.bottom_threshold = array[i]
            print(array[i])
            self.begin_sort(self.output_image_path + str(i) + ".png", self.image_input_path)
            i += 1

        kargs = { 'fps' : duration}
        images = []
        filenames = glob.glob("E:\Scripts\pixel sort\images\*.png")
        print(filenames)

        for filename in filenames:
            images.append(imageio.imread(filename))
        imageio.mimwrite('E:\Scripts\pixel sort\gifs\pixelsort.gif', images, **kargs)

    def recursive_gif(self, duration, length):
        i = 1
        self.begin_sort(self.output_image_path + "0.png", self.image_input_path)
        while i < length:
            self.begin_sort(self.output_image_path + str(i) + ".png", self.output_image_path + str(i-1) + ".png")
            #modify animations here
            self.bottom_threshold = array[i]
            print(self.bottom_threshold)
            print(array[i])

            i += 1

        kargs = { 'fps' : duration}
        images = []
        filenames = glob.glob("E:\Scripts\pixel sort\images\*.png")
        print(filenames)

        for filename in filenames:
            images.append(imageio.imread(filename))
        imageio.mimwrite('E:\Scripts\pixel sort\gifs\pixelsort.gif', images, **kargs)


pxs = PixelSort(__args)

pxs.turn_to_gif(22, __args.animation)    #makes gif by default. change to pxs.turn_to_gif(1, __args.animation)  for singular image


