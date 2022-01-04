
from lxml import etree
import codecs
import simplejson as json
import pyproj

from utils import findPosition, findAlternativeNames, convertImportance
from api import getToken, uploadData



f = codecs.open("posisjoner.json", "w", encoding='utf8')
location_type_object = json.load(open('posisjoner_type.json'))
print("Starting parse of GML file")
tree = etree.parse('stedsnavn.gml')
print("Finished parsing, getting root")
root = tree.getroot()
print("Got root")
locations = []
name = ""
app = "{http://skjema.geonorge.no/SOSI/produktspesifikasjon/StedsnavnForVanligBruk/20181115}"
gml = "{http://www.opengis.net/gml/3.2}"

print("Started iterating GML tree")
for featureMember in tree.findall('{http://www.opengis.net/gml/3.2}featureMember'):
    locationType = featureMember.find('.//' + app + 'navneobjekttype')
    locationType = locationType.text if locationType is not None else 'Ukjent'
    if(location_type_object[locationType] is True):
      # Find position, need to account for "multipoint" and poslist
      coordinates = findPosition(featureMember, gml, app)

      # finds name, need to account for multiple names
      # name = featureMember.find('.//' + app + 'komplettskrivemåte')
      # name = name.text if name is not None else 'No name record'
      
      språkprioriteringNode = featureMember.find('.//' + app + 'språkprioritering')
      if språkprioriteringNode is not None:
        for stedsnavn in featureMember.findall('.//' + app + 'Stedsnavn'):
          node = stedsnavn.find(app + 'språk')
          if node.text == språkprioriteringNode.text.split("-")[0]:
            name = stedsnavn.find('.//' + app + 'komplettskrivemåte').text
            
      alternative_names = findAlternativeNames(featureMember, name, gml, app)
      
      
      importance = featureMember.find('.//' + app + 'sortering')
      importance = convertImportance(importance.text) if importance is not None else -1
      
      municipality = featureMember.find('.//' + app + 'kommunenavn')
      municipality = municipality.text if municipality is not None else "Ukjent"
      # Says something about what kind of location it is

      county = featureMember.find('.//' + app + 'fylkesnavn')
      county = county.text.split(" - ")[0] if county is not None else "Ukjent"
      
      locations.append({
        "name": name, 
        "alternative_names": alternative_names, 
        "coordinates": coordinates, 
        "importance": importance if locationType != "by" else 11, 
        "location_type": locationType,
        "municipality": municipality,
        "county": county
      })
  # print("name=" + name + ", pos=" + pos + ", priority=" + priority)

print("Finished iterating, dumping to file")
token = getToken()
uploadData(token, json.dumps({"locations": locations}, ensure_ascii=False))
f.write(json.dumps({"locations": locations}, ensure_ascii=False))
f.close()
print("Done")
  #Need to append to array, make a json object and write to file
  #coordinates["latitude"], "longitude": coordinates["longitude"]