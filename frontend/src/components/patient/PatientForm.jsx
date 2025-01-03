import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Alert, AlertDescription } from '@/components/ui/alert';

const PatientForm = ({ onComplete }) => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    personalInfo: {
      name: '',
      age: '',
      gender: '',
      contact: '',
    },
    symptoms: {
      description: '',
      duration: '',
      severity: '',
      location: '',
    },
    medicalHistory: {
      chronicConditions: '',
      surgeries: '',
      medications: '',
      allergies: '',
    }
  });

  const [errors, setErrors] = useState({});

  const validateStep = (stepNumber) => {
    const newErrors = {};

    switch (stepNumber) {
      case 1:
        if (!formData.personalInfo.name) newErrors.name = 'Vui lòng nhập họ tên';
        if (!formData.personalInfo.age) newErrors.age = 'Vui lòng nhập tuổi';
        if (!formData.personalInfo.gender) newErrors.gender = 'Vui lòng chọn giới tính';
        if (!formData.personalInfo.contact) newErrors.contact = 'Vui lòng nhập thông tin liên hệ';
        break;
      case 2:
        if (!formData.symptoms.description) newErrors.symptoms = 'Vui lòng mô tả triệu chứng';
        if (!formData.symptoms.duration) newErrors.duration = 'Vui lòng nhập thời gian';
        break;
      case 3:
        if (!formData.medicalHistory.chronicConditions) newErrors.chronic = 'Vui lòng điền thông tin';
        break;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(step)) {
      setStep(step + 1);
    }
  };

  const handleSubmit = async () => {
    if (validateStep(3)) {
      try {
        const response = await fetch('/api/patient', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData),
        });

        if (response.ok) {
          onComplete(formData);
        } else {
          setErrors({ submit: 'Có lỗi xảy ra khi gửi thông tin' });
        }
      } catch (error) {
        setErrors({ submit: 'Không thể kết nối với máy chủ' });
      }
    }
  };

  const updateFormData = (section, field, value) => {
    setFormData(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Thông tin bệnh nhân - Bước {step}/3</CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[500px] pr-4">
          {step === 1 && (
            <div className="space-y-4">
              <div>
                <Label htmlFor="name">Họ và tên</Label>
                <Input
                  id="name"
                  value={formData.personalInfo.name}
                  onChange={(e) => updateFormData('personalInfo', 'name', e.target.value)}
                  error={errors.name}
                />
                {errors.name && <span className="text-red-500 text-sm">{errors.name}</span>}
              </div>
              
              <div>
                <Label htmlFor="age">Tuổi</Label>
                <Input
                  id="age"
                  type="number"
                  value={formData.personalInfo.age}
                  onChange={(e) => updateFormData('personalInfo', 'age', e.target.value)}
                  error={errors.age}
                />
                {errors.age && <span className="text-red-500 text-sm">{errors.age}</span>}
              </div>

              <div>
                <Label>Giới tính</Label>
                <RadioGroup
                  value={formData.personalInfo.gender}
                  onValueChange={(value) => updateFormData('personalInfo', 'gender', value)}
                >
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="male" id="male" />
                    <Label htmlFor="male">Nam</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="female" id="female" />
                    <Label htmlFor="female">Nữ</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="other" id="other" />
                    <Label htmlFor="other">Khác</Label>
                  </div>
                </RadioGroup>
                {errors.gender && <span className="text-red-500 text-sm">{errors.gender}</span>}
              </div>

              <div>
                <Label htmlFor="contact">Thông tin liên hệ (Email/SĐT)</Label>
                <Input
                  id="contact"
                  value={formData.personalInfo.contact}
                  onChange={(e) => updateFormData('personalInfo', 'contact', e.target.value)}
                  error={errors.contact}
                />
                {errors.contact && <span className="text-red-500 text-sm">{errors.contact}</span>}
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <div>
                <Label htmlFor="symptoms">Mô tả triệu chứng</Label>
                <Input
                  id="symptoms"
                  value={formData.symptoms.description}
                  onChange={(e) => updateFormData('symptoms', 'description', e.target.value)}
                  error={errors.symptoms}
                />
                {errors.symptoms && <span className="text-red-500 text-sm">{errors.symptoms}</span>}
              </div>

              <div>
                <Label htmlFor="duration">Thời gian xuất hiện triệu chứng</Label>
                <Input
                  id="duration"
                  value={formData.symptoms.duration}
                  onChange={(e) => updateFormData('symptoms', 'duration', e.target.value)}
                  error={errors.duration}
                />
                {errors.duration && <span className="text-red-500 text-sm">{errors.duration}</span>}
              </div>

              <div>
                <Label htmlFor="severity">Mức độ nghiêm trọng (1-10)</Label>
                <Input
                  id="severity"
                  type="number"
                  min="1"
                  max="10"
                  value={formData.symptoms.severity}
                  onChange={(e) => updateFormData('symptoms', 'severity', e.target.value)}
                />
              </div>

              <div>
                <Label htmlFor="location">Vị trí triệu chứng</Label>
                <Input
                  id="location"
                  value={formData.symptoms.location}
                  onChange={(e) => updateFormData('symptoms', 'location', e.target.value)}
                />
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-4">
              <div>
                <Label htmlFor="chronic">Bệnh mãn tính</Label>
                <Input
                  id="chronic"
                  value={formData.medicalHistory.chronicConditions}
                  onChange={(e) => updateFormData('medicalHistory', 'chronicConditions', e.target.value)}
                  error={errors.chronic}
                />
                {errors.chronic && <span className="text-red-500 text-sm">{errors.chronic}</span>}
              </div>

              <div>
                <Label htmlFor="surgeries">Tiền sử phẫu thuật</Label>
                <Input
                  id="surgeries"
                  value={formData.medicalHistory.surgeries}
                  onChange={(e) => updateFormData('medicalHistory', 'surgeries', e.target.value)}
                />
              </div>

              <div>
                <Label htmlFor="medications">Thuốc đang sử dụng</Label>
                <Input
                  id="medications"
                  value={formData.medicalHistory.medications}
                  onChange={(e) => updateFormData('medicalHistory', 'medications', e.target.value)}
                />
              </div>

              <div>
                <Label htmlFor="allergies">Dị ứng</Label>
                <Input
                  id="allergies"
                  value={formData.medicalHistory.allergies}
                  onChange={(e) => updateFormData('medicalHistory', 'allergies', e.target.value)}
                />
              </div>
            </div>
          )}

          {errors.submit && (
            <Alert variant="destructive" className="mt-4">
              <AlertDescription>{errors.submit}</AlertDescription>
            </Alert>
          )}
        </ScrollArea>

        <div className="flex justify-between mt-6">
          {step > 1 && (
            <Button variant="outline" onClick={() => setStep(step - 1)}>
              Quay lại
            </Button>
          )}
          {step < 3 ? (
            <Button onClick={handleNext}>Tiếp theo</Button>
          ) : (
            <Button onClick={handleSubmit}>Hoàn thành</Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default PatientForm;