import sys; 
import os;
import json
import glob;
import cgi; 
import math;
import random;
import Physics;

from http.server import HTTPServer, BaseHTTPRequestHandler;

from urllib.parse import urlparse, parse_qsl;


# handle get and post 
class MyHandler( BaseHTTPRequestHandler ):

    def do_GET(self):
        # parse the URL 
        parsed  = urlparse( self.path );

        # checks if the web-page has matched
        if parsed.path in [ '/index.html' ]:

            # retreived the HTML file from the server 
            fp = open( '.'+self.path );
            content = fp.read();

            # headers
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/html" );
            self.send_header( "Content-length", len( content ) );
            self.end_headers();

            # send it back
            self.wfile.write( bytes( content, "utf-8" ) );
            fp.close();

        elif parsed.path.endswith('.svg') and parsed.path.startswith('/table-'):
            # Dynamically handling SVG files
            try:
                # Open the file in binary mode
                with open('.' + parsed.path, 'rb') as fp:
                    content = fp.read()
                # send success response
                self.send_response(200)
                self.send_header("Content-type", "image/svg+xml")  
                self.send_header("Content-length", len(content))
                self.end_headers()
                self.wfile.write(content)

            except IOError:
                # return 404 if ile is not found 
                self.send_response(404)
                self.end_headers()
                self.wfile.write(bytes("404: File not found %s" % parsed.path, "utf-8"))

        else:
            self.send_response( 404 );
            self.end_headers();
            self.wfile.write( bytes( "404: %s not found" % self.path, "utf-8" ) );

    def do_POST(self):

        # Default player names
        p1 = "defaultName1" 
        p2 = "defaultName2"
        # Created and saved the tables
        table = createFirstTable()
        # Created the game instance
        game = Physics.Game(gameName="Game 01", player1Name=p1, player2Name=p2) 
        db = Physics.Database()

        # check if we received names from the server
        if self.path == "/handle_names":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # Extracted player names when available
            p1 = data.get('player1')
            p2 = data.get('player2')

            # Updated player names of the existing game object
            if p1 is not None and p2 is not None:
                print("Player 1:", p1)
                print("Player 2:", p2)

                # updated the player names in the database
                game.update(p1,p2)

                # Send success response 
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(bytes("Received player names successfully!", "utf-8"))

        # to handle the drag event
        elif self.path == "/handle_mouse_position":

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # take the velocities
            vx = data.get('vx')
            vy = data.get('vy')


            if vx is not None and vy is not None:
                print("vx:", vx)
                print("vy:", vy)


                # to get the final table id
                tableID = db.getLastTableID() or 0

                # call shoot with the received velocites
                game.shoot("Game 01", p1, table, vx, vy)

                #  created a svg container for the svgs 
                svgs = []
                table = db.readTable(tableID)

                # creating svgs 
                while table is not None:
                    svgdata = table.svg()
                    svgs.append(svgdata)     
                    tableID += 1
                    table = db.readTable(tableID)

                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                # sending svgs to the server 
                response_json = json.dumps(svgs)
                self.wfile.write(response_json.encode('utf-8'))

        else:
            # generate 404 response
            print("Invalid path:", self.path)
            self.send_response(400)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(bytes("Invalid path: " + self.path, "utf-8"))


def saveTable():
    # Generate the table
    table = createFirstTable()

def createFirstTable():
    table = Physics.Table()

    # Define the positions of the balls 
    ball_positions = [
        (675, 2025),  
        (675, 675),   
        (615, 630),   
        (735, 630),
        (555, 585),  
        (675, 585),
        (795, 585),
        (495, 540),  
        (615, 540),
        (735, 540),
        (855, 540)
    ]

    for ball_id, (x, y) in enumerate(ball_positions, start=0):
        pos = Physics.Coordinate(x, y)
        sb = Physics.StillBall(ball_id, pos)
        table += sb

    return table

# to create some distance bt the balls on the table
def nudgeElements():
    return random.uniform( -1.5, 1.5 );


if __name__ == "__main__":
    saveTable()
    httpd = HTTPServer( ( 'localhost', int(sys.argv[1]) ), MyHandler );
    print( "Server listing in port:  ", int(sys.argv[1]) );
    httpd.serve_forever();