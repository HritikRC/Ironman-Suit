import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
import os
import RPi.GPIO as GPIO
import time
import json
import psutil
from mpu6050 import mpu6050

mpu = mpu6050(0x68)

GPIO.setmode(GPIO.BOARD)

data = {"ultrasonic" : 0, "cpu" : 0, "temperature" : 0}

#Ultrasonic Sensor
trigger = 32
echo = 11
GPIO.setup(trigger, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)
GPIO.output(trigger, False)
GPIO.output(trigger, True)
time.sleep(0.00001)
GPIO.output(trigger, False)
starttime = 0
endtime = 0
while GPIO.input(echo) == 0:
    starttime = time.time()
while GPIO.input(echo) == 1:
    endtime = time.time()
duration = endtime - starttime
distance = duration * 17150
print("Distance : ", distance, "cm")
data["ultrasonic"] = distance

#LED
led1 = 7
led2 = 12
GPIO.setup(led1, GPIO.OUT)
GPIO.setup(led2, GPIO.OUT)
GPIO.output(led1, False)
GPIO.output(led2, False)
time.sleep(1)
GPIO.output(led1, True)
GPIO.output(led2, True)
time.sleep(2)
GPIO.output(led1, False)
GPIO.output(led2, False)

GPIO.cleanup()

#CPU
data["cpu"] = psutil.cpu_percent(0)
print("CPU : ", data["cpu"], "%")

#Data
file = open("data.json", "w")
file.write(json.dumps(data))
file.close()

PAGE="""\
<html>
	<head>
		<title>Ironman Helmet HUD</title>
		<style type="text/css">
			#img {
				position : absolute;
				top : 25%;
				left : 0px;
				transform : rotate(180deg);
			}
			#img2 {
				position : absolute;
				top : 25%;
				left : 50%;
				transform : rotate(180deg);
			}
			#hud {
				position : absolute;
				top : 25%;
				left : 0px;
			}
			#hud2 {
				position : absolute;
				top : 25%;
				left : 50%;
			}
			#time {
				position : absolute;
				color : white;
				font-size : 15;
				top : 27.2%;
				left : 22%;
			}
			#time2 {
				position : absolute;
				color : white;
				font-size : 15;
				top : 27.2%;
				left : 72%;
			}
			#cpu {
				position : absolute;
				color : blue;
				font-size : 23;
				top : 29%;
				left : 2%;
				transform : rotate(4deg);
			}
			#cpu2 {
				position : absolute;
				color : blue;
				font-size : 23;
				top : 29%;
				left : 52%;
				transform : rotate(4deg)
			}
			#temp {
				position : absolute;
				color : blue;
				font-size : 15;
				top : 29.7%;
				left : 36%;
				transform : rotate(356deg);
			}
			#temp2 {
				position : absolute;
				color : blue;
				font-size : 15;
				top : 29.7%;
				left : 86%;
				transform : rotate(356deg)
			}
                        body {
                          margin: 0;
                          background : black;
                        }
                        canvas {
                          position : absolute;
                          top : 25%;
                          left : 0px;
                        }
		</style>
	</head>
	<body>
	        <script src = "p5.min.js"></script>
	        <script src = "ml5.min.js"></script>
                    <img src="stream.mjpg" width="640" height="480" id = "img">
                    
                    <img src = "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/e10391ed-a9f8-453f-af78-86f2c2cfd4cf/d5f1cfy-212a2282-9c98-43fe-9ab6-17d34aae592d.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOiIsImlzcyI6InVybjphcHA6Iiwib2JqIjpbW3sicGF0aCI6IlwvZlwvZTEwMzkxZWQtYTlmOC00NTNmLWFmNzgtODZmMmMyY2ZkNGNmXC9kNWYxY2Z5LTIxMmEyMjgyLTljOTgtNDNmZS05YWI2LTE3ZDM0YWFlNTkyZC5wbmcifV1dLCJhdWQiOlsidXJuOnNlcnZpY2U6ZmlsZS5kb3dubG9hZCJdfQ.rADi8FDodvGgaPhtR4aQmUqi36sZJSu63kfPPCwnQGc" id = "hud">

                    <font id = "time" face = "Copperplate"></font>
                    
                    <img src="stream.mjpg" width="640" height="480" id = "img2">
                    
                    <img src = "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/e10391ed-a9f8-453f-af78-86f2c2cfd4cf/d5f1cfy-212a2282-9c98-43fe-9ab6-17d34aae592d.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOiIsImlzcyI6InVybjphcHA6Iiwib2JqIjpbW3sicGF0aCI6IlwvZlwvZTEwMzkxZWQtYTlmOC00NTNmLWFmNzgtODZmMmMyY2ZkNGNmXC9kNWYxY2Z5LTIxMmEyMjgyLTljOTgtNDNmZS05YWI2LTE3ZDM0YWFlNTkyZC5wbmcifV1dLCJhdWQiOlsidXJuOnNlcnZpY2U6ZmlsZS5kb3dubG9hZCJdfQ.rADi8FDodvGgaPhtR4aQmUqi36sZJSu63kfPPCwnQGc" id = "hud2">

                    <font id = "time2" face = "Copperplate"></font>

                    <font id = "cpu" face = "Lintel"></font>
                    <font id = "cpu2" face = "Lintel"></font>

                    <font id = "temp" face = "Lintel"></font>
                    <font id = "temp2" face = "Lintel"></font>
                		
    		<script type="text/javascript">
                        
			var preview = document.getElementById("img");
			var hud = document.getElementById("hud");
			var time = document.getElementById("time");
			var cpu = document.getElementById("cpu");
			var temp = document.getElementById("temp");
			var preview2 = document.getElementById("img2");
			var hud2 = document.getElementById("hud2");
			var cpu2 = document.getElementById("cpu2");
			var temp2 = document.getElementById("temp2");

			var sizeChangeSmoothness = 100;

			function update(){
				preview.width = window.innerWidth / 2;
				preview.height = window.innerHeight / 2;
				hud.width = window.innerWidth / 2;
				hud.height = window.innerHeight / 2;
				preview2.width = window.innerWidth / 2;
				preview2.height = window.innerHeight / 2;
				hud2.width = window.innerWidth / 2;
				hud2.height = window.innerHeight / 2;
			}
			update();

			function checkTime(i) {
				if (i < 10) {
			    	i = "0" + i;
			  	}
			  	return i;
			}

			function startTime() {
		  		var today = new Date();
		  		var h = today.getHours();
		  		var m = today.getMinutes();
		  		var s = today.getSeconds();
		  		// add a zero in front of numbers<10
		  		m = checkTime(m);
		  		s = checkTime(s);
		  		time.innerHTML = h + ":" + m + ":" + s;
		  		time2.innerHTML = h + ":" + m + ":" + s;
		  		t = setTimeout(function(){
		   	    	        startTime();
		  		}, 500);
			}
			startTime();

			window.addEventListener("resize", function(){
				update();
			});

                        // IMAGE DETECTION PART
                        let detector;
                        let detections = [];
                        function modelLoaded(){
                          console.log("Coco-SSD model loaded");
                          alert("Coco-SSD model loaded")
                        }
                        function preload() {
                          detector = ml5.objectDetector('cocossd', modelLoaded);
                        }

                        function gotDetections(error, results) {
                          if (error) {
                            console.error(error);
                          }
                          detections = results;
                        }
                        
                        function setup() {
                          createCanvas(preview.width * 2, preview.height);
                          detector.detect(preview, gotDetections);
                        }

                        function draw() {
                          clear();
                          for (let i = 0; i < detections.length; i++) {
                            let object = detections[i];
                            stroke(0, 0, 220);
                            strokeWeight(4);
                            noFill();
                            var x = width - (object.x + object.width);
                            var y = height - (object.y + object.height);
                            rect(x, y, object.width, object.height);
                            rect(x - preview.width, y, object.width, object.height);
                            
                            noStroke();
                            fill(255);
                            textSize(24);
                            text(object.label, x + 10, y + 24);
                            text(object.label, x + 10 - preview.width, y + 24);
                          }
                          if(frameCount % 120 == 0){
                            detector.detect(preview, gotDetections);
                          }
                        }

                        var data;
                        window.setInterval(function(){
                            var xhr = new XMLHttpRequest();
                            xhr.addEventListener("load", function(){
                              data = JSON.parse(xhr.responseText);
                            });
                            xhr.open("GET", "data.json", true)
                            xhr.send()
                            cpu.innerHTML = "CPU : " + data.cpu + "%";
                            cpu2.innerHTML = "CPU : " + data.cpu + "%";
                            temp.innerHTML = "Temperature : " + data.temperature.toFixed(2).toString();
                            temp2.innerHTML = "Temperature : " + data.temperature.toFixed(2).toString();
                        }, 2000);

		</script>
	</body>
</html>

"""    

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        # HTML and Javascript Files
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/p5.min.js":
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript")
            self.end_headers()
            f = open("p5.min.js", "rb")
            for line in f:
                self.wfile.write(line)
            return
        elif self.path == "/ml5.min.js":
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript")
            self.end_headers()
            f = open("ml5.min.js", "rb")
            for line in f:
                self.wfile.write(line)
            return
        elif self.path == "/data.json":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            f = open("data.json", "rb")
            for line in f:
                self.wfile.write(line)
            return
        # Motion JPEG Stream
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                count = 0
                while True:
                    count = count + 1
                    if count % 60 == 0:
                        data["cpu"] = psutil.cpu_percent(0)
                        data["temperature"] = mpu.get_temp()
                        file = open("data.json", "w")
                        file.write(json.dumps(data))
                        file.close()
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()
            

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='640x480', framerate=30) as camera:
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()
