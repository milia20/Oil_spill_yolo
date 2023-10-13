#! python3
# -*- coding: utf-8 -*-
# pylint: disable=W0622
"""Create a html file that shows the images.
This script create a html file that shows the images in the specified
directory.
usage: create_html.py [-h] [-t TIME] [-w WIDTH] [-e [EXT [EXT ...]]]
                          [-T TEMPLATE] [-o OUTPUT]
                          [path]
"""
from __future__ import print_function
from __future__ import unicode_literals
from builtins import open
from xml.dom import minidom
import time

from pathlib import Path
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
from mako.template import Template


def get_img_list(path, ext_name):
    """Get the filenames of the images with the given path and entension name.
    Args:
        path (str): the path contains the image files.
        ext_name (list of str): the file with the extension name in the
            ext_name will be considered as a image file.
    Returns:
        list of str: a list contains the filenames of the images.
    """
    img_list = []
    for file in path.iterdir():
        if file.suffix in ext_name:
            img_list.append(file.name)
    return img_list


class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def create_html_file(img_list, time_start, oil_image, width, template_file):
    """Create a html string that shows the images.
    Args:
        img_list (list of str): the list contains the filenames of the images.
        width (int): width of the image in the html.
        template_file (str): template filename.
    Returns:
        str: a html string file shows the images.
    """
    info = setenel_data(img_list)

    time_now = time.strftime("%d %b %Y  %H:%M:%S", time.localtime())

    image_count = count_images() 
    var_dict = {
        'width': width,
        'img_list': img_list,
        'info': info,
        'time_start': time_start,
        'time_now': time_now,
        'image_oil_count': oil_image,
        'image_count': image_count

    }
    template = Template(filename=template_file)
    print(Bcolors.OKGREEN + "Анализ окончен" + Bcolors.ENDC)
    return template.render(**var_dict)


def coordinates_rework(coordinates):
    """rework coordinates
    take coordinates 20.116610,37.792671 23.079422,38.203888
    and rework to    20.116610, 37.792671  23.079422, 38.203888
    """
    new_coordinates = ""

    try:
        for coord in coordinates.split(" "):
            numbers = coord.split(",")
            new_coordinates += numbers[0] + ", " + numbers[1] + "; "

    except:
        print(numbers)
        print(new_coordinates)
        print("in coordinates we have '\t''\n'")

    return new_coordinates


def setenel_data(img_list):
    """find information about image
    Args:
        img_list (list of str): the list contains the filenames of the images.
        (0, 1, 4, 5, 6, 7) paramets of сравнение строк:
        S1A_IW_GRDH_1SDV_20170717T024712_20170717T024736_017505_01D444_2D47.SAFE
        s1a-iw-grd -vv  -20170717t024712-20170717t024736-017505-01d444-001.jpg
        предполагается что img_list отсортирован 0 1 4 5 6 7
        они теперь одинаковые вообще почти( т е раньше были маленькие а теперь полностью)
    """
    image = 0
    count = 0
    image_count = len(img_list) #number of images for correct break
    info = []
    unzip_path = Path.cwd().joinpath("unzip")

    for dirs in unzip_path.iterdir():
        #loop only for counting images т е 1 раз

        if dirs.suffix in ".SAFE":
            #print(1)
            dir_name = dirs.name.lower().split("_")
            img_name = img_list[image].lower().split("_")
            for part in (0, 1, 4, 5, 6, 7):
                #calculate True part of directory name
                count += (dir_name[part] == img_name[part])
            #print(str(count) + " " + dirs.name.lower() +" "+img_list[image])

            if count == 6:
                #find correct dir

                file = unzip_path.joinpath(dirs).joinpath("preview").joinpath("map-overlay.kml")

                #minidom.parse error:
                #AttributeError: 'WindowsPath' object has no attribute 'read'
                doc = minidom.parse(file.as_posix())

                coordinates = doc.getElementsByTagName("coordinates")[0].firstChild.data
                coordinates = coordinates_rework(coordinates)
                
                file = unzip_path.joinpath(dirs).joinpath("manifest.safe")
                doc = minidom.parse(file.as_posix())
                
                times = doc.getElementsByTagName("safe:startTime")[0].firstChild.data
                times = time.strptime(times, "%Y-%m-%dT%H:%M:%S.%f")
                times = time.strftime("%Y-%m-%d %H:%M:%S", times)
                
                info.append( (coordinates, times) )
                image += 1
            # break if we find all images - len(img_list)
            if image == image_count:
                break
            count = 0

    return info


def count_images():
    count = 0
    # TypeError: object of type 'generator' has no len()
    # len([name for name in os.listdir('.') if os.path.isfile(name)])
    for dirs in Path.cwd().joinpath("unzip").iterdir():
        count += 1
    return int(count/2) #количество файлов в папке всегда в 2 раза больше директории + файлы к ним


def main():
    """Create a html file that shows the images.
        Step1: Parse the arguments.
        Step2: Get the filenames of the images.
        Step3: Create a html string that shows the images.
        Step4: Write it to a output file.
    """
    time_default = time.strftime("%d %b %Y  %H:%M:%S", time.localtime())

    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description='Create a html file that shows the images.')
    parser.add_argument('path', default='.', nargs='?',
                        help='path that contains the images (default: %(default)s)')
    parser.add_argument('-t', '--time', type=str, default='time_now - ' + time_default,
                        help='time start of program work (default: %(default)s)')
    parser.add_argument('-I', '--image', type=str, default='len(img_list)',
                        help='image oil count (default: %(default)s)')
    parser.add_argument('-w', '--width', type=int, default='800',
                        help='width of the image in the html file (default: %(default)s)')
    parser.add_argument('-e', '--ext', nargs='*', default=['jpg', 'png'],
                        help='extension names of the images (default: %(default)s)')
    parser.add_argument('-T', '--template', default='template.html',
                        help='the template file of the html (default: %(default)s)')
    parser.add_argument('-o', '--output',
                        help='the output file name (default: <Original Path>/View.html)')

    args = parser.parse_args()
    args.ext = ['.' + ext_name for ext_name in args.ext]    #add '.' to ext

    path = Path(args.path)
    #because I cant find correct decision to pass parrametr whitout f"string"
    args.time = args.time.split("f")[1]
    args.image = args.image.split("f")[1]
    
    img_list = get_img_list(path, args.ext)
    img_html = create_html_file(img_list, args.time, args.image, args.width, args.template)

    output_path = args.output or path / 'View.html'

    with open(output_path, 'w', encoding='utf-8', newline='') as output:
        output.write(img_html)


if __name__ == '__main__':
    main()
