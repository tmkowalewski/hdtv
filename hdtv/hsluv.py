# Copyright (c) 2015 Alexei Boronine
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
This module is generated by transpiling Haxe into Python and cleaning
the resulting code by hand, e.g. removing unused Haxe classes. To try it
yourself, clone https://github.com/hsluv/hsluv and run:

    haxe -cp haxe/src hsluv.Hsluv -python hsluv.py
"""

import math as _math  # unexport, see #17
from functools import partial as _partial
from functools import wraps as _wraps  # unexport, see #17

__version__ = "5.0.0"

_m = [
    [3.240969941904521, -1.537383177570093, -0.498610760293],
    [-0.96924363628087, 1.87596750150772, 0.041555057407175],
    [0.055630079696993, -0.20397695888897, 1.056971514242878],
]
_min_v = [
    [0.41239079926595, 0.35758433938387, 0.18048078840183],
    [0.21263900587151, 0.71516867876775, 0.072192315360733],
    [0.019330818715591, 0.11919477979462, 0.95053215224966],
]
_ref_y = 1.0
_ref_u = 0.19783000664283
_ref_v = 0.46831999493879
_kappa = 903.2962962
_epsilon = 0.0088564516


def _normalize_output(conversion):
    # as in snapshot rev 4, the tolerance should be 1e-11
    normalize = _partial(round, ndigits=11 - 1)

    @_wraps(conversion)
    def normalized(*args, **kwargs):
        color = conversion(*args, **kwargs)
        return tuple(normalize(c) for c in color)

    return normalized


def _distance_line_from_origin(line):
    v = line["slope"] ** 2 + 1
    return abs(line["intercept"]) / _math.sqrt(v)


def _length_of_ray_until_intersect(theta, line):
    return line["intercept"] / (_math.sin(theta) - line["slope"] * _math.cos(theta))


def _get_bounds(l):
    result = []
    sub1 = ((l + 16) ** 3) / 1560896
    if sub1 > _epsilon:
        sub2 = sub1
    else:
        sub2 = l / _kappa
    _g = 0
    while _g < 3:
        c = _g
        _g += 1
        m1 = _m[c][0]
        m2 = _m[c][1]
        m3 = _m[c][2]
        _g1 = 0
        while _g1 < 2:
            t = _g1
            _g1 += 1
            top1 = (284517 * m1 - 94839 * m3) * sub2
            top2 = (838422 * m3 + 769860 * m2 + 731718 * m1) * l * sub2 - (
                769860 * t
            ) * l
            bottom = (632260 * m3 - 126452 * m2) * sub2 + 126452 * t
            result.append({"slope": top1 / bottom, "intercept": top2 / bottom})
    return result


def _max_safe_chroma_for_l(l):
    return min(_distance_line_from_origin(bound) for bound in _get_bounds(l))


def _max_chroma_for_lh(l, h):
    hrad = _math.radians(h)
    lengths = [_length_of_ray_until_intersect(hrad, bound) for bound in _get_bounds(l)]
    return min(length for length in lengths if length >= 0)


def _dot_product(a, b):
    return sum(i * j for i, j in zip(a, b))


def _from_linear(c):
    if c <= 0.0031308:
        return 12.92 * c

    return 1.055 * _math.pow(c, 5 / 12) - 0.055


def _to_linear(c):
    if c > 0.04045:
        return _math.pow((c + 0.055) / 1.055, 2.4)

    return c / 12.92


def _y_to_l(y):
    if y <= _epsilon:
        return y / _ref_y * _kappa

    return 116 * _math.pow(y / _ref_y, 1 / 3) - 16


def _l_to_y(l):
    if l <= 8:
        return _ref_y * l / _kappa

    return _ref_y * (((l + 16) / 116) ** 3)


def xyz_to_rgb(_hx_tuple):
    return (
        _from_linear(_dot_product(_m[0], _hx_tuple)),
        _from_linear(_dot_product(_m[1], _hx_tuple)),
        _from_linear(_dot_product(_m[2], _hx_tuple)),
    )


def rgb_to_xyz(_hx_tuple):
    rgbl = (
        _to_linear(_hx_tuple[0]),
        _to_linear(_hx_tuple[1]),
        _to_linear(_hx_tuple[2]),
    )
    return (
        _dot_product(_min_v[0], rgbl),
        _dot_product(_min_v[1], rgbl),
        _dot_product(_min_v[2], rgbl),
    )


def xyz_to_luv(_hx_tuple):
    x = float(_hx_tuple[0])
    y = float(_hx_tuple[1])
    z = float(_hx_tuple[2])
    l = _y_to_l(y)
    if l == 0:
        return (0, 0, 0)
    divider = x + 15 * y + 3 * z
    if divider == 0:
        u = v = float("nan")
        return (l, u, v)
    var_u = 4 * x / divider
    var_v = 9 * y / divider
    u = 13 * l * (var_u - _ref_u)
    v = 13 * l * (var_v - _ref_v)
    return (l, u, v)


def luv_to_xyz(_hx_tuple):
    l = float(_hx_tuple[0])
    u = float(_hx_tuple[1])
    v = float(_hx_tuple[2])
    if l == 0:
        return (0, 0, 0)
    var_u = u / (13 * l) + _ref_u
    var_v = v / (13 * l) + _ref_v
    y = _l_to_y(l)
    x = y * 9 * var_u / (4 * var_v)
    z = y * (12 - 3 * var_u - 20 * var_v) / (4 * var_v)
    return (x, y, z)


def luv_to_lch(_hx_tuple):
    l = float(_hx_tuple[0])
    u = float(_hx_tuple[1])
    v = float(_hx_tuple[2])
    c = _math.hypot(u, v)
    if c < 1e-08:
        h = 0
    else:
        hrad = _math.atan2(v, u)
        h = _math.degrees(hrad)
        if h < 0:
            h += 360
    return (l, c, h)


def lch_to_luv(_hx_tuple):
    l = float(_hx_tuple[0])
    c = float(_hx_tuple[1])
    h = float(_hx_tuple[2])
    hrad = _math.radians(h)
    u = _math.cos(hrad) * c
    v = _math.sin(hrad) * c
    return (l, u, v)


def hsluv_to_lch(_hx_tuple):
    h = float(_hx_tuple[0])
    s = float(_hx_tuple[1])
    l = float(_hx_tuple[2])
    if l > 100 - 1e-7:
        return (100, 0, h)
    if l < 1e-08:
        return (0, 0, h)
    _hx_max = _max_chroma_for_lh(l, h)
    c = _hx_max / 100 * s
    return (l, c, h)


def lch_to_hsluv(_hx_tuple):
    l = float(_hx_tuple[0])
    c = float(_hx_tuple[1])
    h = float(_hx_tuple[2])
    if l > 100 - 1e-7:
        return (h, 0, 100)
    if l < 1e-08:
        return (h, 0, 0)
    _hx_max = _max_chroma_for_lh(l, h)
    s = c / _hx_max * 100
    return (h, s, l)


def hpluv_to_lch(_hx_tuple):
    h = float(_hx_tuple[0])
    s = float(_hx_tuple[1])
    l = float(_hx_tuple[2])
    if l > 100 - 1e-7:
        return (100, 0, h)
    if l < 1e-08:
        return (0, 0, h)
    _hx_max = _max_safe_chroma_for_l(l)
    c = _hx_max / 100 * s
    return (l, c, h)


def lch_to_hpluv(_hx_tuple):
    l = float(_hx_tuple[0])
    c = float(_hx_tuple[1])
    h = float(_hx_tuple[2])
    if l > 100 - 1e-7:
        return (h, 0, 100)
    if l < 1e-08:
        return (h, 0, 0)
    _hx_max = _max_safe_chroma_for_l(l)
    s = c / _hx_max * 100
    return (h, s, l)


def rgb_to_hex(_hx_tuple):
    r = int(_math.floor(_hx_tuple[0] * 255 + 0.5))
    g = int(_math.floor(_hx_tuple[1] * 255 + 0.5))
    b = int(_math.floor(_hx_tuple[2] * 255 + 0.5))
    return f"#{r:02x}{g:02x}{b:02x}"


def hex_to_rgb(_hex):
    # skip leading '#'
    r = int(_hex[1:3], base=16) / 255.0
    g = int(_hex[3:5], base=16) / 255.0
    b = int(_hex[5:7], base=16) / 255.0
    return (r, g, b)


def lch_to_rgb(_hx_tuple):
    return xyz_to_rgb(luv_to_xyz(lch_to_luv(_hx_tuple)))


def rgb_to_lch(_hx_tuple):
    return luv_to_lch(xyz_to_luv(rgb_to_xyz(_hx_tuple)))


def _hsluv_to_rgb(_hx_tuple):
    return lch_to_rgb(hsluv_to_lch(_hx_tuple))


hsluv_to_rgb = _normalize_output(_hsluv_to_rgb)


def rgb_to_hsluv(_hx_tuple):
    return lch_to_hsluv(rgb_to_lch(_hx_tuple))


def _hpluv_to_rgb(_hx_tuple):
    return lch_to_rgb(hpluv_to_lch(_hx_tuple))


hpluv_to_rgb = _normalize_output(_hpluv_to_rgb)


def rgb_to_hpluv(_hx_tuple):
    return lch_to_hpluv(rgb_to_lch(_hx_tuple))


def hsluv_to_hex(_hx_tuple):
    return rgb_to_hex(hsluv_to_rgb(_hx_tuple))


def hpluv_to_hex(_hx_tuple):
    return rgb_to_hex(hpluv_to_rgb(_hx_tuple))


def hex_to_hsluv(s):
    return rgb_to_hsluv(hex_to_rgb(s))


def hex_to_hpluv(s):
    return rgb_to_hpluv(hex_to_rgb(s))
