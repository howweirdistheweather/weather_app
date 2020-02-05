prime_vars = ['wind', 'gust', 'wave', 'temp', 'wtemp', 'period', 'vis', 'ceil', 'dir', 'cover', 'ice', 'rain']
#what all is involved in adding a new column?
#cover is (I think) cloud cover
#ice is ice cover

gap_quant = ['wind', 'shear', 'wave', 'temp', 'vis', 'ceil', 'ice', 'wind_chill', 'rain'] #quantitative components

gap_qual = ['icing_cat'] #qualitative components

gap_vars = gap_qual + gap_quant   #Potential components of the response gap

non_gap_merge = ['gust', 'wtemp', 'steep', 'period', 'cover', 'dir']

merge_columns = gap_vars + non_gap_merge

numerical_merge_columns = gap_quant + non_gap_merge

gap_values = ["Green","Yellow","Red","Exclude"]

#2016-03-31 13:50:00