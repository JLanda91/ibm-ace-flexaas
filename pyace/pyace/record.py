import base64
import json


class Record:
    def __init__(self, record: dict):
        self.__data = record

    @property
    def integration_server(self):
        return self.__data["checkpoint"]["messageFlowData"]["integrationServer"]

    @property
    def application(self) -> str:
        return self.__data["checkpoint"]["messageFlowData"]["application"]

    @property
    def message_flow(self) -> str:
        return self.__data["checkpoint"]["messageFlowData"]["messageFlow"]

    @property
    def thread_id(self) -> int:
        return self.__data["checkpoint"]["messageFlowData"]["threadId"]

    @property
    def source_node(self) -> str:
        return self.__data["checkpoint"]["messageFlowData"]["nodes"]["source"]["name"]

    @property
    def source_terminal(self) -> str:
        return self.__data["checkpoint"]["messageFlowData"]["nodes"]["source"]["terminal"]

    @property
    def target_node(self) -> str:
        return self.__data["checkpoint"]["messageFlowData"]["nodes"]["target"]["name"]

    @property
    def target_terminal(self) -> str:
        return self.__data["checkpoint"]["messageFlowData"]["nodes"]["target"]["terminal"]

    @property
    def inputmessage_uuid(self) -> str:
        return self.__data["checkpoint"]["correlationData"]["inputMessageUUID"]

    @property
    def invocation_uuid(self) -> str:
        return self.__data["checkpoint"]["correlationData"]["invocationUUID"]

    @property
    def flow_sequence_number(self) -> str:
        return self.__data["checkpoint"]["sequenceData"]["flowSequenceNumber"]

    @property
    def is_input_node(self) -> bool:
        return self.__data["checkpoint"]["messageFlowData"]["nodes"]["source"]["inputNode"]

    @property
    def is_first_message(self):
        return self.inputmessage_uuid == self.invocation_uuid

    @property
    def timestamp(self):
        return self.__data["checkpoint"]["sequenceData"]["timestamp"]

    def test_data(self):
        return self.__data["testData"]

    def test_data_json(self):
        return json.dumps(self.test_data)

    def test_data_xml(self):
        test_data = self.test_data
        byte_result = bytearray(b'')
        byte_result += b"<testData>"
        for byte_subtree in list(map(lambda x: base64.b64decode(x), test_data.values())):
            byte_result += byte_subtree
        byte_result += b"</testData>"
        return byte_result.decode('utf-8')
