import React, { useState, useEffect, useRef } from 'react';
import { Send, Clock, User, Bot, AlertCircle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

const ProactiveChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentState, setCurrentState] = useState('initial');
  const [patientInfo, setPatientInfo] = useState({});
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const messagesEndRef = useRef(null);

  // Define conversation flow data
  const conversationStates = {
    initial: 'initial',
    personalInfo: 'personal_info',
    symptoms: 'symptoms',
    medicalHistory: 'medical_history',
    recommendations: 'recommendations',
    completed: 'completed'
  };

  const personalInfoQuestions = [
    "Xin chào! Tôi là trợ lý y tế ảo. Xin cho biết họ tên đầy đủ của bạn?",
    "Bạn bao nhiêu tuổi?",
    "Xin cho biết giới tính của bạn (Nam/Nữ/Khác)?",
    "Vui lòng cung cấp số điện thoại hoặc email để liên hệ?"
  ];

  const symptomQuestions = [
    "Bạn đang gặp phải những triệu chứng gì?",
    "Triệu chứng này đã kéo dài bao lâu?",
    "Mức độ khó chịu của triệu chứng từ 1-10?",
    "Triệu chứng có thường xuyên xuất hiện không?"
  ];

  useEffect(() => {
    startConversation();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const startConversation = () => {
    addBotMessage(personalInfoQuestions[0]);
    setCurrentState(conversationStates.personalInfo);
  };

  const addBotMessage = (content, additionalInfo = {}) => {
    setMessages(prev => [...prev, {
      type: 'bot',
      content,
      timestamp: new Date(),
      ...additionalInfo
    }]);
  };

  const addUserMessage = (content) => {
    setMessages(prev => [...prev, {
      type: 'user',
      content,
      timestamp: new Date()
    }]);
  };

  const processPersonalInfo = (input) => {
    const updatedInfo = { ...patientInfo };
    
    switch (currentQuestionIndex) {
      case 0:
        updatedInfo.name = input;
        break;
      case 1:
        if (isNaN(input) || input < 0 || input > 150) {
          addBotMessage("Vui lòng nhập tuổi hợp lệ (0-150).");
          return false;
        }
        updatedInfo.age = parseInt(input);
        break;
      case 2:
        const gender = input.toLowerCase();
        if (!['nam', 'nữ', 'khác'].includes(gender)) {
          addBotMessage("Vui lòng chọn giới tính: Nam, Nữ hoặc Khác.");
          return false;
        }
        updatedInfo.gender = gender;
        break;
      case 3:
        updatedInfo.contact = input;
        break;
      default:
        return false;
    }

    setPatientInfo(updatedInfo);
    return true;
  };

  const processSymptoms = async (input) => {
    const symptoms = input.toLowerCase().split(',').map(s => s.trim());
    
    try {
      const response = await fetch('/api/analyze-symptoms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          symptoms,
          patientInfo
        })
      });
      
      const data = await response.json();
      
      if (data.needsMoreInfo) {
        addBotMessage(data.followUpQuestion);
        return;
      }
      
      addBotMessage(
        `Dựa trên triệu chứng của bạn, tôi đề xuất khám tại khoa ${data.recommendedSpecialty}. Bạn có tiền sử bệnh lý nào cần lưu ý không?`
      );
      setCurrentState(conversationStates.medicalHistory);
      
    } catch (error) {
      addBotMessage("Xin lỗi, có lỗi xảy ra khi phân tích triệu chứng. Vui lòng thử lại.");
    }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    setLoading(true);
    addUserMessage(input);
    const userInput = input.trim();
    setInput('');

    try {
      switch (currentState) {
        case conversationStates.personalInfo:
          if (processPersonalInfo(userInput)) {
            if (currentQuestionIndex < personalInfoQuestions.length - 1) {
              setCurrentQuestionIndex(prev => prev + 1);
              addBotMessage(personalInfoQuestions[currentQuestionIndex + 1]);
            } else {
              setCurrentState(conversationStates.symptoms);
              addBotMessage(symptomQuestions[0]);
              setCurrentQuestionIndex(0);
            }
          }
          break;

        case conversationStates.symptoms:
          await processSymptoms(userInput);
          break;

        case conversationStates.medicalHistory:
          // Process medical history and generate recommendations
          const response = await fetch('/api/generate-recommendations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              patientInfo,
              medicalHistory: userInput
            })
          });
          
          const recommendations = await response.json();
          
          addBotMessage("Dựa trên thông tin của bạn, đây là các đề xuất của tôi:", {
            recommendations
          });
          setCurrentState(conversationStates.completed);
          break;

        default:
          addBotMessage("Xin lỗi, tôi không hiểu. Vui lòng thử lại.");
      }
    } catch (error) {
      addBotMessage("Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.");
    }

    setLoading(false);
  };

  const handleRestart = () => {
    setMessages([]);
    setPatientInfo({});
    setCurrentQuestionIndex(0);
    setCurrentState(conversationStates.initial);
    startConversation();
  };

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto p-4">
      <Card className="flex-grow overflow-hidden flex flex-col">
        <CardContent className="flex-grow overflow-y-auto p-4 space-y-4">
          {messages.map((message, idx) => (
            <div
              key={idx}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex items-start space-x-2 max-w-[80%] ${
                message.type === 'user' ? 'flex-row-reverse' : 'flex-row'
              }`}>
                {message.type === 'user' ? (
                  <User className="w-6 h-6 text-blue-500" />
                ) : (
                  <Bot className="w-6 h-6 text-green-500" />
                )}
                <div className={`rounded-lg p-3 ${
                  message.type === 'user' 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-100 text-gray-900'
                }`}>
                  <p className="text-sm">{message.content}</p>
                  {message.recommendations && (
                    <div className="mt-2 text-xs">
                      <p className="font-semibold">Đề xuất khám bệnh:</p>
                      <p>Chuyên khoa: {message.recommendations.specialty}</p>
                      <p>Mức độ ưu tiên: {message.recommendations.urgency}</p>
                      <p>Thời gian chờ dự kiến: {message.recommendations.estimatedWaitTime}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </CardContent>
        <div className="p-4 border-t">
          <div className="flex space-x-2">
            {currentState === conversationStates.completed ? (
              <button
                onClick={handleRestart}
                className="w-full p-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
              >
                Bắt đầu cuộc tư vấn mới
              </button>
            ) : (
              <>
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="Nhập câu trả lời của bạn..."
                  className="flex-grow p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={loading}
                />
                <button
                  onClick={handleSend}
                  disabled={loading}
                  className="p-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
                >
                  {loading ? (
                    <Clock className="w-5 h-5 animate-spin" />
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </button>
              </>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
};

export default ProactiveChatInterface;