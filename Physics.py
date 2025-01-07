import phylib
import os
import math
import sqlite3

################################################################################
# import constants from phylib to global varaibles

# All the constants have been added 
BALL_RADIUS   = phylib.PHYLIB_BALL_RADIUS;
BALL_DIAMETER = phylib.PHYLIB_BALL_DIAMETER;
HOLE_RADIUS = phylib.PHYLIB_HOLE_RADIUS;
TABLE_LENGTH = phylib.PHYLIB_TABLE_LENGTH;
TABLE_WIDTH = phylib.PHYLIB_TABLE_WIDTH;
SIM_RATE = phylib.PHYLIB_SIM_RATE;
VEL_EPSILON = phylib.PHYLIB_VEL_EPSILON;
DRAG = phylib.PHYLIB_DRAG;
MAX_TIME = phylib.PHYLIB_MAX_TIME;
MAX_OBJECTS = phylib.PHYLIB_MAX_OBJECTS;
FRAME_RATE = 0.01;

################################################################################

HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg id="mySVG" width="700" height="1375" viewBox="-25 -25 1400 2750"
xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink">
<rect width="1350" height="2700" x="0" y="0" fill="#C0D0C0" />""";
FOOTER = """</svg>\n""";

################################################################################
# the standard colours of pool balls
# if you are curious check this out:  
# https://billiards.colostate.edu/faq/ball/colors/

BALL_COLOURS = [ 
    "WHITE",
    "YELLOW",
    "BLUE",
    "RED",
    "PURPLE",
    "ORANGE",
    "GREEN",
    "BROWN",
    "BLACK",
    "LIGHTYELLOW",
    "LIGHTBLUE",
    "PINK",             # no LIGHTRED
    "MEDIUMPURPLE",     # no LIGHTPURPLE
    "LIGHTSALMON",      # no LIGHTORANGE
    "LIGHTGREEN",
    "SANDYBROWN",       # no LIGHTBROWN 
    ];

################################################################################
class Coordinate( phylib.phylib_coord ):
    """
    This creates a Coordinate subclass, that adds nothing new, but looks
    more like a nice Python class.
    """

################################################################################
class StillBall( phylib.phylib_object ):
    """
    Python StillBall class.
    """

    def __init__( self, number, pos ):
        """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_STILL_BALL, 
                                       number, 
                                       pos, None, None, 
                                       0.0, 0.0 );
      
        # this converts the phylib_object into a StillBall class
        self.__class__ = StillBall;


    # add an svg method here
    def svg(self):
        color = BALL_COLOURS[self.obj.still_ball.number % len(BALL_COLOURS)]
        return f' <circle cx="{self.obj.still_ball.pos.x}" cy="{self.obj.still_ball.pos.y}" r="{BALL_RADIUS}" fill="{color}" />\n'

# Created other python classes
################################################################################
class RollingBall(phylib.phylib_object ):
    """
    Python RollingBall class.
    """

    def __init__( self, number, pos , vel , acc ):
        """
        Constructor function. Requires ball number and position (x,y) velocity (x,y) and acceleration (x,y) as
        arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_ROLLING_BALL, 
                                       number, 
                                       pos, vel, acc, 
                                       0.0, 0.0);
      
        # this converts the phylib_object into a RollingBall class
        self.__class__ = RollingBall;


    # add an svg method here
    def svg(self):
        color = BALL_COLOURS[self.obj.rolling_ball.number % len(BALL_COLOURS)]
        return f' <circle cx="{self.obj.rolling_ball.pos.x}" cy="{self.obj.rolling_ball.pos.y}" r="{BALL_RADIUS}" fill="{color}" />\n'


################################################################################
class Hole( phylib.phylib_object ):
    """
    Python Hole class.
    """

    def __init__( self, pos ):
        """
        Constructor function. Requires position (x,y) as
        arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_HOLE,  
                                       0,
                                       pos, None, None, 
                                       0.0, 0.0 );
      
        # this converts the phylib_object into a Hole class
        self.__class__ = Hole;


    # add an svg method here
    def svg(self):
        return f' <circle cx="{self.obj.hole.pos.x}" cy="{self.obj.hole.pos.y}" r="{phylib.PHYLIB_HOLE_RADIUS}" fill="black" />\n'

################################################################################
class HCushion(phylib.phylib_object):
    """
    Python HCushion class.
    """

    def __init__(self, y):
        """
        Constructor function. Requires y axis as
        argument.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__(self,
                                      phylib.PHYLIB_STILL_BALL,
                                      0,
                                      None, None, None,
                                      0.0, y)

        # this converts the phylib_object into a HCusion class
        self.__class__ = HCushion;

    # add an svg method here
    def svg(self):
        yPos = -25 if self.obj.hcushion.y == 0 else 2700
        return f' <rect width="1400" height="25" x="-25" y="{yPos}" fill="darkgreen" />\n'

################################################################################
class VCushion( phylib.phylib_object ):
    """
    Python VCushion class.
    """

    def __init__( self, x ):
        """
        Constructor function. Requires x axis as
        argument.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_STILL_BALL, 
                                       0, 
                                       None, None, None, 
                                       x, 0.0 );
      
        # this converts the phylib_object into a HCusion class
        self.__class__ = VCushion;

    # add an svg method here
    def svg(self):
        xPos = -25 if self.obj.vcushion.x == 0 else 1350                                               
        return f' <rect width="25" height="2750" x="{xPos}" y="-25" fill="darkgreen" />\n'

################################################################################

class Table( phylib.phylib_table ):
    """
    Pool table class.
    """

    def __init__( self ):
        """
        Table constructor method.
        This method call the phylib_table constructor and sets the current
        object index to -1.
        """
        phylib.phylib_table.__init__( self );
        self.current = -1;

    def __iadd__( self, other ):
        """
        += operator overloading method.
        This method allows you to write "table+=object" to add another object
        to the table.
        """
        self.add_object( other );
        return self;

    def __iter__( self ):
        """
        This method adds iterator support for the table.
        This allows you to write "for object in table:" to loop over all
        the objects in the table.
        """
        self.current = -1

        return self

    def __next__( self ):
        """
        This provides the next object from the table in a loop.
        """
        self.current += 1;  # increment the index to the next object
        if self.current < MAX_OBJECTS:   # check if there are no more objects
            return self[ self.current ]; # return the latest object

        # if we get there then we have gone through all the objects
        self.current = -1;    # reset the index counter
        raise StopIteration;  # raise StopIteration to tell for loop to stop

    def __getitem__( self, index ):
        """
        This method adds item retreivel support using square brackets [ ] .
        It calls get_object (see phylib.i) to retreive a generic phylib_object
        and then sets the __class__ attribute to make the class match
        the object type.
        """
        result = self.get_object( index ); 
        if result==None:
            return None;
        if result.type == phylib.PHYLIB_STILL_BALL:
            result.__class__ = StillBall;
        if result.type == phylib.PHYLIB_ROLLING_BALL:
            result.__class__ = RollingBall;
        if result.type == phylib.PHYLIB_HOLE:
            result.__class__ = Hole;
        if result.type == phylib.PHYLIB_HCUSHION:
            result.__class__ = HCushion;
        if result.type == phylib.PHYLIB_VCUSHION:
            result.__class__ = VCushion;
        return result;

    def __str__( self ):
        """
        Returns a string representation of the table that matches
        the phylib_print_table function from A1Test1.c.
        """
        result = ""  # create empty string
        result += "time = %6.1f;\n" % self.time    # append time
        for i,obj in enumerate(self): # loop over all objects and number them
            result += "  [%02d] = %s\n" % (i,obj);  # append object description
        return result;  # return the string

    def segment( self ):
        """
        Calls the segment method from phylib.i (which calls the phylib_segment
        functions in phylib.c.
        Sets the __class__ of the returned phylib_table object to Table
        to make it a Table object.
        """
        result = phylib.phylib_table.segment( self );
        if result:
            result.__class__ = Table;
            result.current = -1;
        return result;

    def roll( self, t ):
        new = Table();
        for ball in self:
            if isinstance( ball, RollingBall ):
                # create4 a new ball with the same number as the old ball
                new_ball = RollingBall( ball.obj.rolling_ball.number,
                                        Coordinate(0,0),
                                        Coordinate(0,0),
                                        Coordinate(0,0) );
                # compute where it rolls to
                phylib.phylib_roll( new_ball, ball, t );
                # add ball to table
                new += new_ball;

            if isinstance( ball, StillBall ):
                # create a new ball with the same number and pos as the old ball
                new_ball = StillBall( ball.obj.still_ball.number,
                                    Coordinate( ball.obj.still_ball.pos.x,
                                                ball.obj.still_ball.pos.y ) );
                # add ball to table
                new += new_ball;
        # return table
        return new;

    def cueBall(self, table, xvel, yvel):

        """
        This method returns the cueball
        """
        for obj in table:
             # Check condition 
            if isinstance(obj, (StillBall, RollingBall)) and obj.obj.still_ball.number == 0:
                # Return cueball
                return obj

    def svg(self):
        svg_content = HEADER
        for item in self:
           if item is not None:
            svg_content += item.svg()
        svg_content += FOOTER
        return svg_content

################################################################################

class Database():

    def __init__( self, reset=False ):

        """
        Constructor method for database class 
        Sets up the database 
        """

        # Set database name
        db_filename = "phylib.db"

        # check if reset is true
        if reset and os.path.exists(db_filename):
            os.remove(db_filename)

        #Create/Open connection to database and cursor
        self.conn = sqlite3.connect(db_filename)
        self.cursor = self.conn.cursor()
        
    def createDB(self):

        """
        This method adds the different tables required into the database
        """

        # Creates Ball table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Ball (
                BALLID INTEGER PRIMARY KEY AUTOINCREMENT,
                BALLNO INTEGER NOT NULL,
                XPOS FLOAT NOT NULL,
                YPOS FLOAT NOT NULL,
                XVEL FLOAT,
                YVEL FLOAT
            );
        ''')

        # Creates Time table 
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS TTable (
                TABLEID INTEGER PRIMARY KEY AUTOINCREMENT,
                TIME FLOAT NOT NULL
            );
        ''')

        # Creates BallTable 
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS BallTable (
                BALLID INTEGER NOT NULL,
                TABLEID INTEGER NOT NULL,
                FOREIGN KEY (BALLID) REFERENCES Ball(BALLID),
                FOREIGN KEY (TABLEID) REFERENCES TTable(TABLEID)
            );
        ''')

        #  Creates shot table 
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Shot (
                SHOTID INTEGER PRIMARY KEY AUTOINCREMENT,
                PLAYERID INTEGER NOT NULL,
                GAMEID INTEGER NOT NULL,
                FOREIGN KEY (PLAYERID) REFERENCES Player(PLAYERID),
                FOREIGN KEY (GAMEID) REFERENCES Game(GAMEID)  
            );
        ''')

        # Creates tableShot table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS TableShot (
                TABLEID INTEGER NOT NULL,
                SHOTID INTEGER NOT NULL,
                FOREIGN KEY (TABLEID) REFERENCES TTable(TABLEID),
                FOREIGN KEY (SHOTID) REFERENCES Shot(SHOTID)
            );
        ''')

        # Creates Game table 
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Game (
                GAMEID INTEGER PRIMARY KEY AUTOINCREMENT,
                GAMENAME VARCHAR(64) NOT NULL
            );
        ''')

        # Creates Player table 
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Player (
                PLAYERID INTEGER PRIMARY KEY AUTOINCREMENT,
                GAMEID INTEGER NOT NULL,
                PLAYERNAME VARCHAR(64) NOT NULL,
                FOREIGN KEY (GAMEID) REFERENCES Game(GAMEID)
            );
        ''')

        # Message to commit the changes
        self.conn.commit()

    def readTable( self, tableID ):

        """
        This method takes the tableId and extarcts the table from it
        """

        # Used try catch block to prevent errors
        try:
            #Created a new table 
            table = Table()

            # Extracted the time 
            self.cursor.execute('''
                SELECT TIME FROM TTable
                WHERE TTable.TABLEID = ?;
            ''', (tableID + 1,))

            time_returned = self.cursor.fetchall()

            if not time_returned:
                print(f"No data found for TABLEID: {tableID}")
                return None

            time = time_returned[0][0]

            # Set up the time of the table based on data in database 
            table.time = time

            # Extracted the data for table from the database
            self.cursor.execute('''
                SELECT Ball.BALLID, Ball.BALLNO, Ball.XPOS, Ball.YPOS, Ball.XVEL, Ball.YVEL FROM Ball
                INNER JOIN BallTable ON Ball.BALLID = BallTable.BALLID
                WHERE BallTable.TABLEID = ?;
            ''', (tableID + 1,))

            rows = self.cursor.fetchall()

            if not rows:
                print(f"No data found for TABLEID: {tableID}")
                return None

            for row in rows:
                # Created a loop to add each row/ball to the table 
                if len(row) != 6:
                    print(f"Unexpected number of columns in the row: {len(row)}")
                    continue

                # Stored in temp values
                ball_id, ball_number, xpos, ypos, xvel, yvel = row
                pos = Coordinate(xpos, ypos)

                # Condition to check if it is a still ball
                if xvel is None and yvel is None:
                    # Instantiate as StillBall
                    ball = StillBall(ball_number, pos)
                else:
                    # Instantiate as RollingBall with velocity and acceleration
                    vel = Coordinate(xvel, yvel)
                    acc = Coordinate(0.0, 0.0)  
                    ball = RollingBall(ball_number, pos, vel, acc)

                # Added the ball to the table
                table += ball
            
            self.conn.commit()

            return table

        except sqlite3.Error as e:
            print(f"Error reading table: {e}")
            raise

    def writeTable(self, table):

        """
        This method writes the table into the database
        """

        try:
            # Inserted the time into the database
            self.cursor.execute('''
                INSERT INTO TTable (TIME) VALUES (?);
            ''', (table.time,))

            # stored table id in temp variable 
            table_id = self.cursor.lastrowid - 1

            # Used for loop to check the balls and set up their values
            for obj in table:
                if isinstance(obj, StillBall):
                    ball_number = obj.obj.still_ball.number
                    x_pos = obj.obj.still_ball.pos.x
                    y_pos = obj.obj.still_ball.pos.y
                    x_vel = None
                    y_vel = None
                elif isinstance(obj, RollingBall):
                    ball_number = obj.obj.rolling_ball.number
                    x_pos = obj.obj.rolling_ball.pos.x
                    y_pos = obj.obj.rolling_ball.pos.y
                    x_vel = obj.obj.rolling_ball.vel.x
                    y_vel = obj.obj.rolling_ball.vel.y

                else:
                    continue
            
                #  Inserted the values into the table 
                self.cursor.execute('''
                    INSERT INTO Ball (BALLNO, XPOS, YPOS, XVEL, YVEL) VALUES (?, ?, ?, ?, ?);
                ''', (ball_number, x_pos, y_pos, x_vel, y_vel))

                # Stored bal id in temp variable 
                ball_id = self.cursor.lastrowid

                # Inserted data into BallTable
                self.cursor.execute('''
                    INSERT INTO BallTable (BALLID, TABLEID) VALUES (?, ?);
                ''', (ball_id, table_id + 1))

            self.conn.commit()
            return table_id

        except sqlite3.Error as e:
            print(f"Error writing table: {e}")
            return None


    def getGame(self,GameID):

        """
        This method returns the game name and player names if only game id is given
        """

        try:
            # extracted the game name and player names from database
            self.cursor.execute('''
                SELECT Game.GAMENAME, Player1.PLAYERNAME, Player2.PLAYERNAME
                FROM Game
                INNER JOIN Player AS Player1 ON Game.PLAYER1ID = Player1.PLAYERID
                INNER JOIN Player AS Player2 ON Game.PLAYER2ID = Player2.PLAYERID
                WHERE Game.GAMEID = ?;
            ''', (GameID + 1,))
        
            result = self.cursor.fetchone()

            # returned the result to Game 
            if result:
                self.gameName, self.player1Name, self.player2Name = result
                return result
            
            else:
                raise ValueError(f"No data found for gameID: {GameID}")

        except sqlite3.Error as e:
            print(f"Error retrieving data: {e}")
            raise

    def setGame(self, gameName, player1Name, player2Name):

        """
        This method adds the gamename and the player names to the database
        """

        try:
            # Insert gamename and ID into Game Table
            self.cursor.execute('''
                INSERT INTO Game (GAMENAME) VALUES (?)
            ''', ( gameName,))

            gameID = self.cursor.lastrowid

            # Insert player1Name 
            self.cursor.execute('''
                INSERT INTO Player (PLAYERNAME, GAMEID) VALUES (?,?);
            ''', (player1Name,gameID,))
            player1ID = self.cursor.lastrowid

            # Insert player2Name 
            self.cursor.execute('''
                INSERT INTO Player (PLAYERNAME, GAMEID) VALUES (?, ?);
            ''', (player2Name,gameID,))
            player2ID = self.cursor.lastrowid
            
            # Commit the changes 
            self.conn.commit()

        except sqlite3.Error as e:
            print(f"Error setting up the game: {e}")
            raise

    def newShot(self, gameName, playerName, xvel, yvel):

        """
        This method returns shot id
        """
        try:
            # Retrieve playerID based on playerName
            self.cursor.execute('''
                SELECT PLAYERID FROM Player WHERE PLAYERNAME = ?;
            ''', (playerName,))
            playerID = self.cursor.fetchone()

            if playerID is None:
                raise ValueError(f"Player not found: {playerName}")

            # Extract value from the tuple 
            playerID = playerID[0]

            # Retrieve gameID based on gameName
            self.cursor.execute('''
                SELECT GAMEID FROM Game WHERE GAMENAME = ?;
            ''', (gameName,))
            gameID = self.cursor.fetchone()

            if gameID is None:
                raise ValueError(f"Game not found: {gameName}")

            # Extract value from the tuple 
            gameID = gameID[0]

            # Insert the new shot into the Shot table
            self.cursor.execute('''
                INSERT INTO Shot (GAMEID, PLAYERID) VALUES (?, ?);
            ''', (gameID, playerID,))

            shotID = self.cursor.lastrowid

            self.conn.commit()

            # Returned the shotID
            return shotID

        except sqlite3.Error as e:
            print(f"Error adding new shot: {e}")
            raise

    def insertShot(self, tableID , shotID):
        """
        This method adds the tableID and shotID to the table shot
        """
        self.cursor.execute('''
            INSERT INTO TableShot(TABLEID,SHOTID) VALUES (?,?);
        ''', (tableID, shotID))

        self.conn.commit()

    def updatePlayerNames(self, newP1, newP2, gameName):
        
        """
        This method updates the player names in the database.
        """
        try:
            # Update player1Name
            self.cursor.execute('''
                UPDATE Player 
                SET PLAYERNAME = ?
                WHERE PLAYERNAME = ?;
            ''', (newP1, 'defaultName1'))

            # Update player2Name
            self.cursor.execute('''
                UPDATE Player 
                SET PLAYERNAME = ?
                WHERE PLAYERNAME = ?;
            ''', (newP2, 'defaultName2'))

            self.cursor.execute('''
                UPDATE Game 
                SET GAMENAME = ?
                WHERE GAMENAME = ?;
            ''', (gameName, 'Game 01'))

            # Commit the changes
            print("names updated")
            self.conn.commit()

        except sqlite3.Error as e:
            print(f"Error updating player names: {e}")
            raise

    def getLastTableID(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT MAX(TABLEID) FROM TTable")
        last_table_id = cursor.fetchone()[0]
        return last_table_id


    def close(self):
        """
        This method closes the database 
        """
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

################################################################################

class Game():

    def __init__( self, gameID=None, gameName=None, player1Name=None, player2Name=None ):

        """
        This constructor sets up the game for us. 
        """

        # Created database 
        self.db = Database(reset = True)
        self.db.createDB()
        
        # Any other combination of arguments  shall raise a TypeError Python Exception.
        if gameID is not None and (gameName is not None or player1Name is not None or player2Name is not None):
            raise TypeError("Invalid combination of arguments.")
        

        # If only gameID ia given
        if gameID is not None and gameName is None and player1Name is None and player2Name is None:
            result  = self.db.getGame(gameID)
            self.gameName , self.player1Name , self.player2Name  = result
            
        # if all other values except the gameID are given
        if gameID is None and gameName is not None and player1Name is not None and player2Name is not None:
            self.db.setGame(gameName, player1Name, player2Name)
            
    def shoot(self, gameName, playerName, table, xvel, yvel):
        """
        This method takes the tableId and extracts the table from it
        """
        # Called the newShot
        shotID = self.db.newShot(gameName, playerName, xvel, yvel)

        cueBall = table.cueBall(table, xvel, yvel)
        cueBall.type = phylib.PHYLIB_ROLLING_BALL

        # Temporary storage of position
        posx = cueBall.obj.rolling_ball.pos.x
        posy = cueBall.obj.rolling_ball.pos.y

        # Temporary storage of velocity 
        velx = xvel
        vely = yvel               

        # Updated velocities 
        cueBall.obj.rolling_ball.vel.x = velx
        cueBall.obj.rolling_ball.vel.y = vely

        # calculation of speed
        ball_vel = Coordinate(velx, vely)
        speed = phylib.phylib_length(ball_vel)

        acc_x = 0.0
        acc_y = 0.0

        # Checked if ball has non-zero speed
        if speed > VEL_EPSILON:
            acc_x = -(velx / speed) * DRAG
            acc_y = -(vely / speed) * DRAG
        
        # Updated acceleration
        cueBall.obj.rolling_ball.acc.x = acc_x
        cueBall.obj.rolling_ball.acc.y = acc_y

        # While all balls are rolling 
        while table is not None:
            # Stored starting time
            startTime = table.time
            # Stored table in a temp variable
            newTable = table
            # Called segment on the table 
            table = table.segment()
            # Extracted the end time 
            if table is not None:
                endTime = table.time
            # Calculated time difference 
            timeDifference = endTime - startTime
            # More calculation for the loop
            loopVal = int(timeDifference / FRAME_RATE)

            # Went inside the loop for every integer value 
            for i in range(loopVal):
                # Calculated newTime
                newTime = FRAME_RATE * i
                # Called roll method and set up time 
                tableCopy = newTable.roll(newTime)
                tableCopy.time = newTime + startTime
                # Put the table into the database
                newTableID = self.db.writeTable(tableCopy)

                # Inserted the shot into the database
                self.db.insertShot(newTableID, shotID)
                
        return shotID

    def update(self, newP1, newP2, gameName):

        print("calling update palyers")
        # calls the updatePlayers which updates the player names in database
        self.db.updatePlayerNames(newP1,newP2, gameName)

