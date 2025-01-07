# used to get argv
import sys;
# used to parse Mutlipart FormData 
import cgi; 
import os;  
import glob;
import Physics;
import math;

# imported the servers
from http.server import HTTPServer, BaseHTTPRequestHandler;
# used to parse the URL 
from urllib.parse import urlparse, parse_qsl;

# created a handler for the GET and POST requests
class MyHandler( BaseHTTPRequestHandler ):

    # Get method to handle the get requests 
    def do_GET(self):
        # to get path and form data I have parsed the URL
        parsed  = urlparse( self.path );
        # if the web-pages has matched the list
        if parsed.path in [ '/shoot.html' ]:

            # retreived HTML file
            fp = open( '.'+self.path );
            content = fp.read();

            # headers
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/html" );
            self.send_header( "Content-length", len( content ) );
            self.end_headers();

            # sending to the browser
            self.wfile.write( bytes( content, "utf-8" ) );
            fp.close();

        elif parsed.path.startswith('/table-') and parsed.path.endswith('.svg'): 
            # handling svg files dynamically
            try:
                #opening file in binary mode
                with open('.' + parsed.path, 'rb') as fp: 
                    content = fp.read()
                    self.send_response(200)
                # generate headers
                self.send_header("Content-type", "image/svg+xml")  
                self.send_header("Content-length", len(content))
                self.end_headers()
                self.wfile.write(content)

            except IOError:
                # File not found error returning 404
                self.send_response(404)
                self.end_headers()
                self.wfile.write(bytes("404: File not found %s" % parsed.path, "utf-8"))

        # checked if the pages match
        else:
            # generated 404
            self.send_response( 404 );
            self.end_headers();
            self.wfile.write( bytes( "404: %s not found" % self.path, "utf-8" ) );

    # Post method to handle post requests
    def do_POST(self):
        # parsed URL to get data 
        parsed  = urlparse( self.path );

        if parsed.path in [ '/display.html' ]:
            # this will get the data 
            form = cgi.FieldStorage( fp=self.rfile, 
                                    headers=self.headers, 
                                    environ = {'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type'],} );

            # Deleted all the svg files
            for svg_file in glob.glob('table-*.svg'):
                os.remove(svg_file)

            # Compute the relative position vector between a and b      
            delta_x = float(form['rb_x'].value) - float(form['sb_x'].value)
            delta_y = float(form['rb_y'].value) - float(form['sb_y'].value)
            relative_position = Physics.Coordinate(delta_x, delta_y)

            # Calculate the rolling ball velocity vector
            rb_velocity_x = float(form['rb_dx'].value)
            rb_velocity_y = float(form['rb_dy'].value)
            rolling_ball_velocity = Physics.Coordinate(rb_velocity_x, rb_velocity_y)

            # Calculate the length of the relative position vector
            relative_position_length_squared = (delta_x * delta_x) + (delta_y * delta_y)
            if relative_position_length_squared > 0.0:
                relative_position_length = math.sqrt(relative_position_length_squared)

            # Check if relative_position_length is not zero to avoid division by zero
            if relative_position_length > 0.0:
                normalized_x = delta_x / relative_position_length
                normalized_y = delta_y / relative_position_length
            
            normalized_vector = Physics.Coordinate(normalized_x, normalized_y)

            # Calculate the dot product of the relative velocity and the normalized vector
            relative_velocity_dot_normalized = (rolling_ball_velocity.x * normalized_x) + (rolling_ball_velocity.y * normalized_y)

            # Update the velocity based on collision
            rolling_ball_velocity.x -= relative_velocity_dot_normalized * normalized_x
            rolling_ball_velocity.y -= relative_velocity_dot_normalized * normalized_y

            # Calculate the bounce velocity vector
            bounce_velocity_x = relative_velocity_dot_normalized * normalized_x
            bounce_velocity_y = relative_velocity_dot_normalized * normalized_y
            bounce_velocity = Physics.Coordinate(bounce_velocity_x, bounce_velocity_y)

            # Calculate the speed of a and b
            speed_a = math.sqrt((rolling_ball_velocity.x * rolling_ball_velocity.x) + (rolling_ball_velocity.y * rolling_ball_velocity.y)) 
            speed_b = math.sqrt((bounce_velocity.x * bounce_velocity.x) * (bounce_velocity.y * bounce_velocity.y))

            # Condition if speed greater than VEL_EPSILON
            if speed_a > Physics.VEL_EPSILON:
                acceleration_a_x = -(rolling_ball_velocity.x / speed_a) * 150
                acceleration_a_y = -(rolling_ball_velocity.y / speed_a) * 150
                acceleration_a = Physics.Coordinate(acceleration_a_x, acceleration_a_y)

            if speed_b > Physics.VEL_EPSILON:
                acceleration_b_x = -(bounce_velocity.x / speed_b) * 150
                acceleration_b_y = -(bounce_velocity.y / speed_b) * 150
                acceleration_b = Physics.Coordinate(acceleration_b_x, acceleration_b_y)
                
            # Create a table
            file_index = 0
            table = Physics.Table()    

            # Calculate still ball position
            still_ball_num = int(form['sb_number'].value); 
            still_ball_pos_x = float(form['sb_x'].value)
            still_ball_pos_y = float(form['sb_y'].value)
            still_ball_pos = Physics.Coordinate(still_ball_pos_x, still_ball_pos_y)

            # Store the still ball
            still_ball = Physics.StillBall(still_ball_num, still_ball_pos)

            # Calculations for the rolling ball
            rolling_ball_pos_x = float(form['rb_x'].value)
            rolling_ball_pos_y = float(form['rb_y'].value)
            rolling_ball_pos = Physics.Coordinate(rolling_ball_pos_x, rolling_ball_pos_y)
            rolling_ball_vel_x = float(form['rb_dx'].value)
            rolling_ball_vel_y = float(form['rb_dy'].value)
            rolling_ball_vel = Physics.Coordinate(rolling_ball_vel_x, rolling_ball_vel_y)
            
            # Store the rolling ball
            rolling_ball_num = int(form['rb_number'].value); 
            rolling_ball = Physics.RollingBall(rolling_ball_num, rolling_ball_pos, rolling_ball_vel, acceleration_b)

            # Add both to the table 
            table += still_ball
            table += rolling_ball

            # Write the initial state of the table to an SVG file
            write_svg(table, file_index)
            file_index += 1

            while table is not None:
                table = table.segment()
                if table:
                    write_svg(table, file_index)
                    file_index += 1
                else:
                    break
            
            # After SVG file generation
            svg_files = glob.glob('table-*.svg')

            # HTML file
            html_content = f"""
            <html>
            <head>
                <title>Billiards Ball Trajectories</title>
            </head>
            <body>
                <h1 style="font-family:-apple-system;">
                    <u>Original Ball Positions and Velocities<u>
                </h1>
                <h4 style="font-family:-apple-system;">
                    Still Ball Position: ({still_ball_pos_x}, {still_ball_pos_y})
                </h4>
                <h4 style="font-family:-apple-system;">
                    Rolling Ball Initial Position: ({rolling_ball_pos_x}, {rolling_ball_pos_y}), 
                    Velocity: ({rolling_ball_vel_x}, {rolling_ball_vel_y}), 
                    Acceleration: ({acceleration_a_x}, {acceleration_a_y})
                </h4>
                <h1 style="font-family:-apple-system;">
                    Simulation Results
                </h1 style="font-family:-apple-system;">
            """
            # Add image tags
            for svg_file in svg_files:
                html_content += f'<img src="{svg_file}" alt="Simulation Step"/><br>\n'
        
            html_content += '<h2 style="font-family:-apple-system;"> <a href="/shoot.html">Back</a></h2>\n'
            
            html_content += """
            </body>
            </html>
            """
        
            # generate the headers
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-length", len(html_content))
            self.end_headers()
            self.wfile.write(bytes(html_content, "utf-8"))

def write_svg(table, index):
    filename = f"table-{index}.svg"
    with open(filename, 'w') as file:
        file.write(table.svg())
    print(f"SVG written to {filename}")

if __name__ == "__main__":
    httpd = HTTPServer( ( 'localhost', int(sys.argv[1]) ), MyHandler );
    print( "Server listing in port:  ", int(sys.argv[1]) );
    httpd.serve_forever();
