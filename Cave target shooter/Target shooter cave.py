import cavelib3
import math
import viz
import vizshape
import caveapp #not strictly required
import vizact
import random

#x = -left/+right
#y = -below/+above
#z = -behind/+in front

################################################################
#Placement of objects
################################################################

#object.method(x, y, z)

#object = viz.add("map/file.ext")							#Add object to scene
#object.setAxisAngle(0, 1, 0, 90)							#Set the direction of an object
#object.texture(viz.addTexture("textureMap/img.ext")) 		#Connect a texture to an object (.mtl file with the same name pastes the material over the object by itself)
#object.addAction(vizact.spin(0, 1, 0, 20))					#Arguments (x, y, z, speed), a negative number is used to spin in the opposite direction
#object.setScale(0.5, 0.5, 0.5)								#Scaling the object for each specific axis
#object.setPosition(0,2,0)									#Set the position of the object


################################################################
#Code, with respect to she functionality should be in here
################################################################

class CustomCaveApplication(caveapp.CaveApplication):
	
	def __init__(self,use_keyboard = True, desktop_mode = False):
		"""Initialization function."""
		
		caveapp.CaveApplication.__init__(self,desktop_mode) #call constructor of super class, you have to do this explicitly in Python		
		viz.phys.enable()
		
		self.view = viz.MainView;
		
		self.backGroundMusic = viz.addAudio('Windmill hut.wav')
		self.backGroundMusic.volume(0.5)
		self.backGroundMusic.loop(viz.ON)
		self.backGroundMusic.play()
		self.gameMusic = viz.addAudio('Battle.wav')
		self.gameMusic.volume(0.7)
		
		headLight = viz.MainView.getHeadLight()
		headLight.intensity(100)
		headLight.disable()
		
		for i in range(3):
			light = viz.addLight()
			light.setPosition(0, 2, (i*10))
			light.position(0,0,0,1)
				
		self.use_keyboard = use_keyboard #store if we want to use the keyboard
		self.scaleValue = 0.03
		
		self.shootingRange = viz.addChild('ShootingRange.FBX')
		self.shootingRange.setScale(self.scaleValue, self.scaleValue,self.scaleValue )
		self.shootingRange.name = 'shootingRange'
		self.shootingRange.collideMesh()
		self.shootingRange.disable(viz.DYNAMICS)		
		
		self.target = viz.addChild('target.FBX')
		self.target.name = 'target'
		self.target.setScale(0.9, 0.9, 0.9)
		self.target.collideBox(density = 100)
		self.target.enable(viz.COLLIDE_NOTIFY)
		self.target.setPosition(0,0, 15)
				
		self.enemyGun = viz.addChild('Gun.FBX')
		self.enemyGun.name = 'enemyGun'
		self.enemyGun.setScale(self.scaleValue, self.scaleValue, self.scaleValue)
		self.enemyGun.setPosition(0, 1.8, 14)
		self.enemyGun.setEuler(180,0,0)						
				
		self.bullet = viz.add('Bullet.FBX')
		self.bullet.setPosition(0,1,2)
		self.bullet.setScale(self.scaleValue, self.scaleValue,self.scaleValue)
		self.bullet.name = 'bullet'
		self.bullet.collideCapsule(0.2, 0.1, density = 1, hardness = 1)
		self.bullet.enable(viz.COLLIDE_NOTIFY)
		self.nextShot = True
		
		self.enemyBullet = viz.add('Bullet.FBX')
		self.enemyBullet.setPosition(0,1,10)
		self.enemyBullet.setScale(0.05, 0.05, 0.05)
		self.enemyBullet.name = 'enemyBullet'
		
		self.enemyShot = False
		
		self.enemyShootTimer = vizact.ontimer(3, self.repositionEnemyGun)
		self.moveEnemyBulletTimer = vizact.ontimer(0, self.moveEnemyBullet)
		
		self.moveEnemyBulletTimer.setEnabled(False)
		self.enemyShootTimer.setEnabled(False)
		
		self.shootTimer = vizact.ontimer(1, self.schootClick)
		self.shootTimer.setEnabled(False)	
		
		self.rings = ['Ring10', 'Ring20', 'Ring30', 'Ring40', 'Ring50'] 
									
		self.currentScore = 0		
		self.scoreBaseText = 'Score: '
		self.firstLabelText = self.scoreBaseText + str(self.currentScore)
		self.scoreLabel = viz.addText3D(self.firstLabelText)
		self.scoreLabel.setBackdrop(viz.BACKDROP_RIGHT_BOTTOM)
		self.scoreLabel.setPosition(-1.7, 1, 0)
		self.scoreLabel.setEuler(-90,0,0)
		self.scoreLabel.color(viz.SKYBLUE)
		self.scoreLabel.setScale(0.3, 0.3, 0.3)
		self.scoreLabel.alignment(viz.ALIGN_CENTER_BOTTOM)
		
		self.currentHighScore = 0		
		self.highScoreBaseText = 'Highscore: '
		self.firstHighScoreLabelText = self.highScoreBaseText + str(self.currentHighScore)
		self.highScoreLabel = viz.addText3D(self.firstHighScoreLabelText)
		self.highScoreLabel.setPosition(-1.7, 1.5, 0)
		self.highScoreLabel.setEuler(-90,0,0)
		self.highScoreLabel.color(viz.BLUE)
		self.highScoreLabel.setScale(0.3, 0.3, 0.3)
		self.highScoreLabel.alignment(viz.ALIGN_CENTER_BOTTOM)
		
		self.newPointLabel = viz.addText3D('')
		self.newPointLabel.color(viz.GREEN)
		self.newPointLabel.setPosition(self.target.getPosition()[0], self.target.getPosition()[1] + 2, self.target.getPosition()[2])
		self.newPointLabel.alignment(viz.ALIGN_CENTER_BOTTOM)
		self.maxTimeNewPointVisible = 1
		
		self.newHitLabel = viz.addText3D('')
		self.newHitLabel.color(viz.RED)
		self.newHitLabel.setPosition(self.target.getPosition()[0], self.target.getPosition()[1] + 2.5, self.target.getPosition()[2])
		self.newHitLabel.alignment(viz.ALIGN_CENTER_BOTTOM)
		self.maxTimeHitVisible = 1
		
		self.newPointTimer = vizact.ontimer(self.maxTimeNewPointVisible, self.makeNewPointLabelInvisible)
		self.newPointTimer.setEnabled(False)	
		
		self.newHitPointTimer = vizact.ontimer(self.maxTimeHitVisible, self.makeNewHitLabelInvisible)
		self.newHitPointTimer.setEnabled(False)	
									
		self.goodSound = viz.addAudio('good.mp3')
		self.coinSound = viz.addAudio('coin.wav')	
		self.hitSound = viz.addAudio('hit.mp3')
			
		self.playTimer = vizact.ontimer(1, self.timerClick)
		self.playTimer.setEnabled(False)
		self.playTime = 35		
		self.currentTime = 0
		self.isPlaying = False
		
		self.timeBaseText = 'Time: '
		self.timeLabel = viz.addText3D(self.timeBaseText)
		self.timeLabel.setPosition(1.1, 1.3, 3)
		self.timeLabel.setEuler(50,0,0)
		self.timeLabel.setScale(0.3, 0.3, 0.3)
		self.timeLabel.alignment(viz.ALIGN_CENTER_BOTTOM)
		self.timeLabel.visible(False)
				
		self.scope = viz.addChild('Scope.FBX')
		
		viz.startLayer(viz.LINES)
		viz.vertexColor(viz.RED)
		viz.vertex(-0.2, 0,0)
		viz.vertex(0.2, 0, 0)
		self.topLine = viz.endLayer()
		
		viz.startLayer(viz.LINES)
		viz.vertexColor(viz.RED)
		viz.vertex(0, 0,0)
		viz.vertex(0, -0.3, 0)
		self.leftLine = viz.endLayer()
		
		viz.startLayer(viz.LINES)
		viz.vertexColor(viz.RED)
		viz.vertex(0, 0,0)
		viz.vertex(0, -0.3, 0)
		self.rightLine = viz.endLayer()
		
		self.time = 0.0 
		
		
	def updateObjects(self,e):		
		elapsed = e.elapsed 
		self.time += elapsed				
		
		self.scope.setMatrix(self.cavelib.localMatrixToWorld(self.cavelib.getThingMatrix()))
		self.scope.setPosition(self.view.getPosition()[0], self.view.getPosition()[1] - 0.07, self.view.getPosition()[2] + 0.8)
		self.scope.setScale(0.3, 0.3, 0.3)
		
		self.updateBodyLines()
		
		if self.spacePressed():
			self.shoot()
			
		if self.bPressed():
			self.shoot()	
		
		if self.keyPPressed():
			self.startTimer()
			
		if self.aPressed():
			self.startTimer()
	
	def updateBodyLines(self):
		scopePosition = self.scope.getPosition()
		
		leftpos = self.leftLine.getPosition()
		
		rightpos = self.rightLine.getPosition()

		self.topLine.setPosition(scopePosition[0], scopePosition[1] + 0.1, scopePosition[2])
		self.leftLine.setPosition(scopePosition[0] - 0.2, scopePosition[1] + 0.1, scopePosition[2])
		self.rightLine.setPosition(scopePosition[0] + 0.2, scopePosition[1] + 0.1, scopePosition[2])
	
	
	#_______________________________________________________________________________________________________________________________________
	#Shoot the target
	def shoot(self):	
		if self.nextShot:
			self.nextShot = False
			self.shootTimer.setEnabled(True)
			
			scopePosition = self.scope.getPosition()#barrel.getPosition()
			
			bulletStartPosition = [scopePosition[0], scopePosition[1], scopePosition[2]]
			
			print 'shoot'
			self.bullet.setPosition(bulletStartPosition)	
			self.bullet.setEuler(0, 0, 0)
			self.bullet.reset()
			self.bullet.applyForce( dir = [0, 0, 20 ], duration=0.24, pos = bulletStartPosition )
	
	def schootClick(self):
			self.nextShot = True;
			self.shootTimer.setEnabled(False)
	
	#_______________________________________________________________________________________________________________________________________
	#Hitting target and get points
	def updatePoints(self, newPoint):
		self.currentScore += newPoint
		nieuwLabelText = self.scoreBaseText + str(self.currentScore)
		self.scoreLabel.message(nieuwLabelText)

	def getHitPoint(self, hittedName):
		index = self.rings.index(hittedName)
		self.coinSound.play()
		
		newPoint = (index + 1) * 10
		self.showNewPoint(newPoint)
		
		if self.isPlaying:
			self.updatePoints(newPoint)
				
	def getHittedObject(self, e):	
		print 'hit1 =',e.obj1.name
		print 'hit2 =',e.obj2.name
		print 'nextShot = ',self.nextShot
		if e.obj2.name == "target" and self.nextShot == False :
			hitPosition = e.pos
			worldPosition = viz.worldtoscreen(hitPosition)
			pickedObject = viz.pick(pos = [worldPosition[0], worldPosition[1]], info = True, mode = viz.WORLD, all=True)
			
			count = len(pickedObject)			
			hittedRing = ''
			
			for i in range(count):
				obj = pickedObject[i]
				name = obj.name
				print 'pickObject', i, ' = ', name
				if name in self.rings:
					hittedRing = name
					self.getHitPoint(hittedRing)
					return	
	#_______________________________________________________________________________________________________________________________________
	#Showing new points
	def showNewPoint(self, newPoint):
		newPointText = ''
		if newPoint > 0:
			newPointText = '+' + str(newPoint)			
			self.newPointLabel.message(newPointText)
			self.newPointLabel.visible(True)
			
			self.newPointTimer.setEnabled(True)
		else:
			newPointText = str(newPoint)
			self.newHitLabel.message(newPointText)
			self.newHitLabel.visible(True)
			
			self.newHitPointTimer.setEnabled(True)
				
	def makeNewPointLabelInvisible(self):
		self.newPointTimer.setEnabled(False)
		self.newPointLabel.visible(False)
		
	def makeNewHitLabelInvisible(self):
		self.newHitPointTimer.setEnabled(False)
		self.newHitLabel.visible(False)
		
	#_______________________________________________________________________________________________________________________________________
	#Enemy shooting
	def repositionEnemyGun(self):
		maxHeadXDifference = 0.1
		maxHeadYDownDifference = 1
		maxHeadYUpDifference = 0.1
		currentViewPos = self.view.getPosition()
				
		currentMinXPos = (currentViewPos[0] - maxHeadXDifference)
		currentMaxXPos = (currentViewPos[0] + maxHeadXDifference)
		currentMinYPos = (currentViewPos[1] - maxHeadYDownDifference)
		currentMaxYPos = (currentViewPos[1] + maxHeadYUpDifference)
		
		newXPosition = random.uniform(currentMinXPos, currentMaxXPos)
		newYPosition = random.uniform(currentMinYPos, currentMaxYPos)
				
		self.enemyGun.setPosition(newXPosition, newYPosition, self.enemyGun.getPosition()[2])
		self.enemyShoot()
	
	def enemyShoot(self):	
		self.enemyShot = True
		enemyBarrelPosition = self.enemyGun.getPosition()#barrel.getPosition()
		
		enemyBulletStartPosition = [enemyBarrelPosition[0], enemyBarrelPosition[1], enemyBarrelPosition[2] - 0.25]
		
		self.enemyBullet.setPosition(enemyBulletStartPosition)	
		self.enemyBullet.setEuler(180, 0, 0)
		self.enemyBullet.reset()
		
		self.enemyBullet.applyForce( dir = [0, 0, -10 ], duration=10, pos = enemyBulletStartPosition )
		self.moveEnemyBulletTimer.setEnabled(True)
		
	def moveEnemyBullet(self):
		bulletPos = self.enemyBullet.getPosition()
		bulletPos[2] -= 0.1
		self.enemyBullet.setPosition(bulletPos)
		
		scopeZPosition = self.scope.getPosition()[2]
		
		if(bulletPos[2] <= scopeZPosition and self.enemyShot == True):
			self.enemyShot = False
			self.checkPersonHit()
		
	def checkPersonHit(self):
		bulletPos = self.enemyBullet.getPosition()
				
		height = self.scope.getPosition()[1] + 0.1
		left = self.leftLine.getPosition()[0]
		right = self.rightLine.getPosition()[0]
				
		if(bulletPos[1] <= height):
			if(bulletPos[0] >= left and bulletPos[0] <= right):
				self.hitSound.play()
				self.showNewPoint(-50)
				self.updatePoints(-50)
	
	
	#_______________________________________________________________________________________________________________________________________
	#Activating game mode
	def timerClick(self):
		self.currentTime -= 1
		self.timeLabel.message(self.timeBaseText + str(self.currentTime))
		
		if(self.currentTime <= 5):
			self.timeLabel.color(viz.ORANGE)
		
		if(self.currentTime == 0):
			self.isPlaying = False
			self.playTimer.setEnabled(False)
			self.timeLabel.visible(False)
			self.backGroundMusic.play()
			self.goodSound.play();
			self.gameMusic.stop()
			self.enemyShootTimer.setEnabled(False)
			
			if(self.currentScore > self.currentHighScore):
				self.currentHighScore = self.currentScore
				newHighScoreText = self.highScoreBaseText + str(self.currentHighScore)
				self.highScoreLabel.message(newHighScoreText)

	def startTimer(self):	
		if(self.isPlaying == False):
			self.isPlaying = True
			self.currentTime = self.playTime
			self.timeLabel.message(self.timeBaseText + str(self.currentTime))
			self.timeLabel.visible(True)
			self.playTimer.setEnabled(True)
			self.currentScore = 0;
			self.timeLabel.color(viz.WHITE)
			self.gameMusic.play()
			self.backGroundMusic.pause()
			self.enemyShootTimer.setEnabled(True)
	
	def preUpdate(self,e):
		"""This function is executed before the updates are done."""
		pass
		
	def postUpdate(self,e):
		"""This function is exectuted after the updates are done."""		
		pass
						
	def	leftPressed(self):
		"""Virtual function to use keyboard if indicated.
		
		This function can be omitted.
		If this function is omitted, the wiimote will always be used.
		"""
		if self.use_keyboard:
			return viz.iskeydown(viz.KEY_LEFT) #keyboard input
		
		return caveapp.CaveApplication.leftPressed(self) #wiimote input
			
	def	rightPressed(self):
		"""Virtual function to use keyboard if indicated.
		
		This function can be omitted.
		If this function is omitted, the wiimote will always be used.
		"""
		if self.use_keyboard:
			return viz.iskeydown(viz.KEY_RIGHT)#keyboard input
		
		return caveapp.CaveApplication.rightPressed(self) #wiimote input
			
	def	upPressed(self):
		"""Virtual function to use keyboard if indicated.
		
		This function can be omitted.
		If this function is omitted, the wiimote will always be used.
		"""
		if self.use_keyboard:
			return viz.iskeydown(viz.KEY_UP)#keyboard input
		
		return caveapp.CaveApplication.upPressed(self) #wiimote input
			
	def	downPressed(self):
		"""Virtual function to use keyboard if indicated.
		
		This function can be omitted.
		If this function is omitted, the wiimote will always be used.
		"""
		if self.use_keyboard:
			return viz.iskeydown(viz.KEY_DOWN)#keyboard input
		
		return caveapp.CaveApplication.downPressed(self) #wiimote input
			
	def	joystick(self):
		"""Virtual function to use keyboard if indicated.
		
		This function can be omitted.
		If this function is omitted, the wiimote will always be used.
		"""
		if self.use_keyboard:
			
			#keyboard input
			
			result = [0.0,0.0]
			
			if viz.iskeydown('['): 
				result[0] -= 1.0
				
			if viz.iskeydown(']'): 
				result[0] += 1.0
				
			return result
		
		return caveapp.CaveApplication.joystick(self) #wiimote input
			
################################################################
#Cave functionality
################################################################
#Param: True = DesktopMode on
#		False = DesktopMode off

print "Constructing the application class."
application = CustomCaveApplication(use_keyboard=True, desktop_mode=True) #boolean indicated wheter or not to use the keyboard instead of the wiimote

print "Setting the number of samples per pixel."

viz.setMultiSample(4)

application.go()

