# We propose a developing software to be installed in traffic light control boxes.

# Each traffic light control box will have a unique identifier (ID) and will take coordinates (latitude & longitude) to determine its location.

# The software will utilize the Google Map API to fetch real-time traffic data within a specific range around the traffic light’s location.

# Based on the fetched data including congestion levels for different lanes, the software will dynamically calculate the time allocated to each lane during a traffic light cycle.

# The formula we provided, T_lane = (C_lane/C_total) x T_total, will be used to calculate the time allocated to each lane,
               where,
                       T_total is the total time of a traffic light cycle
		  C_lane is the congestion level of specific lane
 		  C_total is the total congestion all lanes.

# The traffic lights will change dynamically according to the calculated time allocations for each lane based on congestion levels.
