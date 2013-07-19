RFC2Kindle
============

## Description
This project is to convert RFC into well formatted mobi files so that it can read on Kindle.

If you try to read RFC from kindle, you will find that figures are not showing correctly, no jumping from TOC, 
texts are flowing crazy etc.

So I wrote this python script based on the RFC-2-Kindle project on github(https://github.com/pingwin/RFC-2-Kindle).

RFC2Kindle is much better than RFC-2-Kindle with the follow reasons:
* delete page breaks
* more image elements
* smarter title handling
* smarter catalog handling

## Package Required
- ImageMagick
- KindleGen(http://www.amazon.com/gp/feature.html?ie=UTF8&docId=1000234621)

## Steps of using RFC2Kindle
- wget your RFC ducument
  wget http://www.ietf.org/rfc/rfc2535.txt

- ./rfc2kindle.py -i rfc2535.txt
- copy rfc2535.mobi to your kindle

## Note
This script works well on Linux. 
If you run RFC2Kindle on windows platform, please do some changes yourself.




