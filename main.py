import math as m
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import parse_map as p
import time
import csv
import numpy
#################################################################################################################################################
# Node of a linked list. Each node represents an information about a given street.
class InfoNode:

	def __init__(self,info=None,info_type=None,orientation=None,coordinates=None,radius=10):
		self.info = info
		self.info_type = info_type
		self.orientation = orientation
		self.coordinates = coordinates
		self.radius = radius
		self.next_node = None
		self.previous_node = None
		self.missed = 0

	def get_info(self):
		return self.info , self.orientation

	def get_next(self):
		return self.next_node

	def set_next(self,new_next):
		self.next_node = new_next

	def set_previous(self,new_previous):
		self.previous_node = new_previous

#################################################################################################################################################
# Each linked list corresponds to a node of the graph (stree_node)
class LinkedList:

	def __init__(self,head=None):#,previous_streets=None):
		#self.previous_streets = previous_streets
		self.head = head

	def __str__(self):
		node = self.head
		temp = []
		while node:
			temp.append(node.get_info())
			node = node.get_next()
		return str(temp)

	def insert(self,new_node): # inserts a new node on top of the list
		new_node.set_next(self.head)
		self.head.set_previous(new_node)
		self.head = new_node

	def size(self): # returns size of list
		current = self.head
		count=0
		while current:
			count += 1
			current = current.get_next()
		return count

	def search(self,data): # searches list for a node containing the requested data and returns that node if found
		current = self.head
		found = False
		while current and found is False:
			if current.get_info() == data:
				found = True
			else:
				current = current.get_next()
		if current is None:
			raise ValueError("Data not in list!")
		return current

	def delete(self,data): # searches list for a node containing the requested data and removes it from list if found
		current = self.head
		previous = None
		found = False
		while current and found is False:
			if current.get_info() == data:
				found = True
			else:
				previous = current
				current = current.get_next()
		if current is None:
			raise ValueError("Data not in list!")
		if previous is None:
			self.head = current.get_next()
		else:
			previous.set_next(current.get_next())


#################################################################################################################################################
# Graph representing a street map
class Graph:

	# Each node of the graph represents a street.
	class StreetNode:

		def __init__(self,street_name,infos1,infos2):
			self.street_name = street_name
			self.infos1 = infos1 # linked list
			self.infos2 = infos2 # linked list
			self.polygon = None # all coordinates that fall within the polygon, belong to the street
			self.connections = [] # connects to

		def __str__(self):
			return self.street_name# + '    ---->    ' + str([x.street_name for x in self.connections])

		def ConnectsTo(self,node,orientation):
			self.connections.append([node, orientation])

		def set_info(self,infos1=None,infos2=None):
			self.infos1 = infos1
			self.infos2 = infos2

		def add_polygon(self,polygon):
			self.polygon = polygon

	def __init__(self):
		self.nodes = []
		self.nodeCount = 0

	def __repr__(self):
		result = ""
		for node in self.nodes:
			for connection in node.connections:
				result += node.street_name + '    ---->    ' + connection.street_name + '\n'
		return result

	def add_node(self,street_name,infos1=None,infos2=None):
		node = self.StreetNode(street_name,infos1,infos2)
		self.nodes.append(node)
		self.nodeCount += 1
		return node

	def street_search(self,street_name):
		for node in self.nodes:
			if node.street_name == street_name:
				return node
		print('"' + street_name + '"' + ' not found!' + '\n')

	def connections_search(self,node,orientation,actual_position):
		counter = 0
		last_distance = 1000000000000
		best_distance = 1000000000000
		for connection in node.connections: # loop on connections (streets)
			if connection[1] == orientation: # if it has the desired orientation
				street = connection[0]
				if street.infos2 is None: ## If there is only one list:
					closest_info = get_closest(street.infos1,actual_position)
					distance = coord_dist(actual_position,closest_info.coordinates)
				else: # If there are two lists:
					closest_info1 = get_closest(street.infos1,actual_position,orientation)
					closest_info2 = get_closest(street.infos2,actual_position,orientation)
					if closest_info1 is not None and closest_info2 is None:
						distance = coord_dist(actual_position,closest_info1.coordinates)
					elif closest_info1 is None and closest_info2 is not None:
						distance = coord_dist(actual_position,closest_info2.coordinates)
					else:
						distance1 = coord_dist(actual_position,closest_info1.coordinates)
						distance2 = coord_dist(actual_position,closest_info2.coordinates)
						if distance1 > distance2: # choose closest info
							distance = distance2
						else:
							distance = distance1
				if distance < last_distance: # the desired connection is the closest to actual_position
					return_connection = street
					best_distance = distance
				last_distance = distance	
				counter = counter + 1
		if counter == 0 or best_distance > 30:
			# print("There are no connections...")
			return None
		else:
			return return_connection


#################################################################################################################################################
# Compute distance between coordinates

earthRadius = 3958.75

def coord_dist(a,b):

	dLat = m.radians(b[0]-a[0])
	dLong = m.radians(b[1]-a[1])
	a = m.sin(dLat/2)*m.sin(dLat/2)+m.cos(m.radians(a[0]))*m.cos(m.radians(b[0]))*m.sin(dLong/2)*m.sin(dLong/2)
	c = 2*m.atan2(m.sqrt(a), m.sqrt(1-a))
	dist = earthRadius*c
	meterConversion = 1609.00
	return dist * meterConversion


#################################################################################################################################################
# Check which street contains the input point
# coord --> [lat, lon]

def check_street(graph,coord):

	lat = coord[0]
	lon = coord[1]
	point = Point(lat, lon)

	for node in graph.nodes:
		if node.polygon.contains(point):
			return node
	print('Point does not fall within any polygon...')
	return None	


#################################################################################################################################################
# Calculates the angle of the direction

# East-North-West-South (clockwise)
def orientation_(vx,vy): # ENWS
	 
	angle = m.atan2(vy,vx)
	
	if (1/4)*m.pi <= angle <= (3/4)*m.pi:
		# direction = 'North'
		direction = 'South'
	elif (-1/4)*m.pi <= angle < (1/4)*m.pi: 
		direction = 'East'
	elif (-3/4)*m.pi <= angle < (-1/4)*m.pi: 
		# direction = 'South'
		direction = 'North'
	else:
		direction = 'West'

	#print(m.degrees(angle))
	return direction


# North-East-South-West (clockwise)
def orientation__(vx,vy):
	 
	angle = m.atan2(vx,vy)
	
	if angle < 0:
		angle = angle + 2*m.pi

	# print(m.degrees(angle))
	return angle
#################################################################################################################################################
#

def not_point_type(info):

	if info.info_type == 'point': # do not return info of 'point' type
		while info.info_type == 'point':
			info = info.get_next()
			if info is None:
				return None # end of road (no more infos)
		return info
	else:
		return info


def get_closest(info_list,actual_position,orientation=None):
	previous_distance = 100000000 # all distances will be lower than this one (random)
	info = info_list.head
	while orientation and info and info.orientation != orientation: # skip initial infos with different orientation than the desired		
			info = info.get_next()
	if info == None:
		return None
	while info: # loop on infos
		distance = coord_dist(actual_position,info.coordinates)
		if distance	< previous_distance: # check if actual info is closest to actual_position than previous one 
			previous_distance = distance
			closest_info = info
		info = info.get_next()
		while orientation and info and info.orientation != orientation: # skip infos with different orientation than the desired
			info = info.get_next()
	return closest_info


def get_2nd_closest(closest_info,actual_position):
	# if its the last item on the list:
	if closest_info.next_node is None: 
		if coord_dist(actual_position,closest_info.previous_node.coordinates) > coord_dist(closest_info.coordinates,closest_info.previous_node.coordinates):
			return None # end of road
		else:
			# return not_point_type(closest_info)
			if coord_dist(actual_position,closest_info.coordinates)<40:
				return closest_info
			else:
				# print('TOO FAR AWAYYYYYYY')
				return None
			# return closest_info	
	# if its the first item on the list:		
	elif closest_info.previous_node is None:
		if coord_dist(actual_position,closest_info.next_node.coordinates) > coord_dist(closest_info.coordinates,closest_info.next_node.coordinates):
			# return not_point_type(closest_info)
			if coord_dist(actual_position,closest_info.coordinates)<40:
				return closest_info
			else:
				# print('TOO FAR AWAYYYYYYY')
				return None
			# return closest_info
		else:
			# return not_point_type(closest_info.next_node)
			if coord_dist(actual_position,closest_info.next_node.coordinates)<40:
				return closest_info.next_node
			else:
				# print('TOO FAR AWAYYYYYYY')
				return None
			# return closest_info.next_node
	# if its in the middle of the list:
	else: 
		#if coord_dist(actual_position,closest_info.previous_node.coordinates) > coord_dist(closest_info.coordinates,closest_info.previous_node.coordinates):
		if coord_dist(actual_position,closest_info.next_node.coordinates) < coord_dist(closest_info.coordinates,closest_info.next_node.coordinates):
			# return not_point_type(closest_info.next_node)
			if coord_dist(actual_position,closest_info.next_node.coordinates)<40:
				return closest_info.next_node
			else:
				# print('TOO FAR AWAYYYYYYY')
				return None
			# return closest_info.next_node
		else:
			# return not_point_type(closest_info)
			if coord_dist(actual_position,closest_info.coordinates)<40:
				return closest_info
			else:
				# print('TOO FAR AWAYYYYYYY')
				return None
			# return closest_info


def select_info(graph,actual_position,orientation,actual_street=None):
	
	if actual_street is None:
		actual_street = check_street(graph,actual_position)
		if actual_street is None:
			return None, None
	if actual_street.infos2 is None: ## If there is only one list:
		# get closest info on infos1 list
		closest_info = get_closest(actual_street.infos1,actual_position,orientation)
		if closest_info == None:
			# print('There are no infos with the desired direction')
			# print('NOT SURE... but returned head anyway')
			# return actual_street.infos1.head, actual_street
			return None,None
		return get_2nd_closest(closest_info,actual_position), actual_street
	else: # If there are two lists:
		# get closest infos
		closest_info1 = get_closest(actual_street.infos1,actual_position,orientation)
		closest_info2 = get_closest(actual_street.infos2,actual_position,orientation)
		if closest_info1 == None and closest_info2 == None: # nothing found
			# print('There are no infos with the desired direction')
			return None,None
		elif closest_info2 == None: # nothing found on info2 list
			return get_2nd_closest(closest_info1,actual_position), actual_street
		elif closest_info1 == None: # nothing found on info1 list
			return get_2nd_closest(closest_info2,actual_position), actual_street
		else: # found infos on both lists
			if coord_dist(actual_position,closest_info1.coordinates) > coord_dist(actual_position,closest_info2.coordinates): # the closest info is the desired one
				return get_2nd_closest(closest_info2,actual_position), actual_street
			else:
				return get_2nd_closest(closest_info1,actual_position), actual_street

	
#################################################################################################################################################
#

def opposite_orientation(orientation):
	if orientation == 'West':
		return 'East'
	elif orientation == 'East':
		return 'West'
	elif orientation == 'North':
		return 'South'
	elif orientation == 'South':
		return 'North'


#################################################################################################################################################
# convert ECEF coordinates to LLA
def ecef_to_lla(x,y,z):

	a = 6378137
	e = 8.1819190842622e-2

	asq = m.pow(a,2)
	esq = m.pow(e,2)

	b   = m.sqrt(asq * (1 - esq) )
	bsq = m.pow(b, 2)

	ep = m.sqrt((asq - bsq)/bsq)
	p = m.sqrt(m.pow(x, 2) + m.pow(y, 2))
	th = m.atan2(a * z, b * p)

	lon_lla = m.atan2(y, x)
	lat_lla = m.atan2( (z + m.pow(ep, 2) * b * m.pow(m.sin(th), 3)), (p - esq * a * m.pow(m.cos(th), 3)) )

	lon_lla = lon_lla * 180 / m.pi
	lat_lla = lat_lla * 180 / m.pi

	return [lat_lla, lon_lla]


#################################################################################################################################################
#
def estimate_coord(actual_position,vx,vy,velocity_mean,sample_time):

	# velocity = m.sqrt((vx*vx)+(vy*vy)+(vz*vz)) # in meters
	velocity = velocity_mean # in meters
	R = 6378.1 # Radius of the Earth
	brng = orientation__(vx,vy) # Bearing
	d = velocity*sample_time*0.001 #Distance in km

	lat1 = m.radians(actual_position[0]) #Current lat point converted to radians
	lon1 = m.radians(actual_position[1]) #Current long point converted to radians

	lat2 = m.asin( m.sin(lat1)*m.cos(d/R) + m.cos(lat1)*m.sin(d/R)*m.cos(brng))

	lon2 = lon1 + m.atan2(m.sin(brng)*m.sin(d/R)*m.cos(lat1),m.cos(d/R)-m.sin(lat1)*m.sin(lat2))

	lat2 = m.degrees(lat2)
	lon2 = m.degrees(lon2)

	return [lat2,lon2]


#################################################################################################################################################
#

def joint_probability(coordinates_gps1,coordinates_gps2,stdXY_gps1,stdXY_gps2,Vel_gps1,Vel_gps2,Velmodule_gps1,Velmodule_gps2):
	
	if Velmodule_gps1>=0.15 and Velmodule_gps2 >=0.15:
		# length between antennas of gps
		dk = 1.42/2
		# orientation
		psi1 = -m.atan2(Vel_gps1[0],Vel_gps1[1])
		psi2 = -m.atan2(Vel_gps2[0],Vel_gps2[1])
		# use the mean of psi angles
		psi = 0.5*(psi1+psi2)
		# calculate gain using standard deviations for x
		Gx = stdXY_gps1[0]*stdXY_gps1[0]/(stdXY_gps1[0]*stdXY_gps1[0] + stdXY_gps2[0]*stdXY_gps2[0])
		#var_xest =stdXY_gps1[0]*stdXY_gps1[0]-Gx*stdXY_gps1[0]*stdXY_gps1[0]
		#stdxest = m.sqrt(var_xest)
		# calculate gain using standard deviations for y
		Gy = stdXY_gps1[1]*stdXY_gps1[1]/(stdXY_gps1[1]*stdXY_gps1[1] + stdXY_gps2[1]*stdXY_gps2[1])
		#var_yest =gps1(i,5)^2-Gy*gps1(i,5)^2;
		#stdyest = m.sqrt(var_yest)
		# calculate joint probability for x coord
		z1 = coordinates_gps1[0]-dk*m.cos(psi)
		z2 = coordinates_gps2[0]+dk*m.cos(psi)
		xest = z1+Gx*(z2-z1)
		# calculate joint probability for y coord
		z1 =  coordinates_gps1[1]-dk*m.sin(psi)
		z2 =  coordinates_gps2[1]+dk*m.sin(psi)
		yest = z1+Gy*(z2-z1)

		# convert to lla
		return ecef_to_lla(xest,yest,coordinates_gps2[2])

	else:
		# convert to lla
		return ecef_to_lla(coordinates_gps2[0],coordinates_gps2[1],coordinates_gps2[2])






#################################################################################################################################################		
#################################################################################################################################################
#############################################################     MAIN    #######################################################################
#################################################################################################################################################
#################################################################################################################################################

if __name__ == '__main__':

	#start = time.time()



	graph = p.create_map()
	#print(coord_dist([38.736965, -9.139067],[38.737018, -9.138904]))

	#print(graph)
	#print(graph.street_search('IST1').infos1)
	#print(type(check_street(graph,[38.737671, -9.139866]).connections))
	
	#print(orientation([38.737394, -9.139085],[38.737398, -9.139045]))
	
	# cenas = select_info(graph,[38.737421, -9.139812],orientation([38.737746, -9.139018],[38.737753, -9.138979]))
	# if cenas: 
	# 	print(cenas.info)



	# end = time.time()
	# print(end - start)
	
	i = 0
	last_i = -1
	change_orientation=0
	info_behind=0
	dist_to_next = 10000000000
	dist_to_next_next = 10000000000
	last_dist_to_next = 10000000000
	last_dist_to_next_next = 10000000000
	end_of_street = False
	end_of_street_normal = False
	wait_flag = False

	vector = []
	vector1 = []
	vector2 = []
	vector3 = []
	vector4 = []

	sample_time = 0.05
	missed_samples = 1

	distance_travelled = 0
	point_out_of_polygon = False

	last_info = None

	times = []
	
	first = True

	velocity_mean=0

	ensure1=0
	ensure2=0
	ensure3=0
	ensure4=0
	ensure5=0
	force_reset = False

	waiting_distance=0

	# file = open('testfile1.txt','w') 
	with open('gps1.csv', mode='r') as csv_file1, open('gps2.csv', mode='r') as csv_file2:
	# with open('test02.csv', mode='r') as csv_file1:
		csv_reader1 = csv.DictReader(csv_file1)
		csv_reader2 = csv.DictReader(csv_file2)

		for row1, row2 in zip(csv_reader1,csv_reader2):
		# for row1 in csv_reader1:
			start = time.time()

			### GET DATA
			PSolStatus_gps1 = float(row1["PSolStatus"])
			PSolStatus_gps2 = float(row2["PSolStatus"])
			VSolStatus_gps1 = float(row1["VSolStatus"])
			VSolStatus_gps2 = float(row2["VSolStatus"])
			coordinates_gps1=[]
			coordinates_gps1.append(float(row1["X"]))
			coordinates_gps1.append(float(row1["Y"]))
			coordinates_gps1.append(float(row1["Z"]))
			coordinates_gps2=[]
			coordinates_gps2.append(float(row2["X"]))
			coordinates_gps2.append(float(row2["Y"]))
			coordinates_gps2.append(float(row2["Z"]))
			stdXY_gps1=[]
			stdXY_gps1.append(float(row1["stdX"]))
			stdXY_gps1.append(float(row1["stdY"]))
			stdXY_gps2=[]
			stdXY_gps2.append(float(row2["stdX"]))
			stdXY_gps2.append(float(row2["stdY"]))
			Vel_gps1=[]
			Vel_gps1.append(float(row1["VX"]))
			Vel_gps1.append(float(row1["VY"]))
			Vel_gps1.append(float(row1["VZ"]))
			Vel_gps2=[]
			Vel_gps2.append(float(row2["VX"]))
			Vel_gps2.append(float(row2["VY"]))
			Vel_gps2.append(float(row2["VZ"]))

			Velmodule_gps1=m.sqrt((Vel_gps1[0]*Vel_gps1[0])+(Vel_gps1[1]*Vel_gps1[1])+(Vel_gps1[2]*Vel_gps1[2]))
			Velmodule_gps2=m.sqrt((Vel_gps2[0]*Vel_gps2[0])+(Vel_gps2[1]*Vel_gps2[1])+(Vel_gps2[2]*Vel_gps2[2]))

			
			# actual_position=[]
			# actual_position.append(float(row["lat"]))
			# actual_position.append(float(row["long"]))
			# vx = float(row["vx"])
			# vy = float(row["vy"])
			# vz = float(row["vz"])
			# orientation = orientation_(vx,vy)
			# orientation = row["orientation"]
			# velocity = m.sqrt((vx*vx)+(vy*vy)+(vz*vz))

			if i>0:
				last_actual_position = actual_position

			vx = (Vel_gps2[0]+Vel_gps1[0])/2
			vy = (Vel_gps2[1]+Vel_gps1[1])/2
			vz = (Vel_gps2[2]+Vel_gps1[2])/2
			velocity = (Velmodule_gps2+Velmodule_gps1)/2
			
			actual_position = joint_probability(coordinates_gps1,coordinates_gps2,stdXY_gps1,stdXY_gps2,Vel_gps1,Vel_gps2,Velmodule_gps1,Velmodule_gps2)

			
			# actual_position=ecef_to_lla(coordinates_gps1[0],coordinates_gps1[1],coordinates_gps1[2])
			# velocity = Velmodule_gps1
			# vx=Vel_gps1[0]
			# vy=Vel_gps1[1]

			orientation = orientation_(vy,vx)

			i=i+1
			vector3.append(actual_position)
			vector4.append(orientation)

############### FIRST LOCALIZATION
			if i == 1 and PSolStatus_gps1 == 0 and VSolStatus_gps1 == 0:# and PSolStatus_gps2 == 0 and VSolStatus_gps2 == 0:
				apagarquandovires =0
				next_info, actual_street = select_info(graph,actual_position,orientation)
				print('## THE VEHICLE IS AT:   ' + actual_street.street_name)
				if actual_street == None:
					i=0
					continue
				if next_info:
					dist_to_next = coord_dist(actual_position,next_info.coordinates)
					distance = dist_to_next
					distance_travelled = 0
					last_orientation = next_info.orientation

					last_valid = actual_position
					first = False

					if next_info.next_node:
						dist_to_next_next = coord_dist(actual_position,next_info.next_node.coordinates)
					if dist_to_next < next_info.radius:
						if (next_info.info_type != 'sign' and next_info.info_type != 'road mark'):
							print('( ' + next_info.info + '   --->   ' + next_info.info_type + ' )')
						else:
							print('                                                    ' + next_info.info + '   --->   ' + next_info.info_type)
						# last_valid = actual_position
						# first = False
						# last_info_aux = next_info
						next_info = next_info.next_node
						if next_info:
							last_orientation = next_info.orientation
							dist_to_next = coord_dist(actual_position,next_info.coordinates)
							distance = dist_to_next
							distance_travelled = 0
							if next_info.next_node:
								dist_to_next_next = coord_dist(actual_position,next_info.next_node.coordinates)
				else:
					i=0
					continue

				# save last valid point
				# vector.append(actual_position)	
				# last_valid = actual_position
				missed_samples = 1
				continue


			### NOT FIRST TIME (MAIN)
			elif PSolStatus_gps1 == 0 and VSolStatus_gps1 == 0:# and PSolStatus_gps2 == 0 and VSolStatus_gps2 == 0:
				

################### OUTLIER DETECTION
				if first == False:
				# if i>16000 and i<20000:
					velocity_mean=(velocity_mean*(missed_samples-1)+velocity)/missed_samples
					# prevent system to discard more than 10 values consecutively
					if missed_samples > 10:
						vector.append(actual_position)	
						last_valid = actual_position
						missed_samples = 1
					# If this point is an outlier
					elif coord_dist(actual_position,estimate_coord(last_valid,vx,vy,velocity_mean,sample_time*missed_samples)) > 2:
						# print(velocity*sample_time*missed_samples)
						# print(str(coord_dist(actual_position,last_valid)) + '-----' + str(velocity*2*sample_time*missed_samples) + '-----' + str(missed_samples) + '-----' + str(actual_position) + '-----' + str(last_valid))
						# skip this point
						apagarquandovires = apagarquandovires +1
						missed_samples = missed_samples + 1
						vector1.append(actual_position)
						continue
					# It is not an outlier
					else:
						# save last valid point
						vector.append(actual_position)	
						last_valid = actual_position
						missed_samples = 1


################### UPDATE VALUES
				last_dist_to_next = dist_to_next
				last_dist_to_next_next = dist_to_next_next
				if next_info: 
					# print(i)
					last_orientation = next_info.orientation
					dist_to_next = coord_dist(actual_position,next_info.coordinates)
					# distance_travelled = distance_travelled + coord_dist(actual_position,last_actual_position) ### ta mal
					distance_travelled = distance_travelled + sample_time*velocity
					# print('nexttt:::    ' + next_info.info)
					if next_info.next_node:
						dist_to_next_next = coord_dist(actual_position,next_info.next_node.coordinates)
				elif actual_street is not None: # end of street
					end_of_street = True
					# print('( end of street... )')

				
################### RESET
				# only for speeds below 80 km/h (22,22(2) m/s)
				if velocity < 23 or point_out_of_polygon == True or force_reset == True:
					# doesn't reset near an intersection
					if (next_info and next_info.previous_node is not None and next_info.info_type != 'intersection' and next_info.previous_node.info_type != 'intersection') or point_out_of_polygon == True or force_reset == True:
						#checked = check_street(graph,actual_position)
						# reset if the distance travelled is twice the initial distance to next info
						if (distance_travelled > 2*distance) or (point_out_of_polygon == True) or (dist_to_next > 100) or (force_reset == True): # or (actual_street != checked and check_street is not None):
							# print(next_info.info)
							# print(dist_to_next)
							# print(actual_position)
							# print(orientation)
							force_reset = False
							next_info, actual_street = select_info(graph,actual_position,orientation)
							if actual_street is None: # Point does not fall within any polygon
								# if i<2511 and i>2509:
								# 	print(str(i) + str(actual_position) + str(orientation))
								point_out_of_polygon = True
								continue
							# print('## Reset ## THE VEHICLE IS AT:   ' + actual_street.street_name + str(i))
							if next_info and actual_street:
								print('## Reset ## THE VEHICLE IS AT:   ' + actual_street.street_name)# + str(i))
								# print(str(actual_position) + str(next_info.info))
								change_orientation = 0
								point_out_of_polygon = False
								dist_to_next = coord_dist(actual_position,next_info.coordinates)
								distance = dist_to_next
								distance_travelled = 0
								last_orientation = next_info.orientation

								last_valid = actual_position
								first = False

								end_of_street = False
								end_of_street_normal = False

								if next_info.next_node:
									dist_to_next_next = coord_dist(actual_position,next_info.next_node.coordinates)
								if dist_to_next < next_info.radius:
									# last_valid = actual_position
									# first = False
									if next_info.info_type != 'sign' and next_info.info_type != 'road mark' and last_info != next_info:
										last_info = next_info
										print('( ' + next_info.info + '   --->   ' + next_info.info_type + ' )')
									elif last_info != next_info: # detect repeated infos - reset function may cause the system to output an information that was already output
										last_info = next_info
										print('                                                    ' + next_info.info + '   --->   ' + next_info.info_type)
										change_orientation = 0
									next_info = next_info.next_node
									if next_info:
										last_orientation = next_info.orientation
										dist_to_next = coord_dist(actual_position,next_info.coordinates)
										distance = dist_to_next
										distance_travelled = 0
										if next_info.next_node:
											dist_to_next_next = coord_dist(actual_position,next_info.next_node.coordinates)
							elif next_info is None:
								point_out_of_polygon = True # not really, but we can use it to wait for the right orientation, and next info
								continue

							# save last valid point
							# vector.append(actual_position)
							# last_valid = actual_position
							missed_samples = 1
							continue
				

################### END OF A STREET
				if end_of_street == True and end_of_street_normal == False and wait_flag == False:
					
					if len(actual_street.connections)==1:
						end_of_street_normal = True
					else: # In IST, a street cant have more than 2 connections... Make generic code for real maps where a street can have more than 2 connections.
						# if i<18308:
							# print('kkk')
						next_street1 = actual_street.connections[0][0]
						orient1 = actual_street.connections[0][1]
						next_street2 = actual_street.connections[1][0]
						orient2 = actual_street.connections[1][1]
						if orient1 != orientation and orient2 != orientation: # NORMAL STREET
							end_of_street_normal = True
						elif orient1 == orientation and orient2 != orientation: # NOT NORMAL STREET
							check_info = select_info(graph,actual_position,orient1,next_street1)[0]
							other_orientation = orient2
							wait_flag = True
							# if i<18308:
							# 	print('kkk')
							continue
						elif orient1 != orientation and orient2 == orientation: # NOT NORMAL STREET
							check_info = select_info(graph,actual_position,orient2,next_street2)[0]
							other_orientation = orient1
							wait_flag = True
							# if i<18308:
							# 	print('kkk')
							continue
				### NOT NORMAL STREET - waiting 			
				elif wait_flag == True: 
					if orientation == other_orientation: # the vehicle didn't go straight
						

						if ensure1 >4:
							# if i<18308:
							# 	print('kkk1' + str(i))
							wait_flag = False
							end_of_street_normal = True
							ensure1=0
						else:
							ensure1=ensure1+1
							continue
					elif coord_dist(actual_position,check_info.coordinates)<2 and orientation != other_orientation: # the vehicle went straight
						if ensure2 >4:
							wait_flag = False
							end_of_street_normal = True
							ensure2=0
						else:
							ensure2=ensure2+1
							continue
					else:
						continue
				# END OF A NORMAL STREET (ITS CONNECTIONS HAVE DIFFERENT ORIENTATIONS)
				if end_of_street_normal == True:
					maybe_actual_street = graph.connections_search(actual_street,orientation,actual_position)
					if maybe_actual_street is None:
							# print("waiting..." + str(waiting_distance) + str(actual_position) + str(i))
							waiting_distance=waiting_distance+velocity*sample_time
							if waiting_distance > 10:
								force_reset = True
								waiting_distance=0
								ensure3=0
								end_of_street = False
								end_of_street_normal = False
							# if i<18000 and i>16000:
							# 	print(orientation+actual_street.street_name+str(actual_position))
							continue
					elif ensure3>3:
						# print('kkk3')
						waiting_distance=0
						ensure3=0
						end_of_street = False
						end_of_street_normal = False
						actual_street = maybe_actual_street
						print('## NEW STREET:   ' + actual_street.street_name)
						# print(actual_position)
						# print(orientation)
						next_info = select_info(graph,actual_position,orientation,actual_street)[0]
						if next_info:
							last_valid = actual_position
							missed_samples = 1
							last_orientation = next_info.orientation
							dist_to_next = coord_dist(actual_position,next_info.coordinates)
							distance = dist_to_next
							distance_travelled = 0
							if next_info.next_node:
								dist_to_next_next = coord_dist(actual_position,next_info.next_node.coordinates)
					elif ensure3<4:
						# print('kkk2')
						ensure3=ensure3+1

################### TURNING BACK	
				if next_info and orientation == opposite_orientation(last_orientation) and last_dist_to_next < dist_to_next:
					if change_orientation > 3: # to ensure its not an error
						print('( TURNED BACK )')#+str(i))
						# flagfag=True
						change_orientation = 0

						force_reset = True
						continue
						# next_info = select_info(graph,actual_position,orientation,actual_street)[0]
						# # print(next_info.info)
						# if next_info:
						# 	last_orientation = next_info.orientation
						# 	dist_to_next = coord_dist(actual_position,next_info.coordinates)
						# 	distance = dist_to_next
						# 	distance_travelled = 0
						# 	if next_info.next_node:
						# 		dist_to_next_next = coord_dist(actual_position,next_info.next_node.coordinates)
						# 	continue
						# else:
						# 	end_of_street = True
						# 	print(str(actual_position)+str(orientation))
						# 	print('( end of street... )')# + str(orientation))
					else:
						change_orientation = change_orientation + 1


################### IF IT'S AN INTERSECTION
				if next_info and next_info.info_type == 'intersection' and orientation != next_info.previous_node.orientation and dist_to_next < next_info.radius:
					if ensure4 > 3:	
						maybe_actual_street = graph.connections_search(actual_street,orientation,actual_position)
						if maybe_actual_street is None:
								# print("waiting...")
								continue
						else:
							ensure4 = 0
							ensure5 = 0
							end_of_street = False
							end_of_street_normal = False
							actual_street = maybe_actual_street
							print('## NEW STREET:   ' + actual_street.street_name)# + str(i))
							# print(actual_position)
							# print(orientation)
						next_info = select_info(graph,actual_position,orientation,actual_street)[0]
						if next_info:
							last_valid = actual_position
							missed_samples = 1
							last_orientation = next_info.orientation
							dist_to_next = coord_dist(actual_position,next_info.coordinates)
							distance = dist_to_next
							distance_travelled = 0
							if next_info.next_node:
								dist_to_next_next = coord_dist(actual_position,next_info.next_node.coordinates)
					else:
						ensure4 = ensure4 + 1
						continue
				# THE CAR DOESNT TURN ON INTERSECTION
				elif next_info and next_info.info_type == 'intersection' and coord_dist(next_info.coordinates,next_info.next_node.coordinates) > dist_to_next_next and orientation == next_info.next_node.orientation: # orientation == next_info.previous_node.orientation:
					if ensure5 > 3:
						print('( ' + next_info.info + ' )')
						next_info = next_info.next_node
						ensure4 = 0
						ensure5 = 0
						if next_info:
							last_orientation = next_info.orientation
							dist_to_next = coord_dist(actual_position,next_info.coordinates)
							distance = dist_to_next
							distance_travelled = 0
							if next_info.next_node:
								dist_to_next_next = coord_dist(actual_position,next_info.next_node.coordinates)
							continue
						else:
							end_of_street = True
							print('( end of street... ??????????????)')
					else:
						ensure5 = ensure5 + 1
						continue

################### IF ITS WAITING FOR AN INFO TO BE DETECTED, BUT IT IS BEHIND
				if dist_to_next > last_dist_to_next and dist_to_next_next < last_dist_to_next_next and end_of_street == False and orientation == last_orientation:
					if info_behind > 2: # to ensure its not a gps error
						last_i = -1
						info_behind = 0
						print('( ignored: ' + next_info.info + ' )')
						next_info = next_info.next_node
						if next_info:
							last_orientation = next_info.orientation
							dist_to_next = coord_dist(actual_position,next_info.coordinates)
							distance = dist_to_next
							distance_travelled = 0
							if next_info.next_node:
								dist_to_next_next = coord_dist(actual_position,next_info.next_node.coordinates)
							continue
						else:
							end_of_street = True
							print('( end of street... )')
					elif info_behind == 0 or i-last_i == 1: # to ensure it is sequentially
						last_i = i
						info_behind = info_behind + 1


################### GET NEXT INFO WHILE ON THE SAME STREET
				if next_info and dist_to_next < next_info.radius and next_info.info_type != 'intersection':
					if next_info.info_type != 'sign' and next_info.info_type != 'road mark' and last_info != next_info:
						last_info = next_info 
						print('( ' + next_info.info + '   --->   ' + next_info.info_type + ' )')
					elif last_info != next_info: # detect repeated infos - reset function may cause the system to output an information that was already output
						last_info = next_info
						print('                                                    ' + next_info.info + '   --->   ' + next_info.info_type)# + str(i))
						change_orientation = 0
					last_valid = actual_position
					first = False
					next_info = next_info.next_node
					# print(next_info.info + '.......')
					if next_info:
						last_orientation = next_info.orientation
						dist_to_next = coord_dist(actual_position,next_info.coordinates)
						distance = dist_to_next
						distance_travelled = 0
						if next_info.next_node: 
							dist_to_next_next = coord_dist(actual_position,next_info.next_node.coordinates)
						continue
					else:
						end_of_street = True
						print('( end of street... )')

			# end = time.time()
			timee = time.time()-start
			times.append(timee)
			# pause = 0.05 -(end-start)
			# if pause < 0:
			# 	print(pause)
			# time.sleep(pause)
		print(numpy.amax(times))
		print(apagarquandovires)
		# print(coord_dist([38.737244,-9.138991],[38.737109,-9.138973]))
		# print(estimate_coord([38.7371092520966,-9.138990724871851],0.186891520396024,-1.844972604681771,0.456491680132001,2))


		# Este código demora no max 0.007 seg e o gps tem um tempo de amostragem de 0.05 seg...
		# 0.03 seg corresponde a 1 m percorrido a uma velocidade de 120 km/h



	with open("valids.txt", "w") as txt_file:
		for line in vector:
			txt_file.write(str(line[0]) + " " + str(line[1]) + "\n")
	with open("outliers.txt", "w") as txt_file:
		for line in vector1:
			txt_file.write(str(line[0]) + " " + str(line[1]) + "\n")
	with open("estimated.txt", "w") as txt_file:
		for line in vector2:
			txt_file.write(str(line[0]) + " " + str(line[1]) + "\n")
	with open("all.txt", "w") as txt_file:
		for line in vector3:
			txt_file.write(str(line[0]) + " " + str(line[1]) + "\n")			
	with open("orient.txt", "w") as txt_file:
		for line in vector4:
			txt_file.write(str(line) + "\n")				

		#		VER SE GET_CLOSEST NAO FUNCIONA MAL COM CARRO ESTACIONADO, TEM QUE ESPERAR PELA ORIENTAçÃO CERTA
		#		METER NO RELATORIO A PRECISAO DAS COORDENADAS DAS INFOS
		#		METER NO RELATORIO A PRECISAO Do GPS

		# 	if intersection or end of street:
					#-separar em duas coisas
					#-implementar 'ensure3'

		# testar só com gps2 
		# testar com test2

		# RESET mais abrangente