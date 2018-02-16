#!/usr/bin/env python3

'''Test file containing example of package use.'''

import sys
import time
sys.path.append('./gforms_automation')
from gforms_automation import *

if __name__ == '__main__':
    TESTFORM = GForm()
    TESTFORM.load_blank_template("NICE MEME", "this is a test")
    TESTFORM.sections[0].add_question()  # add question to Sec1
    # TESTFORM.sections[0].questions[0].set_multiple_choices(["optiona", "optionb", "optionc"])
    # TESTFORM.sections[0].add_question()  # add question to Sec1
    # TESTFORM.sections[0].questions[1].change_question_type(QuestionType.LINEAR_SCALE)
    # TESTFORM.sections[0].questions[1].set_linear_scale(1, 10, "not at all", "yes, totally")
    # TESTFORM.sections[0].add_question()
    TESTFORM.sections[0].questions[0].change_question_type(QuestionType.MULTIPLE_CHOICE_GRID)
    TESTFORM.sections[0].questions[0].set_grid_choices(
        ["1", "2", "3", "4", "5"], ["1", "2", "3", "4", "5"])
    time.sleep(10)
    TESTFORM.quit()
