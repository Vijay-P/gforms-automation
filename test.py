#!/usr/bin/env python3

'''Test file containing example of package use.'''

import sys
import time
sys.path.append('./gforms_automation')
from gforms_automation import *

if __name__ == '__main__':
    TESTFORM = GForm()
    TESTFORM.load_blank_template("NICE MEME 0", "this is a test")
    TESTFORM.add_section("WOAH 1", "this works")
    TESTFORM.add_section("2")
    TESTFORM.add_section("3")
    TESTFORM.add_section("4", "cool")
    TESTFORM.delete_section(4)
    TESTFORM.add_section("4")
    TESTFORM.delete_section(4)
    TESTFORM.delete_section(3)
    TESTFORM.sections[2].add_question()
    TESTFORM.sections[2].questions[0].change_question("0")
    TESTFORM.sections[2].add_question()
    TESTFORM.sections[2].questions[1].change_question("1")
    TESTFORM.sections[2].add_question()
    TESTFORM.sections[2].questions[2].change_question("2")
    TESTFORM.sections[1].add_question()
    TESTFORM.sections[0].add_question()
    # TESTFORM.sections[0].delete_question(0)
    # TESTFORM.sections[2].delete_question(1)
