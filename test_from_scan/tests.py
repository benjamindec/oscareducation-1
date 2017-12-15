from django.test import TestCase
from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
import time
from django.conf import settings
from selenium.webdriver.support.ui import Select
import os
from promotions.utils import *
from django.contrib.auth.models import User
from users.models import Professor, Student
# Create your tests here.

from promotions.utils import insertion_sort_file



class FileOrder():
    def __init__(self, n):
        self.name = n


def check_order(filelist):
    for i in range(0, len(filelist)-1):
        if filelist[i].name > filelist[i + 1].name:
            return False
    return True

class UploadingCopiesTest(TestCase):

    def test_sorting_copies(self):
        filelist = [
            FileOrder("scan001.jpg"),
            FileOrder("scan002.jpg"),
            FileOrder("scan005.jpg"),
            FileOrder("scan011.jpg"),
            FileOrder("scan003.jpg"),
            FileOrder("scan101.jpg"),
            FileOrder("scan102.jpg"),
            FileOrder("scan301.jpg"),
            FileOrder("scan010.jpg")
        ]
        insertion_sort_file(filelist)
        self.assertTrue(check_order(filelist))




    def test_all_different(self):
        l = []
        l2 = ["a", "e", "a","46546"]
        l3 = ["45465", "4", "98", "4"]
        l4 = [25, "banana", "django"]
        l5 = [88, "88", "haml"]

        self.assertTrue(all_different(l))
        self.assertFalse(all_different(l2))
        self.assertFalse(all_different(l3))
        self.assertTrue(all_different(l4))
        self.assertTrue(all_different(l5))

    def test_pdf(self):

        #generate_pdf


        l = [(u'0', u'Question 1'), (u'1', u'Question 2'), (u'2', u'Question 3'), (u'csrfmiddlewaretoken', u'4Ycdsgjwmtmv35XWf3VNaWReQggHug7E1uvdleVEn6uf9Ir6HRbxSHKJ148OIRyv'), (u'titre', u'Titre test')]
        idtest = -1
        filename = generate_pdf(l,idtest)

        self.assertTrue(os.path.isfile(settings.STATIC_ROOT+"/tests/"+str(idtest)+"/"+filename))
        self.assertTrue(os.path.getsize(settings.STATIC_ROOT+"/tests/"+str(idtest)+"/"+filename) > 0)

        #generate_coordinates
        content = generate_coordinates(filename,idtest)
        self.assertTrue(type(content) is dict)
        self.assertTrue(len(content) == 2)
        self.assertTrue(len(content[1][0]) == 6 and len(content[1][1]) == 6)
        self.assertTrue(len(content[2][0]) == 2 and len(content[2][1]) == 2)

    def test_pt_to_px(self):
        self.assertEqual(pt_to_px(150, 500), 1041) #X
        self.assertEqual(pt_to_px(150, 500, 1), 713) #Y
        self.assertEqual(pt_to_px(200, 500), 1388) #X
        self.assertEqual(pt_to_px(200, 500, 1), 950) #Y
        self.assertEqual(pt_to_px(50, 500), 347) #X
        self.assertEqual(pt_to_px(50, 500, 1), 237)

    def test_px_to_pt(self):
        self.assertEqual(px_to_pt(150, 500), 240)  # X
        self.assertEqual(px_to_pt(150, 500, 1), 602)  # Y
        self.assertEqual(px_to_pt(200, 500), 180)  # X
        self.assertEqual(px_to_pt(200, 500, 1), 662)  # Y
        self.assertEqual(px_to_pt(50, 500), 720)  # X
        self.assertEqual(px_to_pt(50, 500, 1), 122)  # Y




class ScanTestCase(StaticLiveServerTestCase):
    fixtures = ['initial_data.json']
    def setUp(self):



        driver = webdriver.Chrome('/bin/chromedriver')  # Optional argument, if not specified will search path.
        driver.get('http://www.google.com/xhtml');



        self.selenium = driver

        selenium = self.selenium

        selenium.get('%s%s' % (self.live_server_url,'/accounts/usernamelogin/'))


        username = selenium.find_element_by_id('id_username')
        username.send_keys('professor')
        time.sleep(2)


        selenium.find_element_by_css_selector(".btn-primary").click()
        passwd = selenium.find_element_by_id('id_password')
        time.sleep(2)
        passwd.send_keys('oscar')

        selenium.find_element_by_css_selector(".btn-primary").click()


        super(ScanTestCase, self).setUp()



    def tearDown(self):

        self.selenium.quit()
        super(ScanTestCase, self).tearDown()

    def test_scan(self):
        selenium = self.selenium
        #Opening the link we want to test

        #Connect

        #Create a test
        selenium.get('%s%s' % (self.live_server_url,'/professor/lesson/1/test/from-scan/add/'))
        time.sleep(2)

        selenium.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        selenium.find_element_by_id('addSkillToTestButtonForStage1').click()
        time.sleep(1)
        selenium.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        for i in range(0,3):

            selenium.find_element_by_name('addQuestion').click()
            time.sleep(1)

        selenium.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        selenium.find_element_by_name('addQuestion').click()

        selenium.find_element_by_name('titre').send_keys('Titre test')
        time.sleep(2)
        for i in range(0,5):
            selenium.find_element_by_name(str(i)).send_keys('Question'+str(i+1))
            time.sleep(1)



        selenium.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        selenium.find_element_by_id('addScan').click()
        time.sleep(2)

        selenium.find_element_by_link_text("Titre test").click()
        time.sleep(1)
        upload = selenium.find_element_by_id("upload_file")
        time.sleep(1)
        upload.send_keys(settings.STATIC_ROOT +"/tests/selenium/scan1.png"+"\n"+settings.STATIC_ROOT +"/tests/selenium/scan2.png"+"\n"+settings.STATIC_ROOT +"/tests/selenium/scan3.png")
        time.sleep(1)
        selenium.find_element_by_id('import').click()
        time.sleep(2)
        #Test Sort by question
        listbox = Select(selenium.find_element_by_id("select_q"));
        listbox.select_by_visible_text('Question 2')
        time.sleep(1)
        selenium.find_element_by_id("sort_q").click()
        time.sleep(2)

        #Go to the associate students page
        selenium.find_element_by_id("match").click()
        time.sleep(2)
        #Click to match names
        selenium.find_element_by_id("match").click()
        time.sleep(2)
        #Go back to the detail
        selenium.find_element_by_id("previous").click()

        #Correct a question
        selenium.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        selenium.find_element_by_id('img').click()
        selenium.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        selenium.find_element_by_class_name('fa-check').click()
        time.sleep(1)
        selenium.find_element_by_name('annotation').send_keys('Pretty Nice answer kiddo')
        time.sleep(1)
        #Validate correction
        selenium.find_element_by_id("correct").click()
        time.sleep(1)
        #return to the detail of the test
        selenium.find_element_by_id("previous").click()
        time.sleep(2)
        #return to test summary
        selenium.find_element_by_id("previous").click()

        selenium.find_element_by_css_selector("img[src='/static/img/icons/delete.png']").click()
        time.sleep(2)
        #Delete the test
        selenium.find_element_by_class_name('btn-danger').click()















