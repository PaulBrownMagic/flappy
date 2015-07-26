'''
Flappy Bird Game with PyGame Zero
Authored by Paul Brown, 26th July 2015
'''
# Import random to position pipes later
import random

# Set constants for main window 
TITLE = "Flappy Bird"
WIDTH = 488
HEIGHT = 675
BG_BLUE = (150,200,255) # Pale blue for background colour
GAP = 225 # Size of gap between pipes
SCROLL_SPEED = 3

# Global Variables
score = 0 #Used to keep score
play_state = 'Flappy Bird' #Used to provide title screen and restart screen
click_length = 0.2 #Used to time duration of mouse down/ touch later


# # # Background
tile1 = Actor('ground')# These create 3 tiles used to scroll
tile2 = Actor('ground')# along bottom of screen as background
tile3 = Actor('ground')# Tile width is 244, so max screen width is 244*2 = 488
tiles = [tile1,tile2,tile3]
for tile in tiles:
    tile.bottom = HEIGHT #position on the bottom of the screen
tile1.left = 0
tile2.left = tile1.right
tile3.left = tile2.right #make one follow the other


# # # The Bird

# # Attributes
bird_pics = ['bird1','bird2','bird3'] #Flat pictures used to make bird flap
bird_pics_up = ['bird1up','bird2up','bird3up'] #Angled up pictures for bird flapping
bird_costume = 0 # Index for picture lists
bird = Actor(bird_pics[bird_costume]) #Create a bird as an actor with the first flat bird picture
bird.pos = WIDTH/3,HEIGHT/2 # Position bird in the center of the screen

# # Methods
def bird_up(): #Called frequently with a schedule_interval to make the bird rise smoothly on click
    bird.top -= 10
    
def bird_level(): #Called to stop the bird from rising, this is needed in a seperate
    clock.unschedule(bird_up) #funtion due to weak references in clock methods
    
def fly_straight(): # Changes bird's costumes whilst flying straight by sending that set of pics to fly()
    global bird_pics
    fly(bird_pics) 
    
def fly_up(): # Changes bird's costumes whilst flying up
    global click_length #click_length increased here as this function is called
    click_length += 0.1 # at regular intervals whilst the mouse is down.
    global bird_pics_up
    fly(bird_pics_up)
    sounds.wing.play()
    
def fly(pictures): # Does the costume changes with the list of pictures given
    global bird_costume
    if bird_costume < 2: # Changes the index number for the costumes
        bird_costume += 1
    else:
        bird_costume = 0
    bird.image = pictures[bird_costume]#Set the birds image to the new costume
    
# # # Pipes

# # Attributes
# top_pipe is used for logic, bottom pipe follows the top one.
top_pipe = Actor('pipe', anchor=('left','bottom')) # Anchors changed for ease of setting their
bottom_pipe = Actor('pipe', anchor=('left','top')) # positions later

top_pipe.pos = WIDTH+100,HEIGHT+100 # Position off screen at start
bottom_pipe.pos = WIDTH+100,HEIGHT+100
# # Methods
def reset_pipes(): # Put pipes back to a new position off the right of the screen 
    top_pipe.left = WIDTH + random.randint(0,WIDTH/2) # left is set off screen to the right plus a random amount up to half the screens width.
    top_pipe.bottom = random.randint(50,380) # top_pipe y is set to a random number between 50 and 350
    bottom_pipe.top = top_pipe.bottom + GAP # the y position is the bottom of the top_pipe plus 220 for a gap of 220
    bottom_pipe.left = top_pipe.left # bottom_pipe x is set to equal top_pipe's,

# # # PyGame Zero Game Loop Hooks
def draw():
    # Fill background
    screen.fill(BG_BLUE)
    for tile in tiles:
        tile.draw()
    # Draw pipes
    top_pipe.draw()
    bottom_pipe.draw()
    # Draw bird
    bird.draw()
    # Print Score
    global score
    # Import flappybirdy font, uses outline too.
    screen.draw.text(str(score), centerx = WIDTH/2, top = 50, fontname = 'flappybirdy', color = "white", fontsize = 50, owidth = 1.5, ocolor = "black")
    # Print titles (play_state) if the game is not in play.
    global play_state
    if play_state != "play":
        screen.draw.text(play_state, centerx = WIDTH/2, top = 200, fontname = 'flappybirdy', color = "orange", fontsize = 50, owidth = 0.5, ocolor = "black")
        with open("score.txt","r") as sc:
            top_score = sc.read()
            if top_score != "0":
                screen.draw.text("Top Score: " + top_score, centerx = WIDTH/2, top = 120, fontname = 'flappybirdy', color = "yellow", fontsize = 40, owidth = 1.5, ocolor = "black")
def update():
    global play_state
    global score
    # Defined as variable as it's used for pipes and background
    #Movement
    if play_state == "play": # If the game is on
        bird.top += 5 # move the bird down
        if bird.bottom > 600: # keeping above the ground, then
            bird.bottom = 600
        top_pipe.left -= SCROLL_SPEED # move the top pipe
        bottom_pipe.left = top_pipe.left # and make the bottom one follow
        if top_pipe.right < 0: # If the pipes are off the screen, reposition them to the right of the screen
            reset_pipes()
            sounds.point.play()
            score += 1 # If the pipes have made it off the screen the bird must have flown through, therefore add one to the score.
        for tile in tiles: # Update the background tiles positions
            tile.left -= SCROLL_SPEED
        if tile1.right < 0: # If the tile is off the screen
            tile1.left = tile3.right # put it to the right of the last one.
        if tile2.right < 0:
            tile2.left = tile1.right
        if tile3.right < 0:
            tile3.left = tile2.right   
    #Collision Detection
    if bird.colliderect(top_pipe) or bird.colliderect(bottom_pipe):
        sounds.lose.play()
        clock.unschedule(bird_up) # stop the bird moving up anymore
        reset_pipes()# move the pipes off the screen back to the start
        bird.pos = WIDTH/3, HEIGHT/2 # Put the bird back to it's start position
        play_state = "Get Ready" # Put the game into "reset"/ paused state

# # # PyGame Zero Events
# # Mouse Down used as most touch interfaces equate a click to a touch
def on_mouse_down():
    # on_mouse_down is a single event, so events to be repeated while the mouse is down must be scheduled
    # with an interval and unscheduled on_mouse_up()
    global play_state
    global score
    if play_state == "play":
        clock.schedule_interval(bird_up,0.01) # Every 100th of a second, move the bird up
        clock.schedule_interval(fly_up,0.05) # Every 50th of a second, flap the birds wings using the tilted pictures
        clock.unschedule(fly_straight) # Stop the bird from changing costumes in the flat flying position
    else:
        if play_state == "Flappy Bird":
            reset_pipes() # Set the pipes into position on the first play
        play_state = "play"
        with open("score.txt","r") as sf:
            ts = int(sf.read())
        if score > ts:
            with open("score.txt","w") as sf:
                sf.write(str(score))
        score = 0 # Reset the score to 0 here so that last score still displays on "Get Ready" screen
        clock.schedule_interval(fly_straight,0.3) # Make the bird flap its wings using the flat pictures
    
def on_mouse_up():
    global click_length
    clock.schedule(bird_level,click_length) # click_length is used to create a delay before the bird stops going up. bird_level is a defined function due to weak references. 
    click_length = 0.2 # reset click_length to a chosen minimum
    clock.schedule_interval(fly_straight,0.3) # make the bird flap using the horizontal pictures
    clock.unschedule(fly_up) # stop the bird from flapping using the flying up pictures
