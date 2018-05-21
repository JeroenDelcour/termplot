# -*- coding: utf-8 -*- 

from colorama import init as colorama_init
from colorama import Fore, Back

def plot(X, Y, marker='·', color=None, size=(96,24), xlim=None, ylim=None, bgcolor=None, silent=False, fmt='G'):
    COLORS = {'fore': {'black': Fore.BLACK,
                       'red': Fore.RED,
                       'green': Fore.GREEN,
                       'yellow': Fore.YELLOW,
                       'blue': Fore.BLUE,
                       'magenta': Fore.MAGENTA,
                       'cyan': Fore.CYAN,
                       'white': Fore.WHITE},
              'back': {'black': Back.BLACK,
                       'red': Back.RED,
                       'green': Back.GREEN,
                       'yellow': Back.YELLOW,
                       'blue': Back.BLUE,
                       'magenta': Back.MAGENTA,
                       'cyan': Back.CYAN,
                       'white': Back.WHITE}
              }
    BRIGHT_COLORS = ['white', 'yellow', 'cyan', 'green']

    colorama_init()

    # expand dimensions
    if type(X[0])   in (int, float): X = [X]
    if type(Y[0])   in (int, float): Y = [Y]
    if not color or type(color)==str: color = [color]*len(X)
    if type(marker)==str: marker = [marker]*len(X)

    width, height = size
    buffer = [[' ' for w in range(width)] for h in range(height)]

    if xlim==None: xlim = (min((min(x) for x in X)), max((max(x) for x in X)))
    if ylim==None: ylim = (min((min(y) for y in Y)), max((max(y) for y in Y)))
    assert(xlim[1]>xlim[0])
    assert(ylim[1]>ylim[0])

    def find_transform():
        "Find transform from data space to plot space"
        x_scaling = (width-margin_left-1) / (xlim[1] - xlim[0])
        x_offset = xlim[0] * -x_scaling + margin_left
        y_scaling = -(height-margin_bottom-1) / (ylim[1] - ylim[0])
        y_offset = ylim[0] * -y_scaling - 1 - margin_bottom
        return lambda x,y: (int(round(x*x_scaling+x_offset)),
                                 int(round(y*y_scaling+y_offset)))
    margin_left, margin_bottom = 0, 0
    transform = find_transform()

    # determine axes positions
    y_axis_pos, x_axis_pos = transform(0,0)
    clamp = lambda x, min_x, max_x: max(min(x, max_x), min_x)
    y_axis_pos = clamp(y_axis_pos, 0, width-1)
    x_axis_pos = clamp(x_axis_pos, -height, -1)
    if y_axis_pos >= width: y_axis_pos = 0
    if x_axis_pos <= -height: x_axis_pos = -1

    # calculate margins for tick labels
    y_tick_min = format(ylim[0], fmt)
    y_tick_max = format(ylim[1], fmt)
    margin_left = max(max(len(y_tick_min), len(y_tick_max)) - y_axis_pos, 0)
    margin_bottom = 0 + (x_axis_pos==-1)

    # correct axes and transform for margins
    y_axis_pos += margin_left
    x_axis_pos -= margin_bottom
    transform = find_transform()

    # if background color is set, set best contrasting default foreground colors
    if not bgcolor: c, cr = ('', '')
    elif bgcolor in BRIGHT_COLORS: c, cr = (COLORS['fore']['black'], Fore.RESET)
    else: c, cr = (COLORS['fore']['white'], Fore.RESET)

    # draw axes
    for y in range(height): # vertical
        buffer[y][y_axis_pos] = c+'│'+cr
    for x in range(margin_left, width):  # horizontal
        buffer[x_axis_pos][x] = c+'─'+cr
    buffer[x_axis_pos][y_axis_pos] = c+'┼'+cr

    # draw tick marks
    buffer[x_axis_pos][-1] = c+'┼'+cr
    buffer[x_axis_pos][margin_left] = c+'┼'+cr
    buffer[0][y_axis_pos] = c+'┼'+cr
    buffer[-1][y_axis_pos] = c+'┼'+cr

    # draw data
    for X_, Y_, marker_, color_ in zip(X, Y, marker, color):
        assert(len(X_)==len(Y_))
        # set marker color
        if color_: marker_ = COLORS['fore'][color_] + marker_ + Fore.RESET
        elif bgcolor in BRIGHT_COLORS: marker_ = COLORS['fore']['black'] + marker_ + Fore.RESET
        # draw data
        for x,y in zip(X_,Y_):
            if xlim[1] >= x >= xlim[0] and ylim[1] >= y >= ylim[0]: # in bounds
                x_buffer, y_buffer = transform(x,y)
                buffer[y_buffer][x_buffer] = marker_

    # draw tick labels
    for i, character in enumerate(format(xlim[0], fmt)): # min x
        buffer[x_axis_pos+1][margin_left+i] = c+character+cr
    for i, character in enumerate(reversed(format(xlim[1]))): # max x
        buffer[x_axis_pos+1][-i-1] = c+character+cr
    for i, character in enumerate(reversed(y_tick_min)): # min y
        buffer[-margin_bottom-1][y_axis_pos-i-1] = c+character+cr
    for i, character in enumerate(reversed(y_tick_max)): # max y`
        buffer[0][y_axis_pos-i-1] = c+character+cr

    # set background color
    if bgcolor: bg, bg_r = (COLORS['back'][bgcolor], Back.RESET)
    else: bg, bg_r = ('','')

    output = '\n'.join([bg+''.join(row)+bg_r for row in buffer])
    if not silent: print(output)
    return output
