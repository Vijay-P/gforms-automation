#!/usr/bin/env python3

import time
from enum import Enum

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

OP_WAIT = 0.5


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

    def __init__(self, driver, index, parent, qtype):
        self.type = qtype
        self.driver = driver
        self.index = index
        self.parent = parent
        return

    def click_question(self, prev):
        time.sleep(OP_WAIT)
        self.driver.find_elements(
            By.XPATH, "//div[@class='freebirdFormeditorViewItemContentWrapper']")[prev + self.index].click()
        return

    def change_question(self, text):
        p_count = self.parent.count_previous()
        self.click_question(p_count)
        time.sleep(OP_WAIT)
        title = self.driver.find_elements(
            By.XPATH, "//textarea[@aria-label='Question title']")[p_count + self.index]
        title.clear()
        title.send_keys(text)
        return

    def change_question_type(self, qtype):
        p_count = self.parent.count_previous()
        print("QUINDEX, PREV, CHANGE TYPE", self.index, p_count)
        self.click_question(p_count)
        time.sleep(OP_WAIT)
        self.driver.find_elements(
            By.XPATH, "//div[@aria-label='Question types']")[p_count + self.index].click()
        time.sleep(OP_WAIT)
        self.driver.find_elements(By.XPATH, qtype.value)[p_count + self.index + 1].click()
        self.type = qtype
        return

    def set_multiple_choices(self, options):
        accept1 = self.type == QuestionType.MULTIPLE_CHOICE
        accept2 = self.type == QuestionType.CHECKBOXES
        accept3 = self.type == QuestionType.DROPDOWN
        assert accept1 or accept2 or accept3
        assert isinstance(options, list)
        self.click_question(self.parent.count_previous())
        time.sleep(OP_WAIT)
        for ndex, opt in enumerate(options):
            if ndex > 0:
                self.driver.find_element(By.XPATH, "//input[@aria-label='Add option']").click()
            option = self.driver.find_elements(
                By.XPATH, "//input[@aria-label='option value']")[ndex]
            option.click()
            option.clear()
            option.send_keys(opt)
            time.sleep(OP_WAIT)
        return

    def set_grid_choices(self, rows, columns):
        pass

    def set_linear_scale(self, bottom, top, bottom_label="", top_label=""):
        assert bottom == 0 or bottom == 1
        assert top > 1 and top < 11
        assert isinstance(bottom_label, str)
        assert isinstance(top_label, str)
        time.sleep(OP_WAIT)
        self.driver.find_element(
            By.XPATH, "//div[@aria-label='Lower scale limit' and @data-value='1']").click()
        time.sleep(OP_WAIT)
        self.driver.find_elements(
            By.XPATH, "//div[@aria-label='Lower scale limit' and @data-value='" + str(bottom) + "']")[1].click()
        self.driver.find_element(
            By.XPATH, "//div[@aria-label='Upper scale limit' and @data-value='5']").click()
        time.sleep(OP_WAIT)
        self.driver.find_elements(
            By.XPATH, "//div[@aria-label='Upper scale limit' and @data-value='" + str(top) + "']")[1].click()
        time.sleep(OP_WAIT)
        self.driver.find_elements(
            By.XPATH, "//input[@aria-label='Label (optional)']")[0].send_keys(bottom_label)
        time.sleep(OP_WAIT)
        self.driver.find_elements(
            By.XPATH, "//input[@aria-label='Label (optional)']")[1].send_keys(top_label)
        return


class Section:

    questions = {}

    def __init__(self, driver, index, parent):
        self.driver = driver
        self.index = index
        self.parent = parent

    def add_question(self):
        time.sleep(OP_WAIT)
        self.driver.find_elements(
            By.XPATH, "//div[@class='freebirdFormeditorViewPagePageCard']")[self.index].click()
        time.sleep(OP_WAIT)
        self.driver.find_element(By.XPATH, "//div[@data-tooltip='Add question']").click()
        self.parent.questions_per[self.index] += 1
        if len(self.questions.keys()) == 0:
            self.questions[0] = Question(self.driver, 0, self,
                                         QuestionType.MULTIPLE_CHOICE)
        else:
            self.questions[max(self.questions.keys()) + 1] = Question(self.driver,
                                                                      max(self.questions.keys()) + 1, self, QuestionType.MULTIPLE_CHOICE)
        print("ADDING QUESTION", max(self.questions.keys()))
        return

    def count_previous(self):
        pre = 0
        for q_index in self.parent.questions_per.keys():
            if q_index < self.index:
                pre += self.parent.questions_per[q_index]
            else:
                break
        print("QINDEX, PREV, COUNT", self.index, pre)
        return pre

    def delete_question(self, index):
        p_count = self.count_previous()
        self.questions[index].click_question(p_count)
        time.sleep(OP_WAIT)
        self.driver.find_element(By.XPATH, "//div[@data-tooltip='Delete']").click()
        self.parent.questions_per[self.index] -= 1
        questionrange = max(self.questions.keys())
        for question in range(index, questionrange):
            self.questions[question] = self.questions[question + 1]
        self.questions.pop(questionrange)
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
        time.sleep(OP_WAIT)
        self.waitfor(By.NAME, "password", self.TIMEOUT)
        elem = self.driver.find_element_by_name("password")
        elem.clear()
        elem.send_keys(password)
        self.driver.find_element_by_id("passwordNext").click()
        self.waitfor(By.CLASS_NAME, "docs-homescreen-templates-templateview-showcase", self.TIMEOUT)
        return

    def edit_title(self, title):
        time.sleep(OP_WAIT)
        form_title = self.driver.find_elements(By.XPATH, "//textarea[@aria-label='Form title']")[0]
        form_title.clear()
        form_title.send_keys(title)
        return

    def edit_description(self, description):
        time.sleep(OP_WAIT)
        form_desc = self.driver.find_elements(
            By.XPATH, "//textarea[@aria-label='Form description']")[0]
        form_desc.send_keys(description)
        return

    def load_blank_template(self, title, description):
        templates = self.driver.find_elements_by_class_name(
            "docs-homescreen-templates-templateview-showcase")
        templates[0].click()
        self.waitfor(By.CLASS_NAME, "docssharedWizOmnilistMorselValue", self.TIMEOUT)
        self.driver.find_elements_by_class_name(
            "freebirdFormeditorViewItemcardRoot")[0].click()
        self.driver.find_elements(By.XPATH, "//div[@data-tooltip='Delete']")[0].click()
        self.edit_title(title)
        self.edit_description(description)
        self.sections[0] = Section(self.driver, 0, self)
        self.questions_per[0] = 0
        return

    def add_section(self):
        time.sleep(OP_WAIT)
        if self.questions_per[max(self.sections.keys())] > 0:
            s_prev = self.sections[max(self.sections.keys())].count_previous()
            self.sections[max(self.sections.keys())].questions[self.questions_per[
                max(self.sections.keys())] - 1].click_question(s_prev)
        else:
            self.driver.find_elements(
                By.XPATH, "//div[@class='freebirdFormeditorViewPagePageCard']")[max(self.sections.keys())].click()
        time.sleep(OP_WAIT)
        self.driver.find_element(By.XPATH, "//div[@data-tooltip='Add section']").click()
        self.sections[max(self.sections.keys()) + 1] = Section(self.driver,
                                                               max(self.sections.keys()) + 1, self)
        self.questions_per[max(self.sections.keys())] = 0
        return

    def delete_section(self, index):
        time.sleep(OP_WAIT)
        self.driver.find_elements(
            By.XPATH, "//div[@aria-label='Overflow Menu']")[index].click()
        time.sleep(OP_WAIT)
        self.driver.find_element(By.XPATH, "//div[@data-action-id='freebird-delete-page']").click()
        sectionrange = max(self.sections.keys())
        for section in range(index + 1, sectionrange):
            self.sections[section] = self.sections[section + 1]
        self.sections.pop(sectionrange)
        return

    def quit():
        self.driver.quit()
        return

if __name__ == '__main__':
    TESTFORM = GForm("***REMOVED***", "***REMOVED***")
    TESTFORM.load_blank_template("NICE MEME", "this is a test")
    TESTFORM.sections[0].add_question()  # add question to Sec1
    TESTFORM.sections[0].questions[0].set_multiple_choices(["optiona", "optionb", "optionc"])
    TESTFORM.sections[0].add_question()  # add question to Sec1
    TESTFORM.sections[0].questions[1].change_question_type(QuestionType.LINEAR_SCALE)
    TESTFORM.sections[0].questions[1].set_linear_scale(1, 10, "not at all", "yes, totally")
    TESTFORM.sections[0].add_question()
    TESTFORM.sections[0].questions[1].change_question_type(QuestionType.MULTIPLE_CHOICE_GRID)
    TESTFORM.sections[0].questions[1].set_grid_choices(
        ["1", "2", "3", "4", "5"], ["1", "2", "3", "4", "5"])
    time.sleep(10)
    TESTFORM.quit()
