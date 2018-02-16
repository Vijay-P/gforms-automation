#!/usr/bin/env python3

'''
Object oriented mapping for Google Forms operations.
'''

import time
from enum import Enum
import getpass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

DRIVER = webdriver.Chrome()
OP_WAIT = 0.5


class QuestionType(Enum):
    '''Enum for QuestionTypes. This class is used both to ID question types and to contain their XPATH identifiers.'''

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
    '''Container class for operations on GForms questions. Instances should always be children of Section'''

    def __init__(self, index, parent, qtype):
        '''Question Constructor

        Keyword arguments:
        index -- index of question in section [0-n)
        parent -- parent Section member
        qtype -- QuestionType member
        '''
        self.type = qtype
        self.index = index
        self.parent = parent
        return

    def click_question(self, prev):
        '''Click on this question

        Keyword arguments:
        prev -- number of previous questions, output of Section.count_previous()
        '''
        time.sleep(OP_WAIT)
        DRIVER.find_elements(
            By.XPATH, "//div[@class='freebirdFormeditorViewItemContentWrapper']")[prev + self.index].click()
        return

    def change_question(self, text):
        '''Change the text for this question

        Keyword arguments:
        text -- the question type(string)
        '''
        p_count = self.parent.count_previous()
        self.click_question(p_count)
        time.sleep(OP_WAIT)
        title = DRIVER.find_elements(
            By.XPATH, "//textarea[@aria-label='Question title']")[p_count + self.index]
        title.clear()
        title.send_keys(text)
        return

    def change_question_type(self, qtype):
        '''Change the type of this question

        Keyword arguments:
        qtype -- QuestionType member to change to
        '''
        p_count = self.parent.count_previous()
        self.click_question(p_count)
        time.sleep(OP_WAIT)
        DRIVER.find_elements(
            By.XPATH, "//div[@aria-label='Question types']")[p_count + self.index].click()
        time.sleep(OP_WAIT)
        DRIVER.find_elements(By.XPATH, qtype.value)[p_count + self.index + 1].click()
        self.type = qtype
        return

    def set_multiple_choices(self, options):
        '''Modify choices for multiple choice question types
        Supported QuestionTypes: MULTIPLE_CHOICE, CHECKBOXES, DROPDOWN

        Keyword arguments:
        options -- list of choices
        '''
        accept1 = self.type == QuestionType.MULTIPLE_CHOICE
        accept2 = self.type == QuestionType.CHECKBOXES
        accept3 = self.type == QuestionType.DROPDOWN
        assert accept1 or accept2 or accept3
        assert isinstance(options, list)
        time.sleep(OP_WAIT)
        self.click_question(self.parent.count_previous())
        time.sleep(OP_WAIT)
        for ndex, opt in enumerate(options):
            if ndex > 0:
                DRIVER.find_element(By.XPATH, "//input[@aria-label='Add option']").click()
            option = DRIVER.find_elements(
                By.XPATH, "//input[@aria-label='option value']")[ndex]
            option.click()
            option.clear()
            option.send_keys(str(opt))
            time.sleep(OP_WAIT)
        return

    def set_grid_choices(self, rows, columns):
        '''Modify choices for grid question types
        Supported QuestionTypes: MULTIPLE_CHOICE_GRID, CHECKBOXE_GRID

        Keyword arguments:
        rows: list of row options
        columns: list of column options
        '''
        accept1 = self.type == QuestionType.MULTIPLE_CHOICE_GRID
        accept2 = self.type == QuestionType.CHECKBOX_GRID
        assert accept1 or accept2
        assert isinstance(rows, list)
        assert isinstance(columns, list)
        time.sleep(OP_WAIT)
        self.click_question(self.parent.count_previous())
        for ndex, row in enumerate(rows):
            time.sleep(OP_WAIT)
            if ndex != 0:
                DRIVER.find_element(By.XPATH, "//input[@aria-label='Add row']").click()
            time.sleep(OP_WAIT)
            row_item = DRIVER.find_element(
                By.XPATH, "//input[@data-initial-value='Row " + str(ndex + 1) + "']")
            row_item.click()
            time.sleep(OP_WAIT)
            row_item.clear()
            time.sleep(OP_WAIT)
            row_item.send_keys(str(row))
        for ndex, col in enumerate(columns):
            time.sleep(OP_WAIT)
            if ndex != 0:
                DRIVER.find_element(By.XPATH, "//input[@aria-label='Add column']").click()
            time.sleep(OP_WAIT)
            col_item = DRIVER.find_element(
                By.XPATH, "//input[@data-initial-value='Column " + str(ndex + 1) + "']")
            col_item.click()
            time.sleep(OP_WAIT)
            col_item.clear()
            time.sleep(OP_WAIT)
            col_item.send_keys(str(col))
        return

    def set_linear_scale(self, bottom, top, bottom_label="", top_label=""):
        '''Modify choices for linear scale question type
        Supported QuestionTypes: LINEAR_SCALE

        Keyword arguments:
        bottom -- bottom of scale [0-1]
        top -- top of scale [2-10]
        bottom_label -- string to label bottom of scale
        top_label -- string to label top of scale
        '''
        assert self.type == QuestionType.LINEAR_SCALE
        assert isinstance(bottom, int)
        assert isinstance(top, int)
        assert bottom == 0 or bottom == 1
        assert top > 1 and top < 11
        assert isinstance(bottom_label, str)
        assert isinstance(top_label, str)
        time.sleep(OP_WAIT)
        DRIVER.find_element(
            By.XPATH, "//div[@aria-label='Lower scale limit' and @data-value='1']").click()
        time.sleep(OP_WAIT)
        DRIVER.find_elements(
            By.XPATH, "//div[@aria-label='Lower scale limit' and @data-value='" + str(bottom) + "']")[1].click()
        DRIVER.find_element(
            By.XPATH, "//div[@aria-label='Upper scale limit' and @data-value='5']").click()
        time.sleep(OP_WAIT)
        DRIVER.find_elements(
            By.XPATH, "//div[@aria-label='Upper scale limit' and @data-value='" + str(top) + "']")[1].click()
        time.sleep(OP_WAIT)
        DRIVER.find_elements(
            By.XPATH, "//input[@aria-label='Label (optional)']")[0].send_keys(bottom_label)
        time.sleep(OP_WAIT)
        DRIVER.find_elements(
            By.XPATH, "//input[@aria-label='Label (optional)']")[1].send_keys(top_label)
        return


class Section:
    '''Container class for operations on GForms sections. Instances should always be children of GForm'''

    questions = {}

    def __init__(self, index, parent):
        '''Section Constructor

        Keyword arguments:
        index -- index of section in form [0-n)
        parent -- parent GForm member
        '''
        self.index = index
        self.parent = parent

    def add_question(self):
        '''Add a question to the section'''
        time.sleep(OP_WAIT)
        DRIVER.find_elements(
            By.XPATH, "//div[@class='freebirdFormeditorViewPagePageCard']")[self.index].click()
        time.sleep(OP_WAIT)
        DRIVER.find_element(By.XPATH, "//div[@data-tooltip='Add question']").click()
        self.parent.questions_per[self.index] += 1
        if len(self.questions.keys()) == 0:
            self.questions[0] = Question(0, self, QuestionType.MULTIPLE_CHOICE)
        else:
            self.questions[max(self.questions.keys(
            )) + 1] = Question(max(self.questions.keys()) + 1, self, QuestionType.MULTIPLE_CHOICE)
        return

    def count_previous(self):
        '''Count the question in sections prior'''
        pre = 0
        for q_index in self.parent.questions_per.keys():
            if q_index < self.index:
                pre += self.parent.questions_per[q_index]
            else:
                break
        return pre

    def delete_question(self, index):
        '''Delete a question from this section

        Keyword arguments:
        index -- index of question to delete in section [0, n)
        '''
        p_count = self.count_previous()
        self.questions[index].click_question(p_count)
        time.sleep(OP_WAIT)
        DRIVER.find_element(By.XPATH, "//div[@data-tooltip='Delete']").click()
        self.parent.questions_per[self.index] -= 1
        questionrange = max(self.questions.keys())
        for question in range(index, questionrange):
            self.questions[question] = self.questions[question + 1]
        self.questions.pop(questionrange)
        return


class GForm:
    '''Google Form object. This class is the only class in the module that the user should instantiate'''

    TIMEOUT = 10
    sections = {}
    questions_per = {}

    def __init__(self):
        '''GForm Constructor'''
        DRIVER.get("https://docs.google.com/forms")
        assert "Google Forms" in DRIVER.title
        self.__login()

    def __waitfor(self, selector, string, secs):
        '''Wait for selenium to detect the presence of an element

        Keyword arguments:
        selector -- member of selenium.webdriver.common.by
        string -- string match against selector
        secs -- maximum wait time in seconds
        '''
        try:
            WebDriverWait(DRIVER, secs).until(
                EC.presence_of_element_located((selector, string))
            )
        except TimeoutException as ex:
            print("Exception has been thrown. " + str(ex))
            DRIVER.quit()
        return

    def __login(self):
        '''Login to Google Forms'''
        elem = DRIVER.find_element_by_name("identifier")
        elem.clear()
        elem.send_keys(input("Username: "))
        DRIVER.find_element_by_id("identifierNext").click()
        time.sleep(OP_WAIT)
        self.__waitfor(By.NAME, "password", self.TIMEOUT)
        elem = DRIVER.find_element_by_name("password")
        elem.clear()
        elem.send_keys(getpass.getpass())
        DRIVER.find_element_by_id("passwordNext").click()
        self.__waitfor(By.CLASS_NAME, "docs-homescreen-templates-templateview-showcase", self.TIMEOUT)
        return

    def edit_title(self, title):
        '''Edit the title of the form

        Keyword arguments:
        title -- new title of the form
        '''
        time.sleep(OP_WAIT)
        form_title = DRIVER.find_elements(By.XPATH, "//textarea[@aria-label='Form title']")[0]
        form_title.clear()
        form_title.send_keys(title)
        return

    def edit_description(self, description):
        '''Edit the description of the form

        Keyword arguments:
        description -- new description of the form
        '''
        time.sleep(OP_WAIT)
        form_desc = DRIVER.find_elements(
            By.XPATH, "//textarea[@aria-label='Form description']")[0]
        form_desc.send_keys(description)
        return

    def load_blank_template(self, title, description):
        '''Loads a new blank template in Google Forms and deletes any template questions

        Keyword arguments:
        title -- title of the form
        description -- description of the form
        '''
        templates = DRIVER.find_elements_by_class_name(
            "docs-homescreen-templates-templateview-showcase")
        templates[0].click()
        self.__waitfor(By.CLASS_NAME, "docssharedWizOmnilistMorselValue", self.TIMEOUT)
        DRIVER.find_elements_by_class_name(
            "freebirdFormeditorViewItemcardRoot")[0].click()
        DRIVER.find_elements(By.XPATH, "//div[@data-tooltip='Delete']")[0].click()
        self.edit_title(title)
        self.edit_description(description)
        self.sections[0] = Section(0, self)
        self.questions_per[0] = 0
        return

    def add_section(self):
        '''Add a section to the form'''
        time.sleep(OP_WAIT)
        if self.questions_per[max(self.sections.keys())] > 0:
            s_prev = self.sections[max(self.sections.keys())].count_previous()
            self.sections[max(self.sections.keys())].questions[self.questions_per[
                max(self.sections.keys())] - 1].click_question(s_prev)
        else:
            DRIVER.find_elements(
                By.XPATH, "//div[@class='freebirdFormeditorViewPagePageCard']")[max(self.sections.keys())].click()
        time.sleep(OP_WAIT)
        DRIVER.find_element(By.XPATH, "//div[@data-tooltip='Add section']").click()
        self.sections[max(self.sections.keys()) + 1] = Section(max(self.sections.keys()) + 1, self)
        self.questions_per[max(self.sections.keys())] = 0
        return

    def delete_section(self, index):
        '''Delete a particular Section from the form

        Keyword arguments:
        index -- index of Section [0,n)
        '''
        time.sleep(OP_WAIT)
        DRIVER.find_elements(
            By.XPATH, "//div[@aria-label='Overflow Menu']")[index].click()
        time.sleep(OP_WAIT)
        DRIVER.find_element(By.XPATH, "//div[@data-action-id='freebird-delete-page']").click()
        sectionrange = max(self.sections.keys())
        for section in range(index + 1, sectionrange):
            self.sections[section] = self.sections[section + 1]
        self.sections.pop(sectionrange)
        return

    def quit(self):
        '''Close the webdriver'''
        DRIVER.quit()
        return
