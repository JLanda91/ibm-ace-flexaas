import base64
import json


class Record:
    def __init__(self, record: dict):
        self.__data = record

    @property
    def _msgflow_data(self):
        return self.__data["checkpoint"]["messageFlowData"]

    @property
    def _nodes(self):
        return self._msgflow_data["nodes"]

    @property
    def _source(self):
        return self._nodes["source"]

    @property
    def _target(self):
        return self._nodes["target"]

    @property
    def application(self) -> str:
        return self._msgflow_data["application"]

    @property
    def message_flow(self) -> str:
        return self._msgflow_data["messageFlow"]

    @property
    def thread_id(self) -> int:
        return self._msgflow_data["threadId"]

    @property
    def source_node(self) -> str:
        return self._source["name"]

    @property
    def source_terminal(self) -> str:
        return self._source["terminal"]

    @property
    def target_node(self) -> str:
        return self._target["name"]

    @property
    def target_terminal(self) -> str:
        return self._target["terminal"]

    @property
    def message_uuid(self) -> str:
        return self.__data["checkpoint"]["correlationData"]["inputMessageUUID"]

    @property
    def flow_sequence_number(self) -> str:
        return self.__data["checkpoint"]["sequenceData"]["flowSequenceNumber"]

    @property
    def is_input_node(self) -> bool:
        return self._source["inputNode"]

    @property
    def test_data(self):
        return self.__data["testData"]

    @property
    def test_data_json(self):
        return json.dumps(self.test_data)

    @property
    def test_data_xml(self):
        test_data = self.test_data
        byte_result = bytearray(b'')
        byte_result += b"<testData>"
        for byte_subtree in list(map(lambda x: base64.b64decode(x), test_data.values())):
            byte_result += byte_subtree
        byte_result += b"</testData>"
        return byte_result.decode('utf-8')
