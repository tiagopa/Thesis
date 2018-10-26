import math as m
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
#################################################################################################################################################
# Node of a linked list. Each node represents an information about a given street.
class InfoNode:

	def __init__(self,info=None,info_type=None,coordinates=None,next_node=None):
		self.info = info
		self.info_type = info_type
		self.coordinates = coordinates
		self.next_node = next_node
		self.missed = 0

	def get_info(self):
		return self.info

	def get_next(self):
		return self.next_node

	def set_next(self,new_next):
		self.next_node = new_next


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
			return self.street_name + '    ---->    ' + str([x.street_name for x in self.connections])

		def ConnectsTo(self,node):
			self.connections.append(node)

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


#################################################################################################################################################
# Compute distance between coordinates

LOCAL_PI = 3.1415926535897932385 
earthRadius = 3958.75

def toRadians(degrees):

	return degrees*LOCAL_PI/180

def coord_dist(a,b):

	dLat = toRadians(b[0]-a[0])
	dLong = toRadians(b[1]-a[1])
	a = m.sin(dLat/2)*m.sin(dLat/2)+m.cos(toRadians(a[0]))*m.cos(toRadians(b[0]))*m.sin(dLong/2)*m.sin(dLong/2)
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
			return node.street_name
	print('Corresponding street not found!')


#################################################################################################################################################




if __name__ == '__main__':

	graph = Graph()

	# ADD STREETS
	ist1 = graph.add_node('IST1')
	ist2 = graph.add_node('IST2')
	ist3 = graph.add_node('IST3')
	ist4 = graph.add_node('IST4')
	ist5 = graph.add_node('IST5')
	ist6 = graph.add_node('IST6')


	# ADD CONNECTIONS BETWEEN STREETS
	ist1.ConnectsTo(ist2)
	ist2.ConnectsTo(ist5)
	ist2.ConnectsTo(ist4)
	ist3.ConnectsTo(ist1)
	ist4.ConnectsTo(ist6)
	ist4.ConnectsTo(ist3)
	ist5.ConnectsTo(ist4)
	ist6.ConnectsTo(ist3)

	
	# ADD POLYGONS
	ist1.add_polygon(Polygon([(38.7363230991576, -9.139001958466078), (38.73619206646635, -9.138992521945305), (38.73617864589788, -9.139013948689843), (38.73538720735966, -9.138931329270916), (38.73550158612309, -9.138092240386911), (38.7356723224085, -9.137737199919027), (38.73717698997828, -9.137931543747657), (38.73814687863733, -9.138029190510972), (38.73812176408418, -9.139219701805338), (38.73734601594125, -9.139128653098094), (38.73733861980222, -9.139113030015157), (38.73721603046326, -9.139083737106727), (38.73718013886931, -9.139111224981475), (38.7363230991576, -9.139001958466078)]))
	ist2.add_polygon(Polygon([(38.73719526310708, -9.139105463875092), (38.73732869152742, -9.139122782958459), (38.7372880889953, -9.139703030510116), (38.73715981247192, -9.139687008408631), (38.73719526310708, -9.139105463875092)]))
	ist3.add_polygon(Polygon([(38.73628463515922, -9.13958606593704), (38.73621035157193, -9.13959223264856), (38.73614214843333, -9.139568406232961), (38.73619374865896, -9.139009516434291), (38.73632164568041, -9.139013815764292), (38.73628463515922, -9.13958606593704)]))
	ist4.add_polygon(Polygon([(38.73613533232054, -9.139839195558723), (38.73615878533402, -9.139590006438715), (38.73626475917681, -9.139604043244823), (38.73629986349925, -9.139578279990491), (38.73714338383206, -9.139672313659524), (38.73715050428667, -9.139698015045163), (38.73729354454682, -9.139709629987681), (38.73726260002417, -9.140038807540687), (38.73613533232054, -9.139839195558723)]))
	ist5.add_polygon(Polygon([(38.73800795690704, -9.139736916334742), (38.73791552344088, -9.140726248487134), (38.73777619370115, -9.140765725414372), (38.73758627314033, -9.140686563490926), (38.73727942289231, -9.139943328037813), (38.73730117868335, -9.139708255953904), (38.73800795690704, -9.139736916334742)]))
	ist6.add_polygon(Polygon([(38.73544601220729, -9.139795877938942), (38.73545388364612, -9.139476559057965), (38.73615489753738, -9.139576844057689), (38.73613027929753, -9.139828376433218), (38.73544601220729, -9.139795877938942)]))


	# ADD STREET INFORMATIONS
	IST_5_0 = LinkedList(InfoNode('prohibit','sign',[38.737288, -9.139697]),ist5)
	IST_5_0.insert(InfoNode('prohibit', 'sign',[38.737175, -9.139682]))
	IST_5_0.insert(InfoNode('crosswalk', 'sign',[38.737335, -9.139882]))
	IST_5_1 = LinkedList(InfoNode('covered car parking','sign',[38.737707, -9.140596]),ist2)
	IST_5_1.insert(InfoNode('no priority road', 'sign',[38.737957, -9.139994]))
	IST_5_1.insert(InfoNode('Go right', 'sign',[38.737871, -9.139864]))
	IST_5_1.insert(InfoNode('No bicycles and motorcycles', 'sign',[38.737877, -9.139870]))
	IST_5_1.insert(InfoNode('Reserved parking', 'sign',[38.737735, -9.139750]))
	ist5.set_info(IST_5_0,IST_5_1)


	IST_2 = LinkedList(InfoNode('handicapped parking','sign',[38.737282, -9.139652]),ist1)
	IST_2.insert(InfoNode('crosswalk', 'sign',[38.737177, -9.139652]))
	IST_2.insert(InfoNode('crosswalk', 'sign',[38.737208, -9.139096]))
	IST_2.insert(InfoNode('crosswalk', 'sign',[38.737317, -9.139107]))
	ist2.set_info(IST_2)


	IST_4 = LinkedList(InfoNode('prohibit','sign',[38.736143, -9.139583]),[ist2, ist5])
	IST_4.insert(InfoNode('crosswalk', 'sign',[38.736263, -9.139810]))
	IST_4.insert(InfoNode('crosswalk', 'sign',[38.736831, -9.139736]))
	IST_4.insert(InfoNode('end of motorcycles parking', 'sign',[38.736893, -9.139694]))
	IST_4.insert(InfoNode('motorcycles parking', 'sign',[38.737110, -9.139685]))
	ist4.set_info(IST_4)


	IST_3 = LinkedList(InfoNode('stop','sign',[38.736201, -9.139005]),[ist4, ist6])
	ist3.set_info(IST_3)


	IST_6 = LinkedList(InfoNode('prohibit','sign',[38.736279, -9.139596]),[ist4, ist6])
	IST_6.insert(InfoNode('Go left', 'sign',[38.736153, -9.139581]))
	IST_6.insert(InfoNode('crosswalk', 'sign',[38.736153, -9.139581]))
	ist6.set_info(IST_6)

	## North -> South
	IST_1_0 = LinkedList(InfoNode('Parking prohibited','sign',[38.736303, -9.137981]))
	IST_1_0.insert(InfoNode('End of handicapped parking','sign',[38.735747, -9.137813]))
	IST_1_0.insert(InfoNode('Handicapped parking', 'sign',[38.735665, -9.137805]))
	IST_1_0.insert(InfoNode('no priority road', 'sign',[38.735759, -9.137921]))
	# turn around
	IST_1_0.insert(InfoNode('Parking prohibited', 'sign',[38.735741, -9.138967]))
	IST_1_0.insert(InfoNode('crosswalk', 'sign',[38.736044, -9.138887]))
	IST_1_0.insert(InfoNode('Parking prohibited', 'sign',[38.736050, -9.138998]))
	IST_1_0.insert(InfoNode('prohibit', 'sign',[38.736192, -9.138999]))
	IST_1_0.insert(InfoNode('prohibit', 'sign',[38.736311, -9.139008]))
	# turn around
	IST_1_0.insert(InfoNode('crosswalk', 'road mark',[38.736775, -9.138851]))
	IST_1_0.insert(InfoNode('crosswalk', 'sign',[38.736929, -9.138990]))
	IST_1_0.insert(InfoNode('Reserved parking', 'sign',[38.736965, -9.139067]))
	IST_1_0.insert(InfoNode('End of reserved parking', 'sign',[38.737090, -9.139078]))
	IST_1_0.insert(InfoNode('crosswalk', 'sign',[38.737208, -9.139096]))
	# turn  right or turn around
	IST_1_0.insert(InfoNode('crosswalk', 'sign',[38.737317, -9.139107]))
	IST_1_0.insert(InfoNode('Parking prohibited', 'sign',[38.737504, -9.139134]))
	IST_1_0.insert(InfoNode('crosswalk', 'sign',[38.737640, -9.139059]))
	IST_1_0.insert(InfoNode('Parking prohibited', 'sign',[38.737782, -9.139154]))
	IST_1_0.insert(InfoNode('Speed limit (20km/h)', 'sign',[38.737893, -9.139069]))
	IST_1_0.insert(InfoNode('crosswalk', 'road mark',[38.737617, -9.138069]))
	# (...)

	## South -> North
	IST_1_1 = LinkedList(InfoNode('crosswalk', 'road mark',[38.737617, -9.138069]))
	IST_1_1.insert(InfoNode('no priority road', 'sign',[38.737882, -9.138137]))
	# turn around
	IST_1_1.insert(InfoNode('crosswalk', 'sign',[38.737493, -9.139015]))
	# turn around
	IST_1_1.insert(InfoNode('End of reserved parking', 'sign',[38.737090, -9.139078]))
	IST_1_1.insert(InfoNode('Reserved parking', 'sign',[38.736965, -9.139067]))
	IST_1_1.insert(InfoNode('crosswalk', 'road mark',[38.736775, -9.138851]))
	IST_1_1.insert(InfoNode('crosswalk', 'sign',[38.736599, -9.138961]))
	# turn around
	IST_1_1.insert(InfoNode('prohibit', 'sign',[38.736311, -9.139008]))
	IST_1_1.insert(InfoNode('prohibit', 'sign',[38.736192, -9.138999]))
	IST_1_1.insert(InfoNode('crosswalk', 'sign',[38.735900, -9.138864]))
	IST_1_1.insert(InfoNode('Speed limit (20km/h)', 'sign',[38.735632, -9.138837]))
	IST_1_1.insert(InfoNode('Handicapped parking', 'sign',[38.735665, -9.137805]))
	IST_1_1.insert(InfoNode('End of handicapped parking','sign',[38.735747, -9.137813]))
	IST_1_1.insert(InfoNode('Parking prohibited', 'sign',[38.736303, -9.137981]))
	IST_1_1.insert(InfoNode('priority road', 'sign',[38.736303, -9.137981]))
	IST_1_1.insert(InfoNode('Parking prohibited', 'sign',[38.736541, -9.138014]))
	ist1.set_info(IST_1_0,IST_1_1)

	#print(coord_dist([38.737283, -9.139612],[38.737180, -9.139585]))

	#print(graph)
	
	#print(ist1.infos1)
	#print(ist1.infos2)

	#print(check_street(graph,[38.736590, -9.141400]))