#!/usr/bin/env python
"""
Author:Brian Smith <pingwin@gmail.com> 
       Cobbliu <keycobing@gmail.com>
Date: 2013/07/15
Description:
  Convert a IETF RFC txt format into an html document readable on the kindle.
"""

import sys, logging, getopt, os
import re

default_font = '/usr/share/cups/fonts/Courier'
font = default_font

def usage():
    global _defaultfont
    """ print usage message """
    print "Convert IETF RFC TXT file to HTML for kindlegen"
    print "-h --help    This message"
    print "-i --input   input file"
    print "-f --font    font file to use for monospace images (default:%s)" % defaultfont
    sys.exit(2)

def find_open_file(c=0):
    try:
        c += 1
        open('img%d.gif' % c)
    except IOError:
        return 'img%d.gif' % c
    return find_open_file(c)

def create_image(picture_me):
    global font
    img = find_open_file()
    os.system("convert -font %s label:'%s' %s" % \
              (font, picture_me.replace("'", "\'"), img))
    return img

def is_image_part(line):
    img_chars = [
        '+-',
        ' | ',
        '---',
        '0                   1',
        '0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5',
        '  /  ',
        '1 1 1 1 1 1',
        '1 1 1 1 1 1 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5'
        ]
    for c in img_chars:
        if line.find(c) != -1:
            return True
    return False

def is_abstract(line):
    if re.match('Status of this Memo', line) or re.match('Abstract', line):
        return True
    return False

def is_blank(line):
    if re.match(r'^\s*$', line):
        return True
    return False

def is_page_break(line):
    if re.match(r'.*\[Page.*\d+?\]', line) or re.match(r'^RFC.*[1-2]\d\d\d', line):
        return True
    return False

def main():
    global font
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "hi:f:",
                                   [
                                       'help',
                                       'input',
                                       'font'
                                       ])
    except getopt.GetoptError, err:
        logging.exception(err)
        usage()

    input       = None
    input_name  = ""
    middle_file = ""
    for opt, a in opts:
        if opt in ('-h', '--help'):
            usage()
        if opt in ('-i', '--input'):
            input = a
            input_name = a
            middle_file = "%s.html" % input_name.split(".")[0]
        if opt in ('-f', '--font'):
            font = a
    if not input:
        usage()

    try:
        open(font)
    except:
        print "Unable to find font: %s" % font
        usage()

    input  = open(input,  'r')
    output = open("%s" % middle_file, 'w')
    in_p   = False
    has_title = False
    has_description = False
    first_img_line = True
    in_image  = False
    pre_blank = False
    catalog    = False

    buffer = []
    buffer.append('<body>')
    for line in input:
        ''' delete page breakers '''
        if is_page_break(line):
            continue;

        ''' delete extra blank lines '''
        if is_blank(line):
            if pre_blank:
                continue
            pre_blank = True
        else:
            pre_blank = False
            
        ''' handle description head '''
        if not has_description:
            if first_img_line:
                desp_image = []
                first_img_line = False
            elif not pre_blank:
                desp_image.append(line)
            else:
                buffer.append('<img src="%s" />' % create_image(''.join(desp_image)))
                has_description = True
                first_img_line = True
            continue

        ''' handle title '''
        if not has_title:
            if not is_blank(line):
                output.write('<title>%s %s</title>' % (input_name.split(".")[0], line.strip()))
                has_title = True
                buffer.append("<h2 align=\"center\">%s</h2>" % line)
            continue

        ''' begin of catalog '''
        if line.find('Table of Contents') != -1 and not catalog:
            catalog = True
            buffer.append("<h3>%s</h3>" % line.rstrip())
            continue

        ''' handle catalog '''
        if catalog:
            if re.search(r'(\d+)$', line.rstrip()):
                m = re.search(r'([\d\.]*\D+)(\d+)$', line.rstrip())
                buffer.append("%s<br />" % m.group(1).rstrip().rstrip('.').rstrip(' .'))
                continue
            elif re.match(r'^(\S+)', line):
                catalog = False

        ''' handle abstract '''
        if is_abstract(line):
            buffer.append("<h3>%s</h3>" % line.rstrip())
            continue
        
        if line[:2] == '  ':
            if is_image_part(line):
                ''' image '''
                if not in_image:
                    image = []
                    in_image = True
                image.append(line)
                continue

        if in_image:
            in_image = False
            buffer.append('<img src="%s" />' % create_image(''.join(image)))
            
        if re.match(r'^\d+\.?\s.*', line):
            buffer.append("<h3>%s</h3>" % line.rstrip())
            continue
        elif re.match(r'^\s*\d+\.\d+\.?\s.*', line):
            buffer.append("<h4>%s</h4>" % line.rstrip())
            continue
        elif re.match(r'^\s*\d+\.\d+\.\d+\.?\s.*', line):
            buffer.append("<h5>%s</h5>" % line.rstrip())
            continue

        ''' handle content '''
        if len(line) < 2:
            if not in_p:
                buffer.append('<p>')
                in_p = True
            else:
                buffer.append('</p><br />')
                in_p = False
            continue
        
        buffer.append(line.replace("\n", ' '))

    buffer.append('</body>')
    buffer = ''.join(buffer)

    output.write(buffer)
    input.close()
    output.close()

    ''' generate and clear intermedia '''
    os.system("./kindlegen %s" % middle_file)
    os.system("rm *.gif *.html")

if __name__ == "__main__":
    main()
