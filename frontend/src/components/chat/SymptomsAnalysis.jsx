import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { 
  Activity, 
  AlertCircle, 
  Clock, 
  FileText, 
  Hospital, 
  Stethoscope 
} from 'lucide-react';

const SymptomsAnalysis = ({ analysisData, onRequestAppointment }) => {
  if (!analysisData) return null;

  const {
    predictedSpecialties,
    recommendedTests,
    urgencyLevel,
    recommendations,
    possibleConditions,
    nextSteps
  } = analysisData;

  const getUrgencyColor = (level) => {
    switch (level) {
      case 'high':
        return 'text-red-500';
      case 'medium':
        return 'text-yellow-500';
      case 'low':
        return 'text-green-500';
      default:
        return 'text-gray-500';
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Stethoscope className="h-5 w-5" />
          Kết quả phân tích
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[600px] pr-4">
          <div className="space-y-6">
            {/* Urgency Level */}
            <div>
              <h3 className="font-semibold flex items-center gap-2 mb-2">
                <AlertCircle className="h-4 w-4" />
                Mức độ khẩn cấp
              </h3>
              <Alert>
                <AlertDescription className={getUrgencyColor(urgencyLevel.level)}>
                  {urgencyLevel.description}
                </AlertDescription>
              </Alert>
            </div>

            {/* Recommended Specialties */}
            <div>
              <h3 className="font-semibold flex items-center gap-2 mb-2">
                <Hospital className="h-4 w-4" />
                Chuyên khoa được đề xuất
              </h3>
              <div className="grid gap-2">
                {predictedSpecialties.map((specialty, index) => (
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
            </div>

            {/* Possible Conditions */}
            <div>
              <h3 className="font-semibold flex items-center gap-2 mb-2">
                <Activity className="h-4 w-4" />
                Các tình trạng có thể
              </h3>
              <div className="grid gap-2">
                {possibleConditions.map((condition, index) => (
                  <Alert key={index}>
                    <AlertDescription>{condition}</AlertDescription>
                  </Alert>
                ))}
              </div>
            </div>

            {/* Recommended Tests */}
            <div>
              <h3 className="font-semibold flex items-center gap-2 mb-2">
                <FileText className="h-4 w-4" />
                Xét nghiệm được đề xuất
              </h3>
              <div className="grid gap-2">
                {recommendedTests.map((test, index) => (
                  <div 
                    key={index}
                    className="p-3 bg-muted rounded-lg"
                  >
                    {test}
                  </div>
                ))}
              </div>
            </div>

            {/* Recommendations */}
            <div>
              <h3 className="font-semibold flex items-center gap-2 mb-2">
                <Clock className="h-4 w-4" />
                Khuyến nghị
              </h3>
              <div className="grid gap-2">
                {recommendations.map((recommendation, index) => (
                  <Alert key={index}>
                    <AlertDescription>{recommendation}</AlertDescription>
                  </Alert>
                ))}
              </div>
            </div>

            {/* Next Steps */}
            <div>
              <h3 className="font-semibold mb-2">Các bước tiếp theo</h3>
              <div className="grid gap-2">
                {nextSteps.map((step, index) => (
                  <div 
                    key={index}
                    className="p-3 bg-muted rounded-lg"
                  >
                    {step}
                  </div>
                ))}
              </div>
            </div>

            {/* Request Appointment Button */}
            <div className="pt-4">
              <Button 
                className="w-full" 
                onClick={onRequestAppointment}
              >
                Đặt lịch khám
              </Button>
            </div>
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

export default SymptomsAnalysis;