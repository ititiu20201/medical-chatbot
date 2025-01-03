// services/api.js

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = {
  // Chat endpoints
  sendMessage: async (message, patientId) => {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message, patient_id: patientId }),
    });
    return response.json();
  },

  // Patient endpoints
  savePatientInfo: async (patientData) => {
    const response = await fetch(`${API_BASE_URL}/patient`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(patientData),
    });
    return response.json();
  },

  // Queue status
  getQueueStatus: async (specialty) => {
    const response = await fetch(`${API_BASE_URL}/queue-status`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ specialty }),
    });
    return response.json();
  },

  // Appointment booking
  bookAppointment: async (bookingData) => {
    const response = await fetch(`${API_BASE_URL}/book-appointment`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(bookingData),
    });
    return response.json();
  },

  // WebSocket connection
  getWebSocketUrl: () => {
    return `ws://${window.location.host}/ws`;
  },
};

// Error handling wrapper
export const withErrorHandling = async (apiCall) => {
  try {
    return await apiCall();
  } catch (error) {
    console.error('API Error:', error);
    throw new Error('Có lỗi xảy ra khi kết nối với server');
  }
};