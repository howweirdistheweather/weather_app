import time
import math
from hig_utils import check_dirs
start_time = time.time()
from RGA_parse3 import (
    calculate_steepness,
    write_parsed,
    extract_csv_data,
    extract_onlns_data,
    extract_NBDC_data,
    extract_Weatherspark_data
)
from RGA_clean3 import (
    clean_extremes,
    clean_duplicates,
    fill_undefined_waves
)
from RGA_analyze3 import (
    merge,
    merge_RGA,
    monthly_averages,
    monthly_rose_data,
    summer_winter_rose_data,
    annual_percentile_wind_rose,
    component_velocity_exceedance_rose,
    wind_dir,
    dawn_dusk,
    cycle_data,
    rgi_calculations,
    compile_summer_winter,
    add_overall_summary,
    average_merge,
    completeness_percentages,
    RGA_timeseries_analysis
)
from populate_columns3 import (
    populate_ceiling,
    populate_gusts,
    blank_is_zero,
    populate_steepness,
    populate_vessel_icing,
    populate_shear,
    normalize_interpolate_ice,
    interpolate_var
)
from RGA_output3 import (
    write_csv_from_list_of_dicts,
    print_summary,
    RG_calendar,
    draw_cycle,
    init_multi_cycle,
    init_multi_cycle_dict,
    close_svg,
    station_kml,
    draw_weather_boxplots,
    draw_multi_rose,
    draw_percentile_wind_rose,
    draw_vis_graph,
    draw_daylight,
    draw_timeseries,
    draw_annual_matrix,
    draw_simple_summary,
    draw_timeseries_comparison,
    draw_limits_graphic,
    completeness_calendar,
    generate_column_statistics
)
from comparisons import (
    best_of_cycle
)

from display_settings3 import (
    Rose_Wind_Thresholds,
    timeseries_range_list
)

from histograms import (
    draw_histogram_multiple_data_sources,
    draw_histogram,
    draw_generic_matrix,
    draw_cycle_histogram,
    draw_cycle_histogram_multiple_data_sources
)

from convert_functions3 import *

from project_specifics3 import (
    inputs,
    output_root,
    raw_model_dict,
    init_model_dict,
    all_RGAs,
    end_summer,
    end_winter,
    multi_cycle_dict,
    inverse_multi_cycle_keys,
    wind_chill_function
)

#Need to complete the transition to using radians interanlly - store radians, and deal with wind roses.


model_dict = init_model_dict(raw_model_dict) #Need to rebuild the dictionary, executing the function-builder functions

try:
    in_years = inputs['years']
except:
    in_years = range(0, 2100) #To make old input settings compatable.

dir_list = [
    'Text/',
    'Text/Merged/',
    'Text/Summary/',
    'Text/RGA_Data/',
    'Text/Parsed/',
    'Text/Monthly_Averages/',
    'Text/Rose_data/',
    'Text/Cycle/',
    'Text/Timeseries/'
    'Visuals/',
    'Visuals/Characterize/',
    'Visuals/RGA/',
    'Visuals/Characterize/Daylight/',
    'Visuals/Characterize/Roses/',
    'Visuals/Characterize/Roses/Monthly/',
    'Visuals/Characterize/Roses/Seasonal/',
    'Visuals/Characterize/Roses/Exceedance/',
    'Visuals/Characterize/Boxplots/',
    'Visuals/Characterize/Vis/',
    'Visuals/Characterize/Matrix/',
    'Visuals/Characterize/Matrix/Annual/',
    'Visuals/Characterize/Histogram/',
    'Visuals/Characterize/Cumulative/',
    'Visuals/Characterize/timeseries/',
    'Visuals/Characterize/Cycle_Histogram/',
    'Visuals/RGA/Cycle/Individual/',
    'Visuals/RGA/Cycle/Multi/',
    'Visuals/RGA/Cycle/Compiled/Average/',
    'Visuals/RGA/Cycle/Compiled/Best_of/',
    'Visuals/RGA/Calendar/',
    'Visuals/RGA/Summary/',
    'Visuals/Limits/'
]

dir_list = [output_root+'/'+path for path in dir_list]

check_dirs(dir_list)

all_summary = []
all_summary_dict = {}
simple_summary = []

draw_limits_graphic()

#Read weather data files
for name, station in inputs['stations'].iteritems():
    print "  Starting: " + name
    if station['file_type'] == 'csv':
        parsed_data = extract_csv_data(station, in_years)
    elif station['file_type'] == 'onlns':
        parsed_data = extract_onlns_data(station, in_years)
    elif station['file_type'] == 'NBDC':
        parsed_data = extract_NBDC_data(station, in_years)
    elif station['file_type'] == 'Weatherspark':
        parsed_data = extract_Weatherspark_data(station, in_years)
    else:
        print("Unknown file type: " + station['file_name'] + ", file not processed.")
    write_parsed(name+'_unclean',parsed_data) #Bookkeeping: output the data before cleaning step
    parsed_data = clean_duplicates(name, clean_extremes(parsed_data, inputs['clean']['extremes'])) #Cleaning step
    if 'fill_undefined_waves' in station and station['fill_undefined_waves']: fill_undefined_waves(parsed_data, name)
    calculate_steepness(parsed_data)
    write_parsed(name, parsed_data) #Fully parsed data, after cleaning
    all_summary.append(parsed_data['summary']) #eventually phase this out, but need to change print function first.
    all_summary_dict.update([[name, parsed_data]])

#The comparison code is in-progress.
saved_RGAs = {}
if 'comparisons' in inputs:
    for comparison in inputs['comparisons'].itervalues():
        for merged in comparison['merges']:
            if 'All' in comparison['models']:
                models = all_RGAs
            else: models = comparison['models']
            for model in models:
                saved_RGAs.update([ ('{0}_{1}'.format(merged,model), None) ]) #Formulaic name like "Port Angeles_OW"

analyzed_summary = []
average_summary = []
completeness_summary = []
mc_x = 0
multi_cycle_files = init_multi_cycle_dict([key for key in multi_cycle_dict])
n_RGAs = len(inputs['merges'])
i = 0
all_datasets_together = []
if 'merge_order' in inputs: merge_order = inputs['merge_order']
else:
    merge_order = [name for name in inputs['merges']]
    merge_order.sort()
weather_stats = []
for name in merge_order: #Merge the weather data, and apply RGA models to it.
    merge_info = inputs['merges'][name]
    i += 1
    merged = merge(all_summary_dict, name, **merge_info)
    all_datasets_together.append(merged['data'])
    print "*************************************"
    print " (merge {0}/{1})".format(i,n_RGAs)
    populate_gusts(merged)
    blank_is_zero(merged,'rain')
    populate_ceiling(merged,inputs['clean']['extremes']['ceil']['maximum'])
    populate_steepness(merged)
    populate_vessel_icing(merged)
    populate_shear(merged)
    wind_chill_function(merged)
    populate_vessel_icing(merged)
    #normalize_interpolate_ice(merged)
    write_csv_from_list_of_dicts(output_root+'/Text/Merged/' + name + '_data.csv', merged['data'])
    weather_stats.append(generate_column_statistics(merged))
    draw_cycle_histogram(name,merged['data'],'datetime','wind',smart_units('1 m/s'))
    draw_cycle_histogram(name,merged['data'],'datetime','wave',smart_units('0.2 m'))
    draw_cycle_histogram(name,merged['data'],'datetime','vis',smart_units('0.2 km'),True)
    draw_cycle_histogram(name,merged['data'],'datetime','temp',smart_units('2 C'),True)
    draw_cycle_histogram(name,merged['data'],'datetime','wind_chill',smart_units('2 C'),True)

    draw_daylight(dawn_dusk(merged['location'], merged['timezone']), name)

    draw_histogram(merged['data'],{'name':'wind','min':0.0, 'max':smart_units('31 m/s'), 'bins':31},name)
    draw_histogram(merged['data'],{'name':'wave','min':0.0, 'max':smart_units('6.2 m'), 'bins':31},name)
    draw_histogram(merged['data'],{'name':'ice','min':0.0, 'max':smart_units('100 %'), 'bins':100},name)
    draw_histogram(merged['data'],{'name':'ceil','min':0.0, 'max':smart_units('2.05 km'), 'bins':41},name)
    draw_histogram(merged['data'],{'name':'vis','min':0.0, 'max':smart_units('6.2 km'), 'bins':31},name)
    draw_histogram(merged['data'],{'name':'temp','min':smart_units('-50 C'), 'max':smart_units('1 C'), 'bins':51},name)
    draw_histogram(merged['data'],{'name':'wind_chill','min':smart_units('-50 C'), 'max':smart_units('1 C'), 'bins':51},name)

    draw_generic_matrix(merged['data'],{'name':'temp','min':smart_units('-50 C'),'max':smart_units('0 C'),'bins':50},{'name':'wind_chill','min':smart_units('-50 C'),'max':smart_units('0 C'),'bins':50},name, True)
    draw_generic_matrix(merged['data'],{'name':'wave','min':0.0,'max':smart_units('6 m'),'bins':40},{'name':'period','min':0,'max':20.0,'bins':40},name, True)
    draw_generic_matrix(merged['data'],{'name':'wave','min':0.0,'max':smart_units('6 m'),'bins':40},{'name':'steep','min':0,'max':0.0125,'bins':40},name, True)
    draw_generic_matrix(merged['data'],{'name':'temp','min':-40.0,'max':20.0,'bins':40},{'name':'wtemp','min':-5.0,'max':15.0,'bins':40},name, True)
    draw_generic_matrix(merged['data'],{'name':'wind','min':0.0,'max': smart_units('30 m/s'),'bins':40},{'name':'wave','min':0.0,'max':smart_units('6 m'),'bins':40},name, True)
    draw_generic_matrix(merged['data'],{'name':'temp','min':-40.0,'max':20.0,'bins':40},{'name':'temp2','min':-40.0,'max':20.0,'bins':40},name, True)
    draw_generic_matrix(merged['data'],{'name':'wind','min':0.0,'max':smart_units('30 m/s'),'bins':40},{'name':'wind2','min':0.0,'max':smart_units('30 m/s'),'bins':40},name, True)
    draw_generic_matrix(merged['data'],{'name':'gust','min':0.0,'max':smart_units('30 m/s'),'bins':40},{'name':'gust2','min':0.0,'max':smart_units('30 m/s'),'bins':40},name, True)
    draw_generic_matrix(merged['data'],{'name':'dir','min':0.0,'max':2*math.pi,'bins':36},{'name':'dir2','min':0.0,'max':2*math.pi,'bins':36},name, True)
    draw_generic_matrix(merged['data'],{'name':'dir','min':0.0,'max':2*math.pi,'bins':36},{'name':'wind','min':0.0,'max':smart_units('30 m/s'),'bins':40},name, True)
    draw_generic_matrix(merged['data'],{'name':'wave','min':0.0,'max':10.0,'bins':40},{'name':'wave2','min':0.0,'max':10.0,'bins':40},name, True)
    draw_generic_matrix(merged['data'],{'name':'wtemp','min':-5.0,'max':15.0,'bins':40},{'name':'wtemp2','min':-5.0,'max':15.0,'bins':40},name, True)
    draw_generic_matrix(merged['data'],{'name':'period','min':0,'max':15.0,'bins':40},{'name':'period2','min':0,'max':15.0,'bins':40},name, True)
    draw_annual_matrix(merged,{'name':'wind','min':0.0,'max':30.0,'bins':40})
    draw_annual_matrix(merged,{'name':'temp','min':-40.0,'max':20.0,'bins':40})
    draw_annual_matrix(merged,{'name':'wave','min':0.0,'max':20.0,'bins':40})
    averages = monthly_averages(merged)
    average_summary.append(average_merge(merged, averages))
    completeness_summary.append(completeness_percentages(merged))
    draw_weather_boxplots(averages)
    draw_vis_graph(averages['vis_months'], 0.5, 1.5, 100, [1.60934, 4.82803, 8.04672],
                   ['rgb(20,33,48)', 'rgb(126,139,146)', 'rgb(202,220,232)', 'rgb(172,199,255)'],
                   averages['name'] + '_vis')
    draw_vis_graph(averages['ceil_months'], 1.0, 4, 40, [0.1524, 0.3048, 0.9144],
                   ['rgb(20,33,48)', 'rgb(126,139,146)', 'rgb(202,220,232)', 'rgb(172,199,255)'],
                   averages['name'] + '_ceil')
    draw_multi_rose('category', [
        wind_dir(merged, 36, Rose_Wind_Thresholds[0], 'wind'),
        wind_dir(merged, 36, Rose_Wind_Thresholds[1], 'wind'),
        wind_dir(merged, 36, Rose_Wind_Thresholds[2], 'wind'),
        wind_dir(merged, 36, Rose_Wind_Thresholds[3], 'wind')
    ],True)
    draw_multi_rose('gust_category', [
        wind_dir(merged, 36, Rose_Wind_Thresholds[0], 'gust'),
        wind_dir(merged, 36, Rose_Wind_Thresholds[1], 'gust'),
        wind_dir(merged, 36, Rose_Wind_Thresholds[2], 'gust'),
        wind_dir(merged, 36, Rose_Wind_Thresholds[3], 'gust')
    ],True)
    for month in monthly_rose_data(merged, Rose_Wind_Thresholds, 36):
        draw_multi_rose('monthly', month, False, 'Monthly')
    for season in summer_winter_rose_data(merged, Rose_Wind_Thresholds, 36):
        draw_multi_rose('seasonal', season, False, 'Seasonal')
#    draw_percentile_wind_rose(annual_percentile_wind_rose(merged, 8, [0.5,0.9,1.0]), merged['name'])
    draw_percentile_wind_rose(component_velocity_exceedance_rose(merged, 36, [0.5, 0.1, 0.01, 0.001, 0.0001]), merged['name']+'_exceedance_component', False,'Exceedance')
    draw_percentile_wind_rose(component_velocity_exceedance_rose(merged, 36, [0.5, 0.1, 0.01, 0.001, 0.0001],False), merged['name']+'_exceedance', False,'Exceedance')
    draw_timeseries(merged, "wind", 0.01, -10.0)
    draw_timeseries(merged, "dir", 0.01, -1.0)
    completeness_calendar(merged, "wind")
    completeness_calendar(merged, "dir")
    completeness_calendar(merged, "wave")
    completeness_calendar(merged, "period")
    completeness_calendar(merged, "vis")
    if inputs['merges'][name]['models'] == "All":
        RGA_list = all_RGAs
        print "  For merge " + name + " applying all models: " + str(RGA_list)
    else:
        RGA_list = inputs['merges'][name]['models']
        print "  For merge " + name + " applying models: " + str(RGA_list)
    mc_y = 0
    for model_name in RGA_list: #Apply RGA models
        model = model_dict[model_name]
        merge_RGA_name = '{0}_{1}'.format(name,model_name)
        RGA = merge_RGA(merged, model, merge_RGA_name)
        #write_csv_from_list_of_dicts('{0}/Text/RGA_data/{1}.csv'.format(output_root, RGA['name']), RGA['data']) #This generates a ridiculously large amount of data - 12 gigs in one example.
        analyzed_summary.append(RGA['summary'])
        #RG_calendar(RGA)
        week_cycle = cycle_data([RGA], RGA['name'] + "_annual", days_per_bin=7)
        write_csv_from_list_of_dicts(output_root+'/Text/Cycle/{0}.csv'.format(RGA['name']),week_cycle['bins'])
        summer_winter_data = cycle_data([RGA], RGA['name'] + "_summer_winter", div_bins=[0, end_winter, end_summer])
        compiled_summer_winter_data = compile_summer_winter(RGA['name'], summer_winter_data, model_name,name)
        draw_cycle(week_cycle, additional_root='Individual',summer_winter_data= compiled_summer_winter_data, multi_cycle_dict= multi_cycle_files,multi_cycle_subset= inverse_multi_cycle_keys[model_name],multi_cycle_loc= (mc_x,mc_y))
        mc_y += 1
        #timeseries_summary, timeseries_output = RGA_timeseries_analysis(RGA, timeseries_range_list)
        #write_csv_from_list_of_dicts(output_root+'/Text/Timeseries/{0}.csv'.format(RGA['name']),timeseries_output)
        #compiled_summer_winter_data.update(timeseries_summary)
        simple_summary.append(compiled_summer_winter_data)
        if merge_RGA_name in saved_RGAs:
            saved_RGAs[merge_RGA_name] = RGA
    mc_x += 1
for key,multi_cycle in multi_cycle_files.iteritems():
    try: close_svg(multi_cycle)
    except AttributeError as error_text:
        print key, multi_cycle
        print error_text
        raise Exception

write_csv_from_list_of_dicts('{0}/Text/Summary/percentile_column_stats.csv'.format(output_root),weather_stats)

draw_histogram_multiple_data_sources(all_datasets_together,{'name':'wind','min':0.0, 'max':smart_units('31 m/s'), 'bins':31},'all_datasets')
draw_histogram_multiple_data_sources(all_datasets_together,{'name':'wave','min':0.0, 'max':smart_units('6.2 m'), 'bins':31},'all_datasets')
draw_histogram_multiple_data_sources(all_datasets_together,{'name':'ice','min':0.0, 'max':smart_units('100 %'), 'bins':100},'all_datasets')
draw_histogram_multiple_data_sources(all_datasets_together,{'name':'ceil','min':0.0, 'max':smart_units('2.05 km'), 'bins':41},'all_datasets')
draw_histogram_multiple_data_sources(all_datasets_together,{'name':'vis','min':0.0, 'max':smart_units('6.1 km'), 'bins':61},'all_datasets')
draw_histogram_multiple_data_sources(all_datasets_together,{'name':'temp','min':smart_units('-50 C'), 'max':smart_units('1 C'), 'bins':51},'all_datasets')
draw_histogram_multiple_data_sources(all_datasets_together,{'name':'wind_chill','min':smart_units('-50 C'), 'max':smart_units('1 C'), 'bins':51},'all_datasets')

#draw_cycle_histogram_multiple_data_sources("All_locations",all_datasets_together,'datetime','wind',smart_units('1 m/s'))
#draw_cycle_histogram_multiple_data_sources("All_locations",all_datasets_together,'datetime','wave',smart_units('0.2 m'))
#draw_cycle_histogram_multiple_data_sources("All_locations",all_datasets_together,'datetime','vis',smart_units('0.2 km'),True)
#draw_cycle_histogram_multiple_data_sources("All_locations",all_datasets_together,'datetime','temp',smart_units('2 C'),True)
#draw_cycle_histogram_multiple_data_sources("All_locations",all_datasets_together,'datetime','wind_chill',smart_units('2 C'),True)
#draw_timeseries_comparison(simple_summary)

if 'comparisons' in inputs: #Backwards compatible. Not an important part of the code yet
    for comparison_name,comparison in inputs['comparisons'].iteritems():
        RGA_list = []
        for merged in comparison['merges']:
            for RGA in comparison['models']:
                name = '{0}_{1}'.format(merged,RGA)
                RGA_list.append(saved_RGAs[name])
        draw_cycle(best_of_cycle(comparison_name,RGA_list,days_per_bin=7),additional_root='Compiled/Best_of')
        draw_cycle(cycle_data(RGA_list,'{0}_average'.format(comparison_name),days_per_bin=7), additional_root='Compiled/Average')

if len(all_summary) > 0:
    print_summary("_full", all_summary)

station_kml(all_summary)

if len(analyzed_summary) > 0:
    rgi_calculations(analyzed_summary)
    print_summary("_full", analyzed_summary, 'a') #append to the already started summary
#	write_summaries_from_list_of_dicts("_individual_summary.csv",analyzed_summary) #could pass a specific sequence of keys at this point.

try:
    add_overall_summary(simple_summary, analyzed_summary)
    simple_summary = sorted(simple_summary, key=lambda k: k['site']) #Alphabetical sorting by name
    draw_simple_summary(simple_summary, 'site_sorted')
    simple_summary = sorted(simple_summary, key=lambda k: k['model']) #Alphabetical sorting by name
    draw_simple_summary(simple_summary, 'model_sorted')
except TypeError: pass

print "  Writing special summaries for RGI, average values, and completeness"

simple_summary_columns = ['summer_green','summer_yellow','summer_red','winter_green','winter_yellow','winter_red','green_overall','yellow_overall','red_overall']
for number in timeseries_range_list:
    simple_summary_columns += [
        'Ambiguous_Green_{0}'.format(number),
        'Green_{0}'.format(number),
        'Ambiguous_Green_or_Yellow_{0}'.format(number),
        'Green_or_Yellow_{0}'.format(number)
    ]
write_csv_from_list_of_dicts(output_root+"/Text/Summary/simple_RGI_summary.csv", simple_summary, keys=simple_summary_columns, options="w")
write_csv_from_list_of_dicts(output_root+"/Text/Summary/averages_summary.csv", average_summary, options="w")
write_csv_from_list_of_dicts(output_root+"/Text/Summary/completeness_summary.csv", completeness_summary, options="w")

print "  Total runtime: {0:.2f} minutes".format((time.time()-start_time)/60)