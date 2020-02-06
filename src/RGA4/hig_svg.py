def svg_header(width, height):
    return '<?xml version="1.0" standalone="no"?>\n\
        <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n\
        <svg xmlns="http://www.w3.org/2000/svg" version="1.1" width ="{0:.2f}" height="{1:.2f}"' \
           ' viewBox="0 0 {0:.2f} {1:.2f}">\n'.format(width, height)


def min_text(value):
    try:
        if round(value,2) == round(value,0): text = '{0:.0f}'.format(value)
        elif round(value,1) == round(value,0): text = '{0:.1f}'.format(value)
        else: text = '{0:.2f}'.format(value)
        if text in ['-0','-0.0','-0.00']: text = '0'
        return text
    except TypeError as error_text:
        print value
        print error_text
        raise Exception


def svg_path(path_string, color):
    if len(path_string) > 1:
        return '\t<path d="{0}" fill="none" stroke="{1}" />\n'.format("".join(path_string), color)
    else: return ""

def svg_circle(center, radius, color):
    if radius > 0:
        return '\t<circle cx="{0}" cy="{1}" r="{2}" fill="{3}" />\n'.format(min_text(center[0]),min_text(center[1]),min_text(radius),color)
    else: return ""

def filled_svg_path(path_string, color):
    if len(path_string) > 1:
        return '\t<path d="{0}" fill="{1}" stroke="none" />\n'.format("".join(path_string), color)
    else: return ""


def svg_h_line(origin,length, color):
    return svg_path("M{0} {1}L{2} {1}".format(min_text(origin[0]),min_text(origin[1]),min_text(origin[0]+length)), color)

def svg_v_line(origin,length, color):
    return svg_path("M{0} {1}L{0} {2}".format(min_text(origin[0]),min_text(origin[1]),min_text(origin[1]+length)), color)

def svg_rect(x, y, width, height, color, transform=""):
    x = min_text(x)
    y = min_text(y)
    width = min_text(width)
    height = min_text(height)
    return '\t<rect transform="{0}" x="{1}" y="{2}" width="{3}" height="{4}"' \
           ' style="fill:{5}; stroke:none" />\n'.format(transform,x,y,width,height,color)


def svg_text(x,y,anchor,color,string, size=9, font="Helvetica"):
    x = min_text(x)
    y = min_text(y)
    return '\t<text x="{0}" y="{1}" text-anchor="{2}" fill="{3}" font-size="{4}" font-family="{5}">{6}</text>\n'.format(x,y,anchor,color,size,font,string)


def svg_close():
    return '</svg>\n'


def svg_linestring_element(x, y, continuation):
    x = min_text(x)
    y = min_text(y)
    if continuation:
        return 'L{0} {1}'.format(x,y)
    else:
        return 'M{0} {1}'.format(x,y)

def svg_path_from_points(points, color):
    continuation = False
    path_strings = []
    for point in points:
        path_strings.append(svg_linestring_element(point[0],point[1],continuation))
        continuation = True
    return svg_path("".join(path_strings),color)

def filled_svg_path_from_points (points, color):
    continuation = False
    path_strings = []
    for point in points:
        path_strings.append(svg_linestring_element(point[0],point[1],continuation))
        continuation = True
    return filled_svg_path("".join(path_strings),color)

def svg_bars(lower_left, bars):
    #bar = {width, height, gap_after, color, name}
    svg = ['<g>\n']
    left = lower_left[0]
    stair = 0
    for bar in bars:
        svg.append(svg_rect(left,lower_left[1]-bar['height'],bar['width'],bar['height'],bar['color']))
        svg.append(svg_text(left,lower_left[1]+10+stair,'left','#441',bar['name']))
        left += bar['width'] + bar['gap_after']
        stair += 10
        #write text
    svg.append('</g>\n')
    return "".join(svg)

def svg_axis(ticks,length,horizontal,origin,color):

    def draw_tick(y,length,horizontal):
        if horizontal:
            path_string = ''.join([svg_linestring_element(-1.0*y,0,False),svg_linestring_element(-1.0*y,-1.0*length,True)])
        else:
            path_string = ''.join([svg_linestring_element(0,y,False),svg_linestring_element(length,y,True)])
        return path_string

    small_tick = 2
    big_tick = 4

    ticks = sorted(ticks) #should sort by first item
    smallest = ticks[0]
    largest = ticks[-1]

    tick_0 = "none"
    tick_1 = "none"
    if horizontal:
        svg = ['\t<g  transform="translate({0} {1})">\n'.format(min_text(origin[0]), min_text(origin[1]))]
        text_anchor = "middle"
        text_offset = (0,15)
    else:
        svg = ['\t<g  transform="translate({0} {1})">\n'.format(min_text(origin[0]), min_text(origin[1]))]
        text_anchor = "end"
        text_offset = (-6,4)
    for tick in ticks:
        if tick not in [smallest,largest]:
            svg.append('\t')
            if tick[1]: svg.append(svg_path(draw_tick(tick[0]*length,big_tick,horizontal),"#231"))
            else: svg.append(svg_path(draw_tick(tick[0]*length,small_tick,horizontal),"#231"))
        svg.append('\t')
        if horizontal:
            svg.append(svg_text(-1.0*tick[0]*length+text_offset[0],text_offset[1],text_anchor,"#222",tick[2]))
        else:
            svg.append(svg_text(text_offset[0],tick[0]*length+text_offset[1],text_anchor,"#222",tick[2]))

    svg.append('\t')
    axis = []
    if horizontal:
        base_x = smallest[0] * length
        top_x = largest[0] * length
        if smallest[1]:
            axis.append(svg_linestring_element(base_x, big_tick, False))
            axis.append(svg_linestring_element(base_x,0,True))
        else:
            axis.append(svg_linestring_element(base_x, small_tick, False))
            axis.append(svg_linestring_element(base_x, 0, True))
        axis.append(svg_linestring_element(top_x, 0, True))
        if largest[1]:
            axis.append(svg_linestring_element(top_x, big_tick, True))
        else:
            axis.append(svg_linestring_element(top_x, small_tick, True))
    else:
        base_y = smallest[0] * length
        top_y = largest[0] * length
        if smallest[1]:
            axis.append(svg_linestring_element(big_tick, base_y, False))
            axis.append(svg_linestring_element(0,base_y,True))
        else:
            axis.append(svg_linestring_element(small_tick, base_y,False))
            axis.append(svg_linestring_element(0,base_y,True))
        axis.append(svg_linestring_element(0, top_y,True))
        if largest[1]:
            axis.append(svg_linestring_element(big_tick, top_y,True))
        else:
            axis.append(svg_linestring_element(small_tick, top_y,True))
    svg.append(svg_path(axis,"#231"))
    svg.append("\t</g>\n")
    return "".join(svg)

