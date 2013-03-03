#!/usr/bin/python
import csv, sys

def print_osm_xml(reader, lat, lon, valid_tags):
  print '<osm version="0.6">'
  i = -1
  for row in reader:
    if 'id' in row:
      osm_id = row['id']
      action = "modify"
    else:
      osm_id = i
      i -= 1
      action = "create"
    version = ''
    if 'version' in row:
      version = 'version="%s"' % row['version']
    print ('  <node id="%s" action="%s" lat="%f" lon="%f" %s visible="true">' %
           (osm_id, action, float(row[lat].replace(',', '.')), float(row[lon].replace(',', '.')), version))
    print_tags(row, lat, lon, valid_tags)
    print '  </node>'
  print '</osm>'


def print_tags(row, lat, lon, valid_tags):
  for k, v in row.iteritems():
    if k != lat and k != lon and v != '' and k in valid_tags:
      print '    <tag k="%s" v="%s" />' % (k,v)


if __name__ == '__main__':
  if len(sys.argv) != 2:
    print 'usage: ', sys.agv[0], ' table.cvs'
    sys.exit(-1)

  valid_tags = ['name',
                'amenity',
                'description',
                'deposit',
                'source',
                'operator',
                'atm']
  with open(sys.argv[1], 'rb') as csv_file:
    reader = csv.DictReader(csv_file, delimiter=',')
    print_osm_xml(reader, 'lat', 'lon', valid_tags)
