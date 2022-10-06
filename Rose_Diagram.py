#@ String (label="Angles", style="text area") angles
#@ String (visibility=MESSAGE, value="<html><br /><br />Rose Diagram Display Options:</html>", required=false) optionsLabel
#@ String (label="Axis Direction", choices={"Counter-Clockwise", "Clockwise"}, style="listBox") axisDirection
#@ String (label="Axis Angle Range", choices={"0 to 360 degrees", "-180 to 180 degrees"}, style="listBox") axisRange
#@ String (label="0 Degrees is due...", choices={"North", "East", "South", "West"}, style="listBox") zeroDirection

import math
from ij import IJ, ImagePlus
from ij.gui import Line, TextRoi, OvalRoi, ShapeRoi
from java.awt import Color, Font, BasicStroke
from java.awt.geom import Arc2D

dashedLine = BasicStroke(1.0, BasicStroke.CAP_BUTT, BasicStroke.JOIN_BEVEL, 10.0, [3.0, 4.0], 0)
legendFont = Font("Arial", Font.PLAIN, 14)
smallFont = Font("Arial", Font.PLAIN, 10)
degreeSign = u"\N{DEGREE SIGN}"
skyblueColor = Color(166, 202, 240)

''' Angle Axis Modes
A: 0 to 360 counter-clockwise, 0 at (0, 1)
B: 0 to 360 counter-clockwise, 0 at (1, 0)
C: 0 to 360 counter-clockwise, 0 at (0, -1)
D: 0 to 360 counter-clockwise, 0 at (-1, 0)
E: 0 to 360 clockwise, 0 at (0, 1)
F: 0 to 360 clockwise, 0 at (1, 0)
G: 0 to 360 clockwise, 0 at (0, -1)
H: 0 to 360 clockwise, 0 at (-1, 0)
I: -180 to 180 counter-clockwise, 0 at (0, 1)
J: -180 to 180 counter-clockwise, 0 at (1, 0)
K: -180 to 180 counter-clockwise, 0 at (0, -1)
L: -180 to 180 counter-clockwise, 0 at (-1, 0)
M: -180 to 180 clockwise, 0 at (0, 1)
N: -180 to 180 clockwise, 0 at (1, 0)
O: -180 to 180 clockwise, 0 at (0, -1)
P: -180 to 180 clockwise, 0 at (-1, 0)
'''

class RoseDiagram:

	@staticmethod
	def generate(angles=[16.0, 31.0, 46.0, 66.0, 66.0], mode="A", barCount=24, scaleMax=-1):	
			
		# Create a new ImageJ image to draw the rose diagram on	
		IJ.newImage("Rose Diagram", "RGB", 600, 600, 1)
		imp = IJ.getImage()
		processor = imp.getProcessor()
	
		# Draw the circles and "crosshairs" of the diagram	
		RoseDiagram.__drawDiagramGrid(processor)
		
		# Draw the directional labels onto the diagram
		RoseDiagram.__drawDirectionalLabels(processor, mode)
		
		# The next thing to draw is the scale labels for the rings on the diagram.
		# We need to do math before we can draw those though.
		
		# For the math, examine the provided angle values and group them based on the number of bars.
		bars = RoseDiagram.__getBarsFromAngles(angles, barCount, mode)
		
		# Also determine the bar with the most members.
		largestBarSize = RoseDiagram.__getLargestBar(bars)
		
		# From this, we can decide what our scale will be, and how to label the grid circles.
		measurementAngles = RoseDiagram.__getCircleLabelValues(largestBarSize, scaleMax)
				
		# We've done enough math to now actually draw the circle labels.
		RoseDiagram.__drawCircleLabels(processor, measurementAngles)		
				
		# Finally we can draw the bars.
		RoseDiagram.__drawBars(processor, mode, bars, largestBarSize)
		
		# Show the average angle as well.
		averageAngle = getCircularMeanOfAngles(angles)
		averageAngle = averageAngle[0]
		RoseDiagram.__drawMeanAngle(processor, averageAngle, mode)
		
		# Refresh and return the ImagePlus.
		imp.updateAndRepaintWindow()
		return imp
		
	@staticmethod
	def __drawDiagramGrid(processor):
		circle = OvalRoi(250, 250, 100, 100)
		circle.setFillColor(None)
		circle.setStrokeColor(Color.BLACK)
		circle.setStroke(dashedLine)
		processor.drawRoi(circle)
		
		circle2 = OvalRoi(200, 200, 200, 200)
		circle2.setFillColor(None)
		circle2.setStrokeColor(Color.BLACK)
		circle2.setStroke(dashedLine)
		processor.drawRoi(circle2)
		
		circle3 = OvalRoi(150, 150, 300, 300)
		circle3.setFillColor(None)
		circle3.setStrokeColor(Color.BLACK)
		circle3.setStroke(dashedLine)
		processor.drawRoi(circle3)
		
		circle4 = OvalRoi(100, 100, 400, 400)
		circle4.setFillColor(None)
		circle4.setStrokeColor(Color.BLACK)
		circle4.setStroke(dashedLine)
		processor.drawRoi(circle4)
		
		circle5 = OvalRoi(50, 50, 500, 500)
		circle5.setFillColor(None)
		circle5.setStrokeColor(Color.BLACK)
		processor.drawRoi(circle5)
		
		vline = Line(300, 40, 300, 560)
		vline.setFillColor(None)
		vline.setStrokeColor(Color.BLACK)
		processor.drawRoi(vline)
		
		hline = Line(40, 300, 560, 300)
		hline.setFillColor(None)
		hline.setStrokeColor(Color.BLACK)
		processor.drawRoi(hline)
	
	@staticmethod
	def __drawDirectionalLabels(processor, mode):
	
		# Directional labels clockwise, starting north
		directionalLabels = ["", "", "", ""]
		
		if mode == "A":
			directionalLabels = ["0", "270", "180", "90"]
		elif mode == "B":
			directionalLabels = ["90", "0", "270", "180"]
		elif mode == "C":
			directionalLabels = ["180", "90", "0", "270"]
		elif mode == "D":
			directionalLabels = ["270", "180", "90", "0"]
		elif mode == "E":
			directionalLabels = ["0", "90", "180", "270"]
		elif mode == "F":
			directionalLabels = ["270", "0", "90", "180"]
		elif mode == "G":
			directionalLabels = ["180", "270", "0", "90"]
		elif mode == "H":
			directionalLabels = ["90", "180", "270", "0"]
			
		elif mode == "I":
			directionalLabels = ["0", "-90", "180", "90"]
		elif mode == "J":
			directionalLabels = ["90", "0", "-90", "180"]
		elif mode == "K":
			directionalLabels = ["180", "90", "0", "-90"]
		elif mode == "L":
			directionalLabels = ["-90", "180", "90", "0"]
		elif mode == "M":
			directionalLabels = ["0", "90", "180", "-90"]
		elif mode == "N":
			directionalLabels = ["-90", "0", "90", "180"]
		elif mode == "O":
			directionalLabels = ["180", "-90", "0", "90"]
		elif mode == "P":
			directionalLabels = ["90", "180", "-90", "0"]
			
		nRoi = TextRoi(300, 15, directionalLabels[0] + degreeSign)
		nRoi.setColor(Color.BLACK)
		nRoi.setFillColor(Color.WHITE)
		nRoi.setFont(legendFont)
		nRoi.setJustification(1)
		processor.drawRoi(nRoi)
		
		eRoi = TextRoi(575, 290, directionalLabels[1] + degreeSign)
		eRoi.setColor(Color.BLACK)
		eRoi.setFillColor(Color.WHITE)
		eRoi.setFont(legendFont)
		eRoi.setJustification(1)
		processor.drawRoi(eRoi)
		
		sRoi = TextRoi(300, 570, directionalLabels[2] + degreeSign)
		sRoi.setColor(Color.BLACK)
		sRoi.setFillColor(Color.WHITE)
		sRoi.setFont(legendFont)
		sRoi.setJustification(1)
		processor.drawRoi(sRoi)
		
		wRoi = TextRoi(20, 290, directionalLabels[3] + degreeSign)
		wRoi.setColor(Color.BLACK)
		wRoi.setFillColor(Color.WHITE)
		wRoi.setFont(legendFont)
		wRoi.setJustification(1)
		processor.drawRoi(wRoi)
		
	@staticmethod
	def __getBarsFromAngles(angles, barCount, mode):
		barAngleSize = 360.0 / float(barCount)
		bars = [0] * barCount
		
		for i in range(barCount):
			startAngle = -180.0 + (barAngleSize * float(i))
			if mode in ["A", "B", "C", "D", "E", "F", "G", "H"]:
				startAngle = 0.0 + (barAngleSize * float(i))
			endAngle = startAngle + barAngleSize
			
			for a in angles:
				af = float(a)
				if mode in ["A", "B", "C", "D", "E", "F", "G", "H"]:
					if af >= startAngle and af < endAngle:
						bars[i] = bars[i] + 1
				else:
					if af > startAngle and af <= endAngle:
						bars[i] = bars[i] + 1
					
		return bars
		
	@staticmethod
	def __getLargestBar(bars):
		largestBarSize = 0
		for b in bars:
			if b > largestBarSize:
				largestBarSize = b
		return largestBarSize
		
	@staticmethod
	def __getCircleLabelValues(largestBarSize, scaleMax):
	
		outerCircleSize = float(scaleMax)
		
		if outerCircleSize < 0.0:
			if largestBarSize < 25:
				outerCircleSize = float(largestBarSize)
			else:
				outerCircleSize = largestBarSize
				while outerCircleSize % 5 <> 0:
					outerCircleSize = outerCircleSize + 1
				outerCircleSize = float(outerCircleSize)
			
		innermostCircleSize = outerCircleSize / 5.0
		
		# We'll store the labels for each circle here:
		measurementAngles = []
		
		for i in range(5):
			value = round(innermostCircleSize * float(i + 1), 2)
			if largestBarSize >= 25 or str(innermostCircleSize).endswith(".0"):
				value = int(value)
			measurementAngles.append(value)
			
		return measurementAngles
		
	@staticmethod
	def __drawCircleLabels(processor, labels):
	
		# This array is a matrix of label positions.
		mPos = [[[300, 243],[350, 293],[300, 343],[250, 293]], [[300, 193],[400, 293],[300, 393],[200, 293]], [[300, 143],[450, 293],[300, 443],[150, 293]], [[300, 93],[500, 293],[300, 493],[100, 293]], [[300, 51],[550, 293],[300, 535],[59, 293]]]
		
		for i in range(5):
	
			for m in range(4):
				x = mPos[i][m][0]
				y = mPos[i][m][1]
				# One specific label needs manually placed...
				if i == 4 and m == 1:
					tRoi = TextRoi(x, y, str(labels[i]))
					r = tRoi.getBoundingRect()
					x = x - (r.width / 2)
				mRoi = TextRoi(x, y, str(labels[i]))
				mRoi.setColor(Color.BLACK)
				mRoi.setFillColor(Color.WHITE)
				mRoi.setFont(smallFont)
				mRoi.setJustification(1)
				processor.drawRoi(mRoi)
				
	@staticmethod
	def __drawBars(processor, mode, bars, largestBarSize):
	
		# Depending on the mode, where each bar goes around the circle will change wildly.
		# Bars are sorted from smallest angle to largest, so they're drawn from 0 or ~-180, depending on mode.
		# When supplying angles to get the arc shape, those measurements always use true polar coordinates on a 0-360 scale.
		
		# Split the mode into its distinct attributes
		
		# Does this mode measure 0 to 360, or -180 to 180?
		zeroTo360 = True
		if mode in ["I", "J", "K", "L", "M", "N", "O", "P"]:
			zeroTo360 = False
			
		# Does this mode increment clockwise or counter-clockwise?
		clockwise = False
		if mode in ["E", "F", "G", "H", "M", "N", "O", "P"]:
			clockwise = True
			
		# For this mode's axis, does 0 degrees point north, south, east, or west?
		zeroDirection = "N"
		if mode in ["B", "F", "J", "N"]:
			zeroDirection = "E"
		elif mode in ["C", "G", "K", "O"]:
			zeroDirection = "S"
		elif mode in ["D", "H", "L", "P"]:
			zeroDirection = "W"
			
		# How wide should the bars be (in angles)? What direction are bars drawn?
		barWidth = 360.0 / float(len(bars))
		if clockwise == True:
			barWidth = barWidth * -1.0
			
		# How does the mode's orientation determine where we start drawing bars?
		startAngle = 0.0 # This is true if zeroDirection is E
		if zeroDirection == "N":
			startAngle = 90.0
		elif zeroDirection == "W":
			startAngle = 180.0
		elif zeroDirection == "S":
			startAngle = 270.0
			
		# The starting location changes if we use the -180 to 180 axis
		if zeroTo360 == False:
			startAngle = startAngle + 180.0
		
		# We should have enough information to draw the bars at this point.
		for i in range(len(bars)):
			
			barValue = bars[i]			
			if barValue > 0 and largestBarSize > 0:
				if float(barValue) <= float(largestBarSize):
					boundingSquareSize = 500.0 * (float(barValue) / float(largestBarSize))
					boundingSquareSize = int(boundingSquareSize)
					if boundingSquareSize > 500:
						boundingSquareSize = 500
					boundingSquareLocation = 50 + int(float((500 - boundingSquareSize) / 2))
					RoseDiagram.__drawBar(processor, boundingSquareLocation, boundingSquareLocation, boundingSquareSize, boundingSquareSize, startAngle, barWidth)
			startAngle = startAngle + (barWidth)		
		
	@staticmethod
	def __drawBar(processor, brectX, brectY, brectWidth, brectHeight, arcStartingAngle, arcAngleWidth):
	
		bar = Arc2D.Float(brectX, brectY, brectWidth, brectHeight, arcStartingAngle, arcAngleWidth, Arc2D.PIE)
		
		bRoi = ShapeRoi(bar)
		bRoi.setStrokeColor(Color.BLACK)
		bRoi.setFillColor(skyblueColor)
		processor.drawRoi(bRoi)
		
		boRoi = ShapeRoi(bar)
		boRoi.setStrokeColor(Color.BLACK)
		processor.drawRoi(boRoi)
		
	@staticmethod
	def __drawMeanAngle(processor, meanAngle, mode):
	
		# First transform the true angle to canvas angle based on mode components
	
		zeroOffset = 0.0
			
		zeroDirection = "N"
		if mode in ["A", "E", "I", "M"]:
			zeroOffset = 90.0
		elif mode in ["C", "G", "K", "O"]:
			zeroOffset = 270.0
		elif mode in ["D", "H", "L", "P"]:
			zeroOffset = 180.0
			
		if mode in ["E", "F", "G", "H", "M", "N", "O", "P"]:
			# Clockwise
			if zeroOffset > 0.0:
				zeroOffset = zeroOffset * -1.0
			meanAngle = 360.0 - (meanAngle + zeroOffset)
		else:
			# Counter-clockwise
			meanAngle = meanAngle + zeroOffset
			
		
		print zeroOffset
		print meanAngle
		
		meanBar = Arc2D.Float(40, 40, 520, 520, meanAngle - 7.5, 15.0, Arc2D.OPEN)
		
		meanBarStartPoint = meanBar.getStartPoint()
		meanBarEndPoint = meanBar.getEndPoint()
		meanBarCX = int((meanBarStartPoint.getX() + meanBarEndPoint.getX()) / 2.0)
		meanBarCY = int((meanBarStartPoint.getY() + meanBarEndPoint.getY()) / 2.0)
		
		mbRoi = ShapeRoi(meanBar)
		mbRoi.setStrokeColor(Color.BLACK)
		mbRoi.setStrokeWidth(3)
		processor.drawRoi(mbRoi)
		
		
		mlRoi = Line(300, 300, meanBarCX, meanBarCY)
		mlRoi.setStrokeColor(Color.BLACK)
		mlRoi.setStrokeWidth(3)
		processor.drawRoi(mlRoi)
		
		sBar1 = Arc2D.Float(35, 35, 530, 530, meanAngle - 7.5, 15.0, Arc2D.OPEN)
		sBar1StartPoint = sBar1.getStartPoint()
		sBar1EndPoint = sBar1.getEndPoint()
		
		sBar2 = Arc2D.Float(45, 45, 510, 510, meanAngle - 7.5, 15.0, Arc2D.OPEN)
		
		sBar2StartPoint = sBar2.getStartPoint()
		sBar2EndPoint = sBar2.getEndPoint()
		
		s1Roi = Line(int(sBar1StartPoint.getX()), int(sBar1StartPoint.getY()), int(sBar2StartPoint.getX()), int(sBar2StartPoint.getY()))
		s1Roi.setStrokeColor(Color.BLACK)
		s1Roi.setStrokeWidth(3)
		processor.drawRoi(s1Roi)
		
		s2Roi = Line(int(sBar1EndPoint.getX()), int(sBar1EndPoint.getY()), int(sBar2EndPoint.getX()), int(sBar2EndPoint.getY()))
		s2Roi.setStrokeColor(Color.BLACK)
		s2Roi.setStrokeWidth(3)
		processor.drawRoi(s2Roi)
		
# Takes a multiline string and returns an array of numbers
def stringToAngles(angleString):
	angleStrs = angleString.split()
	angles = []	
	for angleStr in angleStrs:
		try:
			angles.append(float(angleStr))
		except:
			print 'Skipping invalid angle "' + angleStr + '"'
	return angles

# A function to get the circular mean and angular dispersion of the angles in an array.
# Angles should be in degrees, and be 0 to (not including) 360.
def getCircularMeanOfAngles(angles):
	
	n = float(len(angles))
	s = 0.0
	c = 0.0
	for angle in angles:
		s = s + math.sin(math.radians(angle))
		c = c + math.cos(math.radians(angle))
		
	s = s / n
	c = c / n
	
	r = math.sqrt(pow(s, 2) + pow(c, 2))
	v = 1 - r
	
	sdv = math.sqrt(math.log(1 / pow(r, 2)))
	
	sina = s / r
	cosa = c / r
	
	avg = -1.0
	#m = -1.0
	
	if s > 0.0 and c > 0.0:
		avg = math.degrees(math.atan(s / c))
		#m = math.degrees(math.atan( sina / cosa ))
	elif s < 0.0 and c > 0.0:
		avg = math.degrees(math.atan(s / c)) + 360.0
		#m = math.degrees(math.atan( sina / cosa )) + 360.0
	else:
		avg = math.degrees(math.atan(s / c)) + 180.0
		#m = math.degrees(math.atan( sina / cosa )) + 180.0
		
	#return [avg, r, m]
	return [avg, r, v, sdv]

if __name__ == "__main__" or __name__ == "__builtin__":

	angleNums = stringToAngles(angles)
	
	#axisDirection axisRange zeroDirection
	mode = "A"
	
	if axisDirection == "Counter-Clockwise":	
		if axisRange == "0 to 360 degrees":
			if zeroDirection == "North":
				mode = "A"
			elif zeroDirection == "East":
				mode = "B"
			elif zeroDirection == "South":
				mode = "C"
			elif zeroDirection == "West":
				mode = "D"
		else:
			if zeroDirection == "North":
				mode = "I"
			elif zeroDirection == "East":
				mode = "J"
			elif zeroDirection == "South":
				mode = "K"
			elif zeroDirection == "West":
				mode = "L"
	else:
		if axisRange == "0 to 360 degrees":
			if zeroDirection == "North":
				mode = "E"
			elif zeroDirection == "East":
				mode = "F"
			elif zeroDirection == "South":
				mode = "G"
			elif zeroDirection == "West":
				mode = "H"
		else:
			if zeroDirection == "North":
				mode = "M"
			elif zeroDirection == "East":
				mode = "N"
			elif zeroDirection == "South":
				mode = "O"
			elif zeroDirection == "West":
				mode = "P"
				
	RoseDiagram.generate(angleNums, mode)