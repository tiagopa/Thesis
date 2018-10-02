
#################################################################################################################################################
# Node of a linked list. Each node represents an information about a given street.
class InfoNode:

	def __init__(self,info=None,info_type=None,next_node=None):
		self.info = info
		self.info_type = info_type
		self.next_node = next_node
		self.times_missed = 0

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

		def __init__(self,street_name,infos1,infos2,length):
			self.street_name = street_name
			self.infos1 = infos1 # linked list
			self.infos2 = infos2 # linked list
			self.length = length
			self.connections = [] # connects to

		def __str__(self):
			return self.street_name + '    ---->    ' + str([x.street_name for x in self.connections])

		def ConnectsTo(self,node):
			self.connections.append(node)

		def set_info(self,infos1=None,infos2=None):
			self.infos1 = infos1
			self.infos2 = infos2

	def __init__(self):
		self.nodes = []
		self.nodeCount = 0

	def __repr__(self):
		result = ""
		for node in self.nodes:
			for connection in node.connections:
				result += node.street_name + '    ---->    ' + connection.street_name + '\n'
		return result

	def add_node(self,street_name,infos1=None,infos2=None,length=None):
		node = self.StreetNode(street_name,infos1,infos2,length)
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





if __name__ == '__main__':



	graph = Graph()


	# ADD STREETS
	n0 = graph.add_node('Rua Actor Vale')
	n1 = graph.add_node('Rua Actor Joaquim de Almeida')
	n2 = graph.add_node('Alameda Dom Afonso Henriques')
	n3 = graph.add_node('Rua Carvalho Araújo')
	n4 = graph.add_node('Avenida Manuel da Maia')
	n5 = graph.add_node('Praça de Londres')
	n6 = graph.add_node('Avenida Guerra Junqueiro')
	n7 = graph.add_node('Avenida de António José de Almeida') # SPECIAL CASE: rotunda a meio da avenida!!!
	n8 = graph.add_node('Avenida do México')
	n9 = graph.add_node('Avenida Almirante Reis')
	n10 = graph.add_node('Avenida de Paris')

	n11 = graph.add_node('Rotunda')

	n12 = graph.add_node('Rua Alves Redol') # SPECIAL CASE: rotunda a meio da avenida!!!
	n13 = graph.add_node('Avenida João Crisóstomo')
	n14 = graph.add_node('Avenida Rovisco Pais')
	n15 = graph.add_node('Largo Mendonça e Costa')
	n16 = graph.add_node('Rua Morais Soares')
	n17 = graph.add_node('Rua António Pereira Carrilho')
	n18 = graph.add_node('Largo do Leão')
	n19 = graph.add_node('Rua Visconde de Santarém')
	n20 = graph.add_node('Avenida Duque de Ávila')
	n21 = graph.add_node('Rua Bacelar e Silva')


	# ADD CONNECTIONS BETWEEN STREETS
	n0.ConnectsTo(n1)
	n0.ConnectsTo(n15)
	n15.ConnectsTo(n3)
	n3.ConnectsTo(n15)
	n1.ConnectsTo(n3)
	n2.ConnectsTo(n0)
	n3.ConnectsTo(n2)
	n4.ConnectsTo(n2)
	n2.ConnectsTo(n4)
	n4.ConnectsTo(n5)
	n5.ConnectsTo(n4)
	n5.ConnectsTo(n6)
	n6.ConnectsTo(n2)
	n7.ConnectsTo(n4)
	n4.ConnectsTo(n7)
	n8.ConnectsTo(n4)
	n8.ConnectsTo(n5)
	n5.ConnectsTo(n8)
	n8.ConnectsTo(n7)
	n7.ConnectsTo(n8)
	n9.ConnectsTo(n2)
	n2.ConnectsTo(n9)
	n10.ConnectsTo(n9)
	n5.ConnectsTo(n10)
	n11.ConnectsTo(n7)
	n7.ConnectsTo(n11)
	n11.ConnectsTo(n12)
	n12.ConnectsTo(n11)
	n13.ConnectsTo(n12)
	n12.ConnectsTo(n13)
	n12.ConnectsTo(n14)
	n14.ConnectsTo(n4)
	n9.ConnectsTo(n16)
	n16.ConnectsTo(n9)
	n16.ConnectsTo(n3)
	n9.ConnectsTo(n17)
	n17.ConnectsTo(n9)
	n18.ConnectsTo(n4)
	n4.ConnectsTo(n18)
	n18.ConnectsTo(n17)
	n17.ConnectsTo(n18)
	n18.ConnectsTo(n19)
	n19.ConnectsTo(n18)
	n19.ConnectsTo(n14)
	n12.ConnectsTo(n19)
	n19.ConnectsTo(n12)
	n20.ConnectsTo(n12)
	n20.ConnectsTo(n19)
	n20.ConnectsTo(n14)
	n11.ConnectsTo(n21)









	# ADD STREET INFORMATIONS
	ActorVale = LinkedList(InfoNode('no parking/stop','sign'),n2)

	ActorVale.insert(InfoNode('car park', 'sign'))
	ActorVale.insert(InfoNode('crosswalk','road mark'))
	ActorVale.insert(InfoNode('children','sign'))
	ActorVale.insert(InfoNode('children','sign'))
	ActorVale.insert(InfoNode('crosswalk','sign'))
	ActorVale.insert(InfoNode('crosswalk','sign'))
	ActorVale.insert(InfoNode('Rua Actor Joaquim de Almeida','right intersection'))
	ActorVale.insert(InfoNode('children','sign'))
	ActorVale.insert(InfoNode('children','sign'))
	ActorVale.insert(InfoNode('crosswalk','sign'))
	ActorVale.insert(InfoNode('crosswalk','sign'))
	ActorVale.insert(InfoNode('crosswalk','road mark'))
	ActorVale.insert(InfoNode('car park', 'sign'))
	ActorVale.insert(InfoNode('no parking', 'sign'))
	ActorVale.insert(InfoNode('end of handicap park', 'sign'))
	ActorVale.insert(InfoNode('handicap park', 'sign'))
	ActorVale.insert(InfoNode('car park', 'sign'))
	ActorVale.insert(InfoNode('car park', 'sign'))
	ActorVale.insert(InfoNode('crosswalk','road mark'))

	n0.set_info(ActorVale)



	#print(graph)
	
	#print(n0.infos1)