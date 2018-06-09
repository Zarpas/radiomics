import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

files = [str(p) for p in Path("LIDC-XML-only/tcia-lidc-xml").glob("**/*.xml")]

def prueba():
	print(files)


def leer(fichero):
	tree = ET.parse(fichero)
	print(fichero)

	#
	# objetivo:
	#    lista con z, lista de x e y, include: true of false
	#

	#nodules = [
	#	{
			#"noduleid": "1",
			#"characteristics": {},
			#"rois": { 
				#1450.5: [
					#{
					#	"coords": [(1,2),(2,3)],
					#	"include": True
					#},
					#{
					#	"coords": [(2,1),(3,4)],
					#	"include": False
					#}
			#	]
			#}
	#	}
	#]

	charac = [ 'subtlety', 'internalStructure', 'calcification', 'sphericity', 'margin', 'lobulation', 'spiculation', 'texture', 'malignancy']
	nodules = []
	for reading in tree.iter('{http://www.nih.gov}readingSession'):
		#print('dentro session')
		for nodule in reading.iter('{http://www.nih.gov}unblindedReadNodule'):
			#print('dentro nodule')
			print('NoduleID', nodule.find('{http://www.nih.gov}noduleID').text)
			n = {}
			n['noduleID'] = nodule.find('{http://www.nih.gov}noduleID').text
			n['characteristics'] = {}
			for carac in nodule.iter('{http://www.nih.gov}characteristics'):
				try:
					#print('malignancy', carac.find('{http://www.nih.gov}malignancy').text)
					for cha in charac:
						n['characteristics'][cha] = carac.find('{http://www.nih.gov}'+cha).text
				except AttributeError:
					print('error')
			n['rois'] = defaultdict(list)
			for roi in nodule.iter('{http://www.nih.gov}roi'):
				#print(roi.find('{http://www.nih.gov}imageZposition').text)
				zCoord = roi.find('{http://www.nih.gov}imageZposition').text
				#n['rois'][zCoord] = {}
				#print(roi.find('{http://www.nih.gov}imageSOP_UID').text)
				UID = roi.find('{http://www.nih.gov}imageSOP_UID').text
				#n['rois'][]
				inclusion = roi.find('{http://www.nih.gov}inclusion').text
				coords = []
				for edgemap in roi.iter('{http://www.nih.gov}edgeMap'):
					#print('x: ', edgemap.find('{http://www.nih.gov}xCoord').text, ', y: ', edgemap.find('{http://www.nih.gov}yCoord').text)
					coords.append((int(edgemap.find('{http://www.nih.gov}xCoord').text), int(edgemap.find('{http://www.nih.gov}yCoord').text)))
				n['rois'][zCoord].append({
					'UID': UID,
					'coords': coords,
					'inclusion': inclusion
					})
			nodules.append(n)
	print(nodules)



if __name__ == '__main__':
	#prueba()
	#for file in files:
	leer('158.xml')