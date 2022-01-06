# -*- coding: utf-8 -*-
# from DBManager import DBManager
import time, requests, datetime
import os, shutil, csv
import sys
import pdb
#pdb.set_trace()
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class YahooDownloader:
    def __init__(self, start_date):
        self.out_folder = './output/'
        download_dir = os.path.abspath(self.out_folder)
        self.start_date = start_date
        for the_file in os.listdir(self.out_folder):
            file_path = os.path.join(self.out_folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)

        chrome_options = webdriver.ChromeOptions()
        preferences = {"download.default_directory": download_dir,
                       "download.directory_upgrade": True,
                       "safebrowsing.enabled": True
                       }
        chrome_options.add_experimental_option("prefs", preferences)
        self._browser = webdriver.Chrome(executable_path="./chromedriver/chromedriver.exe", chrome_options=chrome_options)

    def download(self, companyId):
        start_date = int(time.mktime(datetime.datetime.strptime(self.start_date, '%Y%m%d').timetuple()))
        current_time = int(time.time())
        url = 'https://finance.yahoo.com/quote/{}/history?period1={}&period2={}&interval=1d&filter=history&frequency=1d&guccounter=1'.format(companyId, start_date, current_time)
        print(url)

        self._browser.get(url)

        try:
            download_tag = WebDriverWait(self._browser, 180).until(
                EC.presence_of_element_located((By.XPATH, "//a[@class='Fl(end) Mt(3px) Cur(p)']")))
            time.sleep(1)
            self._browser.find_element_by_xpath("//a[@class='Fl(end) Mt(3px) Cur(p)']").click()

            filename = self.out_folder+companyId+'.csv'
            while True:
                if os.path.exists(filename):
                    time.sleep(0.5)
                    break
                time.sleep(0.5)

            csv_data = []
            with open(filename) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    row.pop('Adj Close', None)
                    csv_data.append(row)

            if os.path.isfile(filename):
                os.unlink(filename)

            with open(filename, 'w', newline='') as csvfile:
                fieldnames = csv_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in csv_data:
                    writer.writerow(row)

            pass




        except Exception as e:
            print("Error:")
            print(url)
            print(e)
            return None

        # time.sleep(5)
        # url = self._browser.find_element_by_xpath("//a[@class='Fl(end) Mt(3px) Cur(p)']").get_attribute("href")
        # print ('csv_url: {}'.format(url))
        # self._browser.get(url)
    def end(self):
        self._browser.close()

    def writeCsv(self, csv_url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }

        destfilename = './output/{}.csv'.format(self._compayId)
        if not os.path.exists(destfilename):
            # print "Downloading from {} to {}...".format(csv_url, destfilename)
            try:
                r = requests.get(csv_url, stream=True, headers=headers)
                with open(destfilename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            f.flush()
            except:
                print ("Error downloading file.")

def main(start_date):

    yahoo = YahooDownloader(start_date)
    for line in open("CSI50.txt"):
        companyId = line.strip()
        if companyId == '': continue
        yahoo.download(line.strip())

    yahoo.end()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        start_date = '19901219'
    else:
        start_date = str(sys.argv[1])
    main(start_date)
