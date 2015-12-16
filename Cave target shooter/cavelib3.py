"""FontysVR WorldViz Vizard Cave library version 3.0 alpha"""

import viz
import vizmat
import vizcave
import viztracker
import vizshape


class CaveLib(viz.EventClass):
	"""CaveLib class
	
	You need to specify the mode at constrcution.
	True is desktop mode (do NOT use CAVE)
	False is cave mode (Do use CAVE).
	
	To start a simulation use the go() function of this classs instead of viz.go.	
	"""
	
	TRACKER_LEFT_EYE = 1
	TRACKER_RIGHT_EYE = 2
	TRACKER_HEAD = 3
	TRACKER_WAND = 4
	TRACKER_THING = 5
	TRACKER_CAVE_ORIGIN = 6
	
	DESKTOP_MODE_VIEWPOINT_OVERVIEW = 1
	DESKTOP_MODE_VIEWPOINT_USER = 2	
	
	BALANCE_BOARD_BOTTOM_LEFT = 1
	BALANCE_BOARD_BOTTOM_RIGHT = 2
	BALANCE_BOARD_TOP_LEFT = 3
	BALANCE_BOARD_TOP_RIGHT = 4
	BALANCE_BOARD_TOTAL = 5
	
	def __init__(self,desktop_mode=True):
		"""Initialize Cavelib v 3.0"""	
		
		viz.EventClass.__init__(self)
		
		viz.mouse.setVisible(viz.OFF)
		
		self.__daemon = viz.add("daemon3.dle") #Load the daemon extension
				
		# Declare constants defining the CAVE dimensions
		W = 3.12 
		H = 2.50 
		D = 3.12		

		self.__FLOCK_OFFSET = [0,H / 2.0,0] # Distance the Flock of Birds transmitter is from the floor and center of cave
		self.__EYE_RADIUS = 0.0125 #used for drawing only
		
		# Center the CAVE about the origin
		Wm = +W/2.0
		Wo = -W/2.0
		Hm = H
		Ho = 0
		Dm = +D/2.0
		Do = -D/2.0
		
		

		# Now calculate the wall vertices
		C0 = Wo,Hm,Do     # Front  Wall: C1,C2,C5,C6
		C1 = Wo,Hm,Dm     # Left   Wall: C0,C1,C4,C5
		C2 = Wm,Hm,Dm     # Right  Wall: C2,C3,C6,C7
		C3 = Wm,Hm,Do     # Bottom Wall: C5,C6,C4,C7
		C4 = Wo,Ho,Do
		C5 = Wo,Ho,Dm
		C6 = Wm,Ho,Dm
		C7 = Wm,Ho,Do

		C8 = Wo,Ho,(Hm/2+0.31)
		C9 = Wm,Ho,(Hm/2+0.31)
		C10 = Wo,Ho,(-Hm/2+0.31)
		C11 = Wm,Ho,(-Hm/2+0.31)

		#Create front wall
		self.__front_wall = vizcave.Wall(   upperLeft = C1,
									upperRight = C2,
									lowerLeft = C5,
									lowerRight = C6,
									name = 'Front Wall' )
									
		#Create left wall
		self.__left_wall  = vizcave.Wall(   upperLeft = C0,
									upperRight = C1,
									lowerLeft = C4,
									lowerRight = C5,
									name = 'Left Wall' )

		#Create right wall
		self.__right_wall = vizcave.Wall(   upperLeft = C2,
									upperRight = C3,
									lowerLeft = C6,
									lowerRight = C7,
									name = 'Right Wall' )
									
		#Create bottom wall C7,C4,C6,C5
		self.__bottom_wall = vizcave.Wall(  upperLeft = C11,
									upperRight = C10, 
									lowerLeft = C9, 
									lowerRight = C8,
									name = 'Bottom Wall' )
		
		#The trackers are input proxies
		#The input has to be bound to the trackers
									
		self.__head_tracker = viz.addGroup()
		self.__wand_tracker = viz.addGroup()
		self.__thing_tracker = viz.addGroup()
		self.__left_eye_tracker = viz.addGroup()
		self.__right_eye_tracker = viz.addGroup()		
		self.__cave_origin_tracker = viz.addGroup()
		
		#set the position of the _viewtracker to be one meter off the ground
		self.__head_tracker.setPosition(0,1,0)			
		
		#set the wandtracker to some place away from the viewtracker
		self.__wand_tracker.setPosition(1,1,1)
		
		#set the thingtracker to some place away the other trackers
		self.__thing_tracker.setPosition(-1,1,0)	
		
		
		##mouse sensor
		self.__keyboard_mouse_sensor = viztracker.KeyboardMouse6DOF() 
									
		#head sensor			
		self.__head_sensor_raw = self.__daemon.addHeadSensor()
		self.__head_sensor = self.__correctSensor(self.__head_sensor_raw)
			
			
		#wand sensor		
		self.__wand_sensor_raw = self.__daemon.addWandSensor()
		self.__wand_sensor = self.__correctSensor(self.__wand_sensor_raw)
			
		#thing sensor		
		self.__thing_sensor_raw = self.__daemon.addThingSensor();
		self.__thing_sensor = self.__correctSensor(self.__thing_sensor_raw)
		
		#left eye sensor
		self.__left_eye_sensor_raw = self.__daemon.addLeftEyeSensor()
		self.__left_eye_sensor = self.__correctSensor(self.__left_eye_sensor_raw)
		
		self.__right_eye_auto_update = True
		self.__left_eye_auto_update = True
		self.__head_auto_update = True
		self.__wand_auto_update = True
		self.__thing_auto_update = True
		self.__cave_origin_auto_update = False
				
		#right eye sensor
		self.__right_eye_sensor_raw = self.__daemon.addRightEyeSensor()
		self.__right_eye_sensor = self.__correctSensor(self.__right_eye_sensor_raw)
		
		self.__walls = None
		self.__left_eye = None
		self.__right_eye = None
		self.__cave = vizcave.Cave()
		
		if desktop_mode:
			self.__setDesktopMode()
		else:
			self.__setCaveMode()
			
		self.setNearPlane(1.0 / 256.0)
		self.setFarPlane(65536.0)
		
		self.setDestkopModeViewpoint(self.DESKTOP_MODE_VIEWPOINT_OVERVIEW)

	def __correctSensor(self,sensor):
		"""When given a raw sensor, return a corrected sensor."""
		result = viz.addGroup()
		link = viz.link(sensor, result)
		link.postTrans(self.__FLOCK_OFFSET)
		return result
		
	def __assertBoolean(self,value):
		if value.__class__.__name__ != "bool":
			raise Exception("Cavelib3Exception", "You must specifiy a boolean.")
			
	def __assertInteger(self,value):
		if value.__class__.__name__ != "int":
			raise Exception("Cavelib3Exception", "You must specifiy an integer.")
			
	def __assertMatrix(self,value):
		if (value.__class__.__name__ != "Transform") and (value.__class__.__name__ != "list"):
			raise Exception("Cavelib3Exception", "You must specify a transform or a list.")		
			
	def __assertVector(self,value):
		if (value.__class__.__name__ != "Vector") and (value.__class__.__name__ != "list"):
			raise Exception("Cavelib3Exception", "You must specify a vector or a list.")
			
			
	def setDestkopModeViewpoint(self,desktop_mode_viewpoint):
		"""Set the viewpoint for desktop-mode."""
		if desktop_mode_viewpoint == self.DESKTOP_MODE_VIEWPOINT_OVERVIEW or desktop_mode_viewpoint == self.DESKTOP_MODE_VIEWPOINT_USER:
			self.__desktop_mode_viewpoint = desktop_mode_viewpoint
			
	def setAutoUpdate(self,tracker,boolean):
		"""Set auto update of certain tracker.
		
		Use TRACKER_LEFT_EYE, TRACKER_RIGHT_EYE, TRACKER_HEAD, TRACKER_THING, or TRACKER_CAVE_ORIGIN.
		Use True or False as the second parameter.
		"""
		self.__assertInteger(tracker)
		self.__assertBoolean(boolean)
		
		if (tracker < 1) or (tracker > 6):
			raise Exception("Cavelib3Exception","Tracker has invalid index.")
			
		if tracker == self.TRACKER_LEFT_EYE:
			self.__left_eye_auto_update = boolean			
		elif tracker == self.TRACKER_RIGHT_EYE:
			self.__right_eye_auto_update = boolean
		elif tracker == self.TRACKER_HEAD:
			self.__head_auto_update = boolean
		elif tracker == self.TRACKER_WAND:
			self.__wand_auto_update = boolean
		elif tracker == self.TRACKER_THING:
			self.__thing_auto_update = boolean
		elif tracker == self.TRACKER_CAVE_ORIGIN:
			self.__cave_origin_auto_update = boolean
		
	def localMatrixToWorld(self,local_matrix):	
		"""Convert a local matrix to world matrix.
		
		This function uses the cave origin tracker.
		"""
		self.__assertMatrix(local_matrix)
		result = viz.vizmat.Transform(local_matrix)
		result.postMult(self.getOriginMatrix())
		return result
		
	def localPositionToWorld(self,local_position):
		"""Convert a local position to world position.
		
		This function uses the cave origin tracker.
		"""		
		self.__assertVector(local_position)
		return self.getOriginMatrix().preMultVec(local_position)
		
	def worldMatrixToLocal(self,world_matrix):
		"""Convert a world matrix to local matrix.
		
		This function uses the cave origin tracker (inverse).
		"""
		self.__assertMatrix(local_matrix)
		result = viz.vizmat.Transform(world_matrix)		
		origin_inverse = self.getOriginMatrix().inverse()		
		result.postMult(origin_inverse)
		return result
		
	def worldPositionToLocal(self,world_position):
		"""Convert a world position to local position.
		
		This function uses the cave origin tracker (inverse).
		"""	
		self.__assertVector(world_position)
		origin_inverse = self.getOriginMatrix().inverse()		
		return origin_inverse.preMultVec(world_position)
		
	
	
	def drawWalls(self,draw_walls):
		"""Draw the walls of the CAVE.
		
		The function requires a boolean.
		This function should work regardless of CAVE or desktop mode.
		"""
		self.__assertBoolean(draw_walls)
		if self.__walls != None:
			self.__walls.remove()
			self.__walls = None
			
		if draw_walls:
			self.__walls = self.__cave.drawWalls()
			
	def drawEyes(self,draw_eyes):
		"""Draw the eyes of the user"""		
		
		self.__assertBoolean(draw_eyes)		
		
		if self.__left_eye != None:
			self.__left_eye.remove()
			self.__left_eye = None
				
		if self.__right_eye != None:
			self.__right_eye.remove()
			self.__right_eye = None
			
		if draw_eyes:
			self.__left_eye = vizshape.addSphere(self.__EYE_RADIUS)
			self.__left_eye.color(1,0,0)
			self.__right_eye = vizshape.addSphere(self.__EYE_RADIUS)
			self.__right_eye.color(0,1,0)
			
					
	def __setCaveMode(self):
		self.__cave_mode = True
		
		self.__cave_origin = vizcave.CaveView(self.__head_tracker)
		
		self.__cave.setTracker(leftPos=self.__right_eye_tracker,rightPos=self.__left_eye_tracker)
		
		#Add each wall, make sure that they are ordered in the cluster software correctly to match this ordering 
		self.__cave.addWall(self.__front_wall, mask=viz.cluster.getClientID('CAVEVOOR'))
		self.__cave.addWall(self.__left_wall, mask=viz.cluster.getClientID('CAVELINKS'))
		self.__cave.addWall(self.__right_wall, mask=viz.cluster.getClientID('CAVERECHTS')) 
		self.__cave.addWall(self.__bottom_wall, mask=viz.cluster.getClientID('CAVEVLOER'))
		
		self.drawWalls(False)
				
	def __setDesktopMode(self):
		self.__cave_mode = False
		
		self.__cave_origin = viz.addGroup()
		
		viz.MainWindow.fov (90) # Reset frustum because the vizcave module plays around with all of this
		viz.MainWindow.setViewOffset (viz.Matrix.euler (0,0,0))
		
		#Set cave tracker to viewtracker, (faulty automatic stereo computation)	
		#self.__cave.setTracker(pos = self.__head_tracker, ori = self.__head_tracker)
						
		self.__cave.addWall(self.__front_wall, mask=viz.CLIENT1) 
		self.__cave.addWall(self.__left_wall, mask=viz.CLIENT2) 
		self.__cave.addWall(self.__right_wall, mask=viz.CLIENT3) 
		self.__cave.addWall(self.__bottom_wall, mask=viz.CLIENT4)
				
		self.drawWalls(True)
		self.drawEyes(True)
		
		self.__cave_origin_auto_update = True
		
		
	def inCaveMode(self):
		"""Is the cavelib in CAVE mode."""
		return self.__cave_mode
		
	@property
	def wiimote(self):
		"""Get an object that can access the wiimote."""
		return self.__daemon.wiimote
		
	@property
	def caveorigin(self):
		"""Get a reference to the cave origin object.
		
		This function is identical to getOriginTracker().
		"""
		return self.getOriginTracker()
		
	def getBalanceBoard(self,feature):
		"""Get the weight in kilograms of the given feature."""
		
		if feature == self.BALANCE_BOARD_BOTTOM_LEFT:
			return self.__daemon.wiimote.getBalanceBoardBottomLeft()
			
		if feature == self.BALANCE_BOARD_BOTTOM_RIGHT:
			return self.__daemon.wiimote.getBalanceBoardBottomRight()
			
		if feature == self.BALANCE_BOARD_TOP_LEFT:
			return self.__daemon.wiimote.getBalanceBoardTopLeft()
			
		if feature == self.BALANCE_BOARD_TOP_RIGHT:
			return self.__daemon.wiimote.getBalanceBoardTopRight()
			
		if feature == self.BALANCE_BOARD_TOTAL:
			return self.__daemon.wiimote.getBalanceBoardTotal()
			
		return 0
		
	def getNoseMatrix(self):
		"""Get the nose matrix.
		
		This matrix is computed based on the head matrix and on the eye positions.
		There is no corresponding tracker.
		"""
		matrix = self.getHeadMatrix()
		matrix.setPosition(self.getPositionBetweenEyes())
		matrix.preEuler(180,0,0)
		matrix.preEuler(0,90,0)
		return matrix
		
		
	def getOverviewMatrix(self):
		"""Get the matrix that represents the overview viewpoint in desktop-mode.
		
		When the user is in desktop mode and when the user has selected 
		DESKTOP_MODE_VIEWPOINT_OVERVIEW (the default), the matrix that represents the viepoint within CAVE space is returned.		
		"""
		offset = viz.vizmat.Transform()
		offset.setPosition(0,1.5,-3.0)
		offset.preEuler(180,0,0)	
		offset.preEuler(0,90,0)
		return offset		
		
	def setCaveOriginTracker(self,tracker):
		"""Set the cave origin tracker."""
		self.__cave_origin_tracker = tracker
		
	def getKeyboardAndMouseTracker(self):
		"""Get a keyboard and mouse tracker.
		
		Identical to viztracker.KeyboardMouse6DOF().
		"""
		return self.__keyboard_mouse_sensor	
	
	def getWandPosition(self):
		"""The position of the wand in cave space."""
		return self.__wand_tracker.getPosition()
		
	def getPointerPosition(self):
		"""The position of the wand in cave space.
		
		Here for backwards compatibility, use getWandPosition instead.	
		"""
		return self.getWandPosition()
	
	
	def getWandQuat(self):
		"""The quaternion of the wand in cave space."""
		return self.__wand_tracker.getQuat()
		
	def getWandMatrix(self):
		"""The wand matrix in cave space"""
		return self.__wand_tracker.getMatrix()
	
	def getWandTracker(self):
		"""Return the wandtracker in cave space."""
		return self.__wand_tracker	
		
	def getThingPosition(self):
		"""The position of the thing in cave space."""
		return self.__thing_tracker.getPosition()
		
	def getThingQuat(self):
		"""The quaternion of the thing in cave space."""
		return self.__thing_tracker.getQuat()
		
	def getThingMatrix(self):
		"""The thing matrix in cave space."""
		return self.__thing_tracker.getMatrix()
		
	def getThingTracker(self):
		"""Return the thingtracker in cave space."""
		return self.__thing_tracker
	
	def getHeadPosition(self):
		"""The position of the head tracker in cave space."""
		return self.__head_tracker.getPosition()
	
	def getHeadQuat(self):
		"""The quaternion of the head tracker in cave space."""
		return self.__head_tracker.getQuat()
		
				
	def getHeadMatrix(self):
		"""The matrix of the head tracker in cave space."""
		return self.__head_tracker.getMatrix()
		
	def getHeadTracker(self):
		"""Return the headtracker in cave space."""
		return self.__head_tracker
	
	
	def getLeftEyePosition(self):
		"""The position of the center of the left eye in cave space."""
		return self.__left_eye_tracker.getPosition()
		
	def getRightEyePosition(self):
		"""The position of the center of the right eye in cave space."""
		return self.__right_eye_tracker.getPosition()
		
	def getPositionBetweenEyes(self):
		"""The position between the eyes in cave space."""
		return ((vizmat.Vector(self.getLeftEyePosition()) + self.getRightEyePosition()) * 0.5)
		
	def setNearPlane(self,zNear):
		"""Set the near cutoff plane (set positive distance value)."""
		
		zNear = float(zNear)
		
		if self.__cave_mode:
			self.__cave.setNearPlane(zNear)
		else:
			viz.MainWindow.clip(zNear,self.getFarPlane())		
	
	def setFarPlane(self,zFar):
		"""Set the far cutoff plane (set positive distance value, greater than the near value)."""
		
		zFar = float(zFar)
		
		if self.__cave_mode:
			self.__cave.setFarPlane(zFar)
		else:
			viz.MainWindow.clip(self.getNearPlane(),zFar)
		
	def getOriginTracker(self):
		"""Get the tracker that tracks the origin of the cave, in world space!"""
		return self.__cave_origin_tracker
		
	def getOriginMatrix(self):
		"""Get the matrix that represents the origin of the cave, in world space!"""
		return self.getOriginTracker().getMatrix()
	
	def getNearPlane(self):
		"""Get the near plane distance."""
		if self.__cave_mode:
			return self.__cave.getNearPlane()
			
		return viz.MainWindow.getNearClip()
	
	def getFarPlane(self):
		"""Get the far plane distance."""
		if self.__cave_mode:
			return self.__cave.getFarPlane()
			
		return viz.MainWindow.getFarClip()
	
	def __autoUpdate(self):
		if self.__cave_origin_auto_update:
			self.__cave_origin_tracker.setMatrix(self.__keyboard_mouse_sensor.getMatrix())
			
		if self.__left_eye_auto_update:
			self.__left_eye_tracker.setMatrix(self.__left_eye_sensor.getMatrix())
			
		if self.__right_eye_auto_update:
			self.__right_eye_tracker.setMatrix(self.__right_eye_sensor.getMatrix())
		
		if self.__head_auto_update:
			self.__head_tracker.setMatrix(self.__head_sensor.getMatrix())
			
		if self.__wand_auto_update:
			self.__wand_tracker.setMatrix(self.__wand_sensor.getMatrix())
			
		if self.__thing_auto_update:
			self.__thing_tracker.setMatrix(self.__thing_sensor.getMatrix())
		
	def __onUpdate(self,e):
		
		self.__autoUpdate()		
		
		self.__cave_origin.setMatrix(self.getOriginMatrix())
		
		if self.__walls != None:
			self.__walls.setMatrix(self.getOriginMatrix())
			
		if not self.__cave_mode:
			if self.__desktop_mode_viewpoint == self.DESKTOP_MODE_VIEWPOINT_USER:
				offset = self.getNoseMatrix()
			else:
				offset = self.getOverviewMatrix()
				
			viz.MainView.setMatrix(self.localMatrixToWorld(offset))		
			
		if self.__left_eye != None:
			self.__left_eye.setMatrix(self.localMatrixToWorld(self.__left_eye_tracker.getMatrix()))
					
		if self.__right_eye != None:
			self.__right_eye.setMatrix(self.localMatrixToWorld(self.__right_eye_tracker.getMatrix()))
		
	def go(self):
		"""Use this command to start the application."""
		
			
		if self.__cave_mode:
			viz.go(viz.STEREO | viz.FULLSCREEN)
		else:
			viz.go(viz.FULLSCREEN)
				
		viz.mouse.setOverride(viz.ON)
		
		self.callback(viz.UPDATE_EVENT,self.__onUpdate)
