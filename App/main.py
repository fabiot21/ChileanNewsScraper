import os
import datetime
import requests
import sys
from sys import argv
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# external modules
from requestium import Session
from pdf2image import convert_from_path
from PIL import Image

# internal modules
from scraper import Scraper

MAIN_FOLDER = 'Results'
NEWSPAPERS_FOLDER = 'srclinks'
CHECK_FILES_EXIST = True

def getTargets(file_path):
    '''Return dictionary with name and link of targets'''

    d = {}

    # read txt file and save info in dictionry
    with open(file_path, 'r') as f:
        for line in f:
            (name, link) = line.strip('\n').split(';')
            d[name] = link
    return d

def createRequestSession():
    '''create request session for requests'''

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session

def createDirectory(main_folder, dt, name):

    # create main folder directory
    dir = os.path.join(os.getcwd(), main_folder)
    if not os.path.exists(dir):
        os.mkdir(dir)

    # create folder of latest datetime in format %Y%m%d
    dir_dt = dir + '/' + dt.replace('/', '')
    if not os.path.exists(dir_dt):
        os.mkdir(dir_dt)

    # create folder with name/code
    dir_name_dt = dir_dt + '/' + name
    if not os.path.exists(dir_name_dt):
        os.mkdir(dir_name_dt)

    return dir_name_dt

def generateImages(main_folder, name, dt, imgs, file_format, headers):
    '''Generate images of newspaper inside folder by date'''

    print('Generating images for date:', dt)

    # create request session for requests
    session = createRequestSession()

    # create directory for generated images
    dir_name_dt = createDirectory(main_folder, dt, name)

    if CHECK_FILES_EXIST:
        # check if file exists
        final_path = '{0}/{1}/{2}'.format(MAIN_FOLDER, dt.replace('/', ''), name)
        if os.path.exists(final_path):
            
            n_files = len([name for name in os.listdir(final_path)])

            if n_files == len(imgs):
                print('files already exist')
                return

    # request from source and save images
    for macro_i, i, img_link in imgs:
        # save image in format macroindex_XXX.jpg
        file_name = '{0}_{1:03}.{2}'.format(macro_i, i, 'jpg')

        # final_path = '../{0}/{1}/{2}/{3}'.format(MAIN_FOLDER, dt.replace('/', ''), name, file_name)
        # if os.path.exists(final_path):
        #     print('File {0} already exists'.format(file_name))
        #     continue



        # saving image from source
        img = session.get(img_link, headers=headers)
        print('Saving', file_name)
        path_file = dir_name_dt + '/' + file_name
        with open(path_file, 'wb') as f:
            f.write(img.content)
            # check if file is .webp to convert it to a readable format
            if img_link.find('.webp') != -1:
                Image.open(path_file).convert('RGB').save(path_file, 'JPEG')
            if img_link.find('.png') != -1:
                Image.open(path_file).convert('RGB').save(path_file, 'JPEG')
            if img_link.find('.pdf') != -1:
                convert_from_path(path_file, 500)[0].save(path_file, 'JPEG')

def ScrapingProcess(title, filename, scraperGetImageFunc, file_format):
    '''
    Void function that handle the whole scraping process

    title: The name of the main folder
    filename: Name of txt file that contains name/code of newspaper and target link separated by ';'
    scraperGetImageFunc: function of Scraper class that return the imgs links with its published dates
    file_format: The format of image files
    '''

    input_path = NEWSPAPERS_FOLDER + '/' + filename

    # read info file
    newspapers = getTargets(input_path)

    # init process for each target/newspaper
    for name in newspapers.keys():
        print('Scraping {0}'.format(title), name)

        published_dt, imgs, headers = scraperGetImageFunc(newspapers[name])
        generateImages(MAIN_FOLDER, name, published_dt, imgs, file_format, headers)


    
def main():

    scraper = Scraper()

    if len(argv) == 1 or argv[1] == 'regiones':

        ScrapingProcess('Regiones', 'regiones.txt', scraper.getImagesRegions, 'jpg')


    if len(argv) == 1 or argv[1] == 'elmercurio':

        ScrapingProcess('El Mercurio', 'elmercurio.txt', scraper.getImagesElMercurio, 'png')


    if len(argv) == 1 or argv[1] == 'publimetro':

        ScrapingProcess('Publimetro', 'publimetro.txt', scraper.getImagesPublimetro, 'jpg')


    if len(argv) == 1 or argv[1] == 'hoyxhoy':

        ScrapingProcess('HoyxHoy', 'hoyxhoy.txt', scraper.getImagesHoyxHoy, 'jpg')


    if len(argv) == 1 or argv[1] == 'diariofinanciero':

        ScrapingProcess('Diario Financiero', 'diariofinanciero.txt', scraper.getImagesDf, 'jpg')


    if len(argv) == 1 or argv[1] == 'lun':

        ScrapingProcess('LUN', 'lun.txt', scraper.getImagesLun, 'png')


    if len(argv) == 1 or argv[1] == 'lasegunda':

        ScrapingProcess('La Segunda', 'lasegunda.txt', scraper.getImagesLaSegunda, 'png')


    if len(argv) == 1 or argv[1] == 'latercera':

        ScrapingProcess('La Tercera', 'latercera.txt', scraper.getImagesPapelDigital, 'jpg')


    if len(argv) == 1 or argv[1] == 'lacuarta':

        ScrapingProcess('La Cuarta', 'lacuarta.txt', scraper.getImagesPapelDigital, 'jpg')


    print('Done!')

    scraper.quit()


if __name__ == "__main__":
    main()


