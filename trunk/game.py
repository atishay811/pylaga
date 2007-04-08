#2007-04-1 RJ Marsan
#Pylaga
#Original: 2007-02-20 Derek Mcdonald 
#Subclass of pylaga.py
#################################################################################################################
#
#
#	arguably the most important class, this is the game object
#	it *is* the game. in an object.
#
#import pygame os and sys libraries
try:
	import pygame, os, sys, math, random
	from pygame.locals import*
	import globalvars
	from bullet import Bullet, EnemyBullet
	from background import BackgroundManager, bgstars
	from enemy import Enemy, EnemyManager
	from player import Player
	from stage import Stage
	from display import *
	from menu import Menu
	from menulists import MenuLists,menulists
	import ecollision
except:
	print "A File Was Missing. CHECK!"
	#sys.exit(0)

if not pygame.font: print 'Warning, fonts disabled'
#################################################################################################################
	
#now for the actual game class (I like classes. lets make classes of everything. rainbows are fun.)
class Gamelolz:
	#This is the __init__ 
	#its important.
	def __init__(self,parent):  
		self.parent=parent        
		globalvars.asdf = 0
		self.lagcount=0		
		self.leftkeydown=0
		self.rightkeydown=0
		self.enemylist=[]
		self.list_enemys=EnemyManager()
		self.stage=Stage(self.list_enemys,globalvars.player_list)
		self.list_allie_shots=pygame.sprite.RenderUpdates()
		self.enemy_shots=pygame.sprite.RenderUpdates()

		
	#clears all the variables
	def clear_vars(self):
		self.leftkeydown=0
		self.rightkeydown=0
		health.set_health(globalvars.max_health)
		points.set_points(0)
		globalvars.x=400
		globalvars.y=globalvars.WIN_RESY-60
		self.stage.set_stage(-1) #hax
		globalvars.enemy_bullet_odds=100
		self.list_enemys.empty()
		self.list_allie_shots.empty()
		globalvars.player_list.empty()
		self.enemy_shots.empty()
		print "Game Restarted"
		
	#define function to draw player ship on X, Y plane
	def pship(self, x,y):
		globalvars.player_list.clear(globalvars.surface,globalvars.screen)
		self.enemylist+=globalvars.player_list.draw(globalvars.surface)
	
	#Define function to move the enemy ship
	def emove(self):
		self.list_enemys.clear(globalvars.surface, globalvars.screen)
		self.enemylist+=self.list_enemys.draw(globalvars.surface)
	
	#draws all the enemys you ask it
	def draw_enemys(self):
		#k so now some recursive loops:
		for enemycol in range(self.stage.get_stage()[0]):	
			#now for the rows
			for enemyrow in range(self.stage.get_stage()[1]):
				#make a new enemy object:
				tempenemy=Enemy(self.list_enemys)
				#this ones a long one, but it works:
				tempenemy.set_pos(globalvars.xmin+enemycol*(globalvars.enemy_width+globalvars.enemy_spacing_x),globalvars.ymin+enemyrow*(globalvars.enemy_height+globalvars.enemy_spacing_y)-150)
				#this one is even worse, but works even better:
				tempenemy.set_range(globalvars.xmin+enemycol*(globalvars.enemy_width+globalvars.enemy_spacing_x),globalvars.xmax-(self.stage.get_stage()[0]-enemycol)*(globalvars.enemy_height+globalvars.enemy_spacing_x))                                                                                                     
				#now add the temp enemy to the array and we're good to go
				self.list_enemys.add(tempenemy)
	
	
				
	#So i'm trying out having the program check for collisions, instead of the enemy objects
	#i think i might switch to the objects, but still keep this function just hand the computing to the object
	#seems most efficient
	def test_collision(self):
		todie=pygame.sprite.groupcollide(self.list_enemys, self.list_allie_shots,0,0)
		#print todie
		for enemy,bullet in todie.iteritems():
			self.list_allie_shots.remove(bullet)
			enemy.set_state(0)
			points.add_points(1)
		if pygame.sprite.spritecollideany(self.player, self.enemy_shots):
			#print "ZOMFG SHOTZORZ"
			self.player.set_hit()
			health.hit()
	
	#if there are no enemys left, go to the next stage
	def check_done(self):
		if not self.list_enemys:
			self.stage.next_stage()
			self.draw_enemys()
	
	#checks to see if we can expand the ranges of the bots so its nice and.... umm... nice.
	def check_rows(self):
		if globalvars.asdf % 20==0:
			#simple sorting algorithm to find the highest values
			highest=globalvars.xmin
			lowest=globalvars.xmax
			for enemy in self.list_enemys:
				if enemy.get_range()[1] > highest:
					highest=enemy.get_range()[1]
				if enemy.get_range()[0] < lowest:
					lowest=enemy.get_range()[0]
			highest=globalvars.xmax-highest
			lowest=lowest-globalvars.xmin
			if highest != 0 or lowest != 0: #makes things |--| this much more efficient
				for enemy in self.list_enemys:
					erange=enemy.get_range()
					enemy.set_range(erange[0]-lowest,erange[1]+highest)
					
        #major hack just to get this thing playable..... sorry
	def again(self):
                if health.get_health() <= 0:
                        return False
                return True
		
	
	#this is called if the player shoots
	def pshoot(self, sx, sy):
		self.player.shoot(self.list_allie_shots,sx,sy)
	
	#draws the bullet.... duh. come on dude.
	def drawbullets(self):
		#for x in self.list_allie_shots:
			#x.draw()
		self.list_allie_shots.clear(globalvars.surface,globalvars.screen)
		self.enemy_shots.clear(globalvars.surface,globalvars.screen)
		self.enemylist+=self.list_allie_shots.draw(globalvars.surface)
		self.enemylist+=self.enemy_shots.draw(globalvars.surface)
	
	#...
	def drawsidepanel(self):
		if globalvars.asdf%5==0:
			globalvars.side_panel.update()
		globalvars.side_panel.clear(globalvars.surface,globalvars.screen)
		self.enemylist+=globalvars.side_panel.draw(globalvars.surface)

		
	#goes through all the arrays and makes each of them move 1 space, simple and easy yet it deserves a comment...
	def tick(self):
		self.list_allie_shots.update()
		self.list_enemys.update()
		self.enemy_shots.update()
	
	######################
	#heres a bunch of metafunctions
	#i break it up so its really easy to add new features
	#like if we ant a counter? add something to check() and draw()
	#all of these are called once per frame
	def check(self):
		self.check_done()
		self.test_collision()
		self.check_rows()
		bgstars.update()
		self.list_enemys.shoot(self.enemy_shots)
		self.player.update()
	
	def draw(self):
		self.enemylist+=bgstars.draw()
		self.enemylist+=bgstars.clear()
		self.drawbullets()
		self.pship(globalvars.x,globalvars.y)
		self.emove()
		self.drawsidepanel()
	
	#does just what it sounds like.....
        def clear_screen(self):
                globalvars.surface.fill(globalvars.bgcolor)
		pygame.display.flip()
	
	#for debugging info mostly
	def dispvars(self):
		print "The Enemy Array size is:",len(self.list_enemys.sprites())
		print "The Player Shot Array size is:",len(self.list_allie_shots.sprites())
		print "The Enemy Shot Array size is:",len(self.enemy_shots.sprites())
	
	#does lots and lots of stuff, it really needs to be cleaned up
	def input(self, events):
		global x
		global y
		pygame.event.pump()  #somewhere in their docs it said this line was a good idea
		for event in events:
			if event.type == QUIT:
				sys.exit(0)
			if event.type == pygame.MOUSEMOTION:
				pygame.event.get()
				tempx=pygame.mouse.get_pos()[0]-self.player.rect.width/2
				## Just to make sure we don't get the ship way out there:
				if tempx > globalvars.xmax: #if its outside the globalvars.window, just stick it as far as possible
					self.player.move(globalvars.xmax,globalvars.y)
				elif tempx < globalvars.xmin:
					self.player.move(globalvars.xmin,globalvars.y)
				elif abs(tempx-globalvars.x) > globalvars.smooth_scroll_var1:  #smooth scrolling if the mouse gets far from the ship
					self.player.move(self.player.get_pos().left+(tempx-self.player.get_pos().left)/globalvars.smooth_scroll_var2,globalvars.y)
				else:		#if it gets down to this point, 
						#we've passed all sanity checks so just move it
					self.player.move(tempx,globalvars.y)
						
			## if the mouse is clicked, shoot!
			if event.type == pygame.MOUSEBUTTONDOWN:
				self.pshoot(self.player.rect.centerx-globalvars.BULLET_WIDTH/2,globalvars.y)
			
			## if 'q' is pressed, quit
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_q:
					sys.exit(0)
				if event.key == pygame.K_p:
					menulists.pause_menu()
				if event.key == pygame.K_ESCAPE:
					sys.exit(0)
				#keyboard controls
				if event.key == pygame.K_LEFT:
					self.leftkeydown=1
				if event.key == pygame.K_RIGHT:
					self.rightkeydown=1
				if event.key == pygame.K_SPACE:
					self.pshoot(self.player.rect.centerx-globalvars.BULLET_WIDTH/2,globalvars.y)

			
			#keyboard controls
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_LEFT:
					self.leftkeydown=0
				if event.key == pygame.K_RIGHT:
					self.rightkeydown=0	
		
					
		if self.leftkeydown: self.player.move_one(0)
		if self.rightkeydown: self.player.move_one(1)
		
		pygame.event.clear()
	
	##################################################################################################################                


	#pretty simple
	def start(self):
		self.clear_vars()
		self.player=Player()
		globalvars.player_list.add(self.player)
		self.player.set_pos(globalvars.x,globalvars.y)
		self.loop()

	#Yeah see this one does all of the work
	def loop(self):
		#start loop
		while self.again():
			
			#refresh globalvars.screen...needs to be done once in a while
			if globalvars.asdf>=globalvars.REFRESH_TIME:
				#self.clear_screen()
				globalvars.asdf=0
			globalvars.asdf+=1
			
			#check everythign and see if changes need to be made
			self.check()
			
			#draw bullets
			self.draw()
			
			#move everything 1
			self.tick()
						
			#initiate input function
			self.input(pygame.event.get())
		
			#applies the smart screen updating
			pygame.display.update(self.enemylist)
			self.enemylist=[]
			
			#pauses and waits
			timeittook=globalvars.clock.tick(globalvars.FPS)
			#if timeittook > 1000/globalvars.FPS:
			#	print "LAG:"+str(self.lagcount)+" at "+str(timeittook)+"ms"
				#self.dispvars()
			#	self.lagcount+=1
			#print globalvars.clock.get_fps()
