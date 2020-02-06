import math
import time
import datetime
import os
import sys
import copy
import string
import random as rand

import hig_svg as h_svg
import hig_stats as h_stats

from project_specifics3 import output_root
from convert_functions3 import smart_units
from display_settings3 import green_red_gradient

matrix_color_bins = 5 #How many different colors (grayscale) to display on matrix histogram?


def safe_str(input_str):
    output_str = ''
    for character in input_str:
        if character in string.letters + string.digits:
            output_str += character
    if len(output_str) == 0: return 'none'
    else: return output_str


def generic_matrix(data,X,Y):
    X_res = float(X['max']-X['min']) / X['bins']
    Y_res = float(Y['max']-Y['min']) / Y['bins']
    matrix = []
    lists_for_stats = []
    data_test = False
    for i in range(X['bins']):
        matrix.append([])
        lists_for_stats.append([])
        for j in range(Y['bins']):
            matrix[i].append(0)
    for row in data:
        x = row[X['name']]
        y = row[Y['name']]
        if x != 'none' and y != 'none':
            x_index = int(math.floor((x-X['min'])/ X_res))
            if x_index >= X['bins']: x_index = -1
            elif x_index < 0: x_index = 0
            y_index = int(math.floor((y-Y['min'])/ Y_res))
            if y_index >= Y['bins']: y_index = -1
            elif y_index < 0: y_index = 0
            matrix[x_index][y_index] += 1
            lists_for_stats[x_index].append(y)
            data_test = True
    stats = []
    for y_values in lists_for_stats:
        stats.append(h_stats.simple_stats(y_values, dictionary=True))
    return [[matrix]], stats, data_test




def append_matrix(f, matrix, block_width, block_height):
    A = len(matrix)
    B = len(matrix[0])
    I = len(matrix[0][0])
    J = len(matrix[0][0][0])
    h_cell_size = block_width / I
    h_cell_half = h_cell_size / 2
    v_cell_size = block_height / J
    v_cell_half = v_cell_size / 2
    block_padding = 10
    block_h_spacing = block_width + block_padding
    block_v_spacing = block_height + block_padding
    max_count = 0
    for a in range(A):
        for b in range(B):
            for i in range(I):
                for j in range(J):
                    count = matrix[a][b][i][j]
                    if count > max_count: max_count = count    #maximum in the entire visualization
    color_bin_size = float(max_count) / matrix_color_bins
    transform_template = "translate({0},{1}) scale({2})"
    scaling_basis = 1.0 - (1.0 / (matrix_color_bins))
    for a in range(A):
        h_block_origin = a * block_h_spacing
        for b in range(B):
            v_block_origin = b * block_v_spacing
            f.write('\t<g>\n\t\t<rect x="' + str(h_block_origin) + '" y="' + str(v_block_origin) + '" width = "' + str(
                block_width) + '" height = "' + str(block_height) + '" style="fill:none; stroke:rgb(0,0,1);" />\n')
            for i in range(I):
                for j in range(J):
                    count = matrix[a][b][i][j]
                    if count > 0: #Don't plot points with no data
                        x = h_block_origin + i * h_cell_size
                        y = v_block_origin + block_height - (j + 1) * v_cell_size
                        bin = int(math.floor(float(count - 1) / max_count * matrix_color_bins))
                        gray_value = 180 - bin * 180 / matrix_color_bins
                        scale = math.pow(scaling_basis, matrix_color_bins - bin - 1)
                        color = 'rgb(' + str(gray_value) + ',' + str(gray_value) + ',' + str(gray_value) + ')'
                        scale_txt = h_svg.min_text(scale)
                        x_trans = h_svg.min_text(x+h_cell_half)
                        y_trans = h_svg.min_text(y+v_cell_half)
                        transform_text = transform_template.format(x_trans,y_trans,scale_txt)
                        f.write(h_svg.svg_rect(-1*h_cell_half,-1*v_cell_half,h_cell_size,v_cell_size,color,transform_text))
            f.write('\t</g>\n')
    text_x = -200
    text_y_inc = 20
    f.write('	<g>\n\t\t\t<text fill="black" x="' + str(text_x) + '" y="0">min		max</text>\n')
    for bin in range(matrix_color_bins):
        f.write('\t\t\t<text fill="black" x="' + str(text_x) + '" y="' + str((bin + 1) * text_y_inc) + '">' + str(
            int(math.floor(color_bin_size * bin))) + "	" + str(
            int(math.floor(color_bin_size * (bin + 1)))) + '</text>\n')
    f.write('\t</g>\n')


def append_curves(f, stats, x_increment, y_scale, y_min, height):
    colors = {'min':'#AAA', 'max':'#AAA', 'ave':'#A37', 'median':'#21C', 'p25':'#54E', 'p75':'#54E', 'p95':'#A9F', 'p5':'#A9F', 'p2':'#CCF', 'p98':'#CCF'}
    paths = {}
    f.write('<g>\n')

    def point(x,value,continuation = True):
        try:
            y = height - y_scale * (value - y_min)
            return h_svg.svg_linestring_element(x,y,continuation)
        except TypeError: raise Exception('Some odd value passed:'+str(value))

    for i,x_value in enumerate(stats):
        x = (0.5+i)*x_increment
        for stat,value in x_value.iteritems():
            if stat in colors: #No sense in trying if there's no color assigned.
                if value != "none":
                    try: paths[stat].append(point(x,value))
                    except KeyError: paths.update([(stat, [point(x,value,False)])])
                else:
                    try:
                        f.write(h_svg.svg_path(paths[stat],colors[stat]))
                        paths.pop(stat)
                    except KeyError: pass
    for stat,path in paths.iteritems():
        f.write(h_svg.svg_path(path,colors[stat]))
    f.write('</g>\n')


def simple_p_matrix(data,X,Y,name):
    draw_generic_matrix(data,{'name':X,'min':0.0,'max':1.0,'bins':50},{'name':Y,'min':0.0,'max':1.0,'bins':50},name)

def draw_generic_matrix(data,X,Y,name,curve_bool=False):
    if len(data) > 0:
        start_time = time.time()
        block_width = 400.0
        block_height = 400.0
        x_increment = block_width / X['bins']
        y_scale = block_height / (Y['max'] - Y['min'])
        if X['name'] in data[0] and Y['name'] in data[0]: #only bother if the columns are actually there
            matrix, stats, data_test = generic_matrix(data,X,Y)
            if data_test: #True if there is at least one point in the dataset.
                print "  Creating matrix for {0} using columns {1} and {2}.".format(name, X['name'],Y['name']),
                f = open(output_root+'/Visuals/Characterize/Matrix/{0}_{1}_v_{2}_2D_histogram.svg'.format(name,safe_str(X['name']),safe_str(Y['name'])), 'w')
                f.write(h_svg.svg_header(block_width, block_height))
                f.write('<text x="-100" y="-100">{0} on X Axis, {1} to {2}.  {3} on Y Axis, {4} to {5}</text>\n'.format(X['name'],X['min'],X['max'], Y['name'],Y['min'],Y['max']))
                append_matrix(f, matrix, block_width, block_height)
                if curve_bool: append_curves(f, stats, x_increment, y_scale, Y['min'], block_height)
                f.write("</svg>")
                print "took","{0:.3f}".format(time.time()-start_time),"seconds"


def draw_histogram_multiple_data_sources(dataset_list,settings,name, draw_cumulative = True):
    if len(dataset_list[0]) > 0:
        start_time = time.time()
        if settings['name'] in dataset_list[0][0]:
            bin_width = float(settings['max'] - settings['min']) / settings['bins']
            histogram = [0]*settings['bins']
            for data in dataset_list:
                for row in data:
                    try:
                        value = float(row[settings['name']])
                        bin = int(math.floor((float(value)-settings['min']) / bin_width))
                        if bin < 0: bin = 0 #Dump values off the low end in the leftmost bin
                        elif bin >= settings['bins']: bin = -1 #Dump values off the high end in the rightmost bin
                        histogram[bin] += 1
                    except ValueError: pass
            max = 0
            total = 0
            for bin in histogram:
                if bin > max: max = bin
                total += bin
            if max > 0:
                print "  Creating histogram for {0} using {1} with max count {2} ".format(name, settings['name'],max),
                bars = []
                cumulative_bars = []
                width = 8
                v_scale = 100.0
                cumulative = 0
                for bin in histogram:
                    cumulative += bin
                    bars.append({
                        'width':width,
                        'height':v_scale * bin / max,
                        'gap_after':0,
                        'color':'#012',
                        'name':'{0:.4F}%'.format(100.0*cumulative/total) #print percentile with each bar
                    })
                    if draw_cumulative:
                        cumulative_bars.append({
                            'width':width,
                            'height':v_scale * cumulative / total,
                            'gap_after':0,
                            'color':'#012',
                            'name':'{0:.4F}%'.format(100.0*cumulative/total) #print percentile with each bar
                        })
                origin = (20,v_scale+20)
                graph_width = len(bars)*width
                f = open(output_root+'/Visuals/Characterize/Histogram/{0}_for_{1}.svg'.format(name,settings['name']), 'w')
                f.write(h_svg.svg_header(graph_width+40,v_scale+40))
                f.write(h_svg.svg_bars(origin,bars))
                f.write(h_svg.svg_h_line(origin,graph_width,"#213"))
                f.write(h_svg.svg_text(-100,-100,"left","#233","max: {0}".format(max)))
                f.write(h_svg.svg_close())
                if draw_cumulative:
                    f = open(output_root+'/Visuals/Characterize/Cumulative/{0}_for_{1}.svg'.format(name,settings['name']), 'w')
                    f.write(h_svg.svg_header(graph_width+40,v_scale+40))
                    f.write(h_svg.svg_bars(origin,cumulative_bars))
                    f.write(h_svg.svg_h_line(origin,graph_width,"#213"))
                    f.write(h_svg.svg_text(-100,-100,"left","#233","max: {0}".format(max)))
                    f.write(h_svg.svg_close())
                print "took","{0:.3f}".format(time.time()-start_time),"seconds"


def draw_histogram(data, settings, name, draw_cumulative = True):
    if len(data) > 0:
        start_time = time.time()
        if settings['name'] in data[0]:
            bin_width = float(settings['max'] - settings['min']) / settings['bins']
            histogram = [0]*settings['bins']
            for row in data:
                try:
                    value = float(row[settings['name']])
                    bin = int(math.floor((float(value)-settings['min']) / bin_width))
                    if bin < 0: bin = 0 #Dump values off the low end in the leftmost bin
                    elif bin >= settings['bins']: bin = -1 #Dump values off the high end in the rightmost bin
                    histogram[bin] += 1
                except (TypeError, ValueError): pass
            max = 0
            total = 0
            for bin in histogram:
                if bin > max: max = bin
                total += bin
            if max > 0:
                print "  Creating histogram for {0} using {1} with max count {2} ".format(name, settings['name'],max),
                bars = []
                cumulative_bars = []
                width = 8
                v_scale = 100.0
                cumulative = 0
                for bin in histogram:
                    cumulative += bin
                    bars.append({
                        'width':width,
                        'height':v_scale * bin / max,
                        'gap_after':0,
                        'color':'#012',
                        'name':'{0:.4F}%'.format(100.0*cumulative/total) #print percentile with each bar
                    })
                    if draw_cumulative:
                        cumulative_bars.append({
                            'width':width,
                            'height':v_scale * cumulative / total,
                            'gap_after':0,
                            'color':'#012',
                            'name':'{0:.4F}%'.format(100.0*cumulative/total) #print percentile with each bar
                        })
                origin = (20,v_scale+20)
                graph_width = len(bars)*width
                f = open(output_root+'/Visuals/Characterize/Histogram/{0}_for_{1}.svg'.format(name,settings['name']), 'w')
                f.write(h_svg.svg_header(graph_width+40,v_scale+40))
                f.write(h_svg.svg_bars(origin,bars))
                f.write(h_svg.svg_h_line(origin,graph_width,"#213"))
                f.write(h_svg.svg_text(-100,-100,"left","#233","max: {0}".format(max)))
                f.write(h_svg.svg_close())
                if draw_cumulative:
                    f = open(output_root+'/Visuals/Characterize/Cumulative/{0}_for_{1}.svg'.format(name,settings['name']), 'w')
                    f.write(h_svg.svg_header(graph_width+40,v_scale+40))
                    f.write(h_svg.svg_bars(origin,cumulative_bars))
                    f.write(h_svg.svg_h_line(origin,graph_width,"#213"))
                    f.write(h_svg.svg_text(-100,-100,"left","#233","max: {0}".format(max)))
                    f.write(h_svg.svg_close())
                print "took","{0:.3f}".format(time.time()-start_time),"seconds"

def draw_cycle_histogram(name,timeseries_data, time_column, value_column, value_binning, reverse=False, bin_width = smart_units('7 days'), graph_settings = {'width':100, 'height':100}):
    if len(timeseries_data) > 0:
        print "  Drawing cycle histogram for {0} for {1} values".format(name,value_column)
        width = float(graph_settings['width'])
        height = float(graph_settings['height'])
        n_time_bins = int(smart_units('1 year') / bin_width)+1
        bar_width = width/n_time_bins
        values_organized = [[] for i in range(n_time_bins)]
        max_value = -1*sys.float_info.max
        min_value = sys.float_info.max
        for row in timeseries_data:
            value = row[value_column]
            time = row[time_column]
            this_second_of_year = float(time.timetuple().tm_yday * 86400 + time.timetuple().tm_sec)
            time_bin = int(math.floor(this_second_of_year / bin_width)) #Not very clever in unit-awareness. Internal units are seconds, but that's not clear without going into convert_functions.
            values_organized[time_bin].append(value)
            if value < min_value: min_value = value
            if value > max_value: max_value = value
        if max_value is not 'none' and min_value is not 'none':
            n_bins = int(math.ceil(float(max_value-min_value)/value_binning))+1
            empty_1D_histogram = [0]*n_bins
            f = open(output_root+'/Visuals/Characterize/Cycle_Histogram/{0}_{1}_cycle_histogram.svg'.format(name,value_column), 'w')
            f.write(h_svg.svg_header(width+40,height+40))
            for i,time_bin in enumerate(values_organized): #Make the histograms
                this_histogram = copy.deepcopy(empty_1D_histogram)
                total = 0
                for value in time_bin:
                    if reverse: bin_index = n_bins-int(math.floor((value-min_value)/value_binning))-1
                    else: bin_index = int(math.floor((value-min_value)/value_binning))
                    this_histogram[bin_index] += 1
                    total += 1
                y = height
                for j,count in enumerate(this_histogram):
                    section_height = float(count)/total * height
                    y -= section_height
                    f.write(h_svg.svg_rect(i*bar_width,y,bar_width,section_height,green_red_gradient(n_bins,j)))
            f.write(h_svg.svg_close())

def draw_cycle_histogram_multiple_data_sources(name,timeseries_list, time_column, value_column, value_binning, reverse=False, bin_width = smart_units('7 days'), graph_settings = {'width':100, 'height':100}):
    print "  Drawing cycle histogram for {0} for {1} values".format(name,value_column)
    width = float(graph_settings['width'])
    height = float(graph_settings['height'])
    n_time_bins = int(smart_units('1 year') / bin_width)+1
    bar_width = width/n_time_bins
    values_organized = [[] for i in range(n_time_bins)]
    max_value = -1*sys.float_info.max
    min_value = sys.float_info.max
    for timeseries_data in timeseries_list:
        for row in timeseries_data:
            value = row[value_column]
            time = row[time_column]
            this_second_of_year = float(time.timetuple().tm_yday * 86400 + time.timetuple().tm_sec)
            time_bin = int(math.floor(this_second_of_year / bin_width)) #Not very clever in unit-awareness. Internal units are seconds, but that's not clear without going into convert_functions.
            values_organized[time_bin].append(value)
            if value < min_value: min_value = value
            if value > max_value: max_value = value
    n_bins = int(math.ceil(float(max_value-min_value)/value_binning))+1
    empty_1D_histogram = [0]*n_bins
    f = open(output_root+'/Visuals/Characterize/Cycle_Histogram/{0}_{1}_cycle_histogram.svg'.format(name,value_column), 'w')
    f.write(h_svg.svg_header(width+40,height+40))
    for i,time_bin in enumerate(values_organized): #Make the histograms
        this_histogram = copy.deepcopy(empty_1D_histogram)
        total = 0
        for value in time_bin:
            if reverse: bin_index = n_bins-int(math.floor((value-min_value)/value_binning))
            else: bin_index = int(math.floor((value-min_value)/value_binning))
            try: this_histogram[bin_index] += 1
            except IndexError as error_text:
                print bin_index
                print min_value, max_value, value_binning
                print error_text
                raise Exception
            total += 1
        y = height
        for j,count in enumerate(this_histogram):
            section_height = float(count)/total * height
            y -= section_height
            f.write(h_svg.svg_rect(i*bar_width,y,bar_width,section_height,green_red_gradient(n_bins,j)))
    f.write(h_svg.svg_close())