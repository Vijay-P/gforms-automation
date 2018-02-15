#!/usr/bin/env python3

import time
from enum import Enum

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class QuestionType(Enum):
    SHORT_ANSWER = "//div[content='Short answer']"
    PARAGRAPH = "//div[content='Paragraph']"
    MULTIPLE_CHOICE = "//div[content='Multiple choice']"
    CHECKBOXES = "//div[content='Checkboxes']"
    DROPDOWN = "//div[content='Drowdown']"
    LINEAR_SCALE = "//div[content='Linear scale']"
    MULTIPLE_CHOICE_GRID = "//div[content='Multiple choice grid']"
    CHECKBOX_GRID = "//div[content='Checkboxe grid']"
    DATE = "//div[content='Date']"
    TIME = "//div[content='Time']"


class Question:

    def __init__(self, qtype):
        self.type = qtype
        pass


class Section:

    questions = {}

    def __init__(self, driver, index, parent):
        self.driver = driver
        self.index = index
        self.parent = parent

    def waitfor(self, selector, string, secs):
        try:
            WebDriverWait(self.driver, secs).until(
                EC.visibility_of_element_located((selector, string))
            )
        except TimeoutException as ex:
            print("Exception has been thrown. " + str(ex))
            self.driver.quit()
        return

    def add_question(self):
        # self.waitfor(
        # By.XPATH, "(//div[@class='freebirdFormeditorViewPagePageCard'])[" +
        # str(self.index) + "]", 2)
        time.sleep(.5)
        print(self.index)
        self.driver.find_elements(
            By.XPATH, "//div[@class='freebirdFormeditorViewPagePageCard']")[self.index].click()
        time.sleep(0.5)
        self.driver.find_element(By.XPATH, "//div[@data-tooltip='Add question']").click()
        self.parent.questions_per[self.index] += 1
        if(len(self.questions.keys()) == 0):
            self.questions[0] = Question(QuestionType.MULTIPLE_CHOICE)
        else:
            self.questions[max(self.questions.keys()) + 1] = Question(QuestionType.MULTIPLE_CHOICE)
        print(self.questions)
        return

    def count_previous(self):
        pre = 0
        for x in self.parent.questions_per.keys():
            if x < self.index:
                pre += self.parent.questions_per[x]
            else:
                break
        return pre

    def click_question(self, index, prev):
        time.sleep(0.5)
        self.driver.find_elements(
            By.XPATH, "//div[@class='freebirdFormeditorViewItemContentWrapper']")[prev + index].click()
        return

    def change_question(self, index, text):
        p_count = self.count_previous()
        self.click_question(index, p_count)
        time.sleep(0.5)
        title = self.driver.find_elements(
            By.XPATH, "//textarea[@aria-label='Question title']")[p_count + index]
        title.clear()
        title.send_keys(text)
        print(self.questions)
        return

    def change_question_type(self, index, qtype):
        p_count = self.count_previous()
        self.click_question(index, p_count)
        time.sleep(0.5)
        print(p_count, index)
        self.driver.find_elements(
            By.XPATH, "//div[@aria-label='Question types']")[p_count + index].click()
        time.sleep(0.5)
        self.driver.find_elements(By.XPATH, qtype.value)[p_count + index + 1].click()
        self.questions[index].type = qtype
        return

    def delete_question(self, index):
        p_count = self.count_previous()
        self.click_question(index, p_count)
        time.sleep(0.5)
        self.driver.find_element(By.XPATH, "//div[@data-tooltip='Delete']").click()
        self.parent.questions_per[self.index] -= 1
        questionrange = max(self.questions.keys())
        for x in range(index, questionrange):
            self.questions[x] = self.questions[x + 1]
        self.questions.pop(questionrange)
        print(self.questions)
        return


class GForm:

    TIMEOUT = 10
    sections = {}
    questions_per = {}

    def __init__(self, username, password):
        self.driver = webdriver.Chrome()
        self.driver.get("https://docs.google.com/forms")
        assert "Google Forms" in self.driver.title
        self.login(username, password)

    def close_window(self):
        self.driver.quit()
        return

    def waitfor(self, selector, string, secs):
        try:
            WebDriverWait(self.driver, secs).until(
                EC.presence_of_element_located((selector, string))
            )
        except TimeoutException as ex:
            print("Exception has been thrown. " + str(ex))
            self.driver.quit()
        return

    def login(self, username, password):
        elem = self.driver.find_element_by_name("identifier")
        elem.clear()
        elem.send_keys(username)
        self.driver.find_element_by_id("identifierNext").click()
        time.sleep(1)
        self.waitfor(By.NAME, "password", self.TIMEOUT)
        elem = self.driver.find_element_by_name("password")
        elem.clear()
        elem.send_keys(password)
        self.driver.find_element_by_id("passwordNext").click()
        self.waitfor(By.CLASS_NAME, "docs-homescreen-templates-templateview-showcase", self.TIMEOUT)
        return

    def edit_title(self, title):
        time.sleep(.5)
        form_title = self.driver.find_elements(By.XPATH, "//textarea[@aria-label='Form title']")[0]
        form_title.clear()
        form_title.send_keys(title)
        return

    def edit_description(self, description):
        time.sleep(.5)
        form_desc = self.driver.find_elements(
            By.XPATH, "//textarea[@aria-label='Form description']")[0]
        form_desc.send_keys(description)
        return

    def delete_question(self, index):
        self.driver.find_elements_by_class_name(
            "freebirdFormeditorViewItemcardRoot")[index].click()
        self.driver.find_elements(By.XPATH, "//div[@data-tooltip='Delete']")[index].click()

    def load_blank_template(self, title, description):
        templates = self.driver.find_elements_by_class_name(
            "docs-homescreen-templates-templateview-showcase")
        templates[0].click()
        self.waitfor(By.CLASS_NAME, "docssharedWizOmnilistMorselValue", self.TIMEOUT)
        self.delete_question(0)
        self.edit_title(title)
        self.edit_description(description)
        self.sections[0] = Section(self.driver, 0, self)
        self.questions_per[0] = 0
        return

    def add_section(self):
        time.sleep(0.5)
        self.driver.find_element(By.XPATH, "//div[@data-tooltip='Add section']").click()
        self.sections[max(self.sections.keys()) + 1] = Section(self.driver,
                                                               max(self.sections.keys()) + 1, self)
        self.questions_per[max(self.sections.keys())] = 0
        return

    def delete_section(self, index):
        time.sleep(0.5)
        self.driver.find_elements(
            By.XPATH, "//div[@aria-label='Overflow Menu']")[index].click()
        time.sleep(.5)
        self.driver.find_element(By.XPATH, "//div[@data-action-id='freebird-delete-page']").click()
        sectionrange = max(self.sections.keys())
        for x in range(index + 1, sectionrange):
            self.sections[x] = self.sections[x + 1]
        self.sections.pop(sectionrange)
        return

if __name__ == '__main__':
    TESTFORM = GForm("***REMOVED***", "***REMOVED***")
    TESTFORM.load_blank_template("NICE MEME", "this is a test")
    TESTFORM.add_section()
    TESTFORM.delete_section(1)
    TESTFORM.add_section()
    TESTFORM.add_section()
    TESTFORM.delete_section(1)
    TESTFORM.sections[0].add_question()
    TESTFORM.sections[0].delete_question(0)
    TESTFORM.sections[0].add_question()
    TESTFORM.sections[1].add_question()
    TESTFORM.sections[1].change_question(0, "yeah")
    TESTFORM.sections[1].change_question_type(0, QuestionType.CHECKBOXES)
    TESTFORM.sections[0].add_question()
    TESTFORM.sections[0].change_question_type(0, QuestionType.TIME)
