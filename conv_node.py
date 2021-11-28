from lxml import etree
import codecs
import simplejson as json
import pyproj

from utils import findPosition, findAlternativeNames



f = codecs.open("posisjoner_enkel.json", "w", encoding='utf8')
print("Starting parse of GML file")
tree = etree.parse('stedsnavn_enkel.gml')
print("Finished parsing, getting root")
root = tree.getroot()
print("Got root")
locations = []

app = "{http://skjema.geonorge.no/SOSI/produktspesifikasjon/StedsnavnForVanligBruk/20181115}"
gml = "{http://www.opengis.net/gml/3.2}"

print("Started iterating GML tree")
for featureMember in tree.findall('{http://www.opengis.net/gml/3.2}featureMember'):
  # Find position, need to account for "multipoint" and poslist
  coordinates = findPosition(featureMember, gml, app)

  # finds name, need to account for multiple names
  name = featureMember.find('.//' + app + 'komplettskrivemåte')
  name = name.text if name is not None else 'No name record'
  
  alternative_names = findAlternativeNames(featureMember, name, gml, app)
  
  
  priority = featureMember.find('.//' + app + 'sortering')
  priority = priority.text if priority is not None else 'No priority record'
  
  # Says something about what kind of location it is
  locationType = featureMember.find('.//' + app + 'navneobjekttype')
  locationType = locationType.text if locationType is not None else 'No locationType record'
  
  locations.append({"name": name, "alternative_names": alternative_names, "coordinates": coordinates, "priority": priority, "location_type": locationType})
  # print("name=" + name + ", pos=" + pos + ", priority=" + priority)

print("Finished iterating, dumping to file")
f.write(json.dumps(locations, ensure_ascii=False))
f.close()
print("Done")
  #Need to append to array, make a json object and write to file
  #coordinates["latitude"], "longitude": coordinates["longitude"]