# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
# Copyright (C) <2010-2011>  Gabriel Falcão <gabriel@nacaolivre.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from lettuce import bunch_output
from lettuce import registry
from lettuce import Runner
from os.path import abspath, dirname, join, split, curdir
from lettuce.fs import FileSystem
from nose.tools import assert_equals, assert_true, with_setup
from tests.functional.test_runner import feature_name
from tests.asserts import prepare_stdout
import lxml.etree as ET


def run_check(name, assert_fcn, output_filename):
    runner = Runner(feature_name(name), bunch_output_file=output_filename)
    original_wrt_fcn = bunch_output.write_output
    bunch_output.write_output = assert_fcn
    try:
        runner.run()
    finally:
        bunch_output.write_output = original_wrt_fcn

def every(pred, seq):
    for i in seq:
        if not pred(i): return False
    return True

def any(pred, seq):
    for i in seq:
        if pred(i): return True
    return False

def check_all_passed(items, name):
    assert_true(len(items) > 0, "No %s results" % name)
    assert_true(every(lambda rez: rez.text == "passed",items), "Every %s must have 'passed'" % name)

def check_all_failed(items, name):
    assert_true(len(items) > 0, "No %s results" % name)
    assert_true(every(lambda rez: rez.text == "failed",items), "Every %s must have 'failed'" % name)

def check_some_failed(items, name):
    assert_true(len(items) > 0, "No %s results" % name)
    assert_true(any(lambda rez: rez.text == "failed",items), "Some %s must have 'failed'" % name)


@with_setup(prepare_stdout, registry.clear)
def test_bunch_output_no_errors():
    "Test bunch output without errors"
    called = []
    output_filename = "bunch.xml"
    def assert_correct_xml(filename, element):
        called.append(True)
        assert_equals(filename, output_filename, "Output filename")
        check_all_passed(element.findall('feature/result'), "feature")
        check_all_passed(element.findall('feature/scenarios/scenario/result'), "scenario")
        check_all_passed(element.findall('feature/scenarios/scenario/steps/step/result'), "steps")

        with FileSystem().open(abspath(join(dirname(__file__), 'bunch_test_no_err.xml')), "w") as f:
            f.write(ET.tostring(ET.ElementTree(element),  pretty_print=True))

    run_check('commented_feature', assert_correct_xml, output_filename)
    assert_equals(1, len(called), "Function not called")


@with_setup(prepare_stdout, registry.clear)
def test_bunch_output_one_error():
    "Test bunch output with one error"
    called = []
    output_filename = "bunch.xml"
    def assert_correct_xml(filename, element):
        called.append(True)
        assert_equals(filename, output_filename)
        check_all_failed(element.findall('feature/result'), "feature")
        check_some_failed(element.findall('feature/scenarios/scenario/result'), "scenario")
        check_some_failed(element.findall('feature/scenarios/scenario/steps/step/result'), "steps")
        check_all_failed(element.findall('feature/scenarios/scenario[0]/steps/step/result'), "steps")
        check_all_passed(element.findall('feature/scenarios/scenario[1]/steps/step/result'), "steps")
        with FileSystem().open(abspath(join(dirname(__file__), 'bunch_test_one_err.xml')), "w") as f:
            f.write(ET.tostring(ET.ElementTree(element),  pretty_print=True))

    run_check('error_traceback', assert_correct_xml, output_filename)
    assert_equals(1, len(called), "Function not called")


@with_setup(prepare_stdout, registry.clear)
def test_bunch_output_fail_outline():
    "Test bunch output with failing outline"
    called = []
    output_filename = "bunch.xml"
    def assert_correct_xml(filename, element):
        called.append(True)
        assert_equals(filename, output_filename)

        check_all_failed(element.findall('feature/result'), "feature")
        check_all_failed(element.findall('feature/scenarios/scenario/result'), "scenario")
        check_all_passed(element.findall('feature/scenarios/scenario/steps/step/result'), "steps")
        check_some_failed(element.findall('feature/scenarios/scenario/outlines/outline/result'), "outlines")
        #check_all_failed(element.findall('feature/scenarios/scenario/outlines/outline[2]/result'), "outlines")
        #check_all_passed(element.findall('feature/scenarios/scenario[1]/steps/step/result'), "steps")

        with FileSystem().open(abspath(join(dirname(__file__), 'bunch_test_outline_fail.xml')), "w") as f:
            f.write(ET.tostring(ET.ElementTree(element),  pretty_print=True))

    run_check('fail_outline', assert_correct_xml, output_filename)
    assert_equals(1, len(called), "Function not called")


@with_setup(prepare_stdout, registry.clear)
def test_bunch_output_success_outline():
    "Test bunch output with passing outline"
    called = []
    output_filename = "bunch.xml"
    def assert_correct_xml(filename, element):
        called.append(True)
        assert_equals(filename, output_filename)
        check_all_passed(element.findall('feature/result'), "feature")
        check_all_passed(element.findall('feature/scenarios/scenario/result'), "scenario")
        check_all_passed(element.findall('feature/scenarios/scenario/steps/step/result'), "steps")
        check_all_passed(element.findall('feature/scenarios/scenario/outlines/outline/result'), "outlines")
        with FileSystem().open(abspath(join(dirname(__file__), 'bunch_test_outline_success.xml')), "w") as f:
            f.write(ET.tostring(ET.ElementTree(element),  pretty_print=True))

    run_check('success_outline', assert_correct_xml, output_filename)
    assert_equals(1, len(called), "Function not called")


@with_setup(prepare_stdout, registry.clear)
def test_bunch_output_fail_table():
    "Test bunch output with failed table"
    called = []
    output_filename = "bunch.xml"
    def assert_correct_xml(filename, element):
        called.append(True)
        assert_equals(filename, output_filename)

        check_all_failed(element.findall('feature/result'), "feature")
        check_all_failed(element.findall('feature/scenarios/scenario/result'), "scenario")
        check_some_failed(element.findall('feature/scenarios/scenario/steps/step/result'), "steps")
        check_all_failed(element.findall('feature/scenarios/scenario/steps/step[6]/result'), "steps")

        with FileSystem().open(abspath(join(dirname(__file__), 'bunch_test_table_fail.xml')), "w") as f:
            f.write(ET.tostring(ET.ElementTree(element),  pretty_print=True))

    run_check('fail_table', assert_correct_xml, output_filename)
    assert_equals(1, len(called), "Function not called")

@with_setup(prepare_stdout, registry.clear)
def test_bunch_output_success_table():
    "Test bunch output with passing table"
    called = []
    output_filename = "bunch.xml"
    def assert_correct_xml(filename, element):
        called.append(True)
        assert_equals(filename, output_filename)

        check_all_passed(element.findall('feature/result'), "feature")
        check_all_passed(element.findall('feature/scenarios/scenario/result'), "scenario")
        check_all_passed(element.findall('feature/scenarios/scenario/steps/step/result'), "steps")

        with FileSystem().open(abspath(join(dirname(__file__), 'bunch_test_table_success.xml')), "w") as f:
            f.write(ET.tostring(ET.ElementTree(element),  pretty_print=True))

    run_check('success_table', assert_correct_xml, output_filename)
    assert_equals(1, len(called), "Function not called")
