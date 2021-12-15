# AHLA_netcat  
##Usage:  
'-c', '--command' ,'command shell'    
'-e', '--execute','execute a command'  
'-l', '--listen', 'listen'  
'-p', '--port',default=1234,'port to listen bydefault'  
'-t', '--target', default='127.0.0.1', 'default IP'  
'-u','--upload','upload a file'  
##Examples:  
netcat.py -t <ip> -p <port> -l -c <command> #Command shell  
netcat.py -t <ip> -p <port> -l -u=<pathToFile> #Upload a file  
netcat.py -t <ip> =p <port> -l -e=<command> #execute command  
echo 'TEXT' | ./netcat.py -t <ip> -p <port> #echo text to server port <port>  
netcat.py -t <ip> -p <port> #connect to server port  

