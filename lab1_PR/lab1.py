import os
import re
import socket
import ssl
from urllib.parse import urlparse

model = r'<img.*?src=[\'"](.*?\.(?:jpg|png|gif))[\'"].*?>'

print('1 -> me.utm.md : 80\n'
      '2 -> utm.md    : 443\n')

optiune = int(input('Alegeti o optiune: '))

if optiune == 1:
    schema = 'http'
    host = 'me.utm.md'
    port = 80
elif optiune == 2:
    schema = 'https'
    host = 'utm.md'
    port = 443

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

if port == 443:
    context = ssl.create_default_context()
    sock = context.wrap_socket(sock, server_hostname=host)

cerere_antete = 'GET / HTTP/1.0\r\nHOST: {}' \
                  '\r\nAccept: text/html' \
                  '\r\nSave-Data: on\r\n\r\n'.format(host)

sock.sendall(cerere_antete.encode())

raspuns = b''
while True:
    date = sock.recv(2048)
    if not date:
        break
    raspuns += date

sock.close()

imagini_linkuri_regex = re.findall(model, raspuns.decode())
imagini_linkuri = []
for link in imagini_linkuri_regex:
    if schema not in link:
        link = f"{schema}://{host}/{link}"
    imagini_linkuri.append(link)

while len(imagini_linkuri):

    if not len(imagini_linkuri):
        break

    link = imagini_linkuri.pop()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    if port == 443:
        context = ssl.create_default_context()
        sock = context.wrap_socket(sock, server_hostname=host)
    url = urlparse(link)
    cerere = "GET {} HTTP/1.0\r\nHost: {}\r\n\r\n".format(url.path, host)

    sock.sendall(cerere.encode())
    raspuns = sock.recv(1024)
    antete, date_imagine = raspuns.split(b"\r\n\r\n", 1)

    lungime_continut_mate = re.search(r'content-length:\s*(\d+)', antete.decode().lower())
    lungime_continut = int(lungime_continut_mate.group(1))

    while len(date_imagine) < lungime_continut:
        date_imagine += sock.recv(1024)

    cale_imagine = "D:/lab1_PR/image/" + os.path.basename(url.path)
    with open(cale_imagine, "wb") as f:
        f.write(date_imagine)

    sock.close()
