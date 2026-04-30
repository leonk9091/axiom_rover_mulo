std_msgs/Header header
string  terrain_class        # asphalt|gravel|grass|sand|mud|rock
float32 confidence           # [0,1]
float32 traction_factor      # [0,1] - coefficiente attrito stimato
float32 traversability       # [0,1] - 1=completamente attraversabile
bool    is_soft              # true = terreno cedevole (sabbia, fango)
