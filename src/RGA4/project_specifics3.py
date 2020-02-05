#from input_settings_TEST import (
#from input_settings3_Augustine import (
#from input_settings3_Arctic_DNV import (
#from input_settings3_Arctic import (
#from input_settings3_test import (
#from input_settings3_validate import (
#from input_settings3_Homer_Wind import (
#from input_settings3_GOM import (
#from input_settings4_GOM_airports import (
#from input_settings3_BC import (
from input_settings4_Yakutat import (
#from input_settings3_BC_46147 import (
#from input_settings3_Grays_Harbor import (
    output_root,
    data_root,
    inputs,
    wind_chill_function
)

#from model_settings3_Arctic_DNV import (
#from model_settings3_Arctic import (
#from model_settings3_test import (
#from model_settings3_Validate import (
#from model_settings_Cook_Inlet import (
from model_settings4_GOMv2 import (
    raw_model_dict,
    init_model_dict,
    multi_cycle_dict,
    inverse_multi_cycle_keys,
    all_RGAs,
    primary_RGAs,
    component_list
)


end_winter = 90        #Day of the year when "winter" ends.  Jan 1 = 0  July 1 = 181 Jun 21 = 172 Mar 21 = 80 Mar 31 = 90
end_summer = 304        #Day of the year when "summer" ends.  Jan 1 = 0  Nov 1 = 304 Sept 21 = 264