import React, { useState, useRef, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { AlertCircle, Send, Bot, User, Clock, Activity, Stethoscope } from 'lucide-react';

const ConsultationApp = () => {
  const [step, setStep] = useState('patient-form');
  const [error, setError] = useState(null);
  
  // Patient Form State
  const [patientData, setPatientData] = useState({
    personalInfo: {
      name: '',
      age: '',
      gender: '',
      contact: ''
    },
    symptoms: {
      description: '',
      duration: '',
      severity: '',
      location: ''
    },
    medicalHistory: {
      chronicConditions: '',
      surgeries: '',
      medications: '',
      allergies: ''
    }
  });

  // Chat State
  const [messages, setMessages] = useState([{
    type: 'bot',
    content: 'Xin chào! Tôi là trợ lý y tế ảo. Tôi có thể giúp gì cho bạn hôm nay?'
  }]);
  const [chatInput, setChatInput] = useState('');
  
  // Analysis State
  const [analysisData, setAnalysisData] = useState(null);
  
  // Appointment State
  const [appointmentData, setAppointmentData] = useState({
    date: '',
    time: '',
    specialty: ''
  });

  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // Patient Form Component
  const PatientFormSection = () => (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Thông tin bệnh nhân</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label htmlFor="name">Họ và tên</Label>
          <Input
            id="name"
            value={patientData.personalInfo.name}
            onChange={(e) => setPatientData({
              ...patientData,
              personalInfo: { ...patientData.personalInfo, name: e.target.value }
            })}
          />
        </div>
        
        <div>
          <Label htmlFor="age">Tuổi</Label>
          <Input
            id="age"
            type="number"
            value={patientData.personalInfo.age}
            onChange={(e) => setPatientData({
              ...patientData,
              personalInfo: { ...patientData.personalInfo, age: e.target.value }
            })}
          />
        </div>

        <div>
          <Label>Giới tính</Label>
          <Select 
            value={patientData.personalInfo.gender}
            onValueChange={(value) => setPatientData({
              ...patientData,
              personalInfo: { ...patientData.personalInfo, gender: value }
            })}
          >
            <SelectTrigger>
              <SelectValue placeholder="Chọn giới tính" />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectItem value="male">Nam</SelectItem>
                <SelectItem value="female">Nữ</SelectItem>
                <SelectItem value="other">Khác</SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="contact">Thông tin liên hệ</Label>
          <Input
            id="contact"
            value={patientData.personalInfo.contact}
            onChange={(e) => setPatientData({
              ...patientData,
              personalInfo: { ...patientData.personalInfo, contact: e.target.value }
            })}
          />
        </div>

        <Button 
          className="w-full" 
          onClick={() => setStep('chat')}
        >
          Tiếp tục
        </Button>
      </CardContent>
    </Card>
  );

  // Chat Component
  const ChatSection = () => (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Tư vấn</CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[500px] pr-4" ref={scrollRef}>
          <div className="space-y-4">
            {messages.map((message, index) => (
              <div 
                key={index}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`flex gap-3 max-w-[80%] ${
                  message.type === 'user' ? 'flex-row-reverse' : ''
                }`}>
                  <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full border bg-background">
                    {message.type === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                  </div>
                  <div className={`rounded-lg p-3 ${
                    message.type === 'user' 
                      ? 'bg-primary text-primary-foreground' 
                      : 'bg-muted'
                  }`}>
                    {message.content}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>

        <div className="mt-4 flex gap-4">
          <Textarea
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            placeholder="Nhập tin nhắn..."
            className="min-h-[60px]"
          />
          <Button onClick={() => {
            if (chatInput.trim()) {
              setMessages(prev => [...prev, 
                { type: 'user', content: chatInput },
                { type: 'bot', content: 'Tôi đã hiểu triệu chứng của bạn. Hãy để tôi phân tích.' }
              ]);
              setChatInput('');
              // Simulate analysis after chat
              setTimeout(() => {
                setAnalysisData({
                  predictedSpecialties: [{ name: 'Nội khoa', confidence: 0.85 }],
                  recommendedTests: ['Xét nghiệm máu', 'Chụp X-quang'],
                  urgencyLevel: { level: 'medium', description: 'Cần khám trong tuần này' },
                  recommendations: ['Nên đến khám càng sớm càng tốt']
                });
                setStep('analysis');
              }, 2000);
            }
          }}>
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );

  // Analysis Component
  const AnalysisSection = () => (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Stethoscope className="h-5 w-5" />
          Kết quả phân tích
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Specialties */}
          <div>
            <h3 className="font-semibold mb-2">Chuyên khoa được đề xuất</h3>
            {analysisData?.predictedSpecialties.map((specialty, index) => (
              <div 
                key={index}
                className="p-3 bg-muted rounded-lg flex justify-between items-center"
              >
                <span>{specialty.name}</span>
                <span className="text-sm text-muted-foreground">
                  {Math.round(specialty.confidence * 100)}% phù hợp
                </span>
              </div>
            ))}
          </div>

          {/* Tests */}
          <div>
            <h3 className="font-semibold mb-2">Xét nghiệm đề xuất</h3>
            {analysisData?.recommendedTests.map((test, index) => (
              <div key={index} className="p-3 bg-muted rounded-lg">
                {test}
              </div>
            ))}
          </div>

          <Button 
            className="w-full" 
            onClick={() => setStep('booking')}
          >
            Đặt lịch khám
          </Button>
        </div>
      </CardContent>
    </Card>
  );

  // Appointment Component
  const AppointmentSection = () => {
    const timeSlots = [
      '08:00', '08:30', '09:00', '09:30', '10:00', 
      '10:30', '11:00', '14:00', '14:30', '15:00'
    ];

    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>Đặt lịch khám</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>Chọn ngày khám</Label>
            <Input
              type="date"
              value={appointmentData.date}
              onChange={(e) => setAppointmentData({
                ...appointmentData,
                date: e.target.value
              })}
            />
          </div>

          <div>
            <Label>Chọn giờ khám</Label>
            <Select
              value={appointmentData.time}
              onValueChange={(value) => setAppointmentData({
                ...appointmentData,
                time: value
              })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Chọn giờ khám" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  {timeSlots.map(time => (
                    <SelectItem key={time} value={time}>
                      {time}
                    </SelectItem>
                  ))}
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>

          <Button 
            className="w-full" 
            onClick={() => setStep('complete')}
          >
            Xác nhận đặt lịch
          </Button>
        </CardContent>
      </Card>
    );
  };

  // Completion Component
  const CompletionSection = () => (
    <Card className="w-full max-w-2xl mx-auto">
      <CardContent className="p-6">
        <div className="text-center space-y-4">
          <h2 className="text-2xl font-bold text-green-600">
            Đặt lịch thành công!
          </h2>
          <p className="text-gray-600">
            Thông tin đặt lịch đã được gửi đến email của bạn.
          </p>
          <div className="bg-gray-50 p-4 rounded-lg">
            <p>Thời gian: {appointmentData.date} {appointmentData.time}</p>
            <p>Chuyên khoa: {analysisData?.predictedSpecialties[0]?.name}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  // Progress Indicator
  const ProgressIndicator = () => (
    <div className="flex justify-between mb-8">
      {['Thông tin', 'Tư vấn', 'Kết quả', 'Đặt lịch'].map((label, index) => {
        const stepNumber = index + 1;
        const currentStepNumber = {
          'patient-form': 1,
          'chat': 2,
          'analysis': 3,
          'booking': 4,
          'complete': 4
        }[step];

        return (
          <div 
            key={label} 
            className={`flex items-center ${index !== 0 ? 'flex-1' : ''}`}
          >
            <div 
              className={`w-8 h-8 rounded-full flex items-center justify-center ${
                stepNumber <= currentStepNumber 
                  ? 'bg-primary text-primary-foreground' 
                  : 'bg-gray-200 text-gray-600'
              }`}
            >
              {stepNumber}
            </div>
            {index !== 3 && (
              <div 
                className={`flex-1 h-1 mx-2 ${
                  stepNumber < currentStepNumber 
                    ? 'bg-primary' 
                    : 'bg-gray-200'
                }`}
              />
            )}
            <span className="text-sm">{label}</span>
          </div>
        );
      })}
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto p-4">
      <ProgressIndicator />
      
      {error && (
        <Alert variant="destructive" className="mb-4">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {step === 'patient-form' && <PatientFormSection />}
      {step === 'chat' && <ChatSection />}
      {step === 'analysis' && <AnalysisSection />}
      {step === 'booking' && <AppointmentSection />}
      {step === 'complete' && <CompletionSection />}
    </div>
  );
};

export default ConsultationApp;