RFC2Kindle
============

This project is created to convert RFC into well formatted mobi files so that it can read on Kindle.

If you have tried to read RFC from kindle, you might have found that figures are not showing correctly, no jumping from TOC, texts are flowing crazy etc.

So I wrote this python script based on the RFC-2-Kindle project on github.

RFC2Kindle is much better than RFC-2-Kindle on:
* delete page breaks
* more image elements
* smarter title handling
* smarter catalog handling
* easier to run it.

### Package Required
- ImageMagick
- KindleGen(http://www.amazon.com/gp/feature.html?ie=UTF8&docId=1000234621)  
  you can also download KindleGen from my vdisk(http://vdisk.weibo.com/s/qjqB9BNs69eZ)

### Steps of using RFC2Kindle
- download KindleGen and copy it to the directory where rfc2kindle.py placed
- wget your RFC ducument
  (wget http://www.ietf.org/rfc/rfc2535.txt)

- `./rfc2kindle.py -i rfc2535.txt`  
   This will generate a rfc2535.mobi file on your temporary directory.

- copy rfc2535.mobi to your kindle

### Note
This script works well on Linux.   

If the default font location isn't valid on your machine, use `fc-list | grep Courier` to find the font file, and supply it with -f:

```
$ fc-list | grep Courier
/usr/share/fonts/X11/Type1/c0419bt_.pfb: Courier 10 Pitch:style=Regular
/usr/share/fonts/X11/Type1/c0611bt_.pfb: Courier 10 Pitch:style=Bold Italic
/usr/share/fonts/X11/Type1/c0582bt_.pfb: Courier 10 Pitch:style=Italic
/usr/share/fonts/X11/Type1/c0583bt_.pfb: Courier 10 Pitch:style=Bold
$ ./rfc2kindle.py -i rfc2535.txt -f /usr/share/fonts/X11/Type1/c0419bt_.pfb

```

If you run RFC2Kindle on windows platform, please do some changes yourself.  
please email (keycobing at gmail dot com) for any improvement or any question  
PS: sorry for my code style, but the script works well.

### Author
keycobing@gmail.com





