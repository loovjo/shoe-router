import sys

import zlib
import os
import asyncio
from http_parse import HTTPParser
import random

DEFAULT_PNG = open("static/default.png", "br").read()


def gen_id():
    return str(random.randint(0, 1000000000000)).encode("utf-8")

async def send_response(writer, data, content_type):
    writer.write(f"""\
HTTP/1.1 200 OK\r
Content-Type: {content_type}\r
Server: lol\r
Content-Length: {len(data)}\r
\r
""".encode("utf-8"))

    writer.write(data)
    await writer.drain()
    writer.close()

class UserSession:
    def __init__(self, main_writer, id):
        self.main_writer = main_writer
        self.id = id

        self.t = 0

        self.val_x = 0

    async def init(self):
        self.main_writer.write(b"""\
HTTP/1.1 200 OK\r
Content-Type: text/html; charset=UTF-8\r
Server: lol\r
Transfer-Encoding: chunked\r
\r
""")
        await self.main_writer.drain()
        self.buffer_send_line(self.fmt(open("static/main.html", "br").read()))
        await self.main_writer.drain()

        await self.update()

    def end(self):
        self.buffer_send_line(b"")
        self.main_writer.write(b"\r\n")

    def buffer_send_line(self, line):
        self.main_writer.write(hex(len(line))[2:].encode("utf-8") + b"\r\n")
        self.main_writer.write(line + b"\r\n")

    async def handle_request(self, p, writer):
        if p.method == b"GET":
            if p.path == b"/":
                return

            path = os.path.join("static", p.path.decode("utf-8")[1:])
            print("GETting", path, flush=True)
            if os.path.isfile(path):
                await send_response(writer, open(path, "br").read(), "image/png")
            else:
                await send_response(writer, DEFAULT_PNG, "image/png")

        if p.path == b"/press.png" and p.query == self.fmt(b"{id}&{t}"):
            print("aaaa")
            self.t += 1
            await self.update()

    def fmt(self, data):
        return data.replace(b"{id}", self.id).replace(b"{t}", str(self.t).encode("utf-8"))

    async def update(self):
        self.buffer_send_line(self.fmt(b'''<style>
p::after {
    content: "{t}";
}
'''))
        if self.t % 2 == 0:
            self.buffer_send_line(self.fmt(b'''
#b1 { visibility: visible; }
#b2 { visibility: hidden; }

#b1:active { background: url("press.png?{id}&{t}"); }

</style>'''))
        else:
            self.buffer_send_line(self.fmt(b'''
#b2 { visibility: visible; }
#b1 { visibility: hidden; }

#b2:active { background: url("press.png?{id}&{t}"); }

</style>'''))
        self.buffer_send_line(self.fmt(b'''</style>'''))

        await self.main_writer.drain()

    def __repr__(self):
        return f"UserSession(id={self.id!r})"

SESSIONS = []
def get_session_for(id):
    for s in SESSIONS:
        if s.id == id:
            return s

    return None

async def handle(reader, writer):
    global SESSION
    p = HTTPParser()
    while not p.done:
        dat = await reader.read(1)
        p.pass_ch(dat)

    addr = writer.get_extra_info('peername')

    print(f"Received {p} from {addr!r}", flush=True)

    if p.query == None:
        id = gen_id()
        s = UserSession(writer, id)
        SESSIONS.append(s)
        await s.init()
    else:
        s = get_session_for(p.query.split(b"&")[0])

    if s is not None:
        print(f"Handling {p!r} for session {s!r}", flush=True)
        await s.handle_request(p, writer)

async def main():
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        port = 13080
    server = await asyncio.start_server(
        handle, '0.0.0.0', port)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}', flush=True)

    async with server:
        await server.serve_forever()

print("Starting", flush=True)

asyncio.run(main())
