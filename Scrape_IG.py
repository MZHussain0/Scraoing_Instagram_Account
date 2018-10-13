from selenium import webdriver
from time import sleep
import os
from bs4 import BeautifulSoup
import requests
import shutil
from xlsxwriter import Workbook


class App:
    def __init__(self, username='*******', password='*********', target_username='(Desired users profile)',
                 path='F:/Webscraping/humaq'):

        # print(os.path.exists(path))

        self.username = username
        self.password = password
        self.target_username = target_username
        self.path = path
        self.driver = webdriver.Chrome()
        self.error = False
        self.main_url = 'https://www.instagram.com'
        self.login_url = 'https://www.instagram.com/accounts/login/?source=auth_switcher'
        self.driver.get(self.login_url)

        sleep(1)

        self.log_in()  # Log into the account
        if self.error is False:
            self.close_diag_box()  # closing the dialogue box
            self.close_notif_box()  # Closing notificaton box
            self.open_target_profile()  # Opening the desired persons profile

        if self.error is False:
            self.scroll_down()

        if self.error is False:
            if not os.path.exists(path):
                os.mkdir(path)
            self.downloading_images()

        # input("stop")
        sleep(5)
        self.driver.close()

    def write_captions_to_excel_file(self, images, caption_path):
        print('writing to excel')
        workbook = Workbook(os.path.join(caption_path, 'captions.xlsx'))
        worksheet = workbook.add_worksheet()
        row = 0
        worksheet.write(row, 0, 'Image name')
        worksheet.write(row, 1, 'Caption')
        row += 1
        for index, image in enumerate(images):
            filename = 'image_' + str(index) + '.jpg'
            try:
                caption = image['alt']
            except KeyError:
                caption = 'No caption exists'
            worksheet.write(row, 0, filename)
            worksheet.write(row, 1, caption)
            row += 1
        workbook.close()

    def download_captions(self, images):
        captions_folder_path = os.path.join(self.path, 'captions')
        if not os.path.exists(captions_folder_path):
            os.mkdir(captions_folder_path)
        self.write_captions_to_excel_file(images, captions_folder_path)

    def downloading_images(self):
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        all_images = soup.find_all('img')
        self.download_captions(all_images)
        print('Length of all images', len(all_images))
        for index, image in enumerate(all_images):
            filename = "image_" + str(index) + '.jpg'
            image_path = os.path.join(self.path, filename)
            link = image['src']

            print('Downloading image --->', index)
            response = requests.get(link, stream=True)

            try:
                with open(image_path, 'wb') as file:
                    # print(image['src'])
                    shutil.copyfileobj(response.raw, file)
            except Exception as e:
                print(e)
                print(" image could nt be downloaded", index)
                print(" image link -----> ", link)

    def scroll_down(self):
        try:
            no_of_post = self.driver.find_element_by_xpath(
                '//span[@class="g47SY "]')
            no_of_post = str(no_of_post.text).replace(',', "")
            self.no_of_post = int(no_of_post)

            if (self.no_of_post > 12):
                no_of_scrolls = int(self.no_of_post / 12) + 1

                for value in range(no_of_scrolls):
                    print(value)
                    self.driver.execute_script(
                        'window.scrollTo(0, document.body.scrollHeight);')
                    sleep(5)
        except Exception:
            self.error = True
            print("Some error occurred during the scroll_down")

    def open_target_profile(self):
        try:
            searchBar = self.driver.find_element_by_xpath(
                '//input[@placeholder="Search"]')
            searchBar.send_keys(self.target_username)
            target_profile_url = self.main_url + '/' + self.target_username + '/'
            self.driver.get(target_profile_url)
        except Exception:
            self.error = True
            print('Could not find search bar')

    def close_notif_box(self):
        try:
            sleep(1)
            self.driver.get(self.main_url)
            cls_btn = self.driver.find_element_by_xpath(
                '//button[@class="aOOlW   HoLwm "]')
            cls_btn.click()
            sleep(1)
        except Exception:
            pass

    def close_diag_box(self):
        try:
            sleep(1)
            cls_link = self.driver.find_element_by_xpath(
                '//span[@id="react-root"]//a[@class="_3m3RQ _7XMpj"]')
            cls_link.click()
            sleep(1)
        except Exception:
            pass

    def log_in(self):
        try:
            username_input = self.driver.find_element_by_xpath(
                '//input[@name="username"]')
            username_input.send_keys(self.username)

            password_input = self.driver.find_element_by_xpath(
                '//input[@name="password"]')
            password_input.send_keys(self.password)
            password_input.submit()
        except Exception:
            self.error = True
            print('There is something wrong with login function')


if __name__ == '__main__':
    app = App()
