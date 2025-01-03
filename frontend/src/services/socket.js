// services/socket.js

class ChatWebSocket {
    constructor(url, onMessage) {
      this.url = url;
      this.onMessage = onMessage;
      this.ws = null;
      this.reconnectAttempts = 0;
      this.maxReconnectAttempts = 5;
    }
  
    connect() {
      this.ws = new WebSocket(this.url);
  
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
      };
  
      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.onMessage(data);
      };
  
      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.handleDisconnect();
      };
  
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    }
  
    handleDisconnect() {
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        setTimeout(() => this.connect(), 3000);
      }
    }
  
    sendMessage(message) {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify(message));
      } else {
        console.error('WebSocket is not connected');
      }
    }
  
    disconnect() {
      if (this.ws) {
        this.ws.close();
      }
    }
  }
  
  export default ChatWebSocket;