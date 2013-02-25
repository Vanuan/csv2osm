# coding=utf-8
import sys
from xml.sax.handler import ContentHandler
from xml.sax import parse
import csv

def pnpoly(verts, test):
  '''
  returns True if point is inside a poly
  verts - array of x, y pairs, test - pair of x, y
  '''
  c = False
  for v0, v1 in zip(verts, [verts[-1]] + verts[:-1]):
    if ((v0[1] > test[1]) != (v1[1] > test[1])):
      if (test[0]) <= ((v1[0] - v0[0]) * (test[1] - v0[1]) / (v1[1] - v0[1]) + v0[0]):
        c = not c
  return c


class Filter(object):
  def should_keep(self, node):
    keep = False
    keep_conditions = [{'amenity': 'atm', 'operator': u'Укрсиббанк'},
                       {'amenity': 'bank', 'name': u'Укрсиббанк'}]
    for keep_condition in keep_conditions:
      temp_keep = True
      for key, value in keep_condition.iteritems():
        # all fields should be present
        if key not in node or node[key] != value:
          temp_keep = False
      if temp_keep == True:  # we have a match
        keep = True
        break
    return keep


class TagNames(object):
  HOUSENUMBER = 'addr:housenumber'
  STREET = 'addr:street'


class OsmHandler(ContentHandler):
  def __init__(self, node_filter):
    self.__cur_node = None
    self.__cur_way = None
    self.__cur_relation = None
    self.__relations = []
    self.__nodes = {}
    self.__selected_nodes = []
    self.__buildings = {}
    self.__attr_names = ['id', 'lat', 'lon', TagNames.HOUSENUMBER, TagNames.STREET]
    self.__node_filter = node_filter

  def get_nodes(self):
    return self.__selected_nodes

  def get_buildings(self):
    return self.__buildings

  def get_relations(self):
    return self.__relations

  def get_attr_names(self):
    return self.__attr_names

  def startElement(self, name, attrs):
    if name == 'node':
      self.__cur_node = {}
      attr_names = attrs.getNames()
      if 'lat' not in attr_names or 'lon' not in attr_names:
        print 'not lat or lon found in node'
        sys.exit(-1)
      self.__cur_node['id'] = attrs.getValue('id')
      self.__cur_node['lat'] = attrs.getValue('lat')
      self.__cur_node['lon'] = attrs.getValue('lon')
    if name == 'tag':
      tag_name = attrs['k']
      if self.__cur_way:
        self.__cur_way[tag_name] = attrs['v']
      if self.__cur_node:
        self.__cur_node[tag_name] = attrs['v']
      if self.__cur_relation:
        self.__cur_relation[tag_name] = attrs['v']
    if name == 'way':
      self.__cur_way = {'nodes':[]}
      self.__cur_way['id'] = attrs.getValue('id')
    if name == 'nd':
      self.__cur_way['nodes'] += [self.__nodes[attrs.getValue('ref')]]
    if name == 'relation':
      self.__cur_relation = {'ways':[]}
    if name == 'member':
      ref = attrs.getValue('ref')
      if ref in self.__buildings:
        self.__cur_relation['ways'] += [self.__buildings[ref]]

  def endElement(self, name):
    if name == 'node' and self.__cur_node:
      self.__nodes[self.__cur_node['id']] = self.__cur_node
      if (len(self.__cur_node) > 3 and
          self.__node_filter.should_keep(self.__cur_node)):
        self.__selected_nodes.append(self.__cur_node)
        for tag_name in self.__cur_node.keys():
          if tag_name not in self.__attr_names:
            self.__attr_names.append(tag_name)
      self.__cur_node = None
    if name == 'way' and self.__cur_way:
      if 'building' in self.__cur_way:
        self.__buildings[self.__cur_way['id']] = self.__cur_way
      self.__cur_way = None
    if name == 'relation':
      self.__relations.append(self.__cur_relation)
      self.__cur_relation = None


class BuildingHandler(ContentHandler):
  def __init__(self):
    pass

if __name__ == '__main__':
  if len(sys.argv) != 2:
    print 'usage: ', sys.argv[0], ' filename.osm'
    sys.exit(-1)
  print 'parsing xml file...'
  node_handler = OsmHandler(Filter())
  parse(sys.argv[1], node_handler)
  nodes = node_handler.get_nodes()
  attr_names = node_handler.get_attr_names()
  print 'The map has', len(nodes), 'points.'
  buildings = node_handler.get_buildings()
  print 'The map has', len(buildings), 'buildings.'

  for node in nodes:
    point = [float(node['lon']),
             float(node['lat'])]
    for building in buildings.itervalues():
      points = []
      for building_node in building['nodes']:
        points.append([float(building_node['lon']), float(building_node['lat'])])
      if pnpoly(points, point):
        if TagNames.HOUSENUMBER in building:
          node[TagNames.HOUSENUMBER] = building[TagNames.HOUSENUMBER]
        if TagNames.STREET in building:
          node[TagNames.STREET] = building[TagNames.STREET]
        # search building in relations
        for relation in node_handler.get_relations():
          if relation['type'] == 'associatedStreet':
            for relation_way in relation['ways']:
              if building['id'] == relation_way['id']:
                node[TagNames.STREET] = relation['name']
        break

  #building_handler = BuildingHandler()
  #parse(sys.argv[1], building_handler)

  print 'writing csv file...'
  csv_name = sys.argv[1] + '.csv'
  with open(csv_name, 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(attr_names)
    for node in nodes:
      row = []
      for attr_name in attr_names:
        if attr_name in node:
          row += [node[attr_name]]
        else:
          row += ['']
      writer.writerow([s.encode("utf-8") for s in row])
  print 'written to ', csv_name

