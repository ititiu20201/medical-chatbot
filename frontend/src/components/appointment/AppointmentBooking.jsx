import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Select, 
  SelectContent, 
  SelectGroup, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { Clock, AlertCircle, User } from 'lucide-react';

const AppointmentBooking = ({ specialty, patientInfo, onBookingComplete }) => {
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTime, setSelectedTime] = useState('');
  const [queueStatus, setQueueStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const timeSlots = [
    '08:00', '08:30', '09:00', '09:30', '10:00', 
    '10:30', '11:00', '14:00', '14:30', '15:00', 
    '15:30', '16:00', '16:30'
  ];

  // Generate available dates (next 30 days excluding weekends)
  const getAvailableDates = () => {
    const dates = [];
    const today = new Date();
    let current = new Date(today);
    
    while (dates.length < 30) {
      if (current.getDay() !== 0 && current.getDay() !== 6) { // Skip weekends
        dates.push(new Date(current));
      }
      current.setDate(current.getDate() + 1);
    }
    return dates;
  };

  useEffect(() => {
    fetchQueueStatus();
  }, [specialty]);

  const fetchQueueStatus = async () => {
    try {
      const response = await fetch('/api/queue-status', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ specialty }),
      });

      if (response.ok) {
        const data = await response.json();
        setQueueStatus(data);
      } else {
        setError('Không thể lấy thông tin hàng đợi');
      }
    } catch (error) {
      setError('Lỗi kết nối server');
    }
  };

  const handleBooking = async () => {
    if (!selectedDate || !selectedTime) {
      setError('Vui lòng chọn thời gian khám');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/book-appointment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          specialty,
          patientInfo,
          appointmentDate: selectedDate,
          appointmentTime: selectedTime,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        onBookingComplete(data);
      } else {
        setError('Không thể đặt lịch khám');
      }
    } catch (error) {
      setError('Lỗi kết nối server');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (date) => {
    return new Date(date).toLocaleDateString('vi-VN', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <Card className="w-full max-w-xl mx-auto">
      <CardHeader>
        <CardTitle>Đặt lịch khám - {specialty}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Queue Status */}
        {queueStatus && (
          <div className="rounded-lg bg-muted p-4">
            <h3 className="font-semibold flex items-center gap-2 mb-2">
              <User className="h-4 w-4" />
              Tình trạng hàng đợi
            </h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Số bệnh nhân đang chờ:</span>
                <span className="font-semibold">{queueStatus.current_number}</span>
              </div>
              <div className="flex justify-between">
                <span>Thời gian chờ ước tính:</span>
                <span className="font-semibold">{queueStatus.waiting_time} phút</span>
              </div>
            </div>
          </div>
        )}

        {/* Date Selection */}
        <div>
          <Label className="block mb-2">Chọn ngày khám</Label>
          <Select value={selectedDate} onValueChange={setSelectedDate}>
            <SelectTrigger>
              <SelectValue placeholder="Chọn ngày khám" />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                {getAvailableDates().map(date => (
                  <SelectItem key={date.toISOString()} value={date.toISOString()}>
                    {formatDate(date)}
                  </SelectItem>
                ))}
              </SelectGroup>
            </SelectContent>
          </Select>
        </div>

        {/* Time Selection */}
        <div>
          <Label className="flex items-center gap-2 mb-2">
            <Clock className="h-4 w-4" />
            Chọn giờ khám
          </Label>
          <Select value={selectedTime} onValueChange={setSelectedTime}>
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

        {/* Error Display */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Submit Button */}
        <Button 
          className="w-full" 
          onClick={handleBooking} 
          disabled={loading || !selectedDate || !selectedTime}
        >
          {loading ? 'Đang xử lý...' : 'Xác nhận đặt lịch'}
        </Button>
      </CardContent>
    </Card>
  );
};

export default AppointmentBooking;