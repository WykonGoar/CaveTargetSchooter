import viz
import cavelib3

class CaveApplication(viz.EventClass):
	"""CAVE application
	
	This is an object oriented wrapper around CAVElib.
	It implements movement of the CAVE-origin by using the wiimote (with or without nunchuck).
	
	All the wiimote buttons that are used are implemented as virtual functions.
	You can override these functions in order to assign different input.
	"""
	def __init__(self, desktop_mode):
		"""Initialize this class.
		
		Initiallize CAVElib wrapper class.
		Note that this initializer disables the 6DOF standard input of CAVElib.
		Normally this standard input is used to move the CAVE-origin.		
		"""
		viz.EventClass.__init__(self)
		self.cavelib = cavelib3.CaveLib(desktop_mode)
		
		self.cavelib.setAutoUpdate(self.cavelib.TRACKER_CAVE_ORIGIN,False)#do not automatically update the cave origin
		
		self.yaw = 0 #keep track of the yaw of the cave origin
		self.pitch = 0#keep track of the pitch (not modified within this class)
		self.yawDelta = 90 #90 degrees per second
		self.speed = 4.0 #four meters per second
		
		self.callback( viz.COLLIDE_BEGIN_EVENT, self.getHittedObject )
		
	def getHittedObject(self,e):
		print 'getHittedObject'
	
	def preUpdate(self,e):
		"""This function is executed before the updates are done.
		
		You can override this function.		
		"""
		pass
		
	def postUpdate(self,e):
		"""This function is exectuted after the updates are done.
		
		You can override this function.
		"""		
		pass
		
	def update(self,e):
		"""The update code
		
		This code gets called each frame.
		If you override this function, some functionality may get lost.
		"""
		
		if self.userView(): #poll
			self.cavelib.setDestkopModeViewpoint(self.cavelib.DESKTOP_MODE_VIEWPOINT_USER)
		else:
			self.cavelib.setDestkopModeViewpoint(self.cavelib.DESKTOP_MODE_VIEWPOINT_OVERVIEW)		
		
		self.movementOfCave(e) #fist move the cave a bit (for a small period in time i.e. e.elapsed)
		self.updateObjects(e) #then update all the poses of the objects
		#the latter function can be used as a general update function
		#or you can use the preUpdate and the postUpdate functions		
		#it is recommended that you do not use additional callbacks
		
	def movementOfCave(self,e):
		"""Change the pose of the CAVE
		
		If you want the CAVE origin motion to be different, you should override this function.
		
		"""
		
		elapsed = e.elapsed
		
		originTracker = self.cavelib.getOriginTracker() #a reference to the origin tracker
		#the object above is not updated automatically
		#i.e. self.cavelib.setAutoUpdate(self.cavelib.TRACKER_CAVE_ORIGIN,False), see __init__
		#if it were updated automatically, then this would conflict with the update that is done here		
		
		if self.leftPressed():
			originTracker.setPosition([-self.speed * elapsed,0,0],viz.REL_LOCAL)
	
		if self.rightPressed():
			originTracker.setPosition([self.speed * elapsed,0,0],viz.REL_LOCAL)
	
		if self.upPressed():
			originTracker.setPosition([0,0,self.speed * elapsed],viz.REL_LOCAL)
	
		if self.downPressed():
			originTracker.setPosition([0,0,-self.speed * elapsed],viz.REL_LOCAL)
			
		self.yaw = self.yaw + self.yawDelta * self.joystick()[0] * elapsed
	
		originTracker.setEuler([self.yaw,self.pitch,0])
		
	def updateObjects(self,e):
		"""Update the positions of objects
		
		After the CAVE pose has changed,
		Update poses of the objects in world space.
		"""
		pass
		
	def __onUpdate(self,e):
		"""This function gets called every frame.
		
		You should not have to modify this function.
		"""		
		self.preUpdate(e)
		self.update(e)
		self.postUpdate(e)
		
	def userView(self):
		"""Do we need to show user view.
		
		You can override this function if you want to use a different key/input device for this.
		"""
		return viz.iskeydown('U')
		
	def go(self):
		"""You need to call this function in order to start the application."""
		self.callback(viz.UPDATE_EVENT,self.__onUpdate)
		self.cavelib.go()
		
	def spacePressed(self):
		return viz.iskeydown(' ')
		
	def keyPPressed(self):
		return viz.iskeydown('p')
		
	def aPressed(self):
		return self.cavelib.wiimote.getState() & self.cavelib.wiimote.BUTTON_A != 0
	
	def bPressed(self):
		return self.cavelib.wiimote.getState() & self.cavelib.wiimote.BUTTON_B != 0
		
	def leftPressed(self):
		"""You can override this function."""		
		return self.cavelib.wiimote.getState() & self.cavelib.wiimote.BUTTON_LEFT != 0
		
	def rightPressed(self):
		"""You can override this function."""		
		return self.cavelib.wiimote.getState() & self.cavelib.wiimote.BUTTON_RIGHT != 0
		
	def upPressed(self):
		"""You can override this function."""		
		return self.cavelib.wiimote.getState() & self.cavelib.wiimote.BUTTON_UP != 0
		
	def downPressed(self):
		"""You can override this function."""		
		return self.cavelib.wiimote.getState() & self.cavelib.wiimote.BUTTON_DOWN != 0
		
	def downPressed(self):
		"""You can override this function."""		
		return self.cavelib.wiimote.getState() & self.cavelib.wiimote.BUTTON_DOWN != 0
		
	def joystick(self):
		"""You can override this function."""
		return self.cavelib.wiimote.getJoystick()	