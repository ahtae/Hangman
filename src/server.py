from socket import *
from sys import argv
from random import *
from game import *
import time
import codecs

def main():
  # Parse command line args
  if len(argv) != 2:
    print("usage: python3 server.py <word to guess or '-r' for random word>")
    return 1
  
  print("Server is running...")

  # Create the TCP Socket
  serverSocket = socket(AF_INET, SOCK_STREAM) 
  print("Creating TCP socket...")

  # Bind a port to the TCP socket, letting the OS choose the port number
  # The port number will be a command-line parameter to the client program
  serverSocket.bind(('localhost', 0))

  # Get the port number of the socket from the OS and print it
  # The port number will be a command-line parameter to the client program
  serverPort = serverSocket.getsockname()[1]
  print("Server is listening on port:", serverPort)
    
  # Configure the TCP socket (using listen) to accept a connection request
  serverSocket.listen(1) 
  print("Press Ctrl-C to quit.")
  try: # try/except to catch ctrl-c
    while True:
      # Accept the TCP Connection
      connection, address =  serverSocket.accept() 
      print("Waiting for a client...")
      print("A new client is connected to the server!")
    
      # TCP loop
      while True:
        # Continuously Read in from TCP port
        d = connection.recv(2048) 
        data = d.decode('utf-8')
        data = data.lower()
        data = ''.join(data.split())

        # Keep listening if it doesn't receive a hello message
        if(data[:5] != "hello"):
          serverSocket.listen(1)
        elif(data[:5] == "hello" and len(data) > 5):
            print("User's name: " + data[5:].capitalize())
        # Extract username handling empty case
        elif(data[5:] == ""):
            connection.send(codecs.encode("Please re-enter your name: ", encoding='utf-8'))

        # Create and bind a UDP socket, letting the OS choose the port number
        print("Creating UDP socket...")
        UDPserverSocket = socket(AF_INET, SOCK_DGRAM) 
        UDPserverSocket.bind(('localhost', 0))
        
        # Add a timeout to the UDP socket so that it stops listening
        UDPserverSocket.settimeout(120)
        # after 2 minutes of inactivity

        # Get the port number assigned by the OS and print to console
        UDPserverPort = UDPserverSocket.getsockname()[1]
        print("UDP socket has port number: ", UDPserverPort)

        # Put the UDP port number in a message and send it to the client using TCP
        print("Sending UDP port number to client using TCP connection...")
        message = "Received UDP port#: " + str(UDPserverPort)
        connection.send(codecs.encode(message, encoding='utf-8'))

        # Break from loop once needed info is received
        break

      # game not active by default
      active = False

      # Game (UDP) loop
      while True:
        try:
          # receive on UDP port here
          d, addr = UDPserverSocket.recvfrom(2048)
      
        # catch UDP timeout
        except timeout:
          print("Ending game due to timeout...")
          # break and wait to accept another client
          break
        
        # if ...:
        if(d.decode('utf-8') == 'ready'):
          # Game setup
          # active = True
          active = True
          # word, word_blanks, attempts, win = gameSetup(argv)
          word, word_blanks, attempts, win = gameSetup(argv)
          # print("Hidden Word: {}".format(word))
          print("Hidden Word: {}".format(word))
          # print("Starting game...")
          print("Starting game...")
          # Send inst then stat messages
          beginning = "Sending message: stat Word: " + word_blanks + " Attempts left: " + str(attempts)
          print(beginning)
          UDPserverSocket.sendto(codecs.encode("instr" + INSTRUCTIONS + beginning[21:], encoding='utf-8'), addr)
        elif(d.decode('utf-8')[:5] == 'guess' and active):
          guess = d.decode('utf-8')[5:]
          guess = guess.strip()
          sguess = "Guess is " + guess
          print(sguess)
          # if len(guess) > 1 and not win or attempts == 0 or win:
          if(len(guess) > 1 and not win or attempts == 0 or win):
            guess_word = checkGuess(word, word_blanks, attempts, guess, win)
            word_blanks, attempts, win = guess_word
            guess_word = str(guess_word)
            UDPserverSocket.sendto(codecs.encode(guess_word, encoding='utf-8'), addr)
            beginning = "Sending message: stat Word: " + word_blanks + " Attempts left: " + str(attempts)
            print(beginning)
            active = False
            if(win == 1):
                win_message = "Sending message: end You win! Word was " + word + "."
                UDPserverSocket.sendto(codecs.encode(win_message[21:] , encoding='utf-8'), addr)
            elif(win == 0):
                win_message = "Sending message: end You lose! Word was " + word + "."
                UDPserverSocket.sendto(codecs.encode(win_message[21:] , encoding='utf-8'), addr)
          else:
            guess_word = checkGuess(word, word_blanks, attempts, guess, win)
            word_blanks, attempts, win = guess_word
            status = "Word: " + str(word_blanks) + " Attempts left: " + str(attempts)
            UDPserverSocket.sendto(codecs.encode(str(status), encoding='utf-8'), addr)
            beginning = "Sending message: stat Word: " + word_blanks + " Attempts left: " + str(attempts)
            print(beginning)
            if(win == 1 and attempts == 0):
                win_message = "Sending message: end You win! Word was " + word + "."
                UDPserverSocket.sendto(codecs.encode(win_message[21:] , encoding='utf-8'), addr)
            elif(win == 0 and attempts == 0):
                win_message = "Sending message: end You lose! Word was " + word + "."
                UDPserverSocket.sendto(codecs.encode(win_message[21:] , encoding='utf-8'), addr)
        elif(d.decode('utf-8') == 'end'):
          UDPserverSocket.sendto(codecs.encode('end', encoding='utf-8'), addr)
        elif(d.decode('utf-8') == 'bye'):
          UDPserverSocket.sendto(codecs.encode('bye', encoding='utf-8'), addr)
          UDPserverSocket.close()
          serverSocket.close()
        elif((d.decode('utf-8') != 'end' or d.decode('utf-8') != 'bye' or d.decode('utf-8') != 'ready' or d.decode('utf-8') != 'guess') or ((active) and d.decode('utf-8') == 'guess')):
            UDPserverSocket.sendto(codecs.encode('na', encoding='utf-8'), addr)
      break
      # end of UDP Game loop
      UDPserverSocket.close()
      # close the TCP socket the client was using as well as the udp socket.
    # end of TCP loop
    serverSocket.close()

  except KeyboardInterrupt:
      print('\nDone.')
      # Close sockets
      UDPserverSocket.close()
      serverSocket.close()
      print("Closing TCP and UDP sockets...")

###########################################

if __name__ == "__main__":
  main()
