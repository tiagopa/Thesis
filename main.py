import math as m
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import parse_map as p
import time
import csv

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

	# def connections_search(self,node,street_name):
	# 	for connection in node.connections:
	# 		if connection.street_name == street_name:
	# 			return connection
	# 	print('"' + street_name + '"' + ' is not connected to ' + '"' + node.street_name + '"' + '\n')

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
		if counter == 0 or best_distance > 15:
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
	print('Corresponding street not found!')


#################################################################################################################################################
# Calculates the angle of the direction from two GPS coordinates 'a' and 'b'.
# Point 'a' corresponds to the left gps on the car. The angle is computed with point 'a' fixed in the center of Cartesian coordinate system.

# def orientation(a,b):
	 
# 	angle = m.atan2((b[0]-a[0]),(b[1]-a[1]))
	
# 	if (1/4)*m.pi <= angle <= (3/4)*m.pi:
# 		direction = 'West'
# 	elif (-1/4)*m.pi <= angle < (1/4)*m.pi: 
# 		direction = 'North'
# 	elif (-3/4)*m.pi <= angle < (-1/4)*m.pi: 
# 		direction = 'East'
# 	else:
# 		direction = 'South'

# 	#print(m.degrees(angle))
# 	return direction

def orientation_(vx,vy):
	 
	angle = m.atan2(vy,vx)
	
	if (1/4)*m.pi <= angle <= (3/4)*m.pi:
		direction = 'North'
	elif (-1/4)*m.pi <= angle < (1/4)*m.pi: 
		direction = 'East'
	elif (-3/4)*m.pi <= angle < (-1/4)*m.pi: 
		direction = 'South'
	else:
		direction = 'West'

	#print(m.degrees(angle))
	return direction #, m.degrees(angle)

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
	# get 2nd closest info on infos1 list
	if closest_info.next_node is None: # if its the last item on the list:
		if coord_dist(actual_position,closest_info.previous_node.coordinates) > coord_dist(closest_info.coordinates,closest_info.previous_node.coordinates):
			return None # end of road
		else:
			# return not_point_type(closest_info)
			return closest_info
	elif closest_info.previous_node is None: # if its the first item on the list:
		if coord_dist(actual_position,closest_info.next_node.coordinates) > coord_dist(closest_info.coordinates,closest_info.next_node.coordinates):
			# return not_point_type(closest_info)
			return closest_info
		else:
			# return not_point_type(closest_info.next_node)
			return closest_info.next_node
	else: # if its in the middle of the list:
		#if coord_dist(actual_position,closest_info.previous_node.coordinates) > coord_dist(closest_info.coordinates,closest_info.previous_node.coordinates):
		if coord_dist(actual_position,closest_info.next_node.coordinates) < coord_dist(closest_info.coordinates,closest_info.next_node.coordinates):
			# return not_point_type(closest_info.next_node)
			return closest_info.next_node
		else:
			# return not_point_type(closest_info)
			return closest_info


def select_info(graph,actual_position,orientation,actual_street=None):
	
	if actual_street is None:
		actual_street = check_street(graph,actual_position)
	if actual_street.infos2 is None: ## If there is only one list:
		# get closest info on infos1 list
		closest_info = get_closest(actual_street.infos1,actual_position,orientation)
		if closest_info == None:
			print('There are no infos with the desired direction')
			print('NOT SURE... but returned head anyway')
			return actual_street.infos1.head, actual_street
		return get_2nd_closest(closest_info,actual_position), actual_street
	else: # If there are two lists:
		# get closest infos
		closest_info1 = get_closest(actual_street.infos1,actual_position,orientation)
		closest_info2 = get_closest(actual_street.infos2,actual_position,orientation)
		if closest_info1 == None and closest_info2 == None: # nothing found
			print('There are no infos with the desired direction')
			return None
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
#############################################################     MAIN    #######################################################################
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

	# file = open('testfile1.txt','w') 
	with open('test5_without_tips.csv', mode='r') as csv_file:
		csv_reader = csv.DictReader(csv_file)
		for row in csv_reader:
			# start = time.time()
			# GET DATA
			actual_position=[]
			actual_position.append(float(row["lat"]))
			actual_position.append(float(row["long"]))

			vx = float(row["vx"])
			vy = float(row["vy"])
			orientation = orientation_(vx,vy)
			# orientation = row["orientation"]

			i=i+1
			# print(i)
			# file.write(orientation + str(i) + '\n')

			# FIRST LOCALIZATION
			if i == 1:
				next_info, actual_street = select_info(graph,actual_position,orientation)
				print('## THE VEHICLE IS AT:   ' + actual_street.street_name)
				if next_info:
					dist_to_next = coord_dist(actual_position,next_info.coordinates)
					last_orientation = next_info.orientation
					if next_info.next_node:
						dist_to_next_next = coord_dist(actual_position,next_info.next_node.coordinates)
					if dist_to_next < next_info.radius:
						if (next_info.info_type != 'sign' and next_info.info_type != 'road mark'):
							print('( ' + next_info.info + '   --->   ' + next_info.info_type + ' )')
						else:
							print('                                                    ' + next_info.info + '   --->   ' + next_info.info_type)
						next_info = next_info.next_node
						if next_info:
							last_orientation = next_info.orientation
							dist_to_next = coord_dist(actual_position,next_info.coordinates)
							if next_info.next_node:
								dist_to_next_next = coord_dist(actual_position,next_info.next_node.coordinates)
				else:
					print('No next info')
				# i=i+1
				continue
			# NOT FIRST TIME (MAIN)
			else:
				# i=i+1
				last_dist_to_next = dist_to_next
				last_dist_to_next_next = dist_to_next_next
				if next_info: 
					# print(i)
					last_orientation = next_info.orientation
					dist_to_next = coord_dist(actual_position,next_info.coordinates)
					# if (i>65):
						# print(i)
						# print(dist_to_next)
						# print(actual_position)
						# print(next_info.info)
					# print('nexttt:::    ' + next_info.info)
					if next_info.next_node:
						dist_to_next_next = coord_dist(actual_position,next_info.next_node.coordinates)
				else:
					end_of_street = True
					# print('( end of street... )')

				# IF IT'S THE END OF A STREET
				if (end_of_street == True and end_of_street_normal == False and wait_flag == False):
					
					if (len(actual_street.connections)==1):
						end_of_street_normal = True
					else: # In IST, a street cant have more than 2 connections... Make generic code for real maps where a street can have more than 2 connections.
						next_street1 = actual_street.connections[0][0]
						orient1 = actual_street.connections[0][1]
						# print(orient1)
						next_street2 = actual_street.connections[1][0]
						orient2 = actual_street.connections[1][1]
						# print(orient2)
						# print(orientation)
						if (orient1 != orientation and orient2 != orientation): # NORMAL STREET
							# print('cacacacacaca0')
							end_of_street_normal = True
						elif (orient1 == orientation and orient2 != orientation): # NOT NORMAL STREET
							check_info = select_info(graph,actual_position,orient1,next_street1)[0]
							# print(check_info.info)
							other_orientation = orient2
							wait_flag = True
							# print(other_orientation)
							# print('cacacacacaca1')
							continue
						elif (orient1 != orientation and orient2 == orientation): # NOT NORMAL STREET
							check_info = select_info(graph,actual_position,orient2,next_street2)[0]
							other_orientation = orient1
							wait_flag = True
							# print('cacacacacaca2')
							continue
				elif (wait_flag == True): # NOT NORMAL STREET - waiting 
					if (orientation == other_orientation): # the vehicle didnt go straight
						wait_flag = False
						end_of_street_normal = True
					elif (coord_dist(actual_position,check_info.coordinates)<2 and orientation != other_orientation): # the vehicle went straight
						wait_flag = False
						end_of_street_normal = True
					else:
						continue

				# 	for connect in actual_street.connections:
				# 		dist = coord_dist(actual_position,connect.)
				# 	procurar head das connections
				# 	quando tiver mt perto de uma delas, se a orientaçao é a mesma, é essa
				# 	continue
				
				# IF IT'S TURNING BACK	
				if orientation == opposite_orientation(last_orientation) and last_dist_to_next < dist_to_next:
					if change_orientation > 2: # to ensure its not an error
						print('( TURNED BACK )')
						# flagfag=True
						change_orientation = 0
						next_info = select_info(graph,actual_position,orientation,actual_street)[0]
						# print(next_info.info)
						if next_info:
							last_orientation = next_info.orientation
							dist_to_next = coord_dist(actual_position,next_info.coordinates)
							if next_info.next_node:
								dist_to_next_next = coord_dist(actual_position,next_info.next_node.coordinates)
							continue
						else:
							end_of_street = True
							print('( end of street... )')
					else:
						change_orientation = change_orientation + 1

				# IF IT'S AN INTERSECTION OR THE END OF A NORMAL STREET (ITS CONNECTIONS HAVE DIFFERENT ORIENTATIONS)
				if (next_info and next_info.info_type == 'intersection' and orientation != next_info.previous_node.orientation and dist_to_next < next_info.radius) or (end_of_street_normal == True):
					# end_of_street = False
					# end_of_street_normal = False
					# actual_street = graph.connections_search(actual_street,orientation,actual_position)
					# if actual_street is None: 
					# 		print("NO CONNECTIONS")
					# else:
					# 	print('## NEW STREET:   ' + actual_street.street_name)
					# 	# print(actual_position)
					# next_info = select_info(graph,actual_position,orientation,actual_street)[0]
					maybe_actual_street = graph.connections_search(actual_street,orientation,actual_position)
					if maybe_actual_street is None:
							# print("waiting...")
							continue 
					else:
						end_of_street = False
						end_of_street_normal = False
						actual_street = maybe_actual_street
						print('## NEW STREET:   ' + actual_street.street_name)
						# print(actual_position)
					next_info = select_info(graph,actual_position,orientation,actual_street)[0]
					if next_info:
						last_orientation = next_info.orientation
						dist_to_next = coord_dist(actual_position,next_info.coordinates)
						if next_info.next_node:
							dist_to_next_next = coord_dist(actual_position,next_info.next_node.coordinates)
						# continue
				# ELIF THE CAR DOESNT TURN ON INTERSECTION
				elif (next_info and next_info.info_type == 'intersection' and coord_dist(next_info.coordinates,next_info.next_node.coordinates) > dist_to_next_next and orientation == next_info.previous_node.orientation):
				# elif (next_info and next_info.info_type == 'intersection' and dist_to_next_next < 0.5):
					print('( ' + next_info.info + ' )')
					next_info = next_info.next_node
					if next_info:
						last_orientation = next_info.orientation
						dist_to_next = coord_dist(actual_position,next_info.coordinates)
						if next_info.next_node:
							dist_to_next_next = coord_dist(actual_position,next_info.next_node.coordinates)
						continue
					else:
						end_of_street = True
						print('( end of street... ????)')

				# IF ITS WAITING FOR AN INFO TO BE DETECTED, BUT IT IS BEHIND
				if dist_to_next > last_dist_to_next and dist_to_next_next < last_dist_to_next_next and end_of_street == False and orientation == last_orientation:
					# last_i = i
					if info_behind > 2: # to ensure its not a gps error
						last_i = -1
						info_behind = 0
						print('( ignored: ' + next_info.info + ' )')
						next_info = next_info.next_node
						if next_info:
							last_orientation = next_info.orientation
							dist_to_next = coord_dist(actual_position,next_info.coordinates)
							if next_info.next_node:
								dist_to_next_next = coord_dist(actual_position,next_info.next_node.coordinates)
							continue
						else:
							end_of_street = True
							print('( end of street... )')
					elif((info_behind == 0) or ((i-last_i) == 1)): # to ensure it is sequentially
						last_i = i
						info_behind = info_behind + 1

				# GET NEXT INFO WHILE ON THE SAME STREET
				if (next_info and dist_to_next < next_info.radius and next_info.info_type != 'intersection'):
					if (next_info.info_type != 'sign' and next_info.info_type != 'road mark'):
						print('( ' + next_info.info + '   --->   ' + next_info.info_type + ' )')
					else:
						print('                                                    ' + next_info.info + '   --->   ' + next_info.info_type)
					next_info = next_info.next_node
					# print(next_info.info + '.......')
					if next_info:
						last_orientation = next_info.orientation
						dist_to_next = coord_dist(actual_position,next_info.coordinates)
						if next_info.next_node:
							dist_to_next_next = coord_dist(actual_position,next_info.next_node.coordinates)
						continue
					else:
						end_of_street = True
						print('( end of street... )')

			# end = time.time()
			# pause = 0.05 -(end-start)
			# if pause < 0:
			# 	print(pause)
			# time.sleep(pause)


# ...tipps.csv contains lines 1039-1044 which are outliers, but ...tips.csv doesnt