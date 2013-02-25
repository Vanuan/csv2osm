#!/usr/bin/python
import csv, sys

def print_osm_xml(reader, lat, lon, valid_tags):
  print '<osm version="0.6">'
  i = -1
  for row in reader:
    print ('  <node id="%s" lat="%f" lon="%f" visible="true">' %
           (i, float(row[lat].replace(',', '.')), float(row[lon].replace(',', '.'))))
    for k, v in row.iteritems():
      if k != lat and k != lon and v != '' and k in valid_tags:
        print '    <tag k="%s" v="%s" />' % (k,v)
    print '  </node>'
    i = i-1
  print '</osm>'

if __name__ == '__main__':
  if len(sys.argv) != 2:
    print 'usage: ', sys.agv[0], ' table.cvs'
    sys.exit(-1)

  valid_tags = ['name',
                'amenity',
                'description',
                'source',
                'operator']
  with open(sys.argv[1], 'rb') as csv_file:
    reader = csv.DictReader(csv_file, delimiter=',')
    print_osm_xml(reader, 'lat', 'lon', valid_tags)
