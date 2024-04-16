import logging
from datetime import datetime

from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket
from thrift.transport import TTransport

from thrift_timestamp.gen_py.timestamp_service import TimestampService

# Global variable to hold the Thrift server instance
server = None
# Global variable to control the server loop
server_running = True

class TimestampHandler:
    def getCurrentTimestamp(self):
        """Return the current timestamp in the format 'YYYY-MM-DD HH:MM:SS'"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def start_thrift_server():
    """Start the Thrift server and serve requests indefinitely."""
    # Declare the global variables
    global server
    global server_running
    # Create the Thrift server
    handler = TimestampHandler()
    processor = TimestampService.Processor(handler)
    transport = TSocket.TServerSocket(port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    # Start the server loop
    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    print("Starting the Thrift server...")
    while server_running:
        server.serve()

def stop_thrift_server():
    """Stop the Thrift server."""
    global server_running
    server_running = False

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_thrift_server()
