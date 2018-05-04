#import subprocess
#import shutil
#import glob
#import math
#import os
#import datetime
#import time
#import sys

import prismspf_mcapi
#from prismspf_mcapi.equations import EquationInformation

def remove_block_comment(line, in_block_comment):
    block_comments_fully_stripped = False

    if in_block_comment:
        if '*/' in line:
            block_comment_end = line.find('*/') + 1
            found_block_comment = True
            in_block_comment = False

            line = line[block_comment_end + 1:]
        else:
            line = ''
            block_comments_fully_stripped = True

    while not block_comments_fully_stripped:

        remove_comment_results = remove_nonintroductory_block_comment(line, in_block_comment)
        line = remove_comment_results[0]
        in_block_comment = remove_comment_results[1]
        found_block_comment1 = remove_comment_results[2]

        if not found_block_comment1 or len(line) < 1:
            block_comments_fully_stripped = True

    return line, in_block_comment


def remove_nonintroductory_block_comment(line, in_block_comment):

    found_block_comment = False

    if '/*' in line:
        block_comment_start = line.find('/*')
        found_block_comment = True

        if '*/' in line:
            block_comment_end = line.find('*/') + 1
        else:
            block_comment_end = len(line)
            in_block_comment = True

        line = line[:block_comment_start] + line[block_comment_end + 1:]

    return line, in_block_comment, found_block_comment


def parse_for_attribute_statement(line, attribute_text, equation_information_list):
    if line[:len(attribute_text)] == attribute_text:
        contains_attribute_statement = True
        index_value_block = line[len(attribute_text) + 1:]

        index_value_block = index_value_block.strip()
        index_value_block = index_value_block[1:-2]
        split_index_value_block = index_value_block.split(',')
        index = split_index_value_block[0].strip()
        value = split_index_value_block[1].strip()

        value = value.replace('"', '')

    else:
        contains_attribute_statement = False
        index = -1
        value = ''

    if contains_attribute_statement:
        # Check to see if an EquationInformation object exists for this variable/equation already
        added_info = False
        for equation_information in equation_information_list:
            if equation_information.index == index:
                if attribute_text == 'set_variable_name':
                    equation_information.name = value
                elif attribute_text == 'set_variable_type':
                    equation_information.type = value
                elif attribute_text == 'set_variable_equation_type':
                    equation_information.equation_type = value

                added_info = True

        if not added_info:
            equation_information = prismspf_mcapi.equations.EquationInformation(index)
            if attribute_text == 'set_variable_name':
                equation_information.name = value
            elif attribute_text == 'set_variable_type':
                equation_information.type = value
            elif attribute_text == 'set_variable_equation_type':
                equation_information.equation_type = value

            equation_information.index = index
            equation_information_list.append(equation_information)

    return equation_information_list


def parse_equations_file(file_name):
    in_block_comment = False

    equation_information_list = []

    f = open(file_name)
    for line in f:
        # print('Raw line:', line)

        # First make sure line isn't a comment or blank line
        stripped_line = line.strip()
        if len(stripped_line) < 1 or stripped_line[0:2] == '//':
            continue

        # Strip contents within a block comment
        block_comment_removal_results = remove_block_comment(line, in_block_comment)
        line = block_comment_removal_results[0]
        in_block_comment = block_comment_removal_results[1]

        line = line.strip()
        # print('Processed line:', line)

        if len(line) < 1:
            continue

        equation_information_list = parse_for_attribute_statement(line, 'set_variable_name', equation_information_list)
        equation_information_list = parse_for_attribute_statement(line, 'set_variable_type', equation_information_list)
        equation_information_list = parse_for_attribute_statement(line, 'set_variable_equation_type', equation_information_list)

    # print(equation_information_list[0].name, equation_information_list[0].type, equation_information_list[0].equation_type)

    return equation_information_list
