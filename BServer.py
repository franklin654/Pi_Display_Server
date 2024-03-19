from typing import Union
from PySide6.QtBluetooth import (QBluetoothServer, QBluetoothUuid, QBluetoothLocalDevice, QBluetoothSocket,
                                 QBluetoothServiceInfo)
from PySide6.QtCore import Signal, Slot, QUuid, QObject, QMimeDatabase, qWarning, QByteArray, qDebug
from PySide6.QtGui import QImage, QImageReader

service_uuid = QUuid.fromString("{e8e10f95-1a70-4b27-9ccf-02010264e9c8}")


class BServer(QObject):
    bluetooth_server: Union[None, QBluetoothServer]
    socket: Union[None, QBluetoothSocket]
    displayText = Signal(str)
    displayImage = Signal(QImage)
    clientConnected = Signal(str)
    clientDisconnected = Signal()
    db = QMimeDatabase()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.bluetooth_server = None
        self.bluetooth_service_info = QBluetoothServiceInfo()
        self.socket = None
        self.local_adapter = QBluetoothLocalDevice()
        self.local_address = self.local_adapter.address()
        self.local_adapter.powerOn()
        self.local_adapter.setHostMode(QBluetoothLocalDevice.HostMode.HostDiscoverable)
        self.local_adapter.hostModeStateChanged.connect(self._host_mode_changed)

    def start_server(self):
        if self.bluetooth_server:
            return
        # ![Create the Server]
        self.bluetooth_server = QBluetoothServer(QBluetoothServiceInfo.Protocol.RfcommProtocol, self)
        self.bluetooth_server.newConnection.connect(self._client_connected)

        # self.bluetooth_service_info = self.bluetooth_server.listen(QBluetoothUuid(service_uuid), "bt-display-server")
        # print(self.bluetooth_server.serverPort())
        # print(self.bluetooth_service_info.serverChannel())
        # print(self.bluetooth_service_info.socketProtocol())

        result = self.bluetooth_server.listen()
        if not result:
            qDebug("Cannot bind chat server to " + self.local_address.toString())
            return

        # ![Create the Server]

        # ![set service profile list]
        profile_sequence = QBluetoothServiceInfo.Sequence()
        class_ids = QBluetoothServiceInfo.Sequence()
        class_ids.append(QBluetoothUuid(QBluetoothUuid.ServiceClassUuid.SerialPort.value))
        class_ids.append(int(0x100))
        profile_sequence.append(class_ids)
        self.bluetooth_service_info.setAttribute(QBluetoothServiceInfo.AttributeId.BluetoothProfileDescriptorList.value, profile_sequence)

        # ![set service class ids]
        class_ids.clear()
        class_ids.append(QBluetoothUuid(service_uuid))
        class_ids.append(QBluetoothUuid(QBluetoothUuid.ServiceClassUuid.SerialPort.value))
        self.bluetooth_service_info.setAttribute(QBluetoothServiceInfo.AttributeId.ServiceClassIds.value, class_ids)

        # ![Service name, description and provider]
        service_name = "Bt Display Server"
        service_description = "Server to Display Text and Images"
        service_provider = "qt-project.org"
        self.bluetooth_service_info.setServiceName(service_name)
        self.bluetooth_service_info.setServiceDescription(service_description)
        self.bluetooth_service_info.setServiceProvider(service_provider)

        # ![set service uuid]
        print(service_uuid.toString())
        self.bluetooth_service_info.setServiceUuid(QBluetoothUuid(service_uuid))

        # ![service Discoverability]
        public_browse = QBluetoothServiceInfo.Sequence()
        public_browse.append(QBluetoothUuid(QBluetoothUuid.ServiceClassUuid.PublicBrowseGroup.value))
        self.bluetooth_service_info.setAttribute(QBluetoothServiceInfo.AttributeId.BrowseGroupList.value,
                                                 public_browse)

        # ![protocol descriptor]
        protocol_descriptor_list = QBluetoothServiceInfo.Sequence()
        protocol = QBluetoothServiceInfo.Sequence()
        protocol.append(QBluetoothUuid(QBluetoothUuid.ProtocolUuid.L2cap.value))
        protocol_descriptor_list.append(protocol)
        protocol.clear()
        protocol.append(QBluetoothUuid(QBluetoothUuid.ProtocolUuid.Rfcomm.value))
        protocol.append(self.bluetooth_server.serverPort())
        protocol_descriptor_list.append(protocol)
        self.bluetooth_service_info.setAttribute(QBluetoothServiceInfo.AttributeId.ProtocolDescriptorList.value,
                                                 protocol_descriptor_list)
        if self.bluetooth_service_info.isComplete():
            print("Service is completely defined")
        else:
            print("Service is incomplete")
            exit(1)

        # printing port number
        print("port no: ", self.bluetooth_server.serverPort())

        # @register Service
        if self.bluetooth_service_info.registerService():
            print("Successfully registered and advertised")
            print("service channel: ", self.bluetooth_service_info.serverChannel())
            # print("server port: ", self.bluetooth_server.serverPort())
            print("Socket protocol:", self.bluetooth_service_info.socketProtocol())
        else:
            print("Failed to register service")
            exit(BlockingIOError)
        for i in self.bluetooth_service_info.attribute(QBluetoothServiceInfo.
                                                       AttributeId.ProtocolDescriptorList.value).toList():
            print(i.toList())
        for i in self.bluetooth_service_info.attribute(QBluetoothServiceInfo.
                                                       AttributeId.BluetoothProfileDescriptorList.value).toList():
            print(i.toList())

    def stop_server(self):
        self.bluetooth_service_info.unregisterService()
        del self.socket
        del self.bluetooth_server

    @Slot()
    def _client_connected(self):
        self.socket = self.bluetooth_server.nextPendingConnection()
        if not self.socket:
            return
        self.socket.readyRead.connect(self._read_socket)
        self.socket.disconnected.connect(self._client_disconnected)
        print("socket connected" + self.socket.localName())

    @Slot()
    def _client_disconnected(self):
        if not self.socket:
            return
        self.clientDisconnected.emit()
        del self.socket

    @Slot()
    def _read_socket(self):
        if self.socket.bytesAvailable():
            ba = self.socket.readAll()
            data_type = self.db.mimeTypeForData(ba)
            if data_type.inherits("text/plain"):
                self.displayText.emit(str(ba))
            elif QByteArray(len(data_type.name()), data_type.name()) in QImageReader.supportedMimeTypes():
                img = QImage.fromData(ba)
                self.displayImage.emit(img)
            else:
                qWarning("[!] An Error Occurred")

    @Slot(QBluetoothLocalDevice.HostMode)
    def _host_mode_changed(self, mode):
        if mode.value != QBluetoothLocalDevice.HostMode.HostDiscoverable.value:
            self.local_adapter.setHostMode(QBluetoothLocalDevice.HostMode.HostDiscoverable)
