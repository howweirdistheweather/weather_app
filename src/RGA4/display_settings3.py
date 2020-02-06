import math
from convert_functions3 import smart_units

#Various color schemes
classic_green = "rgb(68,237,34)"
classic_red = "rgb(238,51,0)"
classic_yellow = "rgb(255,255,0)"
greens_a = ("rgb(229,245,224)", "rgb(161,217,155)", "rgb(49,163,84)")
greens_b = ("rgb(247, 252, 185)", "rgb(173, 221, 142)", "rgb(49, 163, 84)")
reds_a = ("rgb(254,240,217)", "rgb(253,212,158)", "rgb(253,187,132)", "rgb(252,141,89)", "rgb(227,74,51)", "rgb(179,0,0)")
reds_b = ("rgb(254, 229, 217)", "rgb(252, 187, 161)", "rgb(252, 146, 114)", "rgb(251, 106, 74)", "rgb(239, 59, 44)","rgb(203, 24, 29)", "rgb(153, 0, 13)")
red_yellow = ("rgb(255, 255, 229)", "rgb(255, 247, 188)", "rgb(254, 227, 145)", "rgb(254, 196, 79)", "rgb(254, 153, 41)","rgb(236, 112, 20)", "rgb(204, 76, 2)", "rgb(140, 45, 4)")
greens_9 = ["rgb(247, 252, 245)", "rgb(229, 245, 224)", "rgb(199, 233, 192)", "rgb(161, 217, 155)","rgb(116, 196, 118)", "rgb(65, 171, 93)", "rgb(35, 139, 69)", "rgb(0, 109, 44)", "rgb(0, 68, 27)"]
reds_8 = ["rgb(254, 224, 210)", "rgb(252, 187, 161)", "rgb(252, 146, 114)", "rgb(251, 106, 74)","rgb(239, 59, 44)", "rgb(203, 24, 29)", "rgb(165, 15, 21)", "rgb(103, 0, 13)"]
yellows_simple = ["rgb({0:.0f}, {0:.0f}, 0)".format(255-i*20) for i in range(12)]
black = "#001"
#Off-black colors
b_0 = "#010002"
b_1 = "#000101"
b_2 = "#030100"
b_3 = "#020201"
b_4 = "#040101"
gray = "#667"

matrix_color_bins = 5 #How many different colors (grayscale) to display?

max_wind = 20.5778        #Matrix analysis extend to here (m/s).  20.5778 = 40 knots
max_wave = 9.144        #Matrix analysis extend to here (m). 9.144 = 30 feet

RGA_matrix_n_wind = 20    #Number of wind bins for the RGA matrix plot
RGA_matrix_n_wave = 20    #Number of wave bins for the RGA matrix plot

Rose_Wind_Thresholds_Australia = [0, smart_units('39 km/hr'), smart_units('62 km/hr'), smart_units('89 km/hr')] ## 39, 62, 89 km/h
Rose_Wind_Thresholds_Alaska = [0, smart_units('22 knots'), smart_units('34 knots'), smart_units('48 kts')] #22, 34, and 48 knots
Rose_Wind_Thresholds_Grays_Harbor = [0, smart_units('10 knots'), smart_units('22 knots'), smart_units('34 kts')] #22, 34, and 48 knots


Rose_Wind_Thresholds = Rose_Wind_Thresholds_Grays_Harbor


timeseries_range_list = [1,2,3,4,5,6,8,10,12,18,24]
timeseries_display_ranges = [1,6,12,24]

def green_red_gradient(steps,index):
    if index > steps or index < 0 or steps < 1: raise RuntimeError('ERROR: Nonsense for green_red_gradient: steps:{0}, index:{1}'.format(steps,index))
    red = 255 * math.pow((1.0/steps*index),2)
    green = 255 * math.pow((1.0 - 1.0/steps*index),2)
    blue = 255 * (1.0-math.pow((1.0/steps*index - 0.5),2))
    return "rgb({0},{1},{2})".format(red,green,blue)