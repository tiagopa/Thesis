import json 
import main as m
from shapely.geometry.polygon import Polygon



def create_map():

	graph = m.Graph()

	json_file = open("map.json", "r")
	streets = json.load(json_file)
	json_file.close()

	i=0
	for rows in streets["streets"]: # loop on nodes
		exec("%s = graph.add_node('%s')" % (streets["streets"][i]["street_name"],streets["streets"][i]["street_name"])) # add nodes
		i=i+1

	j=0
	for rows in streets["streets"]: # loop on streets
		for connection in streets["streets"][j]["connections"]: # loop on connections
			exec("%s.ConnectsTo(%s,'%s')" % (streets["streets"][j]["street_name"],connection["street"],connection["orientation"])) # add connections

		exec("%s.add_polygon(Polygon(%s))" % (streets["streets"][j]["street_name"],streets["streets"][j]["polygon_coord"])) # add polygon

		k=0
		for informations in streets["streets"][j]["infos1"]: # loop on street informations 1 
			if k != 0:
				exec("%s.insert(m.InfoNode('%s','%s','%s',%s,%s))" % ((streets["streets"][j]["street_name"]+'_1'),streets["streets"][j]["infos1"][k]["info"],streets["streets"][j]["infos1"][k]["info_type"],streets["streets"][j]["infos1"][k]["orientation"],streets["streets"][j]["infos1"][k]["coordinates"],streets["streets"][j]["infos1"][k]["radius"])) # add elements to the list
			else:
				exec("%s = m.LinkedList(m.InfoNode('%s','%s','%s',%s,%s))" % ((streets["streets"][j]["street_name"]+'_1'),streets["streets"][j]["infos1"][k]["info"],streets["streets"][j]["infos1"][k]["info_type"],streets["streets"][j]["infos1"][k]["orientation"],streets["streets"][j]["infos1"][k]["coordinates"],streets["streets"][j]["infos1"][k]["radius"])) # create linked list
			k=k+1

		flag = False	
		if streets["streets"][j]["infos2"] is not None: # if there is a second list
			flag = True
			k=0
			for informations in streets["streets"][j]["infos2"]: # loop on street informations 2 
				if k != 0:
					exec("%s.insert(m.InfoNode('%s','%s','%s',%s,%s))" % ((streets["streets"][j]["street_name"]+'_2'),streets["streets"][j]["infos2"][k]["info"],streets["streets"][j]["infos2"][k]["info_type"],streets["streets"][j]["infos2"][k]["orientation"],streets["streets"][j]["infos2"][k]["coordinates"],streets["streets"][j]["infos2"][k]["radius"])) # add elements to the list
				else:	
					exec("%s = m.LinkedList(m.InfoNode('%s','%s','%s',%s,%s))" % ((streets["streets"][j]["street_name"]+'_2'),streets["streets"][j]["infos2"][k]["info"],streets["streets"][j]["infos2"][k]["info_type"],streets["streets"][j]["infos2"][k]["orientation"],streets["streets"][j]["infos2"][k]["coordinates"],streets["streets"][j]["infos2"][k]["radius"])) # create linked list
				k=k+1

		if flag == True: # if there are 2 lists
			exec("%s.set_info(%s,%s)" % (streets["streets"][j]["street_name"],(streets["streets"][j]["street_name"]+'_1'),(streets["streets"][j]["street_name"]+'_2')))
		else: # if there's only 1 list
			exec("%s.set_info(%s)" % (streets["streets"][j]["street_name"],(streets["streets"][j]["street_name"]+'_1')))

		j=j+1
	
	return graph