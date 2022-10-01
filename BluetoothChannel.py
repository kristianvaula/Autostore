import sys
import paramiko  # SSH library
import time


class RobotChannel:
    # Initialized variables for this connection
    robot_name = ""
    job_text = ""
    job_ID = -1

    # Constructor for setting up a new connection to a robot.
    def __init__(self, file, server, host="ev3dev", port=22, username="robot", password="maker"):
        self.command = "brickrun -r ./" + file
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.server = server
        self.robot_name = server.send_name()
        server.print("robot assigned name: " + self.robot_name)
        self.ssh_client = paramiko.client.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())

    # Try to connect to robot and mediate talk between robot and server.
    def run(self):
        server = self.server
        server.print("robot_com for " + self.robot_name + " started")
        loop = True
        # Retry periodically if connection fails
        while loop:
            try:
                # Connect to robot over SSH
                print("attempting to connect to robot: ", self.robot_name)
                self.ssh_client.connect(self.host, self.port, self.username, self.password)
                channel = self.ssh_client.get_transport().open_session()
                # Tell SSH session to also return program console output.
                channel.get_pty()
                # Start python script on robot.
                channel.exec_command(self.command)
                print("robot: ", self.robot_name, "connected")
                # Continues to loop as long as connection is maintained.
                while loop:
                    # Get data from robot.
                    data = channel.recv(1024)
                    if not data:
                        server.lost_robot_connection(self.robot_name)
                        break
                    text: str = data.decode()
                    # Get potential <tag> from data.
                    tag_start = text.find("<")
                    tag_end = text.find(">")
                    if tag_start != -1:
                        tag = text[tag_start+1: tag_end]
                    else:
                        tag = ""
                    # Activate different server method depending on <tag>
                    # Potentially pass rest of data to server depending on method call.
                    if tag == "getJob":
                        # Get job from server, unpack and send job to robot. Keep jobID.
                        wait_for_job = True
                        while wait_for_job:
                            job_package = server.send_job(self.robot_name).split("-")
                            if len(job_package) > 1:
                                self.job_ID = job_package[0]
                                self.job_text = job_package[1]
                            else:
                                self.job_text = job_package[0]
                            if self.job_text == "noJob":
                                time.sleep(5)
                            else:
                                server.write_log("sending job text: " + self.job_text)
                                channel.send((self.job_text + "\n").encode())
                                wait_for_job = False
                    elif tag == "log":
                        # Sends text to the server to be added to the log file.
                        server.write_log(text)
                    else:
                        # Directly print whatever the robot said.
                        sys.stdout.write("robot: " + self.robot_name + " says:" + text)
            except:
                server.no_robot_connection(self.robot_name)
                time.sleep(10)
