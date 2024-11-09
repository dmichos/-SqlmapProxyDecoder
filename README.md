# - SqlmapProxyDecoder
A GET proxy for SQLMap and also decodes the base64  responses


## - You need to create a folder 
   -- example : 
     -- Mkdir sqlproxy
     -- Cd sqlproxy 
     
### Generate SSL Cert 
-openssl genpkey -algorithm RSA -out private_key.pem
-openssl req -new -key private_key.pem -out cert_request.csr
-openssl x509 -req -in cert_request.csr -signkey private_key.pem -out cert.pem -days 365

Put the proxy.py inside the folder and run it 
Example : Python3 proxy.py 

After you will need sqlmap to be runned like this 

sqlmap -u "http://localhost:1337/?id=1" --dbs --batch --random-agent --proxy="https://localhost:8080"   --force-ssl
