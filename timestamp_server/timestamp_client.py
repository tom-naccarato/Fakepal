from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from gen_py.timestamp_service import TimestampService


class ThriftTimestampClient:
    """Thrift client to fetch the current timestamp from the Thrift server."""
    def __init__(self, host='localhost', port=9090):
        """Initialize the Thrift client with the host and port of the Thrift server."""
        self.host = host
        self.port = port

    def get_current_timestamp(self):
        """Fetch the current timestamp from the Thrift server."""
        try:
            transport = TSocket.TSocket(self.host, self.port)
            transport = TTransport.TBufferedTransport(transport)
            protocol = TBinaryProtocol.TBinaryProtocol(transport)
            client = TimestampService.Client(protocol)
            transport.open()
            timestamp = client.getCurrentTimestamp()
            transport.close()
            return timestamp

        except Exception as e:
            print("An error occurred while fetching the timestamp:", e)
            return None
