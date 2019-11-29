#!/usr/bin/env python
"""
Author:Brian Smith <pingwin@gmail.com> 
       Cobbliu <keycobing@gmail.com>
       Anand <ananth.padfoot@gmail.com>
Date: 2016/08/23
Description:
  Convert a IETF RFC txt format into an html document readable on the kindle.

Anand:
TODO: Rewrite to support Windows too
"""

import sys, logging, getopt, os
import re

default_font = '/usr/share/cups/fonts/Courier'
font = default_font

MAX_IMG_HEAD_FOOT_SIZE = 5

#Usage Help Printer
def usage():
    global _defaultfont
    """ print usage message """
    print "Convert IETF RFC TXT file to HTML for kindlegen"
    print "-h --help    This message"
    print "-i --input   input file"
    print "-f --font    font file to use for monospace images (default:%s)" % default_font
    sys.exit(2)

#Try to find a file name that's already not present in the directory.
def find_open_file(c=1):
    try:
        open('img%d.gif' % c)
    except IOError:
        return 'img%d.gif' % c
    return find_open_file(c+1)

#create image using ImageMagick
def create_image(picture_me):
    picture_me = "\\" + picture_me #Prepend a backslash to prevent 'convert' from removing leading spaces
    global font
    img_file_name = find_open_file()

    # Some Debugging
    '''
    imagetxtfile = open("%s" % (img_file_name.replace("gif","txt")), 'w')
    imagetxtfile.write(picture_me)
    imagetxtfile.close()
    print('convert -font %s label:"%s" %s' %  (font, picture_me.replace('"', '\"'), img_file_name))
    '''

    # Escape sequence with single quote has trouble with convert. So replacing with double quotes
    os.system('convert -font %s label:"%s" %s' %  (font, picture_me.replace('"', '\"'), img_file_name))
    return img_file_name

def is_image_part(line):
    img_chars = [
        '+-',
        ' |',
        '| ',
        '---',
        '0                   1',
        '0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5',
        '0   1   2   3   4   5   6   7',
        '  /  ',
        '1 1 1 1 1 1'
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

def addImageTagToBuffer(buffer, image_buf):
    return buffer.append('<img src="%s"/>' % create_image(''.join(image_buf)))
    # for debugging
    #return buffer.append('<a href="%s">link here</a>' % create_image(''.join(image_buf)))

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
    tmp_html_file = ""
    for opt, a in opts:
        if opt in ('-h', '--help'):
            usage()
        if opt in ('-i', '--input'):
            input = a
            input_name = a
            tmp_html_file = "%s.html" % input_name.split(".")[0]
        if opt in ('-f', '--font'):
            font = a
    if not input:
        usage()

    try:
        open(font)
    except:
        print "Unable to find font: %s" % font
        usage()


    input  = open(input_name,  'r')
    output = open("%s" % tmp_html_file, 'w')
    in_p   = False
    has_title = False
    has_description = False
    first_img_line = True
    in_image  = False
    pre_blank = False
    catalog    = False
    lineNo = 0 #not needed
    lastBlankInBuffer = 0;
    imgFooterBuf = []
    buffer = []
    buffer.append('<body>')
    for line in input:
        lineNo += 1
        ''' delete page breakers '''
        if is_page_break(line):
            continue;

        ''' delete extra blank lines.
        Also in case the image had a few lines (<5) of text content as part of the image,
        it would be in imgFooterBuf. Append it. Else add it to text buffer itself '''
        if is_blank(line):
            lastBlankInBuffer = len(buffer)-1;
            if len(imgFooterBuf) > 0:
                if (len(imgFooterBuf) <= MAX_IMG_HEAD_FOOT_SIZE):
                    image_buf += imgFooterBuf;
                    imgFooterBuf = []
                    addImageTagToBuffer(buffer, image_buf)
                    image_buf = []
                else:
                    buffer.append(imgFooterBuf)

                in_image = False
                imgFooterBuf = []

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
                addImageTagToBuffer(buffer, desp_image)
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
        ''' Sometimes, there are non-image chars that are part of the image, a few lines above and below it.
            So, let's accomodate them into the image, if they're a max of 'MAX_IMG_HEAD_FOOT_SIZE' lines '''

        ''' cant expect that image will always be after 2nd column;
            some RFCs have quite huge pictures right from 2nd column. Hence, commenting this condition '''
        #if line[:2] == '  ':

        ''' image '''
        if is_image_part(line):
            if not in_image:
                image_buf = []
                in_image = True

                if ((len(buffer) - lastBlankInBuffer > 0) and (len(buffer) - lastBlankInBuffer <= MAX_IMG_HEAD_FOOT_SIZE)):  # (probably) no. of lines of non-pictorial info above image
                    # remove the image head from buffer n add to image
                    tmpBuffer = buffer[lastBlankInBuffer+1:]

                    for i in range(len(tmpBuffer)):
                        tmpBuffer[i] = tmpBuffer[i] + "\n"

                    image_buf = tmpBuffer;
                    buffer[lastBlankInBuffer+1:] = []

            image_buf.append(line)
            continue

        # TODO: Get the image label if present above/below image

        if in_image:
            if (len(imgFooterBuf) <= MAX_IMG_HEAD_FOOT_SIZE) and not (is_blank(line)):
		#if a space ensues immediately
                imgFooterBuf.append(line)
                continue
            addImageTagToBuffer(buffer, image_buf)
            image_buf = imgFooterBuf = []
            in_image = False

            
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
                buffer.append('</p><br/>')
                in_p = False
            lastBlankInBuffer = len(buffer)-1
            continue
        
        buffer.append(line.replace("\n", ' '))

    buffer.append('</body>')
    buffer = ''.join(buffer)

    output.write(buffer)
    input.close()
    output.close()

    ''' generate and clear intermedia '''
    os.system("./kindlegen %s" % tmp_html_file)
    os.system("rm *.gif *.html")

if __name__ == "__main__":
    main()
