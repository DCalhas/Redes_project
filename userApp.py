#!bin/usr/python

#Client

import socket
import sys
import os

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if (len(sys.argv) == 3):
  if (sys.argv[1] == "-n"):
    host = sys.argv[2]
    port = 58052
  elif (sys.argv[1] == "-p"):
    port = sys.argv[2]
    host = "localhost"

elif (len(sys.argv) == 5):
  if (sys.argv[1] == "-n"):
    host = sys.argv[2]
    if(sys.argv[3] == "-p"):
      port = sys.argv[4]
  elif (sys.argv[1] == "-p"):
    port = sys.argv[2]
    if(sys.argv[3] == "-n"):
      host = sys.argv[4]

else:
  host = socket.gethostname()
  port = 58052

address = (host, port)

print(address)

while(1):
  command = raw_input("Command: ")
  
  if (command == "list"):
    msg = "ULQ\n"

    s.sendto(msg, address)

    d = s.recvfrom(1024)
    reply = d[0]
    addr = d[1]

    rep = reply.split(" ")

    if ( rep[1] == "EOF\n" ): #caso nao haja linguagens disponiveis
      print "No languages available"
    else:
      for i in range(eval(rep[1])):
        print str(i+1) + " - " + rep[i+2]
        
      languages = rep[2:-1] + [rep[-1][:-1]]

  if (command[:7] == "request"):
    comm = command.split(" ")
    lang = eval(comm[1]) - 1
    
    if (len(languages) == 0):
      print "No languages. Try using 'list' first"
      
    elif (lang >= len(languages) or lang < 0):
      print "Language index not valid"
      
    else:
      msg = "UNQ " + languages[lang] + "\n"

      s.sendto(msg, address)

      d = s.recvfrom(1024)
      reply = d[0]

      rep = reply.split(" ")

      if ( rep[0] != "UNR" ):
        print "Algo esta mal..."

      ipTRS = rep[1]
      portTRS = eval(rep[2])
      hostTRS = socket.gethostbyaddr(ipTRS)[0]
      addressTRS = (hostTRS,portTRS)
      
      socketTRS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

      # try:
      socketTRS.connect(addressTRS)
      # except:
      #   print "Erro na conexao com o TRS"
      #   exit()

      if (comm[2] == "t"):
      	nWords = len(comm[3:])
      	msg = "TRQ t " + str(nWords)
      	for i in range(nWords):
      	  msg += " " + comm[3:][i]
      	msg += "\n"
      	print "Sent to TRS: " + msg
      	
      	socketTRS.send(msg)

      	msg = socketTRS.recv(1024)

      	msg = msg.split(" ")

      	translation = ""

      	for i in range(len(msg[3:])):
      	  translation += " " + msg[3:][i]

        # Verificar se deu TRR ERR ou TRR NTA

      	print "Translation:" , translation

      if (comm[2] == "f"):
      	msg = "TRQ f " + comm[3] + " " + str(os.stat(comm[3]).st_size) + " "
      	print msg

        socketTRS.send(msg)
        
        #enviar ficheiro
        print "Uploading file to server..."
        
        file_to_trl = open(comm[3],"rb")
      	
      	data = file_to_trl.read(256)

        while (data):
          socketTRS.send(data)
          data = file_to_trl.read(256)

        file_to_trl.close()
      	
      	socketTRS.send("\n")

        print "File uploaded"

      	#recepcao do ficheiro

        translated = socketTRS.recv(3)

        if ( translated != "TRR"):
          print "Error receiving file translation"
          sys.exit()
        
        translated = socketTRS.recv(3)

        if (translated != " f "):
          print "Error in message format"
          sys.exit()

        #####################################################################
        byte = socketTRS.recv(1)
        filename = ""

        while (byte != " "):
          filename += byte
          byte = socketTRS.recv(1)

        print "Filename: " , filename

        byte = socketTRS.recv(1)
        filesize = ""

        while (byte != " "):
          filesize += byte
          byte = socketTRS.recv(1)

        print "File size: " , filesize

        print "Downloading file..."

        ################################################################
        filesize = eval(filesize)

        recv_file = open("translation_" + filename,"wb+")

        packs_no = filesize / 256

        if ( (filesize % 256) != 0 ):
          packs_no += 1

        print packs_no

        for i in range(packs_no):
          data = socketTRS.recv(256)
          recv_file.write(data)

        recv_file.close()

        print "Download complete"

      socketTRS.close()
    
  if (command == "exit"):
    sys.exit("Thank you! Come again")

s.close()
