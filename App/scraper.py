import requests
import datetime
import time
import ast
import xml.etree.ElementTree as ET

from requestium import Session

class Scraper:
    '''Return selenium based driver session'''

    def __init__(self, webdriver_path='/usr/bin/chromedriver', browser='chrome', timeout=3600, headless=True):

        # change user-agent header to simulate normal user
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'

        arguments = ['--no-sandbox', '--disable-dev-shm-usage', f'user-agent={user_agent}']
        
        if headless: arguments.append('headless')

        # Create selenium session
        s = Session(
            webdriver_path,
            browser,
            timeout,
            {'arguments': arguments}
        )

        self.browser = s.driver

        self.current_date = datetime.datetime.now().strftime('%Y/%m/%d')

    def quit(self):
        self.browser.close()
        self.browser.quit()

    def getImagesPapelDigital(self, link):

        # go to target link
        self.browser.get(link)

        published_date = '/'.join(self.browser.current_url.split('/reader/')[1][:10].split('-')[::-1])

        token = self.browser.execute_script('return window.volpe.token;')

        session_url = 'https://app.publica.la/api/v1/sessions'

        response = requests.post(
            session_url, 
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data = {
                'token' : token
            }
        )

        response_json = response.json()
        files_urls_list = response_json['files_urls']

        files_urls = [item['large'] for item in files_urls_list]

        src_images = [(0, index, src) for index, src in enumerate(files_urls, start=1)]

        return (published_date, src_images, {'referer':'https://volpe.publica.la/'})

    def getImagesElMercurio(self, link):

        self.browser.get(link)
        published_date = self.browser.current_url.split('.com/')[1][:10]

        self.browser.ensure_element_by_xpath
        div_imgs = self.browser.find_elements_by_xpath(
            '/html/body/div[1]/div/div[2]/section/div[2]/div')

        pre_src_images = []

        for elem in div_imgs:
            img = elem.find_element_by_xpath('./div/a/img')
            pre_src_images.append(img.get_attribute('data-src'))

        pre_src_images.append(pre_src_images.pop(1))

        src_images = [(0, index, src) for index, src in enumerate(pre_src_images, start=1)]


        return (published_date, src_images, {})

    def getImagesRegions(self, link):

        self.browser.get(link)
        published_date = self.browser.current_url.split('impresa/')[1].split('/papel')[0]

        image_elems = self.browser.find_elements_by_xpath(
            '/html/body/div/div[1]/div/div/*/*/*/a/img')

        src_images = []

        macro_index = -1

        for img in image_elems:

            link_img = img.get_attribute('data-src')

            if link_img == None:
                link_img = img.get_attribute('src')

            # change image resolution
            link_img = link_img.replace('380', '1440')

            # set image index
            index = int(link_img.split('pag_')[1][0:2])

            if index == 1:
                macro_index += 1

            src_images.append((macro_index, index, link_img))

        return (published_date, src_images, {})

    def getImagesPublimetro(self, link):

        self.browser.get(link)

        text_published_date = self.browser.ensure_element_by_xpath('/html/body/section[1]/div/div/div/h3/span').text

        date_split = text_published_date.split('/')

        published_date = '{0}/{1}/{2}'.format(date_split[2][0:4], date_split[1], date_split[0])

        image_elems = self.browser.find_elements_by_xpath(
            '/html/body/section[2]/div/div/div/div[2]/div[2]/*/div/div/a/img')

        src_images = []

        macro_index = -1

        for img in image_elems:

            link_img = img.get_attribute('data-src')

            if link_img == None:
                link_img = img.get_attribute('src')

            # change image resolution
            link_img = link_img.replace('thumb', 'full')

            # set image index
            index = int(link_img.split('full_')[1].split('-')[0])

            if index == 1:
                macro_index += 1

            src_images.append((macro_index, index, link_img))

        return (published_date, src_images, {})

    def getImagesDf(self, link):

        self.browser.get(link + 'data/lastedic.xml')
        # print(link + 'data/lastedic.xml')
        # print(self.browser.page_source)
        root = ET.fromstring(self.browser.page_source)

        for child in root.iter('lastedic'):
            published_date = child.attrib['dir']
            pages = int(child.attrib['pags'])

        pre_src_images = [link + 'files/' + published_date + '/pages/pag{}.jpg'.format(index + 1) for index in range(pages)]

        if 'papeldigital' in link and len(pre_src_images) % 4 != 0:
            # remove digital ad from df
            q = len(pre_src_images)

            pre_src_images.pop((q // 4) * 4 - 3)

        src_images = [(0, index, link_img) for index, link_img in enumerate(pre_src_images, start=1)]

        return (published_date, src_images, {})

    def getImagesHoyxHoy(self, link):

        self.browser.get(link)
        published_date = self.browser.current_url.split('.cl/')[1].split('/papel')[0]

        image_elems = self.browser.find_elements_by_xpath(
            '/html/body/div[3]/div/div/div/div[2]/div[2]/div/div/*/*/a/img')

        src_images = []

        macro_index = -1

        for img in image_elems:

            link_img = img.get_attribute('data-src')

            if link_img == None:
                link_img = img.get_attribute('src')

            # change image resolution
            link_img = link_img.replace('550', '1440')

            # set image index
            index = int(link_img.split('pag_')[1][0:2])

            if index == 1:
                macro_index += 1

            src_images.append((macro_index, index, link_img))

        return (published_date, src_images, {})

    def getImagesLaSegunda(self, link):

        # check if looking for "viernes"
        if 'section=V' in link:
            # check if today is friday
            if datetime.datetime.today().isoweekday() == 5:
                link = 'https://digital.lasegunda.com/' + self.current_date + '/V'
            else:
                return (self.current_date, [], {})

        self.browser.get(link)
        published_date = self.browser.current_url.split('.com/')[1][:-2]

        image_elems = self.browser.find_elements_by_xpath(
            '/html/body/div[1]/div/div[2]/section/div[2]/*/div/*/img')

        pre_src_images = []

        for img in image_elems:

            link_img = img.get_attribute('data-src')

            if link_img == None:
                link_img = img.get_attribute('src')

            if link_img.split('.cl/')[1].split('/content')[0] != published_date:
                print('...')
                continue

            pre_src_images.append(link_img)

        pre_src_images.append(pre_src_images.pop(1))

        src_images = [(0, index, src) for index, src in enumerate(pre_src_images, start=1)]

        return (published_date, src_images, {})

    def getImagesLun(self, link):

        published_date = self.current_date.replace('/', '-')
        link += 'dt=' + published_date

        self.browser.get(link)

        image_elems = self.browser.find_elements_by_xpath(
            '/html/body/form/div[2]/table/tbody/tr/td/*/table/tbody/tr[2]/td/a/img')

        src_images = []

        for index, img in enumerate(image_elems, start=1):

            link_img = img.get_attribute('src')

            # change image resolution
            link_img = link_img.replace('_30', '_768')

            # change image high-resolution (sometimes doesnt work! Image is not available)
            # link_img = link_img.replace('_30.jpg', '.webp')

            src_images.append((0, index, link_img))

        published_date = published_date.replace('-', '/')

        return (published_date, src_images, {})

