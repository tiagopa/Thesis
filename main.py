import math as m
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import parse_map as p
import time
import csv

#################################################################################################################################################
# Node of a linked list. Each node represents an information about a given street.
class InfoNode:

	def __init__(self,info=None,info_type=None,orientation=None,coordinates=None):
		self.info = info
		self.info_type = info_type
		self.orientation = orientation
		self.coordinates = coordinates
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

	def __init__(self,head=None,previous_streets=None):
		self.previous_streets = previous_streets
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

		def add_coord_point(self,point):
			self.set_of_points.append(point)

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

	def connections_search(self,node,street_name):
		for connection in node.connections:
			if connection.street_name == street_name:
				return connection
		print('"' + street_name + '"' + ' is not connected to ' + '"' + node.street_name + '"' + '\n')

	def connections_orientation_search(self,node,orientation):
		for connection in node.connections:
			if connection[1] == orientation: ### VER DISTANCIAS QUANDO HÀ MAIS LIGAÇOES CM O MESMO SENTIDO
				return connection[0]
		print('connection not found!')


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

def orientation(a,b):
	 
	angle = m.atan2((b[0]-a[0]),(b[1]-a[1]))
	
	if (1/4)*m.pi <= angle <= (3/4)*m.pi:
		direction = 'West'
	elif (-1/4)*m.pi <= angle < (1/4)*m.pi: 
		direction = 'North'
	elif (-3/4)*m.pi <= angle < (-1/4)*m.pi: 
		direction = 'East'
	else:
		direction = 'South'

	#print(m.degrees(angle))
	return direction


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


def get_closest(info_list,actual_position,orientation):
	previous_distance = 100000000 # all distances will be lower than this one (random)
	info = info_list.head
	while info and info.orientation != orientation: # skip initial infos with different orientation than the desired		
			info = info.get_next()
	if info == None:
		return None
	while info: # loop on infos
		distance = coord_dist(actual_position,info.coordinates)
		if distance	< previous_distance: # check if actual info is closest to actual_position than previous one 
			previous_distance = distance
			closest_info = info
		info = info.get_next()
		while info and info.orientation != orientation: # skip infos with different orientation than the desired
			info = info.get_next()
	return closest_info


def get_2nd_closest(closest_info,actual_position):
	# get 2nd closest info on infos1 list
	if closest_info.next_node is None: # if its the last item on the list:
		if coord_dist(actual_position,closest_info.previous_node.coordinates) > coord_dist(closest_info.coordinates,closest_info.previous_node.coordinates):
			return None # end of road
		else:
			return not_point_type(closest_info)
	elif closest_info.previous_node is None: # if its the first item on the list:
		if coord_dist(actual_position,closest_info.next_node.coordinates) > coord_dist(closest_info.coordinates,closest_info.next_node.coordinates):
			return not_point_type(closest_info)
		else:
			return not_point_type(closest_info.next_node)
	else: # if its in the middle of the list:
		#if coord_dist(actual_position,closest_info.previous_node.coordinates) > coord_dist(closest_info.coordinates,closest_info.previous_node.coordinates):
		if coord_dist(actual_position,closest_info.next_node.coordinates) < coord_dist(closest_info.coordinates,closest_info.next_node.coordinates):
			return not_point_type(closest_info.next_node)
		else:
			return not_point_type(closest_info)


def select_info(graph,actual_position,orientation,actual_street=None):
	
	if actual_street is None:
		actual_street = check_street(graph,actual_position)
	if actual_street.infos2 is None: ## If there is only one list:
		# get closest info on infos1 list
		closest_info = get_closest(actual_street.infos1,actual_position,orientation)
		if closest_info == None:
			print('There are no infos with the desired direction')
			return None
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
	#print(coord_dist([38.737283, -9.139612],[38.737180, -9.139585]))

	#print(graph)
	#print(graph.street_search('IST1').infos1)
	#print(check_street(graph,[38.737671, -9.139866]))
	
	#print(orientation([38.737394, -9.139085],[38.737398, -9.139045]))
	
	# cenas = select_info(graph,[38.737421, -9.139812],orientation([38.737746, -9.139018],[38.737753, -9.138979]))
	# if cenas: 
	# 	print(cenas.info)



	# end = time.time()
	# print(end - start)
	
	i = 0
	change_orientation=0
	dist_to_next = 10000000000
	end_of_street = False
	with open('example.csv', mode='r') as csv_file:
		csv_reader = csv.DictReader(csv_file)
		for row in csv_reader:
			actual_position=[]
			actual_position.append(float(row["lat"]))
			actual_position.append(float(row["long"]))
			orientation = row["orientation"]
			if i == 0:
				next_info, actual_street = select_info(graph,actual_position,orientation)
				if next_info: 
					print(next_info.info)
				else:
					print('not next_info')
				i=1
				last_orientation = orientation
				continue
			last_dist_to_next = dist_to_next
			if next_info:
				dist_to_next = coord_dist(actual_position,next_info.coordinates)
				print(dist_to_next)
			if orientation == opposite_orientation(last_orientation) and last_dist_to_next < dist_to_next: # if its turning back while on the same street
				if change_orientation > 2: # to ensure its not an error
					print('--TURNED BACK--')
					change_orientation = 0
					next_info, actual_street = select_info(graph,actual_position,orientation)
					if next_info: 
						print(next_info.info)
					else:
						print('not next_info')
				else:
					change_orientation = change_orientation + 1
			if (next_info and next_info.info_type == 'intersection' and orientation != next_info.previous_node.orientation) or (end_of_street == True and orientation != last_orientation): # look for intersection
				end_of_street = False
				print('--NEW STREET--')
				actual_street = graph.connections_orientation_search(actual_street,orientation) #### PODE HAVER MAIS DO QUE UMA RUA COM A MESMA DIREÇAO, VER QUAL TEM O PONTO MAIS PERTO DE NÓS E DECIDIR
				#print(actual_street.street_name)
				next_info = select_info(graph,actual_position,orientation,actual_street)[0]
				print(next_info.info)
			if next_info and dist_to_next < 10 and next_info.info_type != 'intersection': # get next info while driving on the same street without turning back
				#print('NEW INFO:')
				next_info = next_info.next_node
				if next_info: 
					print(next_info.info)
					last_orientation = next_info.orientation
				else:
					print('NO MORE INFOS...')
			if not next_info:
				end_of_street = True



				#### NAO PODE APARECER O covered car parking, TEM QUE IR BUSCAR A PROXIMA DISTANCIA PARA COMPARAR

















	# cenas = select_info(graph,[38.737950, -9.139130],'South')
	# if cenas: 
	# 	print(cenas.info)