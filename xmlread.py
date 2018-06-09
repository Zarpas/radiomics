import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

files = [str(p) for p in Path("data/lidc-xml").glob("**/*.xml")]

def prueba():
	print(files)


def leer(fichero):
	tree = ET.parse(fichero)
	print(fichero)

	zetas = []

	charac = [ 'subtlety', 'internalStructure', 'calcification', 'sphericity', 'margin', 'lobulation', 'spiculation', 'texture', 'malignancy']
	nodules = []
	response = tree.find('{http://www.nih.gov}ResponseHeader')
	UID = response.find('{http://www.nih.gov}SeriesInstanceUid').text
	for reading in tree.iter('{http://www.nih.gov}readingSession'):
		for nodule in reading.iter('{http://www.nih.gov}unblindedReadNodule'):
			n = {}
			n['noduleID'] = nodule.find('{http://www.nih.gov}noduleID').text
			n['characteristics'] = {}
			n['UID'] = UID
			for carac in nodule.iter('{http://www.nih.gov}characteristics'):
				try:
					for cha in charac:
						n['characteristics'][cha] = carac.find('{http://www.nih.gov}'+cha).text
				except AttributeError:
					print('error')
			n['rois'] = defaultdict(list)
			for roi in nodule.iter('{http://www.nih.gov}roi'):
				zCoord = roi.find('{http://www.nih.gov}imageZposition').text
				inclusion = roi.find('{http://www.nih.gov}inclusion').text
				coords = []
				for edgemap in roi.iter('{http://www.nih.gov}edgeMap'):
					coords.append((int(edgemap.find('{http://www.nih.gov}xCoord').text), int(edgemap.find('{http://www.nih.gov}yCoord').text)))
				n['rois'][zCoord].append({
					'coords': coords,
					'inclusion': inclusion
					})
			nodules.append(n)
	return nodules



if __name__ == '__main__':
	leer('158.xml')