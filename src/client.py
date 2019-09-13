from socket import *
from sys import argv
import codecs

def main():
  # Parse command line args
  if len(argv) != 3 or not argv[2].isdigit():
    print("usage: python3 client.py <server name> <server port>")
    return 1
  
  hostname, serverTCPPort = argv[1], int(argv[2])
  print("Client is running...")
  print("Remote host: {}, remote TCP port: {}".format(hostname, serverTCPPort))

  # Prompt user for their name
  name = input("Please enter your lovely name: ")

  # Create TCP socket
  clientSocket = socket(AF_INET, SOCK_STREAM)

  # Get IP address of server via DNS and print it(optional)
  host_ip = gethostbyname(hostname)
  print("The server address is ", host_ip)

  # Connect to the server program
  clientSocket.connect((hostname, serverTCPPort))

  # Send hello message to the server over TCP connection
  message = "hello " + name.capitalize()
  clientSocket.send(codecs.encode(message, encoding='utf-8'))

  # TCP Loop
  while True:
    # Read in from TCP port
    d = clientSocket.recv(1024)
    data = d.decode('utf-8')
    
    # Keep listening if it doesn't receive a portUDP message
    while(not data.startswith("Received UDP port#: ")):
      continue

    # Read the control message from the TCP socket and print its contents
    print(data)
    # Break from loop once needed info is received
    break

  clientUDPPort = int(data[20:])
#  print("gameport <" + str(serverUDPPort) + ">")
 # print("ready")

  # Create a UDP socket
  clientUDPSocket = socket(AF_INET, SOCK_DGRAM)

  end = False # default end flag

  # Game loop
  while True:
    command = input("> Enter a command (start, end, guess, exit): ") # Prompt
    valid_commands = ['start', 'end', 'guess', 'exit']

    command = command.lower()
    command = ''.join(command.split())
    
    if(command == valid_commands[0]):
      clientUDPSocket.sendto(codecs.encode('ready', encoding='utf-8'), ('localhost', clientUDPPort))
    elif(command == valid_commands[1]):
      clientUDPSocket.sendto(codecs.encode('end', encoding='utf-8'), ('localhost', clientUDPPort))
    elif(command[:5] == valid_commands[2]):
      clientUDPSocket.sendto(codecs.encode(command, encoding='utf-8'), ('localhost', clientUDPPort))
    elif(command == valid_commands[3]):
      clientUDPSocket.sendto(codecs.encode('bye', encoding='utf-8'), ('localhost', clientUDPPort))
      clientUDPSocket.close()

    # UDP loop
    while True:
      # Continuously Read in from UDP port
      message, serverAddress = clientUDPSocket.recvfrom(2048)
      msg = message.decode('utf-8')

      valid_msg_types = ["instr", "stat", "end", "na", "bye"]

      # print message
      # Instruction message should be followed by stat message
      print(msg)
      
      if(msg.lower() == "gameport"):
        UDPPort = msg[9:]
        UDPPort = UDPPort.split()
        UDPPort = int(UDPPort)
        recom = input("> Enter a command (start, end, guess, exit): ")
        clientUDPSocket.sendto(codecs.encode(recom, encoding='utf-8'), ('localhost', clientUDPPort))
      elif(msg == valid_msg_types[0]):
        print(valid_msg_types[0])
      elif(msg == valid_msg_types[1]):
        recom = input("> Enter a command (start, end, guess, exit): ")
        clientUDPSocket.sendto(codecs.encode(recom, encoding='utf-8'), ('localhost', clientUDPPort))
      elif(msg == valid_msg_types[2]):
        recom = input("> Enter a command (start, end, guess, exit): ")
        clientUDPSocket.sendto(codecs.encode(recom, encoding='utf-8'), ('localhost', clientUDPPort))
      elif(msg == valid_msg_types[3]):
        recom = input("> Enter a command (start, end, guess, exit): ")
        clientUDPSocket.sendto(codecs.encode(recom, encoding='utf-8'), ('localhost', clientUDPPort))
      elif(msg == valid_msg_types[4]):
        break
      # Break once receiving info and reprompt user
      break
    #end of UDP loop

    # If end message received, end client process
    if end:
      break
  #end of Game loop

  # Close sockets
  clientUDPSocket.close()
  clientSocket.close()
  print("Closing TCP and UDP sockets...")

 ###########################################

if __name__ == "__main__":
  main()
