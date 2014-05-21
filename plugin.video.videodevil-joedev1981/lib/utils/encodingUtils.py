# -*- coding: latin-1 -*-

import sys, traceback
import re
import htmlentitydefs

from lib.common import smart_unicode

enable_debug = sys.modules["__main__"].enable_debug

name2unicode = {u'apos;': u"'"}
for key in htmlentitydefs.name2codepoint.keys():
    entity = key.lower() + u';'
    name2unicode[entity] = unichr(htmlentitydefs.name2codepoint[key])

entitydefs = {
    u'AElig':    u'\u00C6', # latin capital letter AE = latin capital ligature AE, U+00C6 ISOlat1'
    u'Aacute':   u'\u00C1', # latin capital letter A with acute, U+00C1 ISOlat1'
    u'Acirc':    u'\u00C2', # latin capital letter A with circumflex, U+00C2 ISOlat1'
    u'Agrave':   u'\u00C0', # latin capital letter A with grave = latin capital letter A grave, U+00C0 ISOlat1'
    u'Alpha':    u'\u0391', # greek capital letter alpha, U+0391'
    u'Aring':    u'\u00C5', # latin capital letter A with ring above = latin capital letter A ring, U+00C5 ISOlat1'
    u'Atilde':   u'\u00C3', # latin capital letter A with tilde, U+00C3 ISOlat1'
    u'Auml':     u'\u00C4', # latin capital letter A with diaeresis, U+00C4 ISOlat1'
    u'Beta':     u'\u0392', # greek capital letter beta, U+0392'
    u'Ccedil':   u'\u00C7', # latin capital letter C with cedilla, U+00C7 ISOlat1'
    u'Chi':      u'\u03A7', # greek capital letter chi, U+03A7'
    u'Dagger':   u'\u2021', # double dagger, U+2021 ISOpub'
    u'Delta':    u'\u0394', # greek capital letter delta, U+0394 ISOgrk3'
    u'ETH':      u'\u00D0', # latin capital letter ETH, U+00D0 ISOlat1'
    u'Eacute':   u'\u00C9', # latin capital letter E with acute, U+00C9 ISOlat1'
    u'Ecirc':    u'\u00CA', # latin capital letter E with circumflex, U+00CA ISOlat1'
    u'Egrave':   u'\u00C8', # latin capital letter E with grave, U+00C8 ISOlat1'
    u'Epsilon':  u'\u0395', # grek capital letter epsilon, U+0395'
    u'Eta':      u'\u0397', # greek capital letter eta, U+0397'
    u'Euml':     u'\u00CB', # latin capital letter E with diaeresis, U+00CB ISOlat1'
    u'Gamma':    u'\u0393', # greek capital letter gamma, U+0393 ISOgrk3'
    u'Iacute':   u'\u00CD', # latin capital letter I with acute, U+00CD ISOlat1'
    u'Icirc':    u'\u00CE', # latin capital letter I with circumflex, U+00CE ISOlat1'
    u'Igrave':   u'\u00CC', # latin capital letter I with grave, U+00CC ISOlat1'
    u'Iota':     u'\u0399', # greek capital letter iota, U+0399'
    u'Iuml':     u'\u00CF', # latin capital letter I with diaeresis, U+00CF ISOlat1'
    u'Kappa':    u'\u039A', # greek capital letter kappa, U+039A'
    u'Lambda':   u'\u039B', # greek capital letter lambda, U+039B ISOgrk3'
    u'Mu':       u'\u039C', # greek capital letter mu, U+039C'
    u'Ntilde':   u'\u00D1', # latin capital letter N with tilde, U+00D1 ISOlat1'
    u'Nu':       u'\u039D', # greek capital letter nu, U+039D'
    u'OElig':    u'\u0152', # latin capital ligature OE, U+0152 ISOlat2'
    u'Oacute':   u'\u00D3', # latin capital letter O with acute, U+00D3 ISOlat1'
    u'Ocirc':    u'\u00D4', # latin capital letter O with circumflex, U+00D4 ISOlat1'
    u'Ograve':   u'\u00D2', # latin capital letter O with grave, U+00D2 ISOlat1'
    u'Omega':    u'\u03A9', # greek capital letter omega, U+03A9 ISOgrk3'
    u'Omicron':  u'\u039F', # greek capital letter omicron, U+039F'
    u'Oslash':   u'\u00D8', # latin capital letter O with stroke = latin capital letter O slash, U+00D8 ISOlat1'
    u'Otilde':   u'\u00D5', # latin capital letter O with tilde, U+00D5 ISOlat1'
    u'Ouml':     u'\u00D6', # latin capital letter O with diaeresis, U+00D6 ISOlat1'
    u'Phi':      u'\u03A6', # greek capital letter phi, U+03A6 ISOgrk3'
    u'Pi':       u'\u03A0', # greek capital letter pi, U+03A0 ISOgrk3'
    u'Prime':    u'\u2033', # double prime = seconds = inches, U+2033 ISOtech'
    u'Psi':      u'\u03A8', # greek capital letter psi, U+03A8 ISOgrk3'
    u'Rho':      u'\u03A1', # greek capital letter rho, U+03A1'
    u'Scaron':   u'\u0160', # latin capital letter S with caron, U+0160 ISOlat2'
    u'Sigma':    u'\u03A3', # greek capital letter sigma, U+03A3 ISOgrk3'
    u'THORN':    u'\u00DE', # latin capital letter THORN, U+00DE ISOlat1'
    u'Tau':      u'\u03A4', # greek capital letter tau, U+03A4'
    u'Theta':    u'\u0398', # greek capital letter theta, U+0398 ISOgrk3'
    u'Uacute':   u'\u00DA', # latin capital letter U with acute, U+00DA ISOlat1'
    u'Ucirc':    u'\u00DB', # latin capital letter U with circumflex, U+00DB ISOlat1'
    u'Ugrave':   u'\u00D9', # latin capital letter U with grave, U+00D9 ISOlat1'
    u'Upsilon':  u'\u03A5', # greek capital letter upsilon, U+03A5 ISOgrk3'
    u'Uuml':     u'\u00DC', # latin capital letter U with diaeresis, U+00DC ISOlat1'
    u'Xi':       u'\u039E', # greek capital letter xi, U+039E ISOgrk3'
    u'Yacute':   u'\u00DD', # latin capital letter Y with acute, U+00DD ISOlat1'
    u'Yuml':     u'\u0178', # latin capital letter Y with diaeresis, U+0178 ISOlat2'
    u'Zeta':     u'\u0396', # greek capital letter zeta, U+0396'
    u'aacute':   u'\u00E1', # latin small letter a with acute, U+00E1 ISOlat1'
    u'acirc':    u'\u00E2', # latin small letter a with circumflex, U+00E2 ISOlat1'
    u'acute':    u'\u00B4', # acute accent = spacing acute, U+00B4 ISOdia'
    u'aelig':    u'\u00E6', # latin small letter ae = latin small ligature ae, U+00E6 ISOlat1'
    u'agrave':   u'\u00E0', # latin small letter a with grave = latin small letter a grave, U+00E0 ISOlat1'
    u'alefsym':  u'\u2135', # alef symbol = first transfinite cardinal, U+2135 NEW'
    u'alpha':    u'\u03B1', # greek small letter alpha, U+03B1 ISOgrk3'
    u'amp':      u'\u0026', # ampersand, U+0026 ISOnum'
    u'and':      u'\u2227', # logical and = wedge, U+2227 ISOtech'
    u'ang':      u'\u2220', # angle, U+2220 ISOamso'
    u'aring':    u'\u00E5', # latin small letter a with ring above = latin small letter a ring, U+00E5 ISOlat1'
    u'asymp':    u'\u2248', # almost equal to = asymptotic to, U+2248 ISOamsr'
    u'atilde':   u'\u00E3', # latin small letter a with tilde, U+00E3 ISOlat1'
    u'auml':     u'\u00E4', # latin small letter a with diaeresis, U+00E4 ISOlat1'
    u'bdquo':    u'\u201E', # double low-9 quotation mark, U+201E NEW'
    u'beta':     u'\u03B2', # greek small letter beta, U+03B2 ISOgrk3'
    u'brvbar':   u'\u00A6', # broken bar = broken vertical bar, U+00A6 ISOnum'
    u'bull':     u'\u2022', # bullet = black small circle, U+2022 ISOpub'
    u'cap':      u'\u2229', # intersection = cap, U+2229 ISOtech'
    u'ccedil':   u'\u00E7', # latin small letter c with cedilla, U+00E7 ISOlat1'
    u'cedil':    u'\u00B8', # cedilla = spacing cedilla, U+00B8 ISOdia'
    u'cent':     u'\u00A2', # cent sign, U+00A2 ISOnum'
    u'chi':      u'\u03C7', # greek small letter chi, U+03C7 ISOgrk3'
    u'circ':     u'\u02C6', # modifier letter circumflex accent, U+02C6 ISOpub'
    u'clubs':    u'\u2663', # black club suit = shamrock, U+2663 ISOpub'
    u'cong':     u'\u2245', # approximately equal to, U+2245 ISOtech'
    u'copy':     u'\u00A9', # copyright sign, U+00A9 ISOnum'
    u'crarr':    u'\u21B5', # downwards arrow with corner leftwards = carriage return, U+21B5 NEW'
    u'cup':      u'\u222A', # union = cup, U+222A ISOtech'
    u'curren':   u'\u00A4', # currency sign, U+00A4 ISOnum'
    u'dArr':     u'\u21D3', # downwards double arrow, U+21D3 ISOamsa'
    u'dagger':   u'\u2020', # dagger, U+2020 ISOpub'
    u'darr':     u'\u2193', # downwards arrow, U+2193 ISOnum'
    u'deg':      u'\u00B0', # degree sign, U+00B0 ISOnum'
    u'delta':    u'\u03B4', # greek small letter delta, U+03B4 ISOgrk3'
    u'diams':    u'\u2666', # black diamond suit, U+2666 ISOpub'
    u'divide':   u'\u00F7', # division sign, U+00F7 ISOnum'
    u'eacute':   u'\u00E9', # latin small letter e with acute, U+00E9 ISOlat1'
    u'ecirc':    u'\u00EA', # latin small letter e with circumflex, U+00EA ISOlat1'
    u'egrave':   u'\u00E8', # latin small letter e with grave, U+00E8 ISOlat1'
    u'empty':    u'\u2205', # empty set = null set = diameter, U+2205 ISOamso'
    u'emsp':     u'\u2003', # em space, U+2003 ISOpub'
    u'ensp':     u'\u2002', # en space, U+2002 ISOpub'
    u'epsilon':  u'\u03B5', # greek small letter epsilon, U+03B5 ISOgrk3'
    u'equiv':    u'\u2261', # identical to, U+2261 ISOtech'
    u'eta':      u'\u03B7', # greek small letter eta, U+03B7 ISOgrk3'
    u'eth':      u'\u00F0', # latin small letter eth, U+00F0 ISOlat1'
    u'euml':     u'\u00EB', # latin small letter e with diaeresis, U+00EB ISOlat1'
    u'euro':     u'\u20AC', # euro sign, U+20AC NEW'
    u'exist':    u'\u2203', # there exists, U+2203 ISOtech'
    u'fnof':     u'\u0192', # latin small f with hook = function = florin, U+0192 ISOtech'
    u'forall':   u'\u2200', # for all, U+2200 ISOtech'
    u'frac12':   u'\u00BD', # vulgar fraction one half = fraction one half, U+00BD ISOnum'
    u'frac14':   u'\u00BC', # vulgar fraction one quarter = fraction one quarter, U+00BC ISOnum'
    u'frac34':   u'\u00BE', # vulgar fraction three quarters = fraction three quarters, U+00BE ISOnum'
    u'frasl':    u'\u2044', # fraction slash, U+2044 NEW'
    u'gamma':    u'\u03B3', # greek small letter gamma, U+03B3 ISOgrk3'
    u'ge':       u'\u2265', # greater-than or equal to, U+2265 ISOtech'
    u'gt':       u'\u003E', # greater-than sign, U+003E ISOnum'
    u'hArr':     u'\u21D4', # left right double arrow, U+21D4 ISOamsa'
    u'harr':     u'\u2194', # left right arrow, U+2194 ISOamsa'
    u'hearts':   u'\u2665', # black heart suit = valentine, U+2665 ISOpub'
    u'hellip':   u'\u2026', # horizontal ellipsis = three dot leader, U+2026 ISOpub'
    u'iacute':   u'\u00ED', # latin small letter i with acute, U+00ED ISOlat1'
    u'icirc':    u'\u00EE', # latin small letter i with circumflex, U+00EE ISOlat1'
    u'iexcl':    u'\u00A1', # inverted exclamation mark, U+00A1 ISOnum'
    u'igrave':   u'\u00EC', # latin small letter i with grave, U+00EC ISOlat1'
    u'image':    u'\u2111', # blackletter capital I = imaginary part, U+2111 ISOamso'
    u'infin':    u'\u221E', # infinity, U+221E ISOtech'
    u'int':      u'\u222B', # integral, U+222B ISOtech'
    u'iota':     u'\u03B9', # greek small letter iota, U+03B9 ISOgrk3'
    u'iquest':   u'\u00BF', # inverted question mark = turned question mark, U+00BF ISOnum'
    u'isin':     u'\u2208', # element of, U+2208 ISOtech'
    u'iuml':     u'\u00EF', # latin small letter i with diaeresis, U+00EF ISOlat1'
    u'kappa':    u'\u03BA', # greek small letter kappa, U+03BA ISOgrk3'
    u'lArr':     u'\u21D0', # leftwards double arrow, U+21D0 ISOtech'
    u'lambda':   u'\u03BB', # greek small letter lambda, U+03BB ISOgrk3'
    u'lang':     u'\u2329', # left-pointing angle bracket = bra, U+2329 ISOtech'
    u'laquo':    u'\u00AB', # left-pointing double angle quotation mark = left pointing guillemet, U+00AB ISOnum'
    u'larr':     u'\u2190', # leftwards arrow, U+2190 ISOnum'
    u'lceil':    u'\u2308', # left ceiling = apl upstile, U+2308 ISOamsc'
    u'ldquo':    u'\u201C', # left double quotation mark, U+201C ISOnum'
    u'le':       u'\u2264', # less-than or equal to, U+2264 ISOtech'
    u'lfloor':   u'\u230A', # left floor = apl downstile, U+230A ISOamsc'
    u'lowast':   u'\u2217', # asterisk operator, U+2217 ISOtech'
    u'loz':      u'\u25CA', # lozenge, U+25CA ISOpub'
    u'lrm':      u'\u200E', # left-to-right mark, U+200E NEW RFC 2070'
    u'lsaquo':   u'\u2039', # single left-pointing angle quotation mark, U+2039 ISO proposed'
    u'lsquo':    u'\u2018', # left single quotation mark, U+2018 ISOnum'
    u'lt':       u'\u003C', # less-than sign, U+003C ISOnum'
    u'macr':     u'\u00AF', # macron = spacing macron = overline = APL overbar, U+00AF ISOdia'
    u'mdash':    u'\u2014', # em dash, U+2014 ISOpub'
    u'micro':    u'\u00B5', # micro sign, U+00B5 ISOnum'
    u'middot':   u'\u00B7', # middle dot = Georgian comma = Greek middle dot, U+00B7 ISOnum'
    u'minus':    u'\u2212', # minus sign, U+2212 ISOtech'
    u'mu':       u'\u03BC', # greek small letter mu, U+03BC ISOgrk3'
    u'nabla':    u'\u2207', # nabla = backward difference, U+2207 ISOtech'
    u'nbsp':     u'\u00A0', # no-break space = non-breaking space, U+00A0 ISOnum'
    u'ndash':    u'\u2013', # en dash, U+2013 ISOpub'
    u'ne':       u'\u2260', # not equal to, U+2260 ISOtech'
    u'ni':       u'\u220B', # contains as member, U+220B ISOtech'
    u'not':      u'\u00AC', # not sign, U+00AC ISOnum'
    u'notin':    u'\u2209', # not an element of, U+2209 ISOtech'
    u'nsub':     u'\u2284', # not a subset of, U+2284 ISOamsn'
    u'ntilde':   u'\u00F1', # latin small letter n with tilde, U+00F1 ISOlat1'
    u'nu':       u'\u03BD', # greek small letter nu, U+03BD ISOgrk3'
    u'oacute':   u'\u00F3', # latin small letter o with acute, U+00F3 ISOlat1'
    u'ocirc':    u'\u00F4', # latin small letter o with circumflex, U+00F4 ISOlat1'
    u'oelig':    u'\u0153', # latin small ligature oe, U+0153 ISOlat2'
    u'ograve':   u'\u00F2', # latin small letter o with grave, U+00F2 ISOlat1'
    u'oline':    u'\u203E', # overline = spacing overscore, U+203E NEW'
    u'omega':    u'\u03C9', # greek small letter omega, U+03C9 ISOgrk3'
    u'omicron':  u'\u03BF', # greek small letter omicron, U+03BF NEW'
    u'oplus':    u'\u2295', # circled plus = direct sum, U+2295 ISOamsb'
    u'or':       u'\u2228', # logical or = vee, U+2228 ISOtech'
    u'ordf':     u'\u00AA', # feminine ordinal indicator, U+00AA ISOnum'
    u'ordm':     u'\u00BA', # masculine ordinal indicator, U+00BA ISOnum'
    u'oslash':   u'\u00F8', # latin small letter o with stroke, = latin small letter o slash, U+00F8 ISOlat1'
    u'otilde':   u'\u00F5', # latin small letter o with tilde, U+00F5 ISOlat1'
    u'otimes':   u'\u2297', # circled times = vector product, U+2297 ISOamsb'
    u'ouml':     u'\u00F6', # latin small letter o with diaeresis, U+00F6 ISOlat1'
    u'para':     u'\u00B6', # pilcrow sign = paragraph sign, U+00B6 ISOnum'
    u'part':     u'\u2202', # partial differential, U+2202 ISOtech'
    u'permil':   u'\u2030', # per mille sign, U+2030 ISOtech'
    u'perp':     u'\u22A5', # up tack = orthogonal to = perpendicular, U+22A5 ISOtech'
    u'phi':      u'\u03C6', # greek small letter phi, U+03C6 ISOgrk3'
    u'pi':       u'\u03C0', # greek small letter pi, U+03C0 ISOgrk3'
    u'piv':      u'\u03D6', # greek pi symbol, U+03D6 ISOgrk3'
    u'plusmn':   u'\u00B1', # plus-minus sign = plus-or-minus sign, U+00B1 ISOnum'
    u'pound':    u'\u00A3', # pound sign, U+00A3 ISOnum'
    u'prime':    u'\u2032', # prime = minutes = feet, U+2032 ISOtech'
    u'prod':     u'\u220F', # n-ary product = product sign, U+220F ISOamsb'
    u'prop':     u'\u221D', # proportional to, U+221D ISOtech'
    u'psi':      u'\u03C8', # greek small letter psi, U+03C8 ISOgrk3'
    u'quot':     u'\u0022', # quotation mark = APL quote, U+0022 ISOnum'
    u'rArr':     u'\u21D2', # rightwards double arrow, U+21D2 ISOtech'
    u'radic':    u'\u221A', # square root = radical sign, U+221A ISOtech'
    u'rang':     u'\u232A', # right-pointing angle bracket = ket, U+232A ISOtech'
    u'raquo':    u'\u00BB', # right-pointing double angle quotation mark = right pointing guillemet, U+00BB ISOnum'
    u'rarr':     u'\u2192', # rightwards arrow, U+2192 ISOnum'
    u'rceil':    u'\u2309', # right ceiling, U+2309 ISOamsc'
    u'rdquo':    u'\u201D', # right double quotation mark, U+201D ISOnum'
    u'real':     u'\u211C', # blackletter capital R = real part symbol, U+211C ISOamso'
    u'reg':      u'\u00AE', # registered sign = registered trade mark sign, U+00AE ISOnum'
    u'rfloor':   u'\u230B', # right floor, U+230B ISOamsc'
    u'rho':      u'\u03C1', # greek small letter rho, U+03C1 ISOgrk3'
    u'rlm':      u'\u200F', # right-to-left mark, U+200F NEW RFC 2070'
    u'rsaquo':   u'\u203A', # single right-pointing angle quotation mark, U+203A ISO proposed'
    u'rsquo':    u'\u2019', # right single quotation mark, U+2019 ISOnum'
    u'sbquo':    u'\u201A', # single low-9 quotation mark, U+201A NEW'
    u'scaron':   u'\u0161', # latin small letter s with caron, U+0161 ISOlat2'
    u'sdot':     u'\u22C5', # dot operator, U+22C5 ISOamsb'
    u'sect':     u'\u00A7', # section sign, U+00A7 ISOnum'
    u'shy':      u'\u00AD', # soft hyphen = discretionary hyphen, U+00AD ISOnum'
    u'sigma':    u'\u03C3', # greek small letter sigma, U+03C3 ISOgrk3'
    u'sigmaf':   u'\u03C2', # greek small letter final sigma, U+03C2 ISOgrk3'
    u'sim':      u'\u223C', # tilde operator = varies with = similar to, U+223C ISOtech'
    u'spades':   u'\u2660', # black spade suit, U+2660 ISOpub'
    u'sub':      u'\u2282', # subset of, U+2282 ISOtech'
    u'sube':     u'\u2286', # subset of or equal to, U+2286 ISOtech'
    u'sum':      u'\u2211', # n-ary sumation, U+2211 ISOamsb'
    u'sup':      u'\u2283', # superset of, U+2283 ISOtech'
    u'sup1':     u'\u00B9', # superscript one = superscript digit one, U+00B9 ISOnum'
    u'sup2':     u'\u00B2', # superscript two = superscript digit two = squared, U+00B2 ISOnum'
    u'sup3':     u'\u00B3', # superscript three = superscript digit three = cubed, U+00B3 ISOnum'
    u'supe':     u'\u2287', # superset of or equal to, U+2287 ISOtech'
    u'szlig':    u'\u00DF', # latin small letter sharp s = ess-zed, U+00DF ISOlat1'
    u'tau':      u'\u03C4', # greek small letter tau, U+03C4 ISOgrk3'
    u'there4':   u'\u2234', # therefore, U+2234 ISOtech'
    u'theta':    u'\u03B8', # greek small letter theta, U+03B8 ISOgrk3'
    u'thetasym': u'\u03D1', # greek small letter theta symbol, U+03D1 NEW'
    u'thinsp':   u'\u2009', # thin space, U+2009 ISOpub'
    u'thorn':    u'\u00FE', # latin small letter thorn with, U+00FE ISOlat1'
    u'tilde':    u'\u02DC', # small tilde, U+02DC ISOdia'
    u'times':    u'\u00D7', # multiplication sign, U+00D7 ISOnum'
    u'trade':    u'\u2122', # trade mark sign, U+2122 ISOnum'
    u'uArr':     u'\u21D1', # upwards double arrow, U+21D1 ISOamsa'
    u'uacute':   u'\u00FA', # latin small letter u with acute, U+00FA ISOlat1'
    u'uarr':     u'\u2191', # upwards arrow, U+2191 ISOnum'
    u'ucirc':    u'\u00FB', # latin small letter u with circumflex, U+00FB ISOlat1'
    u'ugrave':   u'\u00F9', # latin small letter u with grave, U+00F9 ISOlat1'
    u'uml':      u'\u00A8', # diaeresis = spacing diaeresis, U+00A8 ISOdia'
    u'upsih':    u'\u03D2', # greek upsilon with hook symbol, U+03D2 NEW'
    u'upsilon':  u'\u03C5', # greek small letter upsilon, U+03C5 ISOgrk3'
    u'uuml':     u'\u00FC', # latin small letter u with diaeresis, U+00FC ISOlat1'
    u'weierp':   u'\u2118', # script capital P = power set = Weierstrass p, U+2118 ISOamso'
    u'xi':       u'\u03BE', # greek small letter xi, U+03BE ISOgrk3'
    u'yacute':   u'\u00FD', # latin small letter y with acute, U+00FD ISOlat1'
    u'yen':      u'\u00A5', # yen sign = yuan sign, U+00A5 ISOnum'
    u'yuml':     u'\u00FF', # latin small letter y with diaeresis, U+00FF ISOlat1'
    u'zeta':     u'\u03B6', # greek small letter zeta, U+03B6 ISOgrk3'
    u'zwj':      u'\u200D', # zero width joiner, U+200D NEW RFC 2070'
    u'zwnj':     u'\u200Cu'  # zero width non-joiner, U+200C NEW RFC 2070'
}

entitydefs2 = {
    u'$':    u'%24',
    u'&':    u'%26',
    u'+':    u'%2B',
    u',':    u'%2C',
    u'/':    u'%2F',
    u':':    u'%3A',
    u';':    u'%3B',
    u'=':    u'%3D',
    u'?':    u'%3F',
    u'@':    u'%40',
    u' ':    u'%20',
    u'"':    u'%22',
    u'<':    u'%3C',
    u'>':    u'%3E',
    u'#':    u'%23',
    u'%':    u'%25',
    u'{':    u'%7B',
    u'}':    u'%7D',
    u'|':    u'%7C',
    u'\\':   u'%5C',
    u'^':    u'%5E',
    u'~':    u'%7E',
    u'[':    '%5B',
    u']':    u'%5D',
    u'`':    u'%60'
}

entitydefs3 = {
    u'ÂÁÀÄÃÅ':  u'A',
    u'âáàäãå':  u'a',
    u'ÔÓÒÖÕ':   u'O',
    u'ôóòöõðø': u'o',
    u'ÛÚÙÜ':    u'U',
    u'ûúùüµ':   u'',
    u'ÊÉÈË':    u'E',
    u'êéèë':    u'e',
    u'ÎÍÌÏ':    u'I',
    u'îìíï':    u'i',
    u'ñ':       u'n',
    u'ß':       u'B',
    u'÷':       u'%',
    u'ç':       u'c',
    u'æ':       u'aeu'
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
    return pat.sub(sub, s)

def clean3(s): # remove &#XXX;
    pat = re.compile(r'&#(\d+);')
    def sub(mo):
        return unichr(int(mo.group(1)))
    return decode(decode(pat.sub(sub, s))) # Once in a while site triple their source

def decode(s):
    if not s:
        return u''
    for key in name2codepoint.keys():
        s = s.replace(key, name2codepoint[key])
    return s

def clean_safe(s):
    if not s:
        return u''
    s = clean2(smart_unicode(s))
    if s.find(u'&') != -1:
        s_references = s.split(u'&')
        s = s_references[0]
        for ref in s_references[1:]:
            idx = ref.find(u';')
            if idx != -1:
                if ref.startswith(u'#'):
                    s += unichr(int(ref[1:idx])) + ref[idx + 1:]
                else:
                    entity = ref[:idx + 1].lower()
                    if entity == u'amp;' and ref[idx + 1:].startswith(u'#'):
                        if ref[idx + 1:].find(u';') != -1:
                            idx += ref[idx + 1:].find(u';') + 1
                            s += unichr(int(ref[5:idx])) + ref[idx + 1:]
                        else:
                            s += name2unicode.get(entity, ref[:idx + 1]) + ref[idx + 1:]
                    else:
                        s += name2unicode.get(entity, ref[:idx + 1]) + ref[idx + 1:]
            else:
                s += u'&' + ref
    return s

def unquote(s): # unquote
    if not s:
        return u''
    try:
        for key, value in entitydefs2.iteritems():
            s = s.replace(value, key)
    except:
        if enable_debug:
            traceback.print_exc(file = sys.stdout)
    return s

def quote(s): # quote
    if not s:
        return u''
    try:
        for key, value in entitydefs2.iteritems():
            s = s.replace(key, value)
    except:
        if enable_debug:
            traceback.print_exc(file = sys.stdout)
    return s2