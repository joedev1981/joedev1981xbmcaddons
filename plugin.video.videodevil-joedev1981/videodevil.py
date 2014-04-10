# -*- coding: latin-1 -*-
from string import capitalize, lower
import sys, os.path
import tempfile
import urllib, urllib2
import re
import os, traceback
import cookielib, htmlentitydefs
import threading
import Queue

import xbmcplugin, xbmcaddon
import xbmc, xbmcgui

import sesame

addon = xbmcaddon.Addon(id='plugin.video.videodevil-joedev1981')
__language__ = addon.getLocalizedString
rootDir = addon.getAddonInfo('path')
if rootDir[-1] == u';':
    rootDir = rootDir[0:-1]
rootDir = xbmc.translatePath(rootDir)
settingsDir = addon.getAddonInfo('profile')
settingsDir = xbmc.translatePath(settingsDir)
cacheDir = os.path.join(settingsDir, 'cache')
resDir = os.path.join(rootDir, 'resources')
imgDir = os.path.join(resDir, 'images')
catDir = os.path.join(resDir, 'catchers')

urlopen = urllib2.urlopen
cj = cookielib.LWPCookieJar()
Request = urllib2.Request
USERAGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-GB; rv:1.8.1.18) Gecko/20081029 Firefox/2.0.0.18'

if cj != None:
    if os.path.isfile(xbmc.translatePath(os.path.join(settingsDir, 'cookies.lwp'))):
        cj.load(xbmc.translatePath(os.path.join(settingsDir, 'cookies.lwp')))
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
else:
    opener = urllib2.build_opener()
    urllib2.install_opener(opener)

if addon.getSetting('enable_debug') == u'true':
    enable_debug = True
    xbmc.log('VideoDevil debug logging enabled')
else:
    enable_debug = False

entitydefs = {
    'AElig':    u'\u00C6', # latin capital letter AE = latin capital ligature AE, U+00C6 ISOlat1'
    'Aacute':   u'\u00C1', # latin capital letter A with acute, U+00C1 ISOlat1'
    'Acirc':    u'\u00C2', # latin capital letter A with circumflex, U+00C2 ISOlat1'
    'Agrave':   u'\u00C0', # latin capital letter A with grave = latin capital letter A grave, U+00C0 ISOlat1'
    'Alpha':    u'\u0391', # greek capital letter alpha, U+0391'
    'Aring':    u'\u00C5', # latin capital letter A with ring above = latin capital letter A ring, U+00C5 ISOlat1'
    'Atilde':   u'\u00C3', # latin capital letter A with tilde, U+00C3 ISOlat1'
    'Auml':     u'\u00C4', # latin capital letter A with diaeresis, U+00C4 ISOlat1'
    'Beta':     u'\u0392', # greek capital letter beta, U+0392'
    'Ccedil':   u'\u00C7', # latin capital letter C with cedilla, U+00C7 ISOlat1'
    'Chi':      u'\u03A7', # greek capital letter chi, U+03A7'
    'Dagger':   u'\u2021', # double dagger, U+2021 ISOpub'
    'Delta':    u'\u0394', # greek capital letter delta, U+0394 ISOgrk3'
    'ETH':      u'\u00D0', # latin capital letter ETH, U+00D0 ISOlat1'
    'Eacute':   u'\u00C9', # latin capital letter E with acute, U+00C9 ISOlat1'
    'Ecirc':    u'\u00CA', # latin capital letter E with circumflex, U+00CA ISOlat1'
    'Egrave':   u'\u00C8', # latin capital letter E with grave, U+00C8 ISOlat1'
    'Epsilon':  u'\u0395', # grek capital letter epsilon, U+0395'
    'Eta':      u'\u0397', # greek capital letter eta, U+0397'
    'Euml':     u'\u00CB', # latin capital letter E with diaeresis, U+00CB ISOlat1'
    'Gamma':    u'\u0393', # greek capital letter gamma, U+0393 ISOgrk3'
    'Iacute':   u'\u00CD', # latin capital letter I with acute, U+00CD ISOlat1'
    'Icirc':    u'\u00CE', # latin capital letter I with circumflex, U+00CE ISOlat1'
    'Igrave':   u'\u00CC', # latin capital letter I with grave, U+00CC ISOlat1'
    'Iota':     u'\u0399', # greek capital letter iota, U+0399'
    'Iuml':     u'\u00CF', # latin capital letter I with diaeresis, U+00CF ISOlat1'
    'Kappa':    u'\u039A', # greek capital letter kappa, U+039A'
    'Lambda':   u'\u039B', # greek capital letter lambda, U+039B ISOgrk3'
    'Mu':       u'\u039C', # greek capital letter mu, U+039C'
    'Ntilde':   u'\u00D1', # latin capital letter N with tilde, U+00D1 ISOlat1'
    'Nu':       u'\u039D', # greek capital letter nu, U+039D'
    'OElig':    u'\u0152', # latin capital ligature OE, U+0152 ISOlat2'
    'Oacute':   u'\u00D3', # latin capital letter O with acute, U+00D3 ISOlat1'
    'Ocirc':    u'\u00D4', # latin capital letter O with circumflex, U+00D4 ISOlat1'
    'Ograve':   u'\u00D2', # latin capital letter O with grave, U+00D2 ISOlat1'
    'Omega':    u'\u03A9', # greek capital letter omega, U+03A9 ISOgrk3'
    'Omicron':  u'\u039F', # greek capital letter omicron, U+039F'
    'Oslash':   u'\u00D8', # latin capital letter O with stroke = latin capital letter O slash, U+00D8 ISOlat1'
    'Otilde':   u'\u00D5', # latin capital letter O with tilde, U+00D5 ISOlat1'
    'Ouml':     u'\u00D6', # latin capital letter O with diaeresis, U+00D6 ISOlat1'
    'Phi':      u'\u03A6', # greek capital letter phi, U+03A6 ISOgrk3'
    'Pi':       u'\u03A0', # greek capital letter pi, U+03A0 ISOgrk3'
    'Prime':    u'\u2033', # double prime = seconds = inches, U+2033 ISOtech'
    'Psi':      u'\u03A8', # greek capital letter psi, U+03A8 ISOgrk3'
    'Rho':      u'\u03A1', # greek capital letter rho, U+03A1'
    'Scaron':   u'\u0160', # latin capital letter S with caron, U+0160 ISOlat2'
    'Sigma':    u'\u03A3', # greek capital letter sigma, U+03A3 ISOgrk3'
    'THORN':    u'\u00DE', # latin capital letter THORN, U+00DE ISOlat1'
    'Tau':      u'\u03A4', # greek capital letter tau, U+03A4'
    'Theta':    u'\u0398', # greek capital letter theta, U+0398 ISOgrk3'
    'Uacute':   u'\u00DA', # latin capital letter U with acute, U+00DA ISOlat1'
    'Ucirc':    u'\u00DB', # latin capital letter U with circumflex, U+00DB ISOlat1'
    'Ugrave':   u'\u00D9', # latin capital letter U with grave, U+00D9 ISOlat1'
    'Upsilon':  u'\u03A5', # greek capital letter upsilon, U+03A5 ISOgrk3'
    'Uuml':     u'\u00DC', # latin capital letter U with diaeresis, U+00DC ISOlat1'
    'Xi':       u'\u039E', # greek capital letter xi, U+039E ISOgrk3'
    'Yacute':   u'\u00DD', # latin capital letter Y with acute, U+00DD ISOlat1'
    'Yuml':     u'\u0178', # latin capital letter Y with diaeresis, U+0178 ISOlat2'
    'Zeta':     u'\u0396', # greek capital letter zeta, U+0396'
    'aacute':   u'\u00E1', # latin small letter a with acute, U+00E1 ISOlat1'
    'acirc':    u'\u00E2', # latin small letter a with circumflex, U+00E2 ISOlat1'
    'acute':    u'\u00B4', # acute accent = spacing acute, U+00B4 ISOdia'
    'aelig':    u'\u00E6', # latin small letter ae = latin small ligature ae, U+00E6 ISOlat1'
    'agrave':   u'\u00E0', # latin small letter a with grave = latin small letter a grave, U+00E0 ISOlat1'
    'alefsym':  u'\u2135', # alef symbol = first transfinite cardinal, U+2135 NEW'
    'alpha':    u'\u03B1', # greek small letter alpha, U+03B1 ISOgrk3'
    'amp':      u'\u0026', # ampersand, U+0026 ISOnum'
    'and':      u'\u2227', # logical and = wedge, U+2227 ISOtech'
    'ang':      u'\u2220', # angle, U+2220 ISOamso'
    'aring':    u'\u00E5', # latin small letter a with ring above = latin small letter a ring, U+00E5 ISOlat1'
    'asymp':    u'\u2248', # almost equal to = asymptotic to, U+2248 ISOamsr'
    'atilde':   u'\u00E3', # latin small letter a with tilde, U+00E3 ISOlat1'
    'auml':     u'\u00E4', # latin small letter a with diaeresis, U+00E4 ISOlat1'
    'bdquo':    u'\u201E', # double low-9 quotation mark, U+201E NEW'
    'beta':     u'\u03B2', # greek small letter beta, U+03B2 ISOgrk3'
    'brvbar':   u'\u00A6', # broken bar = broken vertical bar, U+00A6 ISOnum'
    'bull':     u'\u2022', # bullet = black small circle, U+2022 ISOpub'
    'cap':      u'\u2229', # intersection = cap, U+2229 ISOtech'
    'ccedil':   u'\u00E7', # latin small letter c with cedilla, U+00E7 ISOlat1'
    'cedil':    u'\u00B8', # cedilla = spacing cedilla, U+00B8 ISOdia'
    'cent':     u'\u00A2', # cent sign, U+00A2 ISOnum'
    'chi':      u'\u03C7', # greek small letter chi, U+03C7 ISOgrk3'
    'circ':     u'\u02C6', # modifier letter circumflex accent, U+02C6 ISOpub'
    'clubs':    u'\u2663', # black club suit = shamrock, U+2663 ISOpub'
    'cong':     u'\u2245', # approximately equal to, U+2245 ISOtech'
    'copy':     u'\u00A9', # copyright sign, U+00A9 ISOnum'
    'crarr':    u'\u21B5', # downwards arrow with corner leftwards = carriage return, U+21B5 NEW'
    'cup':      u'\u222A', # union = cup, U+222A ISOtech'
    'curren':   u'\u00A4', # currency sign, U+00A4 ISOnum'
    'dArr':     u'\u21D3', # downwards double arrow, U+21D3 ISOamsa'
    'dagger':   u'\u2020', # dagger, U+2020 ISOpub'
    'darr':     u'\u2193', # downwards arrow, U+2193 ISOnum'
    'deg':      u'\u00B0', # degree sign, U+00B0 ISOnum'
    'delta':    u'\u03B4', # greek small letter delta, U+03B4 ISOgrk3'
    'diams':    u'\u2666', # black diamond suit, U+2666 ISOpub'
    'divide':   u'\u00F7', # division sign, U+00F7 ISOnum'
    'eacute':   u'\u00E9', # latin small letter e with acute, U+00E9 ISOlat1'
    'ecirc':    u'\u00EA', # latin small letter e with circumflex, U+00EA ISOlat1'
    'egrave':   u'\u00E8', # latin small letter e with grave, U+00E8 ISOlat1'
    'empty':    u'\u2205', # empty set = null set = diameter, U+2205 ISOamso'
    'emsp':     u'\u2003', # em space, U+2003 ISOpub'
    'ensp':     u'\u2002', # en space, U+2002 ISOpub'
    'epsilon':  u'\u03B5', # greek small letter epsilon, U+03B5 ISOgrk3'
    'equiv':    u'\u2261', # identical to, U+2261 ISOtech'
    'eta':      u'\u03B7', # greek small letter eta, U+03B7 ISOgrk3'
    'eth':      u'\u00F0', # latin small letter eth, U+00F0 ISOlat1'
    'euml':     u'\u00EB', # latin small letter e with diaeresis, U+00EB ISOlat1'
    'euro':     u'\u20AC', # euro sign, U+20AC NEW'
    'exist':    u'\u2203', # there exists, U+2203 ISOtech'
    'fnof':     u'\u0192', # latin small f with hook = function = florin, U+0192 ISOtech'
    'forall':   u'\u2200', # for all, U+2200 ISOtech'
    'frac12':   u'\u00BD', # vulgar fraction one half = fraction one half, U+00BD ISOnum'
    'frac14':   u'\u00BC', # vulgar fraction one quarter = fraction one quarter, U+00BC ISOnum'
    'frac34':   u'\u00BE', # vulgar fraction three quarters = fraction three quarters, U+00BE ISOnum'
    'frasl':    u'\u2044', # fraction slash, U+2044 NEW'
    'gamma':    u'\u03B3', # greek small letter gamma, U+03B3 ISOgrk3'
    'ge':       u'\u2265', # greater-than or equal to, U+2265 ISOtech'
    'gt':       u'\u003E', # greater-than sign, U+003E ISOnum'
    'hArr':     u'\u21D4', # left right double arrow, U+21D4 ISOamsa'
    'harr':     u'\u2194', # left right arrow, U+2194 ISOamsa'
    'hearts':   u'\u2665', # black heart suit = valentine, U+2665 ISOpub'
    'hellip':   u'\u2026', # horizontal ellipsis = three dot leader, U+2026 ISOpub'
    'iacute':   u'\u00ED', # latin small letter i with acute, U+00ED ISOlat1'
    'icirc':    u'\u00EE', # latin small letter i with circumflex, U+00EE ISOlat1'
    'iexcl':    u'\u00A1', # inverted exclamation mark, U+00A1 ISOnum'
    'igrave':   u'\u00EC', # latin small letter i with grave, U+00EC ISOlat1'
    'image':    u'\u2111', # blackletter capital I = imaginary part, U+2111 ISOamso'
    'infin':    u'\u221E', # infinity, U+221E ISOtech'
    'int':      u'\u222B', # integral, U+222B ISOtech'
    'iota':     u'\u03B9', # greek small letter iota, U+03B9 ISOgrk3'
    'iquest':   u'\u00BF', # inverted question mark = turned question mark, U+00BF ISOnum'
    'isin':     u'\u2208', # element of, U+2208 ISOtech'
    'iuml':     u'\u00EF', # latin small letter i with diaeresis, U+00EF ISOlat1'
    'kappa':    u'\u03BA', # greek small letter kappa, U+03BA ISOgrk3'
    'lArr':     u'\u21D0', # leftwards double arrow, U+21D0 ISOtech'
    'lambda':   u'\u03BB', # greek small letter lambda, U+03BB ISOgrk3'
    'lang':     u'\u2329', # left-pointing angle bracket = bra, U+2329 ISOtech'
    'laquo':    u'\u00AB', # left-pointing double angle quotation mark = left pointing guillemet, U+00AB ISOnum'
    'larr':     u'\u2190', # leftwards arrow, U+2190 ISOnum'
    'lceil':    u'\u2308', # left ceiling = apl upstile, U+2308 ISOamsc'
    'ldquo':    u'\u201C', # left double quotation mark, U+201C ISOnum'
    'le':       u'\u2264', # less-than or equal to, U+2264 ISOtech'
    'lfloor':   u'\u230A', # left floor = apl downstile, U+230A ISOamsc'
    'lowast':   u'\u2217', # asterisk operator, U+2217 ISOtech'
    'loz':      u'\u25CA', # lozenge, U+25CA ISOpub'
    'lrm':      u'\u200E', # left-to-right mark, U+200E NEW RFC 2070'
    'lsaquo':   u'\u2039', # single left-pointing angle quotation mark, U+2039 ISO proposed'
    'lsquo':    u'\u2018', # left single quotation mark, U+2018 ISOnum'
    'lt':       u'\u003C', # less-than sign, U+003C ISOnum'
    'macr':     u'\u00AF', # macron = spacing macron = overline = APL overbar, U+00AF ISOdia'
    'mdash':    u'\u2014', # em dash, U+2014 ISOpub'
    'micro':    u'\u00B5', # micro sign, U+00B5 ISOnum'
    'middot':   u'\u00B7', # middle dot = Georgian comma = Greek middle dot, U+00B7 ISOnum'
    'minus':    u'\u2212', # minus sign, U+2212 ISOtech'
    'mu':       u'\u03BC', # greek small letter mu, U+03BC ISOgrk3'
    'nabla':    u'\u2207', # nabla = backward difference, U+2207 ISOtech'
    'nbsp':     u'\u00A0', # no-break space = non-breaking space, U+00A0 ISOnum'
    'ndash':    u'\u2013', # en dash, U+2013 ISOpub'
    'ne':       u'\u2260', # not equal to, U+2260 ISOtech'
    'ni':       u'\u220B', # contains as member, U+220B ISOtech'
    'not':      u'\u00AC', # not sign, U+00AC ISOnum'
    'notin':    u'\u2209', # not an element of, U+2209 ISOtech'
    'nsub':     u'\u2284', # not a subset of, U+2284 ISOamsn'
    'ntilde':   u'\u00F1', # latin small letter n with tilde, U+00F1 ISOlat1'
    'nu':       u'\u03BD', # greek small letter nu, U+03BD ISOgrk3'
    'oacute':   u'\u00F3', # latin small letter o with acute, U+00F3 ISOlat1'
    'ocirc':    u'\u00F4', # latin small letter o with circumflex, U+00F4 ISOlat1'
    'oelig':    u'\u0153', # latin small ligature oe, U+0153 ISOlat2'
    'ograve':   u'\u00F2', # latin small letter o with grave, U+00F2 ISOlat1'
    'oline':    u'\u203E', # overline = spacing overscore, U+203E NEW'
    'omega':    u'\u03C9', # greek small letter omega, U+03C9 ISOgrk3'
    'omicron':  u'\u03BF', # greek small letter omicron, U+03BF NEW'
    'oplus':    u'\u2295', # circled plus = direct sum, U+2295 ISOamsb'
    'or':       u'\u2228', # logical or = vee, U+2228 ISOtech'
    'ordf':     u'\u00AA', # feminine ordinal indicator, U+00AA ISOnum'
    'ordm':     u'\u00BA', # masculine ordinal indicator, U+00BA ISOnum'
    'oslash':   u'\u00F8', # latin small letter o with stroke, = latin small letter o slash, U+00F8 ISOlat1'
    'otilde':   u'\u00F5', # latin small letter o with tilde, U+00F5 ISOlat1'
    'otimes':   u'\u2297', # circled times = vector product, U+2297 ISOamsb'
    'ouml':     u'\u00F6', # latin small letter o with diaeresis, U+00F6 ISOlat1'
    'para':     u'\u00B6', # pilcrow sign = paragraph sign, U+00B6 ISOnum'
    'part':     u'\u2202', # partial differential, U+2202 ISOtech'
    'permil':   u'\u2030', # per mille sign, U+2030 ISOtech'
    'perp':     u'\u22A5', # up tack = orthogonal to = perpendicular, U+22A5 ISOtech'
    'phi':      u'\u03C6', # greek small letter phi, U+03C6 ISOgrk3'
    'pi':       u'\u03C0', # greek small letter pi, U+03C0 ISOgrk3'
    'piv':      u'\u03D6', # greek pi symbol, U+03D6 ISOgrk3'
    'plusmn':   u'\u00B1', # plus-minus sign = plus-or-minus sign, U+00B1 ISOnum'
    'pound':    u'\u00A3', # pound sign, U+00A3 ISOnum'
    'prime':    u'\u2032', # prime = minutes = feet, U+2032 ISOtech'
    'prod':     u'\u220F', # n-ary product = product sign, U+220F ISOamsb'
    'prop':     u'\u221D', # proportional to, U+221D ISOtech'
    'psi':      u'\u03C8', # greek small letter psi, U+03C8 ISOgrk3'
    'quot':     u'\u0022', # quotation mark = APL quote, U+0022 ISOnum'
    'rArr':     u'\u21D2', # rightwards double arrow, U+21D2 ISOtech'
    'radic':    u'\u221A', # square root = radical sign, U+221A ISOtech'
    'rang':     u'\u232A', # right-pointing angle bracket = ket, U+232A ISOtech'
    'raquo':    u'\u00BB', # right-pointing double angle quotation mark = right pointing guillemet, U+00BB ISOnum'
    'rarr':     u'\u2192', # rightwards arrow, U+2192 ISOnum'
    'rceil':    u'\u2309', # right ceiling, U+2309 ISOamsc'
    'rdquo':    u'\u201D', # right double quotation mark, U+201D ISOnum'
    'real':     u'\u211C', # blackletter capital R = real part symbol, U+211C ISOamso'
    'reg':      u'\u00AE', # registered sign = registered trade mark sign, U+00AE ISOnum'
    'rfloor':   u'\u230B', # right floor, U+230B ISOamsc'
    'rho':      u'\u03C1', # greek small letter rho, U+03C1 ISOgrk3'
    'rlm':      u'\u200F', # right-to-left mark, U+200F NEW RFC 2070'
    'rsaquo':   u'\u203A', # single right-pointing angle quotation mark, U+203A ISO proposed'
    'rsquo':    u'\u2019', # right single quotation mark, U+2019 ISOnum'
    'sbquo':    u'\u201A', # single low-9 quotation mark, U+201A NEW'
    'scaron':   u'\u0161', # latin small letter s with caron, U+0161 ISOlat2'
    'sdot':     u'\u22C5', # dot operator, U+22C5 ISOamsb'
    'sect':     u'\u00A7', # section sign, U+00A7 ISOnum'
    'shy':      u'\u00AD', # soft hyphen = discretionary hyphen, U+00AD ISOnum'
    'sigma':    u'\u03C3', # greek small letter sigma, U+03C3 ISOgrk3'
    'sigmaf':   u'\u03C2', # greek small letter final sigma, U+03C2 ISOgrk3'
    'sim':      u'\u223C', # tilde operator = varies with = similar to, U+223C ISOtech'
    'spades':   u'\u2660', # black spade suit, U+2660 ISOpub'
    'sub':      u'\u2282', # subset of, U+2282 ISOtech'
    'sube':     u'\u2286', # subset of or equal to, U+2286 ISOtech'
    'sum':      u'\u2211', # n-ary sumation, U+2211 ISOamsb'
    'sup':      u'\u2283', # superset of, U+2283 ISOtech'
    'sup1':     u'\u00B9', # superscript one = superscript digit one, U+00B9 ISOnum'
    'sup2':     u'\u00B2', # superscript two = superscript digit two = squared, U+00B2 ISOnum'
    'sup3':     u'\u00B3', # superscript three = superscript digit three = cubed, U+00B3 ISOnum'
    'supe':     u'\u2287', # superset of or equal to, U+2287 ISOtech'
    'szlig':    u'\u00DF', # latin small letter sharp s = ess-zed, U+00DF ISOlat1'
    'tau':      u'\u03C4', # greek small letter tau, U+03C4 ISOgrk3'
    'there4':   u'\u2234', # therefore, U+2234 ISOtech'
    'theta':    u'\u03B8', # greek small letter theta, U+03B8 ISOgrk3'
    'thetasym': u'\u03D1', # greek small letter theta symbol, U+03D1 NEW'
    'thinsp':   u'\u2009', # thin space, U+2009 ISOpub'
    'thorn':    u'\u00FE', # latin small letter thorn with, U+00FE ISOlat1'
    'tilde':    u'\u02DC', # small tilde, U+02DC ISOdia'
    'times':    u'\u00D7', # multiplication sign, U+00D7 ISOnum'
    'trade':    u'\u2122', # trade mark sign, U+2122 ISOnum'
    'uArr':     u'\u21D1', # upwards double arrow, U+21D1 ISOamsa'
    'uacute':   u'\u00FA', # latin small letter u with acute, U+00FA ISOlat1'
    'uarr':     u'\u2191', # upwards arrow, U+2191 ISOnum'
    'ucirc':    u'\u00FB', # latin small letter u with circumflex, U+00FB ISOlat1'
    'ugrave':   u'\u00F9', # latin small letter u with grave, U+00F9 ISOlat1'
    'uml':      u'\u00A8', # diaeresis = spacing diaeresis, U+00A8 ISOdia'
    'upsih':    u'\u03D2', # greek upsilon with hook symbol, U+03D2 NEW'
    'upsilon':  u'\u03C5', # greek small letter upsilon, U+03C5 ISOgrk3'
    'uuml':     u'\u00FC', # latin small letter u with diaeresis, U+00FC ISOlat1'
    'weierp':   u'\u2118', # script capital P = power set = Weierstrass p, U+2118 ISOamso'
    'xi':       u'\u03BE', # greek small letter xi, U+03BE ISOgrk3'
    'yacute':   u'\u00FD', # latin small letter y with acute, U+00FD ISOlat1'
    'yen':      u'\u00A5', # yen sign = yuan sign, U+00A5 ISOnum'
    'yuml':     u'\u00FF', # latin small letter y with diaeresis, U+00FF ISOlat1'
    'zeta':     u'\u03B6', # greek small letter zeta, U+03B6 ISOgrk3'
    'zwj':      u'\u200D', # zero width joiner, U+200D NEW RFC 2070'
    'zwnj':     u'\u200C'  # zero width non-joiner, U+200C NEW RFC 2070'
}

entitydefs2 = {
    '$':    '%24',
    '&':    '%26',
    '+':    '%2B',
    ',':    '%2C',
    '/':    '%2F',
    ':':    '%3A',
    ';':    '%3B',
    '=':    '%3D',
    '?':    '%3F',
    '@':    '%40',
    ' ':    '%20',
    '"':    '%22',
    '<':    '%3C',
    '>':    '%3E',
    '#':    '%23',
    '%':    '%25',
    '{':    '%7B',
    '}':    '%7D',
    '|':    '%7C',
    '\\':   '%5C',
    '^':    '%5E',
    '~':    '%7E',
    '[':    '%5B',
    ']':    '%5D',
    '`':    '%60'
}

entitydefs3 = {
    u'ÂÁÀÄÃÅ':  u'A',
    u'âáàäãå':  u'a',
    u'ÔÓÒÖÕ':   u'O',
    u'ôóòöõðø': u'o',
    u'ÛÚÙÜ':    u'U',
    u'ûúùüµ':   u'u',
    u'ÊÉÈË':    u'E',
    u'êéèë':    u'e',
    u'ÎÍÌÏ':    u'I',
    u'îìíï':    u'i',
    u'ñ':       u'n',
    u'ß':       u'B',
    u'÷':       u'%',
    u'ç':       u'c',
    u'æ':       u'ae'
}

def clean1(s): # remove &XXX;
    if not s:
        return ''
    for name, value in entitydefs.iteritems():
        if u'&' in s:
            s = s.replace(u'&' + name + u';', value)
    return s

def clean2(s): # remove \\uXXX
    pat = re.compile(r'\\u(....)')
    def sub(mo):
        return unichr(int(mo.group(1), 16))
    return pat.sub(sub, smart_unicode(s))

def clean3(s): # remove &#XXX;
    pat = re.compile(r'&#(\d+);')
    def sub(mo):
        return unichr(int(mo.group(1)))
    return decode(decode(pat.sub(sub, smart_unicode(s)))) # Once in a while site triple their source

def decode(s):
    if not s:
        return ''
    try:
        dic = htmlentitydefs.name2codepoint
        for key in dic.keys():
            entity = '&' + key + ';'
            s = s.replace(entity, unichr(dic[key]))
    except:
        if enable_debug:
            traceback.print_exc(file = sys.stdout)
    return s

def unquote(s): # unquote
    if not s:
        return ''
    try:
        for key, value in entitydefs2.iteritems():
            s = s.replace(value, key)
    except:
        if enable_debug:
            traceback.print_exc(file = sys.stdout)
    return s

def quote(s): # quote
    if not s:
        return ''
    try:
        for key, value in entitydefs2.iteritems():
            s = s.replace(key, value)
    except:
        if enable_debug:
            traceback.print_exc(file = sys.stdout)
    return s2

def smart_unicode(s):
    if not s:
        return ''
    try:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = unicode(str(s), 'UTF-8')
        elif not isinstance(s, unicode):
            s = unicode(s, 'UTF-8')
    except:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = unicode(str(s), 'ISO-8859-1')
        elif not isinstance(s, unicode):
            s = unicode(s, 'ISO-8859-1')
    return s

def clean_safe(s):
    if not s:
        return ''
    try:
        s = clean1(clean2(clean3(smart_unicode(s))))
    except:
        if enable_debug:
            traceback.print_exc(file = sys.stdout)
    return s

def clean_filename(s):
    if not s:
        return ''
    badchars = '\\/:*?\"<>|'
    for c in badchars:
        s = s.replace(c, '_')
    return s;

def smart_read_file(filename):
    for directory in [catDir, resDir, cacheDir, '']:
        try:
            f = open(os.path.join(directory, filename), 'r')
            break
        except:
            if directory == '':
                traceback.print_exc(file = sys.stdout)
            if directory == '':
                return None, None, 'File Not Found'

    key = []
    value = []

    for line in f:
        line =  smart_unicode(line)
        if line and line.startswith(u'#'):
            continue
        try:
            line = line.replace(u'\r\n', u'').replace(u'\n', u'')
        except:
            continue
        try:
            k, v = line.split(u'=', 1)
        except:
#            log('Line does not start with a \'#\' or does not contain an \'=\'')
#            log('Line = ' + line.encode('utf-8'))
            continue
        if v.startswith(u'video.devil.'):
            idx = v.find(u'|')
            if v[:idx] == u'video.devil.locale':
                v = u'  ' + __language__(int(v[idx+1:])) + u'  '
            elif v[:idx] ==u'video.devil.image':
                v = os.path.join(imgDir, v[idx+1:])
            elif v[:idx] == u'video.devil.context':
                v = u'context.' + __language__(int(v[idx+1:]))
        key.append(k)
        value.append(v)
    f.close()
    return key, value, 'File Opened'

def parseActions(item, convActions, url = None):
#    print('item = ' + str(item))
    for convAction in convActions:
        if convAction.find(u"(") != -1:
            action = convAction[0:convAction.find(u'(')]
#            print('action = ' + action)
            param = convAction[len(action) + 1:-1]
#            print('param = ' + param)
            if param.find(u', ') != -1:
                params = param.split(u', ')
                if action == u'replace':
                    item[params[0]] = item[params[0]].replace(params[1], params[2])
                elif action == u'join':
                    j = []
                    for i in range(1, len(params)):
                        j.append(item[params[i]])
                    item[params[1]] = params[0].join(j)
                elif action == u'decrypt':
                    item[u'match'] = sesame.decrypt(item[params[0]], item[params[1]], 256)
            else:
                if action == u'unquote':
                    item[param] = urllib.unquote(item[param])
                elif action == u'quote':
                    item[param] = urllib.quote(item[param])
                elif action == u'decode':
                    item[param] = decode(item[param])

        else:
            action = convAction

            if action == u'append':
                item[u'url'] = url + item[u'url']
            elif action == u'appendparam':
                if url[-1] == u'?':
                    item[u'url'] = url + item[u'url']
                else:
                    item[u'url'] = url + u'&' + item[u'url']
            elif action == u'replaceparam':
                if url.rfind('?') == -1:
                    item[u'url'] = url + u'?' + item[u'url']
                else:
                    item[u'url'] = url[:url.rfind('?')] + u'?' + item[u'url']
            elif action == u'striptoslash':
                if url.rfind(u'/'):
                    idx = url.rfind(u'/')
                    if url[:idx + 1] == u'http://':
                        item[u'url'] = url + u'/' + item[u'url']
                    else:
                        item[u'url'] = url[:idx + 1] + item[u'url']
#            elif action == u'space':
#                try:
#                    item[u'title'] = u'  ' + item[u'title'].strip(u' ') + u'  '
#                except:
#                    pass
    return item

def log(s):
    if enable_debug:
        xbmc.log(s)
    return

def run_parallel_in_threads(target, args_list):
    result = Queue.Queue()
    # wrapper to collect return value in a Queue
    def task_wrapper(*args):
        result.put(target(*args))
    threads = [threading.Thread(target=task_wrapper, args=args) for args in args_list]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return result

def inheritInfos(item, lItem):
    for k in lItem.keys():
        if k not in item:
            item[k] = lItem[k]
    return None

def getFileExtension(filename):
    ext_pos = filename.rfind(u'.')
    if ext_pos != -1:
        return smart_unicode(filename[ext_pos+1:])
    return ''

def getKeyboard(default = '', heading = '', hidden = False):
    kboard = xbmc.Keyboard(default, heading, hidden)
    kboard.doModal()
    if kboard.isConfirmed():
        return kboard.getText()
    return ''

def getSearchPhrase():
    try:
        curr_phrase = addon.getSetting('curr_search')
    except:
        addon.setSetting('curr_search', '')
        curr_phrase = ''
    search_phrase = getKeyboard(default = curr_phrase, heading = __language__(30102))
    addon.setSetting('curr_search', search_phrase)
    return search_phrase.replace(' ', '+')

class Mode:
    START = 0
    PLAY = 1
    DOWNLOAD = 2
    ADD = 5
    REMOVE = 6
    VIEW_RSS = 10
    VIEW_SEARCH = 11
    VIEW_DIRECTORY = 12
    VIEWALL_RSS = 20
    VIEWALL_SEARCH = 21
    VIEWALL_DIRECTORY = 22


class CCatcherRuleItem:
    def __init__(self):
        self.target = None
        self.actions = []
        self.dkey = None
        self.dkey_actions = []
        self.info = None
        self.extension = u'flv'
        self.quality = u'standard'
        self.build = None
        self.type = u'video'
        self.priority = 0


class CCatcherRuleSite:
    def __init__(self):
        self.url = ''
        self.startRE = None
        self.stopRE = None
        self.txheaders = {'User-Agent':USERAGENT}
        self.limit = 0
        self.data = ''
        self.rules = []


class CCatcherList:
    def __init__(self):
        self.status = {}
        self.player = ''
        self.skill = ''
        self.sites = []
        self.urlList = []
        self.extensionList = []
        self.selectionList = []
        self.decryptList = []
        self.videoExtension = u'.flv'
        self.dkey = None
        self.link = None

    def getDirectLink(self, lItem):
        self.loadCatcher(lItem[u'catcher'])
        embedded = self.parseVideoPage(lItem[u'url'])
        if embedded:
            self.status = embedded['status']
            self.player = embedded['player']
            self.skill = embedded['skill']
            self.videoExtension = embedded['videoExtension']
            self.link = embedded['link']
        if self.link != None:
            return self.link
        elif len(self.urlList) > 0:
            self.selectLink()
        else:
            tmp_catcher = CCatcherList()
            lItem[u'catcher'] = u'simple-match'
            tmp_attr = self.getEmbeddedLink(lItem)
            if tmp_attr != None and tmp_attr['link'] != None:
                self.status = tmp_attr['status']
                self.player = tmp_attr['player']
                self.skill = tmp_attr['skill']
                self.videoExtension = tmp_attr['videoExtension']
                self.link = tmp_attr['link']
        return self.link

    def getEmbeddedLink(self, lItem):
        self.loadCatcher(lItem[u'catcher'])
        self.parseVideoPage(lItem[u'url'])
        if len(self.urlList) > 0:
            self.selectLink()
        else:
            return None
        return {'status': self.status, 'player': self.player, 'skill': self.skill, 'videoExtension': self.videoExtension, 'link': self.link}

    def loadCatcher(self, title):
        key, value, self.status['file'] = smart_read_file(title)
        if key == None and value == None:
            return None
        line = 0
        length = len(key)
        breaker = -10
        site = None
        rule = None
        if key[line] == u'player':
            self.player = value[line]
            line += 1
        while line < length:
            breaker += 1
            if key[line] == u'url':
                if site:
                    self.sites.append(site)
                site = CCatcherRuleSite()
                site.url = value[line]
                line += 1
            if key[line] == u'data':
                site.data = value[line]
                line += 1
            if key[line] == u'header':
                index = value[line].find(u'|')
                site.txheaders[value[line][:index]] = value[line][index+1:]
                line += 1
            if key[line] == u'limit':
                site.limit = int(value[line])
                line += 1
            if key[line] == u'startRE':
                site.startRE = value[line]
                line += 1
            if key[line] == u'stopRE':
                site.stopRE = value[line]
                line += 1
            while line < length:
                breaker += 1
                if key[line] == u'target':
                    if rule:
                        site.rules.append(rule)
                    rule = CCatcherRuleItem()
                    rule.target = value[line]
                    line += 1
                if key[line] == u'quality':
                    rule.quality = value[line]
                    line += 1
                    continue
                if key[line] == u'priority':
                    rule.priority = int(value[line])
                    line += 1
                    continue
                if key[line] == u'type':
                    rule.type = value[line]
                    line += 1
                    if rule.type == u'forward' or rule.type.startswith(u'redirect'):
                        site.rules.append(rule)
                        rule = None
                        break
                else:
                    if key[line] == u'actions':
                        if value[line].find(u'|'):
                            rule.actions = value[line].split(u'|')
                        else:
                            rule.actions.append(value[line])
                        line += 1
                    if key[line] == u'build':
                        rule.build = value[line]
                        line += 1
                    if key[line] == u'dkey':
                        rule.dkey = value[line]
                        line += 1
                        if key[line] == u'dkey_actions':
                            if value[line].find(u'|'):
                                rule.dkey_actions = value[line].split(u'|')
                            else:
                                rule.dkey_actions.append(value[line])
                            line += 1
                    if key[line] == u'extension':
                        rule.extension = value[line]
                        line += 1
                    if key[line] == u'info':
                        rule.info = value[line]
                        line += 1
                if breaker == length:
                    break
            if breaker == length:
                break
        if rule != None:
            site.rules.append(rule)
        self.sites.append(site)
        if breaker == length:
            self.status['syntax'] = 'Cfg syntax is invalid.\nKey error in line %s' % str(line)
        else:
            self.status['syntax'] = 'Cfg syntax is valid'
        return None

    def parseVideoPage(self, url):
        video_found = False
        for index, site in enumerate(self.sites):
            if video_found:
                break
            print('url = ' + url)
            # Download website
            if site.data == '':
                if site.url.find(u'%') != -1:
                    url = site.url % url
                req = Request(url, None, site.txheaders)
                urlfile = opener.open(req)
                if site.limit == 0:
                    data = urlfile.read()
                else:
                    data = urlfile.read(site.limit)
            else:
                data_url = site.data % url
                req = Request(site.url, data_url, site.txheaders)
                response = urlopen(req)
                if site.limit == 0:
                    data = response.read()
                else:
                    data = response.read(site.limit)
            if enable_debug:
                f = open(os.path.join(cacheDir, 'site.html'), 'w')
                f.write(u'<Titel>'+ url + u'</Title>\n\n')
                f.write(data)
                f.close()

            if site.startRE:
                start = data.find(site.startRE.encode('utf-8'))
                if start == -1:
                    print('startRe not found for %s' % url)
                else:
                    data = data[start:]
                    if site.stopRE:
                        stop = data.find(site.stopRE.encode('utf-8'))
                        if stop == -1:
                            print('stopRe not found for %s' % url)
                        else:
                            data = data[:stop]

            # If user setting is not set to "Ask me"
            # Sort rules to parse in the order specified in the settings
            # Parsing will continue until a match is found with rule.priority anything other than 0
            if len(site.rules) > 1:
                decorated1 = [(rule.priority, i, rule) for i, rule in enumerate(site.rules) if rule.priority < 0]
                decorated1 = sorted(decorated1, reverse = True)
                if int(addon.getSetting('video_type')) == 3:
                    decorated = [(rule.priority, i, rule) for i, rule in enumerate(site.rules) if rule.priority >= 0]
                    decorated = sorted(decorated)
                    site.rules = [rule for priority, i, rule in decorated]
                elif int(addon.getSetting('video_type')) == 2:
                    decorated = [(rule.priority, i, rule) for i, rule in enumerate(site.rules) if rule.priority > 0]
                    decorated = sorted(decorated)
                    if len(decorated) % 2 == 0:
                        decorated = decorated[len(decorated) // 2 - 1:] + list(reversed(decorated[:len(decorated) // 2 - 1]))
                    else:
                        decorated = decorated[len(decorated) // 2:] + list(reversed(decorated[:len(decorated) // 2]))
                    site.rules = [rule for rule in site.rules if rule.priority == 0] + [rule for priority, i, rule in decorated]
                elif int(addon.getSetting('video_type')) == 1:
                    decorated = [(rule.priority, i, rule) for i, rule in enumerate(site.rules) if rule.priority > 0]
                    decorated = sorted(decorated, reverse = True)
                    site.rules = [rule for rule in site.rules if rule.priority == 0] + [rule for priority, i, rule in decorated]
                site.rules += [rule for priority, i, rule in decorated1]
                if site.startRE:
                    start = data.find(site.startRE.encode('utf-8'))
                    if start == -1:
                        print('startRe not found for %s' % url)
                    else:
                        data = data[start:]
                        if site.stopRE:
                            stop = data.find(site.stopRE.encode('utf-8'))
                            if stop == -1:
                                print('stopRe not found for %s' % url)
                            else:
                                data = data[:stop]
#            print('self.sites.rules = ' + str(self.sites[0].rules))
            for rule in site.rules:
                print('rule.priority = ' + str(rule.priority))
            # Parse Website
            for rule in site.rules:
                print('parsing site')
                print('with rule: ' + rule.target)
                match = re.search(rule.target, data, re.IGNORECASE + re.DOTALL + re.MULTILINE)
                if match:
                    print('match found' + str(rule.priority))
                    link = match.group(1)
                    if len(rule.actions) > 0:
                        for group in range(1, len(match.groups()) + 1):
                            if group == 1:
                                link = {u'match' : link}
                            else:
                                link[u'group' + str(group)] = match.group(group)
                        print(link)
                        link = parseActions(link, rule.actions)[u'match']
                    if rule.build != None:
                        link = rule.build % link
                    if rule.type == u'video':
                        video_found = True
                        print(link)
                        self.urlList.append(link)
                        self.extensionList.append(rule.extension)
                        if rule.dkey != None:
                            match = re.search(rule.dkey, data, re.IGNORECASE + re.DOTALL + re.MULTILINE)
                            if match:
                                dkey = match.group(1)
                                if len(rule.dkey_actions) > 0:
                                    dkey = {u'match' : dkey}
                                    print('dkey = '  + str(dkey))
                                    dkey = parseActions(dkey, rule.dkey_actions)[u'match']
                                print('dkey = '  + str(dkey))
                                self.decryptList.append(dkey)
                        else:
                            self.decryptList.append(None)
                        if int(addon.getSetting('video_type')) == 0:
                            selList_type = {
                                u'low' : __language__(30056), 
                                u'standard' : __language__(30057), 
                                u'high' : __language__(30058)
                            }
                            append = rule.info or rule.extension
                            self.selectionList.append(selList_type[rule.quality] + u' (' + append + u')')
                    elif rule.type == u'dkey':
                        self.dkey = link
                        print('self.dkey = ' + self.dkey)
                    elif rule.type == u'forward':
                        url = clean_safe(urllib2.unquote(link))
                        break
                    elif rule.type.startswith(u'redirect'):
                        tmp_catcher = CCatcherList()
                        tmp_lItem = {u'url': clean_safe(urllib2.unquote(link))}
                        print('len(self.sites) = ' + str(len(self.sites)))
                        print('url' + url)
                        if rule.type.find(u"(") != -1:
                            tmp_lItem[u'catcher'] = rule.type[rule.type.find(u"(") + 1:-1]
                        ### need to make the else statement below an elif statement 
                        ### and make the else default to simple-match catcher 
                        else:
                            for root, dirs, files in os.walk(catDir):
                                for filename in files:
                                    print('filename = ' + filename)
                                    if url.find(filename) != -1:
                                        tmp_lItem[u'catcher'] = filename
                        ret_attr = tmp_catcher.getEmbeddedLink(tmp_lItem)
                        if ret_attr['link']:
                            return ret_attr
                        print('len(self.sites) = ' + str(len(self.sites)))
                        break
                    if int(addon.getSetting('video_type')) != 0 and rule.priority != 0:
                        break
        return None

    def selectLink(self):
        if int(addon.getSetting('video_type')) != 0:
            selection = 0
        else:
            dia = xbmcgui.Dialog()
            selection = dia.select(__language__(30055), self.selectionList)
        self.videoExtension = u'.' + self.extensionList[selection]
        self.urlList[selection] = clean_safe(urllib2.unquote(self.urlList[selection]))
        if self.dkey != None:
            self.dkey = clean_safe(urllib2.unquote(self.dkey))
            link = sesame.decrypt(self.urlList[selection], self.dkey, 256)
        elif self.decryptList[selection] != None:
            self.decryptList[selection] = clean_safe(urllib2.unquote(self.decryptList[selection]))
            link = sesame.decrypt(self.urlList[selection], self.decryptList[selection], 256)
        else:
            link = self.urlList[selection]
        print('link = ' + link)
        self.link = link
        return None


class CItemTypes(object):
    def __init__(self):
        self.types = []
        self.infos = []
        self.items_list = []

    def __getitem__(self, x):
        return self.items_list[self.types.index(x)]

    def __setitem__(self, x, y):
        if x in self.types:
            self.items_list[self.types.index(x)].extend(y[1])
        else:
            self.types.append(x)
            self.infos.append(y[0])
            self.items_list.append(y[1])

    def __delitem__(self, x):
        del self.items_list[self.types.index(x)]
        del self.types[x]

    def __contains__(self, x):
        if x in self.types:
            return True
        else:
            return False

    def __len__(self):
        return len(self.types)

    def files(self):
        return list(zip(self.types, self.infos, self.items_list))


class CItemInfo:
    def __init__(self):
        self.name = ''
        self.src = u'url'
        self.rule = ''
        self.default = ''
        self.build = ''


class CRuleItem:
    def __init__(self):
        self.infos = ''
        self.infosRE = ''
        self.order = []
        self.skill = ''
        self.curr = ''
        self.currRE = ''
        self.type = ''
        self.info_list = []
        self.actions = []
        self.url_build = ''


class CRuleSite:
    def __init__(self):
        self.status = {}
        self.start = ''
        self.txheaders = {
            'User-Agent': USERAGENT,
            'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.7'
        }
        self.startRE = ''
        self.cfg = ''
        self.data = ''
        self.rules = []
        self.items = CItemTypes()
        self.links = CItemTypes()


class CCurrentList:
    def __init__(self):
        self.sort = [u'label', u'genre']
        self.skill = ''
        self.sites = []
        self.items = CItemTypes()
        self.links = CItemTypes()

    def videoCount(self):
        count = 0
        for item in self.items:
            if item[u'type'] == u'video':
                count = count +1
        return count

    def getVideo(self):
        for item in self.items:
            if item[u'type'] == u'video':
                return item
 
    def loadLocal(self, filename, lItem):
        site = CRuleSite()
        key, value, site.status['file'] = smart_read_file(filename)
        if key == None and value == None:
            return None
        site.cfg = filename
        if u'cfg' not in lItem:
            if getFileExtension(filename) == u'cfg':
                lItem[u'cfg'] = filename
        tmp = None
        line = 0
        length = len(key) - 1
        breaker = -10
        if key[line] == u'start':
            site.start = value[line]
            line += 1
        if key[line] == u'header':
            index = value[line].find(u'|')
            site.txheaders[value[line][:index]] = value[line][index+1:]
            line += 1
        if key[line] == u'sort':
            self.sort.append(value[line])
            line += 1
        if key[line] == u'skill':
            self.skill = value[line]
            skill_file = filename[:filename.find(u'.')] + u'.lnk'
            if self.skill.find(u'redirect') != -1:
                try:
                    f = open(str(os.path.join(resDir, skill_file)), 'r')
                    forward_cfg = f.read()
                    f.close()
                    if forward_cfg != filename:
                        return self.loadLocal(forward_cfg, lItem)
                    return site
                except:
                    pass
            elif self.skill.find(u'store') != -1:
                f = open(str(os.path.join(resDir, skill_file)), 'w')
                f.write(filename)
                f.close()
            line += 1
        if key[line] == u'startRE':
            site.startRE = value[line]
            line += 1
        while line < length:
            breaker += 1
            while line < length and key[line].startswith(u'item'):
                breaker += 1
                if key[line] == u'item_infos':
                    rule_tmp = CRuleItem()
                    rule_tmp.infos = value[line]
                    line += 1
                if key[line] == u'item_order':
                    if value[line].find(u'|'):
                        rule_tmp.order = value[line].split(u'|')
                    else:
                        rule_tmp.order.append(value[line])
                    line += 1
                if key[line] == u'item_skill':
                    rule_tmp.skill = value[line]
                    line += 1
                if key[line] == u'item_curr':
                    rule_tmp.curr = value[line]
                    line += 1
                if key[line] == u'item_type':
                    rule_tmp.type = value[line]
                    line += 1
                while key[line].startswith(u'item_info_'):
                    breaker += 1
                    if key[line] == u'item_info_name':
                        info_tmp = CItemInfo()
                        info_tmp.name = value[line]
                        line += 1
                    if key[line] == u'item_info_from':
                        info_tmp.src = value[line]
                        line += 1
                    if key[line] == u'item_info':
                        info_tmp.rule = value[line]
                        line += 1
                    if key[line] == u'item_info_default':
                        info_tmp.default = value[line]
                        line += 1
                    if key[line] == u'item_info_build':
                        info_tmp.build = value[line]
                        rule_tmp.info_list.append(info_tmp)
                        line += 1
                    if breaker == length:
                        break
                if key[line] == u'item_infos_actions':
                    rule_tmp.actions = value[line].split(u'|') or [value[line]]
                    line += 1
                if key[line] == u'item_url_build':
                    rule_tmp.url_build = value[line]
                    site.rules.append(rule_tmp)
                    line += 1
            if breaker == length:
                break
            while line < length:
                breaker += 1
                if key[line] == u'title':
                    tmp = {}
                    tmp[u'title'] = value[line]
                    line += 1
                while line < length and key[line] != u'url':
                    if tmp:
                        if key[line] == u'mode':
                            tmp[key[line]] = int(value[line])
                        else:
                            tmp[key[line]] = value[line]
                        line += 1
                    else:
                        break
                if key[line] == u'url':
                    tmp[u'url'] = value[line]
                    if lItem != None:
                        inheritInfos(tmp, lItem)
                    if lItem[u'mode'] == Mode.START:
                        tmp[u'mode'] = Mode.VIEW_RSS
                    elif lItem[u'mode'] == Mode.VIEW_RSS:
                        if tmp[u'type'] == u'search':
                            tmp[u'mode'] = Mode.VIEW_SEARCH
                    elif lItem[u'mode'] == Mode.VIEW_SEARCH:
                        tmp[u'mode'] = Mode.VIEW_RSS
                    elif lItem[u'mode'] == Mode.VIEW_DIRECTORY:
                        tmp[u'mode'] = Mode.VIEW_RSS
                        tmp[u'type'] = u'rss'
                    elif lItem[u'mode'] == Mode.VIEWALL_RSS:
                        if tmp[u'type'] == u'search':
                            tmp[u'mode'] = Mode.VIEWALL_SEARCH
                    elif lItem[u'mode'] == Mode.VIEWALL_SEARCH:
                        tmp[u'mode'] = Mode.VIEWALL_RSS
                    site.links[tmp[u'type']] = (tmp, [tmp])
                    tmp = None
                    line += 1
                if line >= length or breaker == length:
                    break
        if breaker == length:
            site.status['syntax'] = 'Cfg syntax is invalid.\nKey error in line %s' % str(line)
        else:
            site.status['syntax'] = 'Cfg syntax is valid'
        return site

    def loadRemote(self, site, lItem):
        # Get HTML site
        try:
            if enable_debug:
                f = open(os.path.join(cacheDir, site.cfg + u'.page.html'), 'w')
                f.write(u'<Title>'+ site.start + u'</Title>\n\n')
            req = Request(site.start, None, site.txheaders)
            try:
                handle = urlopen(req)
                site.status['web_request'] = 'Successfully opened %s' % site.start
            except:
                site.status['web_request'] = 'Failed to open "%s"\r\nUrl is invalid' % site.start
                print('Failed to open "%s"\r\nUrl is invalid' % site.start)
                if enable_debug:
                    traceback.print_exc(file = sys.stdout)
                return
            data = handle.read()
            cj.save(os.path.join(settingsDir, 'cookies.lwp'))
            site.status['web_response'] = 'Successfully fetched'
            if enable_debug:
                f.write(data)
                f.close()
        except IOError:
            site.status['web_response'] = 'Failed to receive a response from ' % site.start
            print('Failed to receive a response from ' % site.start)
            if enable_debug:
                traceback.print_exc(file = sys.stdout)
            return
        # Create variables while loop
        interests = []
        interests2 = []
        if site.startRE:
            point = data.find(site.startRE.encode('utf-8'))
            if point == -1:
                print('startRe not found for %s' % site.cfg)
                point = 0
        else:
            point = 0
        length = len(data)
        # Append interests lists and modify rule RE patterns
        interestRE = re.compile(r'[-a-zA-Z0-9/,:;%!&$_#=~@<> ]+', re.IGNORECASE + re.DOTALL + re.MULTILINE)
        for item_rule in site.rules:
            item_rule.infos = item_rule.infos.encode('utf-8')
            if item_rule.curr:
                item_rule.curr = item_rule.curr.encode('utf-8')
            match = interestRE.match(item_rule.infos)
            if match:
                interests.append(match.group(0))
            else:
                print('RE pattern in ' +
                    site.cfg + 
                    'starts with a special character.\n RE pattern = \' ' +
                    item_rule.infos +
                    '\''
                    )
            if item_rule.curr:
                match = interestRE.match(item_rule.curr)
                if match:
                    interests2.append(match.group(0))
                else:
                    print('RE pattern in ' +
                        site.cfg + 
                        ' starts with a special character.\n RE pattern = \' ' +
                        item_rule.curr +
                        '\''
                    )
        # Combine interests list
        interests2.extend(interests)
        # Remove longer matches that may cause the while loop to shorter matches
        # i.e. remove '<img src' if '<img' is in the list
#        print('interests2 = ' + str(interests2))
        interesting_items = self.listFormatter(interests2)
#        print('interesting_items = ' + str(interesting_items))
        # Create interestingRE from interesting_items list
        interesting_pattern = '(' + '|'.join(interesting_items) + ')'
        interestingRE = re.compile(interesting_pattern, re.IGNORECASE + re.DOTALL + re.MULTILINE)
        # Create REs for while loop
        for item_rule in site.rules:
            match = interestingRE.match(item_rule.infos)
            if match:
                item_rule.infos = item_rule.infos[match.end():]
            item_rule.infosRE = re.compile(item_rule.infos, re.IGNORECASE + re.DOTALL + re.MULTILINE)
            if item_rule.curr:
                item_rule.currRE = re.compile(item_rule.curr, re.IGNORECASE + re.DOTALL + re.MULTILINE)
        # Find links
#        print('start point = ' + str(point))
#        print('start point datachunk = ' + data[point:point + 100])
        while point < length:
            interest = interestingRE.search(data, point)
            if interest:
                point = interest.start()
                intersting_point = interest.start()
                jump = len(interest.group(0))
#                print('point of interest = ' + str(point))
#                print('interesting point found = ' + interest.group(0))
                for index, rule_name in enumerate(interests):
                    item_rule = site.rules[index]
                    if rule_name.startswith(interest.group(0)):
#                        print('rule_name = ' + rule_name)
#                        print('datachunk = ' + data[point:point + 25])
#                        print('trying to match at datachunk = ' + data[point + jump:point + jump + 25])
#                        print('With rule pattern = ' + item_rule.infos)
                        match = item_rule.infosRE.match(data, point + jump)
                        if match:
#                            print('match found')
                            while match:
#                                print('match found = ' + match.group(0))
                                if not match.group(0):
                                    break
                                point += jump + len(match.group(0))
                                self.itemBuilder(site, item_rule, lItem, site.start, match)
                                match = item_rule.infosRE.match(data, point + jump)
                            break
                    if point == intersting_point and item_rule.curr and item_rule.curr.startswith(interest.group(0)):
                        match = item_rule.currRE.match(data, point)
                        if match:
                            while match:
                                if not match.group(0):
                                    break
                                point += len(match.group(0))
                                self.currBuilder(site, item_rule, lItem, site.start, match)
                                match = item_rule.currRE.match(data, point)
                            break
                if point == intersting_point:
                    point += 1
            else:
                log('Parsing complete')
                break
        return

    # Helper functions for loadRemote

    def itemBuilder(self, site, rule, lItem, url, match):
        tmp = {}
        tmp = self.loadDict(tmp, rule, url, match)
        tmp[u'type'] = rule.type
        if rule.type in site.items:
            for item in site.items[rule.type]:
                if tmp[u'url'] == item['url']:
                    tmp = None
                    return
        tmp = self.infoFormatter(tmp)
        try:
            if rule.skill.find(u'space') != -1:
                tmp[u'title'] = u'  ' + tmp[u'title'] + u'  '
            elif rule.skill.find(u'bottom') != -1:
                tmp[u'title'] = tmp[u'title'].strip()
        except:
            pass
        inheritInfos(tmp, lItem)
        if rule.skill.find(u'recursive') != -1:
            site.start = tmp[u'url']
            self.loadRemote(site, tmp)
            tmp = None
        else:
            if lItem[u'mode'] == Mode.VIEW_RSS:
                if tmp[u'type'] == u'video':
                    tmp[u'mode'] = Mode.PLAY
            elif lItem[u'mode'] == Mode.VIEW_SEARCH:
                if tmp[u'type'] == u'video':
                    tmp[u'mode'] = Mode.PLAY
                elif tmp[u'type'] == u'next':
                    tmp[u'mode'] = Mode.VIEW_RSS
                else:
                    tmp[u'mode'] = Mode.VIEW_DIRECTORY
            elif lItem[u'mode'] == Mode.VIEWALL_RSS:
                if tmp[u'type'] == u'video':
                    tmp[u'mode'] = Mode.PLAY
                elif tmp[u'type'] != u'next':
                    tmp[u'mode'] = Mode.VIEWALL_DIRECTORY
            elif lItem[u'mode'] == Mode.VIEWALL_SEARCH:
                if tmp[u'type'] == u'video':
                    tmp[u'mode'] = Mode.PLAY
                elif tmp[u'type'] == u'next':
                    tmp[u'mode'] = Mode.VIEWALL_RSS
                else:
                    tmp[u'mode'] = Mode.VIEWALL_DIRECTORY
            elif lItem[u'mode'] == Mode.VIEWALL_DIRECTORY:
                if tmp[u'type'] == u'video':
                    tmp[u'mode'] = Mode.PLAY
                else:
                    tmp[u'mode'] = Mode.VIEWALL_RSS
            if rule.type in site.items:
                site.items[rule.type] = (tmp, [tmp])
            else:
                tmp_infos = {u'type': rule.type}
                for info in rule.info_list:
                    if info.name == 'title':
                        tmp_infos['title'] = info.build
                    elif info.name == 'icon':
                        tmp_infos['icon'] = info.build
                inheritInfos(tmp_infos, lItem)
                site.items[rule.type] = (tmp_infos, [tmp])
        return

    def loadDict(self, item, rule, url, match):
        infos_names = rule.order
        infos_values = match.groups()
        for (infos_name, infos_value) in zip(infos_names, infos_values):
#            if infos_name.startswith(u'url') or infos_name.startswith(u'icon'):
#                item[infos_name] = smart_unicode(infos_value)
#            else:
#                item[infos_name] = clean_safe(infos_value)
            item[infos_name] = clean_safe(infos_value)
        for info in rule.info_list:
            info_value = u''
            if info.name in item:
                if info.build.find(u'%s') != -1:
                    item[info.name] = info.build % item[info.name]
                continue
            if info.rule != u'':
                info_rule = info.rule
                if info.rule.find(u'%s') != -1:
                    src = item[info.src]
                    info_rule = info.rule % src
                infosearch = re.search(info_rule, data)
                if infosearch:
                    info_value = infosearch.group(1).strip()
                    if info.build.find(u'%s') != -1:
                        info_value = info.build % info_value
                elif info.default != '':
                    info_value = info.default
            else:
                if info.build.find(u'%s') != -1:
                    src = item[info.src]
                    info_value = info.build % src
                else:
                    info_value = info.build
            item[info.name] = info_value
        if len(rule.actions) > 0:
            item = parseActions(item, rule.actions, url)
        item[u'url'] = rule.url_build % item[u'url']
        return item

    def infoFormatter(self, item):
        keep = {}
        for info_name, info_value in item.iteritems():
            if info_name == u'title':
                if info_value != u'':
                    try:
                        info_value = info_value.replace(u'\r\n', u'').replace(u'\n', u'').replace(u'\t', u'')
                        info_value = info_value.lstrip(u' -!@#$%^&*_-+=.,)\'<>;:"[{]}\|/?`~')
                        info_value = info_value.rstrip(u' -@#$%^&*_-+=.,<>;(:\'"[{]}\|/?`~')
                        info_value = info_value.split(u' ')
                        title = []
                        for word in info_value:
                            if word:
                                word = word.lower().capitalize()
                            title.append(word)
                        info_value = u' '.join(title).replace(u'  ', u' ')
                        info_value = u' ' + info_value + u' '
                    except:
                        info_value = u' ... '
                else:
                    info_value = u' ... '
            elif info_name == u'duration':
                if info_value[-2] == u';':
                    info_value = info_value.insert(-1, 0)
            elif info_name == u'icon':
                if info_value == u'':
                    info_value = os.path.join(imgDir, u'video.png')
            elif info_name.rfind(u'.tmp') != -1:
                continue
            keep[info_name] = info_value
        
        return keep

    def currBuilder(self, site, rule, lItem, url, match):
        title = clean_safe(match.group(1).strip())
        tmp = {}
        if rule.skill.find(u'space') != -1:
            tmp[u'title'] = u'   ' + title + u' (' + __language__(30106) + u')   '
        else:
            tmp[u'title'] = u'  ' + title + u' (' + __language__(30106) + u')  '
        tmp[u'url'] = url
        tmp[u'type'] = rule.type
#        for info in rule.info_list:
#            if info.name == u'title':
#                tmp[u'title'] = info.build
#            if info.name == u'icon':
#                tmp[u'icon'] = info.build
        inheritInfos(tmp, lItem)
        if lItem[u'mode'] == Mode.VIEW_RSS:
            if tmp[u'type'] == u'video':
                tmp[u'mode'] = Mode.PLAY
            elif tmp[u'type'] != u'next':
                tmp[u'mode'] = Mode.VIEW_DIRECTORY
        elif lItem[u'mode'] == Mode.VIEW_SEARCH:
            if tmp[u'type'] == u'video':
                tmp[u'mode'] = Mode.PLAY
            elif tmp[u'type'] == u'next':
                tmp[u'mode'] = Mode.VIEW_RSS
            else:
                tmp[u'mode'] = Mode.VIEW_DIRECTORY
        elif lItem[u'mode'] == Mode.VIEWALL_RSS:
            if tmp[u'type'] == u'video':
                tmp[u'mode'] = Mode.PLAY
            elif tmp[u'type'] != u'next':
                tmp[u'mode'] = Mode.VIEWALL_DIRECTORY
        elif lItem[u'mode'] == Mode.VIEWALL_SEARCH:
            if tmp[u'type'] == u'video':
                tmp[u'mode'] = Mode.PLAY
            elif tmp[u'type'] == u'next':
                tmp[u'mode'] = Mode.VIEWALL_RSS
            else:
                tmp[u'mode'] = Mode.VIEWALL_DIRECTORY
        elif lItem[u'mode'] == Mode.VIEWALL_DIRECTORY:
            tmp[u'mode'] = Mode.VIEWALL_RSS
        if rule.type in site.items:
            site.items[rule.type] = (tmp, [tmp])
        else:
            tmp_infos = {u'type': rule.type}
            for info in rule.info_list:
                if info.name == 'title':
                    tmp_infos['title'] = info.build
                elif info.name == 'icon':
                    tmp_infos['icon'] = info.build
            inheritInfos(tmp_infos, lItem)
            site.items[rule.type] = (tmp_infos, [tmp])
        return

    def listFormatter(self, List):
        list1 = set(List)
        list2 = []
        list3 = set(List)
        while len(list1) > 0:
            x = list1.pop()
            for y in list1:
                if x.startswith(y):
                    if y not in list2:
                        list2.append(y)
                elif y.startswith(x):
                    list2.append(x)
                    break
        for x in list3:
            if x not in list2:
                for z in list2:
                    if x.startswith(z):
                        break
                else:
                    list2.append(x)
        return list2

    # Helper functions for the class

    def addItem(self, name):
        item = self.getItem(name)
        del self.items[:]
        try:
            self.loadLocal('entry.list')
        except:
            del self.items[:]
        if item and not self.itemInLocalList(name):
            self.items.append(item)
            self.saveList(resDir, 'entry.list', self.items, u'Added sites and live streams', {skill : remove})
        return

    def getItem(self, name):
        item = None
        for root, dirs, files in os.walk(resDir):
            for listname in files:
                if getFileExtension(listname) == u'list' and listname != 'catcher.list':
                    item = self.getItemFromList(listname, name)
                if item != None:
                    return item
        return None

    def itemInLocalList(self, name):
        for item in self.items:
            if item[u'url'] == name:
                return True
        return False

    def getItemFromList(self, listname, name):
        self.loadLocal(listname)
        for item in self.items:
            if item[u'url'] == name:
                return item
        return None

    def removeItem(self, name):
        item = self.getItemFromList('entry.list', name)
        if item != None:
            self.items.remove(item)
            self.saveList(resDir, 'entry.list', self.items, u'Added sites and live streams', {skill : remove})
        return

class Main:
    def __init__(self):
        xbmc.log('Initializing VideoDevil')
        self.pDialog = None
        self.curr_file = ''
        self.handle = 0
        self.currentlist = None
        self.catcher = None
        xbmc.log('VideoDevil initialized')
        self.items = []
        self.links = CItemTypes()
        self.run()

    def playVideo(self, videoItem):
        print(videoItem)
        if videoItem[u'url'] == None:
            return
        print('playVideo url = ' + videoItem[u'url'])
        url = videoItem[u'url']
        if u'icon' not in videoItem:
            videoItem[u'icon'] = os.path.join(imgDir, 'video.png')
        if u'title' not in videoItem:
            videoItem[u'title'] = '...'
        try:
            urllib.urlretrieve(videoItem[u'icon'], os.path.join(cacheDir, 'thumb.tbn'))
            videoItem[u'icon'] = os.path.join(cacheDir, 'thumb.tbn')
        except:
            if enable_debug:
                traceback.print_exc(file = sys.stdout)
            videoItem[u'icon'] = os.path.join(imgDir, 'video.png')
        listitem = xbmcgui.ListItem(videoItem[u'title'], videoItem[u'title'], videoItem[u'icon'], videoItem[u'icon'])
        listitem.setInfo('video', {'Title': videoItem[u'title']})
        for info_name, info_value in videoItem.iteritems():
            try:
                listitem.setInfo(type = 'Video', infoLabels = {info_name: info_value})
            except:
                pass
        if self.catcher.skill.find(u'nodownload') == -1:
            if addon.getSetting('download') == 'true':
                videoItem[u'url'] = self.downloadMovie(videoItem)
            elif addon.getSetting('download') == 'false' and addon.getSetting('download_ask') == 'true':
                dia = xbmcgui.Dialog()
                if dia.yesno('', __language__(30052)):
                    videoItem[u'url'] = self.downloadMovie(videoItem)

        player_type = {
            0:xbmc.PLAYER_CORE_AUTO, 
            1:xbmc.PLAYER_CORE_MPLAYER, 
            2:xbmc.PLAYER_CORE_DVDPLAYER
        }
        player_type = player_type[int(addon.getSetting('player_type'))]
        if self.catcher.player == u'auto':
            player_type = xbmc.PLAYER_CORE_AUTO
        elif self.catcher.player == u'mplayer':
            player_type = xbmc.PLAYER_CORE_MPLAYER
        elif self.catcher.player == u'dvdplayer':
            player_type = xbmc.PLAYER_CORE_DVDPLAYER

        xbmc.Player(player_type).play(str(videoItem[u'url']), listitem)
        xbmc.sleep(200)

    def downloadMovie(self, videoItem):
        download_path = addon.getSetting('download_path')
        if download_path == u'':
            try:
                download_path = xbmcgui.Dialog().browse(0, __language__(30017), 'files', '', False, False)
                addon.setSetting(id='download_path', value=download_path)
                if not os.path.exists(download_path):
                    os.mkdir(download_path)
            except:
                pass
        tmp_file = tempfile.NamedTemporaryFile(suffix = self.catcher.videoExtension, dir=download_path)
        tmp_file = clean_filename(tmp_file.name)
        vidfile = clean_filename(download_path + clean_filename(videoItem[u'title']) + self.catcher.videoExtension)
        self.pDialog = xbmcgui.DialogProgress()
        self.pDialog.create('VideoDevil', __language__(30050), __language__(30051))
        urllib.urlretrieve(videoItem[u'url'], tmp_file, self.video_report_hook)
        self.pDialog.close()
        if not os.path.exists(tmp_file):
            dialog = xbmcgui.Dialog()
            dialog.ok('VideoDevil Info', __language__(30053))
        try:
            os.rename(tmp_file, vidfile)
            return vidfile
        except:
            return tmp_file

    def video_report_hook(self, count, blocksize, totalsize):
        percent = int(float(count * blocksize * 100) / totalsize)
        self.pDialog.update(percent, __language__(30050), __language__(30051))
        if self.pDialog.iscanceled():
            raise KeyboardInterrupt

    def parseView(self, url):
        result = 0
        lItem = self.decodeUrl(url)
        ext = getFileExtension(lItem[u'url'])
        if lItem[u'mode'] == Mode.PLAY or lItem[u'mode'] == Mode.DOWNLOAD:
            self.catcher = CCatcherList()
            lItem[u'url'] = self.catcher.getDirectLink(lItem)
            if lItem[u'mode'] == Mode.PLAY:
                result = self.playVideo(lItem)
            elif lItem[u'mode'] == Mode.DOWNLOAD:
                self.downloadMovie(lItem[u'url'], lItem[u'title'])
        elif lItem[u'mode'] == Mode.ADD:
            self.addItem(lItem[u'url'][:-4], lItem)
            result = -2
        elif lItem[u'mode'] == Mode.REMOVE:
            dia = xbmcgui.Dialog()
            if dia.yesno('', __language__(30054)):
                self.removeItem(lItem[u'url'][:-7])
                xbmc.executebuiltin(u'Container.Refresh')
            result = -2
        else:
            #loadLocal
            self.currentlist = CCurrentList()
            print('Loading Local Files')
            if lItem[u'mode'] == Mode.VIEW_RSS or lItem[u'mode'] == Mode.VIEW_SEARCH:
                if ext == u'cfg':
                    List = self.currentlist.loadLocal(lItem[u'url'], lItem)
                else:
                    List = self.currentlist.loadLocal(lItem[u'cfg'], lItem)
                    if lItem[u'type'] == u'search':
                        lItem[u'url'] = lItem[u'url'] % getSearchPhrase()
                    List.start = lItem[u'url']
                self.currentlist.sites.append((List, lItem))
            elif lItem[u'mode'] == Mode.VIEW_DIRECTORY or lItem[u'mode'] == Mode.START:
                List = self.currentlist.loadLocal(lItem[u'url'], lItem)
            elif lItem[u'mode'] == Mode.VIEWALL_SEARCH:
                search_phrase = getSearchPhrase()
                List = self.currentlist.loadLocal(lItem[u'url'], lItem)
                for type, infos, items in List.links.files():
                    for item in items:
                        item[u'type'] = u'rss'
                        site = self.currentlist.loadLocal(item[u'cfg'], item)
                        site.start = item[u'url'] % search_phrase
                        print('site.start = ' + site.start)
                        self.currentlist.sites.append((site, item))
            else:
                List = self.currentlist.loadLocal(lItem[u'url'], lItem)
                if lItem[u'mode'] == Mode.VIEWALL_RSS:
                    if lItem[u'url'] == u'sites.list':
                        for type, infos, items in List.links.files():
                            for item in items:
                                site = self.currentlist.loadLocal(item[u'url'], item)
                                self.currentlist.sites.append((site, item))
                    else:
                        for type, infos, items in List.links.files():
                            for item in items:
                                site = self.currentlist.loadLocal(item[u'cfg'], item)
                                site.start = item[u'url']
                                self.currentlist.sites.append((site, item))
                elif lItem[u'mode'] == Mode.VIEWALL_DIRECTORY:
                    for type, infos, items in List.links.files():
                        for item in items:
                            if item[u'mode'] == Mode.VIEWALL_DIRECTORY:
                                print(item[u'mode'])
                                item[u'mode'] = Mode.VIEWALL_RSS
                                self.currentlist.items[type] = (infos, [item])
                            else:
                                site = self.currentlist.loadLocal(item[u'cfg'], item)
                                site.start = item[u'url']
                                self.currentlist.sites.append((site, item))
            #loadRemote
            print('Parsing Websites')
            if self.currentlist.sites == []:
                print('No further sites to parse')
            elif len(self.currentlist.sites) == 1:
                self.currentlist.loadRemote(self.currentlist.sites[0][0], self.currentlist.sites[0][1])
            else:
                run_parallel_in_threads(self.currentlist.loadRemote, self.currentlist.sites)
            #Combine item lists
            print('Gathering Items')
            if lItem[u'mode'] == Mode.VIEW_RSS or lItem[u'mode'] == Mode.VIEW_SEARCH or lItem[u'mode'] == Mode.VIEWALL_RSS or lItem[u'mode'] == Mode.VIEWALL_SEARCH:
                for (site, item) in self.currentlist.sites:
                    for type, infos, items in site.items.files():
                        self.currentlist.items[type] = (infos, items)
                    for type, infos, items in site.links.files():
                        self.currentlist.links[type] = (infos, items)
            elif lItem[u'mode'] == Mode.VIEW_DIRECTORY or lItem[u'mode'] == Mode.START:
                for type, infos, items in List.links.files():
                    self.currentlist.items[type] = (infos, items)
            elif lItem[u'mode'] == Mode.VIEWALL_DIRECTORY:
                for (site, item) in self.currentlist.sites:
                    for type, infos, items in site.items.files():
                        self.currentlist.items[type] = (infos, items)
            sort_dict = {
                u'label' : xbmcplugin.SORT_METHOD_LABEL, 
                u'size' : xbmcplugin.SORT_METHOD_SIZE, 
                u'duration' : xbmcplugin.SORT_METHOD_DURATION, 
                u'genre' : xbmcplugin.SORT_METHOD_GENRE, 
                u'rating' : xbmcplugin.SORT_METHOD_VIDEO_RATING, 
                u'date' : xbmcplugin.SORT_METHOD_DATE
            }
            for sort_method in self.currentlist.sort:
                xbmcplugin.addSortMethod(handle = self.handle, sortMethod = sort_dict[sort_method])
            if self.currentlist.skill.find(u'play') != -1 and self.currentlist.videoCount() == 1:
                result = self.parseView(self.currentlist.getVideo())
            else:
                cmp = lItem[u'mode'] == Mode.VIEW_RSS or lItem[u'mode'] == Mode.VIEW_SEARCH
                cmp2 = lItem[u'mode'] == Mode.VIEWALL_RSS or lItem[u'mode'] == Mode.VIEWALL_SEARCH
                if cmp or cmp2:
                    print(self.currentlist.items.types)
                    print(self.currentlist.links.types)
                    try:
                        totalItems = len(self.currentlist.items[u'video']) + len(self.currentlist.items) + len(self.currentlist.links) - 1
                    except:
                        try:
                            totalItems = len(self.currentlist.items[lItem[u'type']]) + len(self.currentlist.items) + len(self.currentlist.links) - 1
                            if lItem[u'type'] in self.currentlist.items:
                                totalItems -= 1
                        except:
                            totalItems = len(self.currentlist.items) + len(self.currentlist.links)
                    print(totalItems)
                    for type, infos, items in self.currentlist.items.files():
                        if type == u'video':
                            self.addListItems(items, totalItems)
                        elif type == u'next' and cmp:
                            self.addListItems(items, totalItems)
                        elif type == lItem[u'type'] and cmp:
                            self.addListItems(items, totalItems)
                        else:
                            filename = clean_filename(infos[u'title'].strip(u' ') + u'.list')
                            self.saveList(cacheDir, filename, items, Listname = infos[u'title'].strip(u' '))
                            tmp = {
                                u'title': infos[u'title'],
                                u'url': filename,
                                u'type': infos[u'type'],
                                u'icon': infos[u'icon']
                            }
#                            if tmp[u'type'] == u'search':
#                                tmp[u'mode'] = Mode.VIEWALL_SEARCH
                            if tmp[u'type'] == u'next':
                                tmp[u'mode'] = Mode.VIEWALL_RSS
                            elif cmp:
                                tmp[u'mode'] = Mode.VIEW_DIRECTORY
                            else:
                                tmp[u'mode'] = Mode.VIEWALL_DIRECTORY
                            inheritInfos(tmp, lItem)
                            print(tmp)
                            self.addListItem(tmp, totalItems)
                    if cmp:
                        for type, infos, items in self.currentlist.links.files():
                            if type not in self.currentlist.items:
                                self.addListItems(items, totalItems)
                    else:
                        for type, infos, items in self.currentlist.links.files():
                            filename = clean_filename(infos[u'title'].strip(u' ') + u'.list')
                            self.saveList(cacheDir, filename, items, Listname = infos[u'title'].strip(u' '), mode = 'a')
                            if type not in self.currentlist.items:
                                tmp = {
                                    u'title': infos[u'title'],
                                    u'url': filename,
                                    u'type': infos[u'type'],
                                    u'icon': infos[u'icon'],
                                }
                                print(tmp)
                                if tmp[u'type'] == u'search':
                                    tmp[u'mode'] = Mode.VIEWALL_SEARCH
                                else:
                                    tmp[u'mode'] = Mode.VIEWALL_DIRECTORY
                                print(tmp)
                                inheritInfos(tmp, lItem)
                                self.addListItem(tmp, totalItems)
                elif lItem[u'mode'] == Mode.VIEW_DIRECTORY or lItem[u'mode'] == Mode.START:
                    totalItems = 0
                    print(totalItems)
                    if lItem[u'mode'] == Mode.START:
                        totalItems += 1
                        print(totalItems)
                        tmp = {
                            u'title': u' All Sites',
                            u'mode': str(Mode.VIEWALL_RSS),
                            u'icon': os.path.join(imgDir, u'face_devil_grin.png'),
                            u'director': u'VideoDevil',
                            u'url': u'sites.list',
                            u'type': u'rss'
                        }
                        inheritInfos(tmp, lItem)
                        self.addListItem(tmp, totalItems)
                    for type, infos, items in self.currentlist.items.files():
                        totalItems += len(self.currentlist.items[type])
                        print(totalItems)
                        self.addListItems(items, totalItems)
                elif lItem[u'mode'] == Mode.VIEWALL_DIRECTORY:
                    self.createDirs(self.currentlist.items[lItem[u'type']])
                    totalItems = len(self.links)
                    for item_title, infos, item_value in self.links.files():
                        filename = clean_filename(lItem[u'title'].strip() + u'.' + item_title.strip() + u'.list')
                        self.saveList(cacheDir, filename, item_value, Listname = item_title.strip())
                        tmp = {
                            u'title': capitalize(item_title),
                            u'type': u'rss',
                            u'icon': infos[u'icon'],
                            u'url': filename,
                            u'mode': str(Mode.VIEWALL_RSS)
                        }
                        inheritInfos(tmp, lItem)
                        self.addListItem(tmp, totalItems)
        return result

    def addListItems(self, items, totalItems):
        for item in items:
            self.addListItem(item, totalItems)
        return None

    def addListItem(self, item, totalItems):
        if item[u'type'] != u'once':
            url = sys.argv[0] + '?' + self.codeUrl(item)
            liz = xbmcgui.ListItem(item[u'title'], item[u'title'], item[u'icon'], item[u'icon'])
            if item[u'type'] == u'video' and self.currentlist.skill.find(u'nodownload') == -1:
                action = 'XBMC.RunPlugin(%s)' % url.replace('mode=' + str(Mode.PLAY), 'mode=' + str(Mode.DOWNLOAD))
                try:
                    liz.addContextMenuItems([(__language__(30007), action)])
                except:
                    pass
            if self.currentlist.skill.find(u'add') != -1:
                action = 'XBMC.RunPlugin(%s)' % url.replace('mode=' + str(Mode.play), 'mode=' + str(Mode.ADD))
                try:
                    liz.addContextMenuItems([(__language__(30010), action)])
                except:
                    pass
            elif self.currentlist.skill.find(u'remove') != -1:
                action = 'XBMC.RunPlugin(%s.remove)' % url.replace('mode=' + str(Mode.play), 'mode=' + str(Mode.ADD))
                try:
                    liz.addContextMenuItems([(__language__(30011), action)])
                except:
                    pass
            for info_name, info_value in item.iteritems():
                if info_name.startswith(u'context.'):
                    try:
                        cItem = {}
                        cItem[u'url'] = info_value
                        cItem[u'type'] = u'rss'
                        inheritInfos(cItem, item)
                        action = 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?' + self.codeUrl(cItem))
                        liz.addContextMenuItems([(info_name[8:], action)])
                    except:
                        pass
                elif info_name != u'url' and info_name != u'title' and info_name != u'icon' and info_name != u'type' and info_name != u'extension':
                    try:
                        if info_name.rfind(u'.int') != -1:
                            liz.setInfo('Video', infoLabels = {capitalize(info_name[:-4]): int(info_value)})
                        elif info_name.rfind(u'.once') != -1:
                            liz.setInfo('Video', infoLabels = {capitalize(info_name[:-5]): info_value})
                        else:
                            liz.setInfo('Video', infoLabels = {capitalize(info_name): info_value})
                    except:
                        pass
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, liz, True, totalItems)
        return None

    def codeUrl(self, item):
        # in Frodo url parameters need to be encoded
        # ignore characters that can't be converted to ascii
        #this is added for handling the stupid &nbsp;
        params = []
        for info_name, info_value in item.iteritems():
            if info_name.find(u'.once') == -1 and info_name != u'mode':
                if info_name == u'url':
                    info_value.replace(u'\xa0', u' ')
                info_name = info_name.encode('utf-8')
                info_value = info_value.encode('utf-8')
                try:
                    params.append(info_name + '=' + info_value.replace('&', '%26'))
                except KeyError:
                    xbmc.log('Skipping %s probably has unicode' % info_value.encode('utf-8'))
        params.append('mode=' + str(item[u'mode']))
        tmp_attr = '&'.join(params)
#        print(tmp_attr)
        return tmp_attr

    def decodeUrl(self, url):
        item = {}
        if url.find('&') == -1:
            item[u'url'] = urllib.unquote(url)
            item[u'type'] = u'start'
            item[u'mode'] = Mode.START
        else:
            for info_name_value in url.split('&'):
                info_name, info_value = info_name_value.split('=')
                item[smart_unicode(info_name)] = smart_unicode(urllib.unquote(info_value))
            item[u'mode'] = int(item[u'mode'])
        return item

    def saveList(self, directory, filename, items, Listname, List_dict = None, mode = 'w'):
        f = open(str(os.path.join(directory, filename)), mode)
        Listname = u'#' + Listname.center(54) + u'#\n'
        f.write(u'########################################################\n')
        f.write(Listname)
        f.write(u'########################################################\n')
        if List_dict != None:
            for info_name, info_value in List_dict.iteritems():
                f.write(info_name + u'=' + info_value + u'\n')
            f.write(u'########################################################\n')
        for item in items:
            try:
                f.write(u'title=' + item[u'title'] + u'\n')
            except:
                f.write(u'title=...\n')
            for info_name, info_value in item.iteritems():
                if info_name != u'url' and info_name != u'title':
                    if info_name == u'mode':
                        f.write(info_name + u'=' + str(info_value) + u'\n')
                    else:
                        f.write(info_name + u'=' + info_value + u'\n')
            f.write(u'url=' + item[u'url'] + u'\n')
            f.write(u'########################################################\n')
        f.close()
        return

    def createDirs(self, List):
        keys = []
        Dict = {}
        for item in List:
            keys.append(item[u'title'])
        for i in range(len(keys)):
            key = keys.pop().lower().strip()
            value = List.pop()
            if key in Dict:
                Dict[key].append(value)
            else:
                Dict[key] = [value]

        keys1 = sorted(Dict.keys())
        keys1.reverse()
        keys2 = sorted(Dict.keys())
        keys2.reverse()
        while len(keys1)> 0:
            key1 = keys1.pop()
            for key2 in keys2:
                if key1 != key2:
                    if key2.startswith(key1):
                        if key1 not in self.links:
                            self.links[key1] = (Dict[key1][0], Dict[key1])
                        self.links[key1] = (Dict[key2][0], Dict[key2])
                        keys1.remove(key2)
        return None

    def purgeCache(self):
        for root, dirs, files in os.walk(cacheDir , topdown = False):
            for name in files:
                os.remove(os.path.join(root, name))

    def run(self):
        xbmc.log('VideoDevil running')
        print('sys.argv = ' + str(sys.argv))
        try:
            self.handle = int(sys.argv[1])
            paramstring = sys.argv[2]
            if len(paramstring) <= 2:
                if addon.getSetting('hide_warning') == 'false':
                    dialog = xbmcgui.Dialog()
                    if not dialog.yesno(__language__(30061), __language__(30062), __language__(30063), __language__(30064), __language__(30065), __language__(30066)):
                        return
                log(
                    'Settings directory: ' + str(settingsDir) + '\n' +
                    'Cache directory: ' + str(cacheDir) + '\n' +
                    'Resource directory: ' + str(resDir) + '\n' +
                    'Image directory: ' + str(imgDir) + '\n' +
                    'Catchers directory: ' + str(catDir)
                )
                if not os.path.exists(settingsDir):
                    log('Creating settings directory ' + str(settingsDir))
                    os.mkdir(settingsDir)
                    log('Settings directory created')
                if not os.path.exists(cacheDir):
                    log('Creating cache directory ' + str(cacheDir))
                    os.mkdir(cacheDir)
                    log('Cache directory created')
                log('Purging cache directory')
                self.purgeCache()
                log('Cache directory purged')
                self.parseView('sites.list')
#                if xbmcplugin.getSetting('custom_entry') == 'false':
#                    self.parseView('sites.list')
#                    del self.currentlist.items[:]
#                self.parseView('entry')
                xbmc.log('End of directory')
                xbmcplugin.endOfDirectory(handle = int(sys.argv[1]))
            else:
                params = sys.argv[2]
                currentView = params[1:]
                log(
                    'currentView: ' +
                     urllib2.unquote(repr(currentView).replace('&', '\n')))
                if self.parseView(currentView) == 0:
                    xbmcplugin.endOfDirectory(int(sys.argv[1]))
                    xbmc.log('End of directory')
        except Exception, e:
            if enable_debug:
                traceback.print_exc(file = sys.stdout)
            dialog = xbmcgui.Dialog()
            dialog.ok('VideoDevil Error', 'Error running VideoDevil.\n\nReason:\n' + str(e))