from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from gen_py.timestamp_service import TimestampService

def run_client():
    try:
        transport = TSocket.TSocket('localhost', 9090)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)

        client = TimestampService.Client(protocol)
        transport.open()

        print("Connected to server. Retrieving current timestamp...")
        result = client.getCurrentTimestamp()
        print("Current Timestamp:", result)

        transport.close()
    except Exception as e:
        print("An error occurred:", e)

if __name__ == '__main__':
    run_client()
