import logging
from datetime import datetime

from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket
from thrift.transport import TTransport

from gen_py.timestamp_service import TimestampService


class TimestampHandler:
    def getCurrentTimestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def start_thrift_server():
    handler = TimestampHandler()
    processor = TimestampService.Processor(handler)
    transport = TSocket.TServerSocket(port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    print("Starting the Thrift server...")
    server.serve()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_thrift_server()
