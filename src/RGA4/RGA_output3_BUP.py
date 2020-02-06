import math
import re
import csv
import datetime
import time
import sys
import random as rand

import hig_svg as hs
from hig_stats import *
from hig_utils import safe_get_float
from convert_functions3 import *
from histograms import append_curves, append_matrix

from model_settings3_Arctic_DNV import *

from project_specifics3 import (
    end_summer,
    end_winter
)

from RGA_analyze3 import (
    generic_matrix
)

from project_specifics3 import output_root

from display_settings3 import * #Constants used in visualizations.

default_keys = [
    'name',
    'merge_name',
    'limit_name',
    'Red_porportion_minimum',
    'Red_porportion_maximum',
    'Red_porportion_estimate',
    'Red_porportion_best',
    'Yellow_porportion_minimum',
    'Yellow_porportion_maximum',
    'Yellow_porportion_best',
    'Green_porportion_minimum',
    'Green_porportion_maximum',
    'Green_porportion_estimate',
    'Green_porportion_best',
    'lat',
    'lon',
    'total_hours',
    'start',
    'end',
    'complete',
    'incomplete',
    'green',
    'red',
    'ambiguous',
    'green_complete', #These keys have changed - need to update. Shouldn't crash though.
    'red_complete',
    'red_incomplete',
    'day',
    'night',
    'winter_red',
    'winter_yellow',
    'winter_green',
    'overall_red',
    'summer_yellow',
    'summer_green'
] #If these keys occur, they will be listed first and in this order.  But if they don't occur, they'll be ignored.


def order_list(original_list, ordered_items):
    try:
        new_list = ordered_items
        for key in original_list:
            if key not in new_list:
                new_list.append(key)
        new_list = [x for x in new_list if x in original_list]
    except AttributeError:
        print "WARNING: bad data sent to order_list:"
        print "original list:", original_list
        print "ordered items:", ordered_items
        print "new list:", new_list
    return new_list


def write_summaries_from_list_of_dicts(suffix, data, keys=False):
    if len(data) > 0:
        if not keys: keys = sorted(data[0].keys()) #unordered columns
        print_keys = order_list(keys, default_keys)
        for row in data:
            write_csv_from_list_of_dicts(output_root+'/Text/Summary/' + row['name'] + suffix, [row], print_keys)


def write_csv_from_list_of_dicts(file_name, data, keys=False, options='wb'):
    start_time = time.time()
    if len(data) > 0:
        print "  Writing data: " + file_name,
        key_set = set([])
        for row in data:
            key_set.update(row.keys())
        print list
        key_set = sorted(list(key_set))
        if keys:
            print_keys = order_list(keys, default_keys)
            print_keys = order_list(key_set, print_keys)
        else:
            print_keys = order_list(key_set, default_keys)
        with open(file_name, options) as out_file:
            dw = csv.DictWriter(out_file, dialect=csv.excel, fieldnames=print_keys)
            dw.writeheader()
            for row in data:
                dw.writerow(row)
    else:
        print "\nWARNING:  No data in list, " + file_name + " not written",
    print "took",'{0:.3f}'.format(time.time() - start_time),"seconds"


#Writes the full_summary text file
def print_summary(name, summary, options="w"):
    print("  Print summary for " + name + " with options " + options)
    all_keys = sorted(summary[0].keys()) #assumes the keys are the same for all summaries in summary, as they should be.
    print_keys = order_list(all_keys, default_keys)
    write_csv_from_list_of_dicts(output_root+'/Text/Summary/' + name + '_summary.csv', summary, print_keys, options)

#functions related to drawing wind rose.  Some can be moved inside other functions to clean up.
def linearize_r(ref_number, r_scale):
    return math.sqrt(float(ref_number) * r_scale)


def get_ref_radii(n, r_scale, total): #	draw reference circles
    ref_mag = 0.01 #1%
    ref_number = int(ref_mag * total)
    r1 = linearize_r(ref_number, r_scale)
    r2 = linearize_r(ref_number * 2, r_scale)
    return (r1, r2, ref_mag, ref_number)


def draw_inner_slice(f, r, theta0, theta1, color):
    SVG_rose_petal = '		<path d="M0 0 L{0:.3f} {1:.3f} A{2:.3f} {2:.3f} 0 0 0 {3:.3f} {4:.3f} L0 0" fill="{5}" stroke="none" />\n'
    x0 = math.sin(math.radians(theta0)) * r
    y0 = math.cos(math.radians(theta0)) * r
    x1 = math.sin(math.radians(theta1)) * r
    y1 = math.cos(math.radians(theta1)) * r
    f.write(SVG_rose_petal.format(x0, y0, r, x1, y1, color))


def draw_outer_slice(f, r1, r2, theta0, theta1, color):
    SVG_rose_petal = '		<path d="M{0:.3f} {1:.3f} L{2:.3f} {3:.3f} A{4:.3f} {4:.3f} 0 0 0 {5:.3f} {6:.3f} L{7:.3f} {8:.3f} A{9:.3f} {9:.3f} 0 0 0 {10:.3f} {11:.3f}" fill="{12}" stroke="none" />'
    x0 = math.sin(math.radians(theta0)) * r1
    y0 = math.cos(math.radians(theta0)) * r1
    x1 = math.sin(math.radians(theta1)) * r1
    y1 = math.cos(math.radians(theta1)) * r1
    x2 = math.sin(math.radians(theta0)) * r2
    y2 = math.cos(math.radians(theta0)) * r2
    x3 = math.sin(math.radians(theta1)) * r2
    y3 = math.cos(math.radians(theta1)) * r2
    f.write(SVG_rose_petal.format(x0, y0, x2, y2, r2, x3, y3, x1, y1, r1, x0, y0, color))


def ref_circle_svg(r, label):
    return '<circle cx="0" cy="0" r="' + str(r) + '" stroke="#125" fill="none" />\n\
	<text x="0" y="-' + str(r) + '" fill="#125">' + label + '</text>\n'


def draw_split_petal(f, r, r1, r2, t0, t1):
    if r <= r1:
        draw_inner_slice(f, r, t0, t1, '#123')
    else:
        draw_inner_slice(f, r1, t0, t1, '#123')
        if r <= r2:
            draw_outer_slice(f, r1, r, t0, t1, '#456')
        else:
            draw_outer_slice(f, r1, r2, t0, t1, '#456')
            draw_outer_slice(f, r2, r, t0, t1, '#89A')


def draw_petal(f, r, t0, t1, color):
    draw_inner_slice(f, r, t0, t1, color)


def append_rose(data, f, radius, r_scale, n, split, r1, r2, color, area_correct = True):
    th_delta = float(360) / n
    f.write('	<g transform="rotate(180,0,0)">\n')
    for i in range(n):
        value = data[i]
        if value > 0:
            theta1 = th_delta * i * (-1)
            theta0 = theta1 - th_delta
            if area_correct: r = linearize_r(float(value), r_scale)
            else: r = value * r_scale
            #currently some wasted mismatch between these two cases... don't need r1,r2 for draw_petal, and don't need color for draw_split_petal
            if split:
                draw_split_petal(f, r, r1, r2, theta0, theta1)
            else:
                draw_petal(f, r, theta0, theta1, color)
    f.write('	</g>\n')


def draw_rose(binned):
    radius = 50
    total = binned['n']
    n = len(binned['data'])
    r_scale = float(radius * radius) / total * n
    print("  Drawing rose for " + str(binned['name']) + "with sqrt(r_scale) = " + str(math.sqrt(r_scale)))
    f = open(output_root+'/Visuals/Characterize/Roses/' + binned['name'] + '_rose.svg', 'w')
    f.write(svg_header(radius * 2, radius * 2))
    (r1, r2, ref_mag, ref_number) = get_ref_radii(n, r_scale, total)
    f.write('<g transform="rotate(0,0,0) translate(' + str(radius) + ',' + str(radius) + ')">\n')
    append_rose(binned['data'], f, radius, r_scale, n, True, r1, r2, '#123') #color not actually used
    f.write(ref_circle_svg(r1, str(round(ref_mag * 100, 1)) + '%, ' + str(ref_number) + ' observations'))
    f.write(ref_circle_svg(r2, str(round(ref_mag * 200, 1)) + '%, ' + str(ref_number * 2) + ' observations'))
    f.write('</g></svg>')


def draw_multi_rose(type_name, list_binned, report, sub_folder = 'none'): #Assume first rose sets scale for others
    if report: print "  Drawing", type_name, "multi-rose for", list_binned[0]['name']
    radius = 50
    total = list_binned[0]['n'] #doesn't seem right...
    n = len(list_binned[0]['data'])
    if total > 0 and n > 0:
        r_scale = float(radius * radius) / total * n
        if sub_folder != 'none': path_append = sub_folder+'/'
        else: path_append = ''
        f = open(output_root+'/Visuals/Characterize/Roses/'+ path_append + list_binned[0]['name'] + '_' + type_name + '_multi_rose.svg', 'w')
        f.write(svg_header(radius * 2, radius * 2))
        color_list = ['rgb(202,197,189)', 'rgb(169,109,76)', 'rgb(134,38,15)', 'rgb(20,0,0)']
        n_color = len(color_list)
        c_i = 0
        f.write('<g transform="rotate(0,0,0) translate(' + str(radius) + ',' + str(radius) + ')">\n')
        for binned in list_binned:
            color = color_list[c_i]
            append_rose(binned['data'], f, radius, r_scale, n, False, 0, 0, color)
            c_i = (c_i + 1) % n_color
        (r1, r2, ref_mag, ref_number) = get_ref_radii(n, r_scale, total)
        f.write(ref_circle_svg(r1 / 10, str(round(ref_mag, 3)) + '%, ' + str(
            ref_number / 100) + ' observations')) #1/100 of the ref provided by r1
        f.write(ref_circle_svg(r1, str(round(ref_mag * 100, 1)) + '%, ' + str(ref_number) + ' observations'))
        f.write(ref_circle_svg(r2, str(round(ref_mag * 200, 1)) + '%, ' + str(ref_number * 2) + ' observations'))
        f.write('</g></svg>')
    else:
        print "WARNING: No multi-rose generated because there didn't seem to be any data in the first range."

def draw_percentile_wind_rose((data,writeable_data), name, area_correct = True, sub_folder = 'none'):
    write_csv_from_list_of_dicts(output_root+'/Text/Rose_data/percentile_rose_{0}.csv'.format(name), writeable_data)
    n = len(writeable_data[0]) - 1
    radius = 200
    if area_correct: r_scale = float(radius * radius) / n
    else: r_scale = radius / n
    if sub_folder != 'none': path_append = sub_folder+'/'
    else: path_append = ''
    f = open(output_root+'/Visuals/Characterize/Roses/{0}{1}_percentile_rose.svg'.format(path_append, name), 'w')
    f.write(svg_header(400,400))
    color = ['rgb(43,140,190)','rgb(123,204,196)','rgb(186,228,188)','rgb(240,249,232)']
    P_keys = data.keys()
    n_P = len(P_keys)
    color = {P_keys[i]:color[i%len(color)] for i in range(n_P)}
    #If data is an ordered dict, it would be good to reverse the order.
    f.write('<g transform="translate(200,200)">\n\t<g>\n')
    for P,values in data.iteritems():
        append_rose(values,f,radius,r_scale,len(values),False,0,0,color[P], area_correct)
    f.write('\t</g>\n\t<g>\n')
    if area_correct:
        f.write(ref_circle_svg(linearize_r(velocity(40,'knots'),r_scale),"40 knots"))
        f.write(ref_circle_svg(linearize_r(velocity(20,'knots'),r_scale),"20 knots"))
        f.write(ref_circle_svg(linearize_r(velocity(10,'knots'),r_scale),"10 knots"))
        f.write(ref_circle_svg(linearize_r(velocity(5,'knots'),r_scale),"5 knots"))
    else: #linear
        f.write(ref_circle_svg(velocity(40,'knots')*r_scale,"40 knots"))
        f.write(ref_circle_svg(velocity(20,'knots')*r_scale,"20 knots"))
        f.write(ref_circle_svg(velocity(10,'knots')*r_scale,"10 knots"))
        f.write(ref_circle_svg(velocity(5,'knots')*r_scale,"5 knots"))
    f.write('\t</g>\n</g>\n')
    f.write('</svg>\n')


def svg_header(width, height):
    return '<?xml version="1.0" standalone="no"?>\n\
        <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n\
        <svg xmlns="http://www.w3.org/2000/svg" version="1.1" width ="' + str(width) + '" height="' + str(
        height) + '" viewBox="0 0 ' + str(width) + ' ' + str(height) + '">\n'


def svg_path(path_string, color): return '<path d="' + path_string + '" fill="none" stroke="' + color + '" />\n'


def svg_rect(x, y, width, height, color): return '<rect x="' + str(round(x, 2)) + '" y="' + str(
    round(y, 2)) + '" width="' + str(round(width, 2)) + '" height="' + str(
    round(height, 2)) + '" style="fill:' + color + '; stroke:none" />\n'


def draw_weather_boxplots(averages):
    print "  Drawing boxplots for ", averages['name']
    obs_keys = averages['data'][0].keys()
    n_plots = len(obs_keys)
    v_scaler_dict = {"temp": 22.22222, "wtemp":22.22222, "wave": 9.144, "wind": 15.4333, "gust": 15.4333, "shear": 15.4333, "steep": 0.0025, "vis": 16.0934, "cover": 1.0,
                     "ceil": 1.524, "period": 10, 'dir': 180.0, "wind_chill": 22.22222}
    v_offset = 500
    pad = 1.0 #points between boxes
    width = 9.0 #point width of boxes
    h_scaler = pad + width
    h_step = h_scaler * 20
    total_width = h_step * n_plots
    # add a circle at mean: 		<circle cx="{3:.1f}" cy="{8:.1f}" r="'+str(h_scaler/4)+'" style="fill:#F8A;" />\n
    SVG_boxplot_template = '	<g><rect x="{0:.1f}" y="{1:.1f}" width="' + str(width) + '" height="{2:.1f}" style="fill:rgb(68,10,0);"/>\n\
        <path d="M{3:.1f} {4:.1f} L{3:.1f} {5:.1f}" fill="none" stroke="rgb(68,10,0)" stroke-width="1" />\n\
        <path d="M{0:.1f} {6:.1f} L{7:.1f} {6:.1f}" fill="none" stroke="#FFF" stroke-width="1" />\n\
        <path d="M{9:.1f} {11:.1f} L{10:.1f} {11:.1f}" fill="none" stroke = "rgb(68,10,0)" stroke-width = "1" />\n\
        <path d="M{9:.1f} {12:.1f} L{10:.1f} {12:.1f}" fill="none" stroke = "rgb(68,10,0)" stroke-width = "1" />\n\
        <path d="M{13:.1f} {15:.1f} L{14:.1f} {15:.1f}" fill="none" stroke = "rgb(68,10,0)" stroke-width = "1" />\n\
        <path d="M{13:.1f} {16:.1f} L{14:.1f} {16:.1f}" fill="none" stroke = "rgb(68,10,0)" stroke-width = "1" />\n\
        </g>\n'
    f = open(output_root+'/Visuals/Characterize/Boxplots/' + averages['name'] + '_box_whisker.svg', 'w')
    f.write(svg_header(total_width, 1000))
    h_base = 0
    reference = -100.0
    f.write('<path d="M0 ' + str(v_offset) + ' L' + str(total_width) + ' ' + str(
        v_offset) + '" stroke="#002" fill="none" />')
    f.write('<path d="M0 ' + str(v_offset + reference) + ' L' + str(total_width) + ' ' + str(
        v_offset + reference) + '" stroke="#002" fill="none" />')
    for key in obs_keys:
        f.write('<g>\n	<text x="' + str(h_base + h_step / 2) + '" y="' + str(
            v_offset + reference * 2) + '" text-anchor="middle">' + key + '</text>\n')
        try:
            v_scaler = reference / v_scaler_dict[key]
        except KeyError:
            v_scaler = -1.0
        f.write('<text x="' + str(h_base + h_step / 2) + '" y="' + str(
            v_offset + reference - 2) + '" text-anchor="middle">' + str(reference / v_scaler) + '</text>\n')
        total = 0
        for m in range(12):
            stats = averages['data'][m][key]
            if stats['median'] != 'none':
                p75 = stats['p75']
                mean = stats['ave']
                median = stats['median']
                minimum = stats['min']
                maximum = stats['max']
                mid_range = p75 - stats['p25']
                left = m * h_scaler + h_base
                f.write(SVG_boxplot_template.format(
                    left, #0: rect x, median path start x
                    p75 * v_scaler + v_offset, #1: rect y
                    math.fabs(mid_range * v_scaler), #2: rect height
                    left + width / 2, #3: whisker x, mean circle x
                    minimum * v_scaler + v_offset, #4: whisker y base
                    maximum * v_scaler + v_offset, #5: whisker y top
                    median * v_scaler + v_offset, #6: median path y
                    left + width, #7: median path end x
                    mean * v_scaler + v_offset, #8: mean circle y
                    left + width * 0.2, #9: cross-bar1 start x
                    left + width * 0.8, #10: cross-bar1 end x
                    stats['p5'] * v_scaler + v_offset, #11: 5% cross-bar y
                    stats['p95'] * v_scaler + v_offset, #12: 95% cross-bar y
                    left + width * 0.3, #13: cross-bar2 start x
                    left + width * 0.7, #14: cross-bar2 end x
                    stats['p2'] * v_scaler + v_offset, #15: 2% cross-bar y
                    stats['p98'] * v_scaler + v_offset    #16: 98% cross-bar y
                ))
            total += stats['n']
        f.write('	<text x="' + str(h_base + h_step / 2) + '" y="' + str(
            v_offset + reference * 3) + '" text-anchor="middle">' + str(total) + ' Observations</text>\n')
        f.write('</g>\n')
        h_base += h_step
    f.write('</svg>')


def draw_vis_graph(vis_month, max_proportion, x_scaler, y_scaler, thresholds, colors, name):
    print "  Drawing vis graph (v2) for", name
    f = open(output_root+'/Visuals/Characterize/Vis/' + name + '_plot.svg', 'w')
    y_max = max_proportion * y_scaler
    x_pad = 4.0
    x0 = 0
    total = []
    f.write(svg_header(600, 100))
    for month in range(12):
        month_total = 0
        for key in vis_month[month]:
            month_total += vis_month[month][key]
        total.append(month_total)
    for month in range(12):
        value_dict = vis_month[month]
        if len(value_dict) > 0:
            vd_keys = sorted(list(value_dict.keys())) #dictionary keys are in arbitrary order, but I need them sorted.
            right = vd_keys[-1] * x_scaler
            month_total = total[month]
            y = 0
            prev_x = 0
            f.write('<g transform="translate(' + str(x0) + ',0)">\n')
            for key in vd_keys:
                if key > thresholds[-1]:
                    color_index = -1
                else:
                    color_index = 0
                    while key > thresholds[color_index]: color_index += 1
                y_delta = float(value_dict[key]) / month_total * y_scaler #integral of delta should be (y_step - y_pad)
                width = key * x_scaler
                y += y_delta
                if y > y_max:
                    y_delta -= y - y_max
                    plot_y = 0
                else:
                    plot_y = y_max - y
                f.write(svg_rect(0, plot_y, width, y_delta, colors[color_index]))
            f.write('</g>\n')
            x0 += right + x_pad
    f.write('</svg>')


def draw_annual_matrix(merged,Y):
    start_time = time.time()
    block_width = 400.0
    block_height = 400.0

    x_min = min(merged['Years'])
    x_max = max(merged['Years'])
    x_bins = x_max-x_min+1
    Y_res = (Y['max']-Y['min']) / Y['bins']
    x_increment = block_width / x_bins
    y_scale = block_height / (Y['max'] - Y['min'])
    matrix = []
    lists_for_stats = []
    for i in range(x_bins):
        matrix.append([])
        lists_for_stats.append([])
        for j in range(Y['bins']):
            matrix[i].append(0)
    data_count = 0
    for hour in merged['data']:
        x = hour['datetime'].year
        y = hour[Y['name']]
        if y != 'none':
            data_count += 1
            x_index = x-x_min
            y_index = int(math.floor((y-Y['min'])/ Y_res))
            if y_index >= Y['bins']: y_index = -1
            try: matrix[x_index][y_index] += 1
            except IndexError:
                print x, x_index, y_index, x_bins, Y['bins'], merged['Years']
                raise Exception()
            lists_for_stats[x_index].append(y)
    if data_count > 0:
        stats = []
        for y_values in lists_for_stats:
            stats.append(simple_stats(y_values, dictionary=True))
        matrix = [[matrix]]
        f = open(output_root+'/Visuals/Characterize/Matrix/Annual/' + merged['name'] + '_'+Y['name']+'_matrix.svg', 'w')
        f.write(svg_header(block_width, block_height))
        f.write('<text x="-100" y="-100">Years on X Axis, {0} to {1}.  {2} on Y Axis, {3} to {4}. {5} values</text>\n'.format(x_min, x_max, Y['name'],Y['min'],Y['max'],data_count))
        append_matrix(f, matrix, block_width, block_height)
        append_curves(f, stats, x_increment, y_scale, Y['min'], block_height)
        f.write("</svg>")
        print "  Annual histogram took {0:.3f} seconds".format(time.time()-start_time)
    else: print "WARNING: No data for {0} so no annual matrix generated".format(Y['name'])


def draw_timeseries(merged, var, x_scale, y_scale):

    def init():
        path_string = ['M']
        first = True
        skip = False
        y_prev = -10000000 #A pretty unlikely value - only relevant if the first point shows up as equal to this.
        return path_string, first, skip, y_prev

    print "  Drawing time-series for",merged['name'],"for", var
    f = open(output_root+'/Visuals/Characterize/timeseries/' + merged['name'] + '_' + var + '_timeseries.svg', 'w')
    f.write(svg_header(1000,1000))
    base_date = datetime.datetime(2005, 1, 1, 0, 0)
    color = "#364"
    annotation = "#001"
    path_string, first, skip, y_prev = init()
    for row in merged['data']:
        x_base = row['datetime'] - base_date
        x = x_scale * (x_base.total_seconds()/3600)
        try:
            y = y_scale * row[var] #Throws an error if row[var] is not a number, in which case the path is broken appropriately.
            if y != y_prev:
                if first:
                    first = False
                    path_string.append("{0:.2f} {1:.2f}".format(x,y))
                elif skip: path_string.append("L{0:.2f} {1:.2f}L{2:.2f} {3:.2f}".format(x_prev, y_prev, x, y))
                else: path_string.append("L{0:.2f} {1:.2f}".format(x,y))
                skip = False
            else: skip = True
            y_prev = y
            x_prev = x
        except (ValueError, TypeError) as e:
            if len(path_string) > 1:
                if skip: path_string.append("L{0:.2f} {1:.2f}L{2:.2f} {3:.2f}".format(x_prev, y_prev, x, y))
                f.write(svg_path("".join(path_string), color))
                path_string, first, skip, y_prev = init()
    if len(path_string) > 1:
        if skip: path_string.append("L{0:.2f} {1:.2f}L{2:.2f} {3:.2f}".format(x_prev, y_prev, x, y))
        f.write(svg_path("".join(path_string), color))
    f.write(svg_path("M0 0L1000 0","#001"))
    f.write(svg_path("M0 {0:.2f}L1000 {0:.2f}".format(float(y_scale*10)),annotation))
    f.write('<text x="-20" y="{0:.2f}">10 standard units for {1}</text>'.format(float(y_scale*10),var) )
    for year in range(2008,2014):
        x = x_scale * ((datetime.datetime(year,1,1,0,0) - base_date).total_seconds())/3600
        f.write(svg_path("M{0} 0L{0} -4".format(x),annotation))
        f.write('<text x="{0}" y="15" text-anchor="start">{1}</text>\n'.format(x,year))
    f.write(hs.svg_close())


def init_multi_cycle():
    f = open(output_root+'/Visuals/RGA/Cycle/Multi/' + 'multi_cycle.svg', 'w')
    f.write(svg_header(1000,1000))
    return f

def init_multi_cycle_dict(key_list):
    cycle_dict = {}
    for key in key_list:
        f = open(output_root+'/Visuals/RGA/Cycle/Multi/{0}_multi_cycle.svg'.format(key), 'w')
        f.write(svg_header(1000,1000))
        cycle_dict.update([ (key, f) ])
    return cycle_dict

def close_svg(f):
    f.write(hs.svg_close())

#Draw annual pattern of red vs. green
def draw_cycle(cycle_data, additional_root=None, summer_winter_data = None, multi_cycle_dict = None, multi_cycle_subset = [], multi_cycle_loc = (0,0)):
    start_time = time.time()
    Years = sorted(cycle_data['Years']) #Years is now a sorted list instead of a set.
    if len(Years) > 0:
        h_scaler = 1.0
        v_scaler = 250.0
        comp_yr_v = 12
        comp_yr_space = 3
        comp_base = (len(Years)+1) * (comp_yr_v + comp_yr_space)
        plot_width = 366*h_scaler
        if additional_root: file_name = '{0}/Visuals/RGA/Cycle/{1}/{2}_cycle.svg'.format(output_root,additional_root,cycle_data['name'])
        else: file_name = '{0}/Visuals/RGA/Cycle/{2}_cycle.svg'.format(output_root,cycle_data['name'])
        f = open(file_name, 'w')
        f.write(svg_header(plot_width,v_scaler))
        cycle_svg_text, completeness_graphic_text = append_cycle(cycle_data,h_scaler,v_scaler,comp_yr_v,comp_yr_space,comp_base)
        f.write(cycle_svg_text)
        f.write(completeness_graphic_text)
        if summer_winter_data:
            winter_end_x = float(end_winter)*h_scaler
            summer_end_x = float(end_summer)*h_scaler
            summer_red_y = summer_winter_data['summer_red'] * v_scaler
            winter_red_y = summer_winter_data['winter_red'] * v_scaler
            summer_yellow_y = summer_winter_data['summer_yellow'] * v_scaler + summer_red_y
            winter_yellow_y = summer_winter_data['winter_yellow'] * v_scaler + winter_red_y
            f.write('<g>\n')
            f.write(hs.svg_h_line((0,winter_red_y),winter_end_x,"#201"))
            f.write(hs.svg_text(2,winter_red_y-3,"start","#211","Red:{0:.0f}%".format(summer_winter_data['winter_red']*100)))
            f.write(hs.svg_h_line((winter_end_x,summer_red_y),summer_end_x-winter_end_x,"#201"))
            f.write(hs.svg_text(winter_end_x+2,summer_red_y-3,"start","#211","Red:{0:.0f}%".format(summer_winter_data['summer_red']*100)))
            f.write(hs.svg_h_line((summer_end_x,winter_red_y),plot_width-summer_end_x,"#201"))
            f.write(hs.svg_text(summer_end_x+2,winter_red_y-3,"start","#211","Red:{0:.0f}%".format(summer_winter_data['winter_red']*100)))
            f.write(hs.svg_h_line((0,winter_yellow_y),winter_end_x,"#201"))
            f.write(hs.svg_text(2,winter_yellow_y-3,"start","#211","Yellow+Red:{0:.0f}%".format((1.0-summer_winter_data['winter_green'])*100)))
            f.write(hs.svg_h_line((winter_end_x,summer_yellow_y),summer_end_x-winter_end_x,"#201"))
            f.write(hs.svg_text(winter_end_x+2,summer_yellow_y-3,"start","#211","Yellow+Red:{0:.0f}%".format((1.0-summer_winter_data['summer_green'])*100)))
            f.write(hs.svg_h_line((summer_end_x,winter_yellow_y),plot_width-summer_end_x,"#201"))
            f.write(hs.svg_text(summer_end_x+2,winter_yellow_y-3,"start","#211","Yellow+Red:{0:.0f}%".format((1.0-summer_winter_data['winter_green'])*100)))
            f.write('</g>\n')
        if multi_cycle_dict:
            for key in multi_cycle_subset:
                multi_svg = [
                    '<g transform ="translate({0} {1})">\n'.format(multi_cycle_loc[0]*100,multi_cycle_loc[1]*100),
                    hs.svg_text(0,-20,"start",'#022',cycle_data['name']),
                    '\t<g transform="scale({0:.2f} {1:.2f})">\n'.format(100.0/(h_scaler*366),100.0/v_scaler),
                    cycle_svg_text,
                    "\t</g>\n</g>\n"
                ]
                multi_cycle_dict[key].write("".join(multi_svg)) #Writing to a totally separate file.
        for year in Years:
            y = v_scaler + comp_base - (comp_yr_v + comp_yr_space) * (year - Years[0]) + comp_yr_space
            f.write(hs.svg_text(-5,y,"end",black,str(year)))
        f.write(hs.svg_close())
        print "  Drawing cycle for: {0} took {1:.1f} seconds".format(cycle_data['name'],time.time()-start_time)


def append_cycle(cycle_data, h_scaler, v_scaler,comp_yr_v,comp_yr_space,comp_base):
    cycle_svg_text = ""
    completeness_graphic_text = ""
    Years = sorted(cycle_data['Years']) #Years is now a sorted list instead of a set.

    def get_color((value,bin)): #A hard-coded approach
        #Green, Yellow0, Yellow1, etc., Red0, Red1, etc.
        try:
            if bin[:5] == "Green": return greens_9[7]
            elif bin[:3] == "Red":
                return reds_8[int(value)]
            else: #Yellow
                return yellows_simple[int(value)]
        except ValueError as error_text:
            print error_text
            print value, bin
            raise Exception
        #except: return "rgb(1,0,4)" #Nearly black - error color

    def order_green_yellow_red(list_of_strings):
        list_of_strings.sort()
        red_list = []
        yellow_list = []
        green_list = []
        for item in list_of_strings:
            if item[1][:5] == "Green": green_list.append(item)
            elif item[1][:3] == "Red": red_list.append(item)
            else: yellow_list.append(item)
        return green_list + yellow_list + red_list, green_list, yellow_list, red_list

    if len(Years) > 0:
        bins = cycle_data['bins']
        cycle_graphic_svg = []
        completeness_graphic_svg = []
        valid_RG_values = set([])
        re_pattern = re.compile('(Red|Yellow|Green)(\d+)')
        for bin in bins: #Inefficient, but robust
            for key in bin:
                regex=re.match(re_pattern,key)
                if regex:
                    try: valid_RG_values.add((int(regex.groups(0)[1]),key))
                    except ValueError: valid_RG_values.add((0,key))
        valid_RG_values = list(valid_RG_values)
        valid_RG_values, green_list, yellow_list, red_list = order_green_yellow_red(valid_RG_values)
        red_tally = 0
        yellow_tally = 0
        green_tally = 0
        all_tally = 0
        completeness_graphic_svg.append('<g>\n')
        cycle_graphic_svg.append('<g>\n')
        for bin in bins:
            complete_observations = bin['complete'] #For the main cycle graphic
            base = v_scaler
            x = h_scaler * bin['start']
            width = h_scaler * bin['end'] - x
            if complete_observations > 0:
                for key in valid_RG_values:
                    try:
                        count = bin[key[1]]
                        if count > 0:
                            all_tally += count
                            if key in green_list: green_tally += count
                            elif key in yellow_list: yellow_tally += count
                            elif key in red_list: red_tally += count
                            color = get_color(key)
                            height = float(count) / complete_observations * v_scaler
                            top = base - height
                            base = top
                            cycle_graphic_svg.append(hs.svg_rect(x,top,width,height,color) + '\n')
                    except KeyError:
                        pass #This valid RG value doesn't actually occur in this bin
                for year in Years:
                    try:
                        total_hours = float(bin['total_hours_{0}'.format(year)])#The number of hours in one bin - for drawing completeness histogram below cycle
                        greens = safe_get_float('{0}_{1}_complete'.format(year,'Green'),bin)
                        yellows = safe_get_float('{0}_{1}_complete'.format(year,'Yellow'),bin)
                        reds = safe_get_float('{0}_{1}_complete'.format(year,'Red'),bin)
                        h_green = float(greens) / total_hours * comp_yr_v
                        h_yellow = float(yellows) / total_hours * comp_yr_v
                        h_red = float(reds) / total_hours * comp_yr_v
                        h_nothing = comp_yr_v - h_green - h_yellow - h_red
                        top = v_scaler + comp_base - ((comp_yr_v + comp_yr_space) * (year - Years[0]) + comp_yr_space) + h_nothing
                        completeness_graphic_svg.append(hs.svg_rect(x, top, width, h_red, classic_red) + '\n')
                        top += h_red
                        completeness_graphic_svg.append(hs.svg_rect(x, top, width, h_yellow, classic_yellow) + '\n')
                        top += h_yellow
                        completeness_graphic_svg.append(hs.svg_rect(x, top, width, h_green, greens_9[7]) + '\n')
                    except KeyError: pass
        completeness_graphic_svg.append('</g>\n')
        cycle_graphic_svg.append('</g>\n')
        if all_tally > 0:
            green_percent = float(green_tally)/all_tally
            yellow_percent = float(yellow_tally)/all_tally
            red_percent = float(red_tally)/all_tally
            cycle_graphic_svg.append(hs.svg_text(5,20,'start','#144','R:{0:.0f}%'.format(red_percent*100)))
            cycle_graphic_svg.append(hs.svg_text(5,40,'start','#144','Y:{0:.0f}%'.format(yellow_percent*100)))
            cycle_graphic_svg.append(hs.svg_text(5,60,'start','#144','G:{0:.0f}%'.format(green_percent*100)))
        cycle_svg_text = "".join(cycle_graphic_svg)
        completeness_graphic_text = "".join(completeness_graphic_svg)
    return cycle_svg_text, completeness_graphic_text

def draw_simple_summary(summary):
    y = 0
    h_scale = 150
    bar_height = 4 #16
    text_shift = 13
    bar_h_spacing = 30
    bar_v_spacing = 4 #30
    f = open(output_root+'/Visuals/RGA/Summary/summary.svg', 'w')
    f.write(svg_header(100,100))
    f.write(hs.svg_text(0,-20,"start",black,"Summer"))
    f.write(hs.svg_text(h_scale+bar_h_spacing,-20,"start",black,"Winter"))
    f.write(hs.svg_text(2*(h_scale+bar_h_spacing),-20,"start",black,"Overall"))
    for row in summary:
        x=0
        f.write('\t<g>\n')
        f.write(hs.svg_text(x-5,y+text_shift,"end",black,row['name']))
        try:
            summer_green_width = row['summer_green']*h_scale
            summer_yellow_width = row['summer_yellow']*h_scale
            summer_red_width = row['summer_red']*h_scale
            winter_green_width = row['winter_green']*h_scale
            winter_yellow_width = row['winter_yellow']*h_scale
            winter_red_width = row['winter_red']*h_scale
            overall_green_width = row['overall_green']*h_scale
            overall_yellow_width = row['overall_yellow']*h_scale
            overall_red_width = row['overall_red']*h_scale
            f.write(hs.svg_rect(x,y,summer_green_width,bar_height,classic_green))
            f.write(hs.svg_text(x+2,y+text_shift,"start",black,'{0:.0f}%'.format(row['summer_green']*100)))
            x += summer_green_width
            f.write(hs.svg_rect(x,y,summer_yellow_width,bar_height,classic_yellow))
            f.write(hs.svg_text(x+2,y+text_shift,"start",black,'{0:.0f}%'.format(row['summer_yellow']*100)))
            x += summer_yellow_width
            f.write(hs.svg_rect(x,y,summer_red_width,bar_height,classic_red))
            f.write(hs.svg_text(x+2,y+text_shift,"start",black,'{0:.0f}%'.format(row['summer_red']*100)))
            x += bar_h_spacing + summer_red_width
            f.write(hs.svg_rect(x,y,winter_green_width,bar_height,classic_green))
            f.write(hs.svg_text(x+2,y+text_shift,"start",black,'{0:.0f}%'.format(row['winter_green']*100)))
            x += winter_green_width
            f.write(hs.svg_rect(x,y,winter_yellow_width,bar_height,classic_yellow))
            f.write(hs.svg_text(x+2,y+text_shift,"start",black,'{0:.0f}%'.format(row['winter_yellow']*100)))
            x += winter_yellow_width
            f.write(hs.svg_rect(x,y,winter_red_width,bar_height,classic_red))
            f.write(hs.svg_text(x+2,y+text_shift,"start",black,'{0:.0f}%'.format(row['winter_red']*100)))
            x += bar_h_spacing + winter_red_width
            f.write(hs.svg_rect(x,y,overall_green_width,bar_height,classic_green))
            f.write(hs.svg_text(x+2,y+text_shift,"start",black,'{0:.0f}%'.format(row['overall_green']*100)))
            x += overall_green_width
            f.write(hs.svg_rect(x,y,overall_yellow_width,bar_height,classic_yellow))
            f.write(hs.svg_text(x+2,y+text_shift,"start",black,'{0:.0f}%'.format(row['overall_yellow']*100)))
            x += overall_yellow_width
            f.write(hs.svg_rect(x,y,overall_red_width,bar_height,classic_red))
            f.write(hs.svg_text(x+2,y+text_shift,"start",black,'{0:.0f}%'.format(row['overall_red']*100)))
        except TypeError: pass
        f.write('\t</g>\n')
        y += bar_v_spacing
    f.write(hs.svg_close())



def initialize_svg_calendar(Years, name):
    Years = sorted(Years) #Years is now a sorted list instead of a set.
    year_0 = Years[0]
    scaler = 1 #number of points (pixels) per hour in vertical, and per day in horizontal
    space_between_years = 10
    year_incr = 24 * scaler + space_between_years
    start_year = year_incr * len(Years)
    SVG_rect_template = '	<rect x="{0:.1f}" y="{1:.1f}" width="' + str(
        scaler) + '" height="{2:.1f}" style="fill:{3};"/>'
    f = open(output_root+'/Visuals/RGA/Calendar/' + name + '_calendar.svg', 'w')
    f.write(svg_header(366 * scaler, start_year + year_incr))
    return ((Years, year_0, scaler, space_between_years, f, SVG_rect_template, start_year, year_incr))

#draw rectangular calendar with two colors
def RG_calendar(RGA):
    n = len(RGA['data'])
    print "  Drawing calendar for: " + RGA['name'] + " with " + str(n) + " items."
    if n > 0:
        (Years, year_0, scaler, space_between_years, f, SVG_rect_template, start_year,
         year_incr) = initialize_svg_calendar(RGA['Years'], RGA['name'])

        def write_svg_rect(f_svg, x, y, h, case):
            if case == "red":
                f_svg.write(SVG_rect_template.format(x, y, h, classic_red) + '\n')
            elif case == "green":
                f_svg.write(SVG_rect_template.format(x, y, h, classic_green) + '\n')

        previous_case = "default" #the case variable is used to check if the same conditions are repeated.
        previous_day = -1
        first_datapoint = True
        repeat_count = 0
        this_year = 0
        f.write('<g>')
        for hour in RGA['data']:
            hour_of_day = hour['datetime'].timetuple().tm_hour
            this_day = hour['datetime'].timetuple().tm_yday
            year = hour['datetime'].timetuple().tm_year
            case = hour['conditions'] #red, green, or ambiguous
            if case == previous_case and this_day == previous_day:
                repeat_count += 1
            else:
                if not first_datapoint:
                    write_svg_rect(f, previous_day * scaler, upper_hour * scaler + start_year - year_offset,
                                   repeat_count * scaler, previous_case)
                else:
                    first_datapoint = False
                upper_hour = hour_of_day
                repeat_count = 1
                year_offset = year_incr * (year - year_0)
                if year != this_year:
                    f.write('</g><g>')
                    f.write('<text x="-50" y="' + str(
                        start_year - year_offset + 12 * scaler) + '" color = "rgb(20,0,0)">' + str(year) + '</text>')
                    f.write('<rect x="0" y="' + str(start_year - year_offset) + '" width="' + str(
                        datetime.datetime(year, 12, 31, 0, 0).timetuple().tm_yday * scaler) + '" height="' + str(
                        24 * scaler) + '" style="fill: none; stroke: #B3F;"/>')
                    this_year = year
            previous_case = case
            previous_day = this_day
        write_svg_rect(f, previous_day * scaler, upper_hour * scaler + start_year - year_offset, repeat_count * scaler,
                       previous_case) #handle dangling data at end of dataset
        f.write('</g>')
        f.write("</svg>")


def completeness_calendar(merged):
    n = len(merged['data'])
    if n > 0:
        (Years, year_0, scaler, space_between_years, f, SVG_rect_template, start_year,
         year_incr) = initialize_svg_calendar(merged['Years'], merged['name'] + '_completeness')
        print "  Drawing completeness calendar for: " + merged['name']

        def write_svg_rect(f_svg, x, y, h, case):
            if case == "buoy_complete":
                f_svg.write(SVG_rect_template.format(x, y, h, '#129') + '\n')
            elif case == "vis_complete":
                f_svg.write(SVG_rect_template.format(x, y, h, '#A21') + '\n')
            elif case == "wwt_complete":
                f_svg.write(SVG_rect_template.format(x, y, h, '#55C') + '\n')
            elif case == "some_data":
                f_svg.write(SVG_rect_template.format(x, y, h, '#ABC') + '\n')

        previous_case = "default" #the case variable is used to check if the same conditions are repeated.
        previous_day = -1
        first_datapoint = True
        repeat_count = 0
        this_year = 0
        f.write('<g>')
        for hour in merged['data']:
            hour_of_day = hour['datetime'].timetuple().tm_hour
            this_day = hour['datetime'].timetuple().tm_yday
            year = hour['datetime'].timetuple().tm_year
            if hour['buoy_complete']:
                case = 'buoy_complete'
            elif hour['vis_complete']:
                case = 'vis_complete'
            elif hour['wwt_complete']:
                case = 'wwt_complete'
            elif hour['empty']:
                case = 'empty'
            else:
                case = 'some_data'
            if case == previous_case and this_day == previous_day:
                repeat_count += 1
            else:
                if not first_datapoint:
                    write_svg_rect(f, previous_day * scaler, upper_hour * scaler + start_year - year_offset,
                                   repeat_count * scaler, previous_case)
                else:
                    first_datapoint = False
                upper_hour = hour_of_day
                repeat_count = 1
                year_offset = year_incr * (year - year_0)
                if year != this_year:
                    f.write('</g><g>')
                    f.write('<text x="-50" y="' + str(
                        start_year - year_offset + 12 * scaler) + '" color = "rgb(20,0,0)">' + str(year) + '</text>')
                    f.write('<rect x="0" y="' + str(start_year - year_offset) + '" width="' + str(
                        datetime.datetime(year, 12, 31, 0, 0).timetuple().tm_yday * scaler) + '" height="' + str(
                        24 * scaler) + '" style="fill: none; stroke: #B3F;"/>')
                    this_year = year
            previous_case = case
            previous_day = this_day
        write_svg_rect(f, previous_day * scaler, upper_hour * scaler + start_year - year_offset, repeat_count * scaler,
                       previous_case) #handle dangling data at end of dataset
        f.write('</g>')
        f.write("</svg>")


def station_kml(summary):
    f = open(output_root+'/Text/Summary/summary.kml', 'w')
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n' +
            '<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">\n' +
            '<Document>\n<name>RGA summary</name>\n<Folder><name>RGA summary</name>\n')
    for row in summary:
        f.write('<Placemark>\n	<name>' + row['name'] + '</name>\n	<Point>\n		<coordinates>' + str(
            row['lon']) + ',' + str(row['lat']) + ',0</coordinates>\n		</Point>\n	</Placemark>\n')
    f.write('</Folder></Document></kml>')


def draw_daylight(dawn_dusk,
                  name): #Not sure how this will handle high latitudes where there are days with no dawn or dusk.
    print "  Drawing daylight for", name
    v_scaler = 120.0
    h_scaler = 1.0
    path_list = ['M',
                 'M'] #In the simplest scenario, there's one path for dawn and one for dusk.  But this is not always so.
    dawn_i = 0
    dusk_i = 1
    start = True
    for day in range(366): #These are midnights... including two new-years, so +1 days.
        x = h_scaler * day
        if dawn_dusk[day]['test']:
            dawn = dawn_dusk[day]['dawn']
            dusk = dawn_dusk[day]['dusk']
            y_dawn = v_scaler * dawn
            y_dusk = v_scaler * dusk
            if start:
                dawn_test = y_dawn
                dusk_test = y_dusk
                start = False
            else:
                path_list[dawn_i] += 'L'
                path_list[dusk_i] += 'L'
            if math.fabs(
                            y_dawn - dawn_test) > 0.5: #The path needs to be broken.  Tricky part is to make the path extend slightly beyond the space so that Illustrator's divide tool will have desired effect.
                if y_dawn > dawn_test:
                    old_y = y_dawn - v_scaler
                    new_y = dawn_test + v_scaler
                else:
                    old_y = y_dawn + v_scaler
                    new_y = dawn_test - v_scaler
                path_list[dawn_i] += str(round(x, 3)) + ' ' + str(round(old_y, 3))
                path_list.append('M' + str(round(x - 1, 3)) + ' ' + str(round(new_y, 3)) + ' L')
                dawn_i = len(path_list) - 1
            if math.fabs(y_dusk - dusk_test) > 0.5:
                if y_dusk > dusk_test:
                    old_y = y_dusk - v_scaler
                    new_y = dusk_test + v_scaler
                else:
                    old_y = y_dusk + v_scaler
                    new_y = dusk_test - v_scaler
                path_list[dusk_i] += str(round(x, 3)) + ' ' + str(round(old_y, 3))
                path_list.append('M' + str(round(x - 1, 3)) + ' ' + str(round(new_y, 3)) + ' L')
                dusk_i = len(path_list) - 1
            path_list[dawn_i] += str(round(x, 3)) + ' ' + str(round(y_dawn, 3)) + ' '
            path_list[dusk_i] += str(round(x, 3)) + ' ' + str(round(y_dusk, 3)) + ' '
            dawn_test = y_dawn
            dusk_test = y_dusk
        else:
            while not dawn_dusk[day]['test'] and day < 365: day += 1
    f = open(output_root+'/Visuals/Characterize/Daylight/' + name + '_daylight.svg', 'w')
    width = h_scaler * 365
    f.write(svg_header(width, v_scaler))
    f.write('<g transform="scale(1,-1) translate(0,-120)">')
    f.write(svg_rect(0, 0, width, v_scaler, '#BBB'))
    for path in path_list:
        f.write(svg_path(path, '#123'))
    f.write('</g></svg>')

def draw_timeseries_comparison(ts_summary):
    start_time = time.time()
    print "  Drawing timeseries summary.",

    def extrapolate_to_0((x1,y1),(x2,y2)):
        slope = (float(y2)-y1)/(float(x2)-x1)
        y = y1 - slope * x1
        if y > 1: y = 1 #These are %, so you can't extrapolate to >1
        return (0, y)

    def trans_raw(point, x_off=0, y_off=0, x_scale=1, y_scale=1):
        return (float(point[0])*x_scale + x_off, float(point[1])*y_scale*-1 + y_off+y_scale)

    ranges = sorted(timeseries_range_list)
    transforms = {"x_off":0, "y_off":0, "x_scale":3, "y_scale":120}
    x_jump = 100
    y_jump = 200
    columns = 10
    f = open(output_root+'/Visuals/RGA/timeseries_grid.svg', 'w')
    f.write(svg_header(1000, 1000))
    for i,row in enumerate(ts_summary):
        f.write('<g>\n')
        f.write(hs.svg_rect(
            transforms['x_off'],
            transforms['y_off'],
            transforms['x_scale']*ranges[-1],
            transforms['y_scale'],
            classic_red
        ))
        f.write(hs.svg_text(transforms['x_off'],transforms['y_off'],'start',black,row['name']))
        yellow_keys = ['Green_or_Yellow_{0:02d}_best'.format(x) for x in ranges]
        green_keys = ['Green_{0:02d}_best'.format(x) for x in ranges]
        extrapolated_yellow_0 = extrapolate_to_0((ranges[0],row[yellow_keys[0]]),(ranges[1],row[yellow_keys[1]]))
        extrapolated_green_0 = extrapolate_to_0((ranges[0],row[green_keys[0]]),(ranges[1],row[green_keys[1]]))
        yellow_points = [trans_raw((ranges[-1],0),**transforms),trans_raw((0,0),**transforms),trans_raw(extrapolated_yellow_0,**transforms)]
        green_points = [trans_raw((ranges[-1],0),**transforms),trans_raw((0,0),**transforms),trans_raw(extrapolated_green_0,**transforms)]
        for j,number in enumerate(ranges):
            yellow_points.append(trans_raw((number,row[yellow_keys[j]]),**transforms))
            green_points.append(trans_raw((number,row[green_keys[j]]),**transforms))
        yellow_points.append(trans_raw((ranges[-1],0),**transforms))
        green_points.append(trans_raw((ranges[-1],0),**transforms))
        f.write(hs.filled_svg_path_from_points(yellow_points,classic_yellow))
        f.write(hs.filled_svg_path_from_points(green_points,classic_green))
        for number in timeseries_display_ranges:
            if number in ranges:
                j = ranges.index(number)
                yellow_p = row[yellow_keys[j]]
                green_p = row[green_keys[j]]
                yellow_center = trans_raw((number, yellow_p),**transforms)
                green_center = trans_raw((number, green_p),**transforms)
                f.write(hs.svg_circle(yellow_center,1.5,b_0))
                x,y = yellow_center
                f.write(hs.svg_text(x,y,'start',b_1, '{0:.0f}%'.format(yellow_p*100)))
                f.write(hs.svg_circle(green_center,1.5,b_0))
                x,y = green_center
                f.write(hs.svg_text(x,y,'start',b_1, '{0:.0f}%'.format(green_p*100)))
            else: print "WARNING: Reference number ({0}) not in range, list ({1}) - not plotted.".format(number,ranges)
        if (i+1)%columns: transforms["x_off"] += x_jump
        else:
            transforms["x_off"] = 0
            transforms["y_off"] += y_jump
        f.write('</g>\n')
    f.write(hs.svg_close())
    print "({0:.2f} seconds)".format(time.time()-start_time)

def draw_limits_graphic():
    tactic_spacing = 60
    bar_length = 300
    bar_height = 8
    tactics = [name for name in primary_RGAs]
    type_settings = {
        'wind':{'min_text':'0',     'max_text':'30 m/s','y_off':0},
        'wave':{'min_text':'0',     'max_text':'6 m',   'y_off':10},
        'ice': {'min_text':0,       'max_text':'100 %', 'y_off':20},
        'vis': {'min_text':0,       'max_text':'6 km',  'y_off':30},
        'cold':{'min_text':'-50 C', 'max_text':'0 C',   'y_off':40}
    }
    for type in type_settings.values():
        type.update([('max',smart_units(type['max_text']))])
        type.update([('min',smart_units(type['min_text']))])
    colors = {'Green':classic_green, 'Yellow':classic_yellow, 'Red':classic_red}
    component_organization_dict = {}
    for component in component_list:
        for thing, info in component.iteritems():
            try: component_organization_dict[info['type']].append(info['name'])
            except KeyError: component_organization_dict.update([(info['type'],[info['name']])])

    def parse_params(param_string):
        inequalities = ['<','>','=','<=','>=','!=']
        input_parts = param_string.split(';')
        transition_dict = {'Green':{'top':None,'bottom':None}, 'Yellow':{'top':None,'bottom':None}, 'Red':{'top':None,'bottom':None}}
        for part in input_parts:
            items = clean_string_list(part.split(' '))
            if items[0] not in acceptable_values: raise RuntimeError('Nonsense: {0} is not a possible output'.format(items[0]))
            if items[1] not in inequalities: raise RuntimeError('Bad inequality: {0}'.format(items[1]))
            if items[2] in zero: comparison_value = 0.0
            else: comparison_value = smart_units('{0} {1}'.format(items[2],items[3]))
            if items[1] in ['<', '<=']:
                transition_dict[items[0]]['top'] = comparison_value
            elif items[1] in ['>', '>=']:
                transition_dict[items[0]]['bottom'] = comparison_value
        biggest = -1.0*sys.float_info.max, None
        smallest = sys.float_info.max, None
        unused = ['Green','Yellow','Red']
        for color,t_b_dict in transition_dict.iteritems():
            if t_b_dict['top'] is not None and t_b_dict['top'] < smallest[0]:
                smallest = t_b_dict['top'], color
                if color in unused: unused.pop(unused.index(color))
            if t_b_dict['bottom'] is not None and t_b_dict['bottom'] > biggest[0]:
                biggest = t_b_dict['bottom'],color
                if color in unused: unused.pop(unused.index(color))
        transition_dict[smallest[1]]['bottom'] = -1.0*sys.float_info.max
        transition_dict[biggest[1]]['top'] = sys.float_info.max
        if len(unused) > 1: raise RuntimeError("Poorly constrained - can't make limit graphic")
        elif len(unused) == 1:
            transition_dict[unused[0]]['top'] = biggest[0]
            transition_dict[unused[0]]['bottom'] = smallest[0]
        return transition_dict

    tactic_svg = open(output_root+'/Visuals/Limits/tactic_limit_graphic.svg', 'w')
    tactic_svg.write(hs.svg_header(1000,1000))
    component_svg = open(output_root+'/Visuals/Limits/component_limit_graphic.svg', 'w')
    component_svg.write(hs.svg_header(1000,1000))
    for type, setting in type_settings.iteritems():
        component_svg.write(hs.svg_text(0,type_settings[type]['y_off']*10-4,'middle','#001',setting['min_text']))
        component_svg.write(hs.svg_text(bar_length,type_settings[type]['y_off']*10-4,'middle','#001',setting['max_text']))
        component_svg.write(hs.svg_text(bar_length/2,type_settings[type]['y_off']*10-8,'middle','#001',type))
    for component in component_list:
        for thing, info in component.iteritems():
            try:
                transitions = parse_params(info['params'][0])
                conventional = True
            except (AttributeError, IndexError):
                conventional = False
            if conventional:
                tactic_svg.write('\t<g>\n')
                component_svg.write('\t<g>\n')
                type = info['type']
                min = type_settings[type]['min']
                max = type_settings[type]['max']
                component_labeled = False
                tactic_labeled = False
                tactic_labeled_for_components = False
                for kind in ['Green','Yellow','Red']:
                    if transitions[kind]['top'] > max:
                        if transitions[kind]['bottom'] > max:
                            bottom = None
                            top = None
                        else: top = max
                    else: top = transitions[kind]['top']
                    if transitions[kind]['bottom'] < min:
                        if transitions[kind]['top'] < min:
                            bottom = None
                            top = None
                        else: bottom = min
                    else: bottom = transitions[kind]['bottom']
                    if top is not None and bottom is not None:
                        x = (bottom-min)/(max-min)*bar_length
                        width = (top-bottom)/(max-min)*bar_length
                        component_y = type_settings[type]['y_off']*10 + component_organization_dict[type].index(info['name'])*10
                        component_svg.write(hs.svg_rect(x,component_y,width,bar_height,colors[kind]))
                        if not component_labeled:
                            component_svg.write(hs.svg_text(bar_length + 10,component_y+bar_height,'start','#100',info['name']))
                            component_labeled = True
                        for tactic in info['tactics']:
                            tactic_number = tactics.index(tactic)
                            tactic_y = tactic_number * tactic_spacing + type_settings[type]['y_off']
                            tactic_svg.write(hs.svg_rect(x,tactic_y,width,bar_height,colors[kind]))
                            if not tactic_labeled:
                                tactic_svg.write(hs.svg_text(-120,tactic_y+bar_height,'start','#010',"{0}: {1}".format(tactic,info['name'])))
                            if not tactic_labeled_for_components:
                                component_svg.write(hs.svg_text(-150+tactic_number*10,component_y+bar_height,'start','#010',tactic))
                                component_svg.write(hs.svg_circle((-150+tactic_number*10,component_y+bar_height),3,'#200'))
                        tactic_labeled_for_components = True
                        tactic_labeled = True
                tactic_svg.write('\t</g>\n')
                component_svg.write('\t</g>\n')

    tactic_svg.write(hs.svg_close())
    component_svg.write(hs.svg_close())