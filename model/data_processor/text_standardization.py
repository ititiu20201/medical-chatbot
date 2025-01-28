import unicodedata
import re

class TextStandardizer:
    def __init__(self):
        self.canonical_forms = {
            'dau mat|đau mắt|mat dau|Dau mat|Dau Mat|Đau Mắt|Đau mắt': 'đau mắt',
            'mat do|mắt đỏ|do mat|Mat do|Mat Do|Mắt Đỏ|Mắt đỏ': 'mắt đỏ',
            'sung tay|sưng tấy|mat sung|Sung tay|Sưng tấy|Mat sung': 'sưng tấy',
            'mat sung|mắt sưng|sưng mắt|Mat sung|Mat Sưng|Mắt Sưng|Mắt sưng': 'mắt sưng',
            'giam thi luc|giảm thị lực|mat yeu|mắt yếu|mat kem|mắt kém|Giam thi luc|Giảm Thị Lực|Mắt Yếu|Mắt Kém': 'giảm thị lực',
            'ngua mat|ngứa mắt|cam giac kho chiu o mat|Ngua mat|Ngứa Mắt|Ngứa mắt': 'ngứa mắt',
            'chay nuoc mat|chảy nước mắt|Chay nuoc mat|Chảy Nước Mắt|Chảy nước mắt': 'chảy nước mắt',
            'noi mun mat|mụn mắt|vet loi trong mat|Noi mun mat|Nổi Mụn Mắt|Nổi mụn mắt': 'nổi mụn mắt',
            'cam giac lo lang|lo lắng|cam giac so hai vo co|Cam giac lo lang|Lo Lắng|Lo lắng': 'lo lắng',
            'mat ngu|mất ngủ|ngu khong yen giac|Mat ngu|Mất Ngủ|Mất ngủ': 'mất ngủ',
            'dau nguc|đau ngực|khong ro nguyen nhan|Dau nguc|Đau Ngực|Đau ngực': 'đau ngực',
            'danh trong nguc|đánh trống ngực|nhip tim bat thuong|Danh trong nguc|Đánh Trống Ngực|Đánh trống ngực': 'đánh trống ngực',
            'tram cam|trầm cảm|cam giac buon ba|Tram cam|Trầm Cảm|Trầm cảm': 'trầm cảm',
            'kho tho|khó thở|tho gap|Kho tho|Khó Thở|Khó thở': 'khó thở',
            'so hai vo co|sợ hãi|am anh|So hai vo co|Sợ Hãi|Sợ hãi': 'sợ hãi',
            'dau bung|đau bụng|quặn thắt|Dau bung|Đau Bụng|Đau bụng': 'đau bụng',
            'tao bon|táo bón|thay doi hinh dang phan|Tao bon|Táo Bón|Táo bón': 'táo bón',
            'noi mun|nổi mụn|sưng đỏ|Noi mun|Nổi Mụn|Nổi mụn': 'nổi mụn',
            'dau dau|đau đầu|Dau dau|Đau Đầu|Đau đầu': 'đau đầu',
            'hon me|hôn mê|mat y thuc|Hon me|Hôn Mê|Hôn mê': 'hôn mê',
            'ho|ho khan|Ho|Ho Khan|Ho khan': 'ho',
            'nhip tim tang|nhịp tim tăng|nhip tim khong deu|Nhip tim tang|Nhịp Tim Tăng|Nhịp tim tăng': 'nhịp tim bất thường',
            'hoi mieng|hôi miệng|Hoi mieng|Hôi Miệng|Hôi miệng': 'hôi miệng',
            'suong ham|sưng hàm|kho nhai|Suong ham|Sưng Hàm|Sưng hàm': 'sưng hàm',
            'dau ham|đau hàm|cang co ham|Dau ham|Đau Hàm|Đau hàm|căng cơ hàm|Căng cơ hàm': 'đau hàm',
            'sung moi|sưng môi|Sung moi|Sưng Môi|Sưng môi': 'sưng môi',
            'kho noi|khó nói|khan giong|Kho noi|Khó Nói|Khó nói': 'khàn giọng',
            'co ngan|cổ ngắn|xuat hien nep gap|Co ngan|Cổ Ngắn|Cổ ngắn': 'cổ ngắn',
            'tac tinh hoan|tắc tinh hoàn|dau tinh hoan|Tac tinh hoan|Tắc Tinh Hoàn|Tắc tinh hoàn': 'tắc tinh hoàn',
            'ngua am dao|ngứa âm đạo|kho am dao|Ngua am dao|Ngứa Âm Đạo|Ngứa âm đạo': 'ngứa âm đạo',
            'loet mieng|loét miệng|to chuc hong|Loet mieng|Loét Miệng|Loét miệng': 'loét miệng'
        }

        self.compiled_patterns = {
            re.compile(pattern): canonical
            for variations, canonical in self.canonical_forms.items()
            for pattern in variations.split('|')
        }

    def standardize_vietnamese(self, text):
        if not text:
            return text
        text = unicodedata.normalize('NFC', text)
        text = text.lower().strip()
        return text

    def standardize_symptoms(self, symptoms_list):
        if not symptoms_list:
            return []
        
        standardized = []
        for symptom in symptoms_list:
            symptom = self.standardize_vietnamese(symptom)
            for pattern, canonical in self.compiled_patterns.items():
                if pattern.match(symptom):
                    standardized.append(canonical)
                    break
            else:
                standardized.append(symptom)
        return list(set(standardized))  # Remove duplicates

    def standardize_medical_text(self, text):
        if not text:
            return text
        
        text = self.standardize_vietnamese(text)
        
        # Standardize measurements
        text = re.sub(r'(\d+)\s*(mg|ml|g|kg)', r'\1\2', text)
        
        # Standardize frequencies
        text = re.sub(r'(\d+)\s*lan/ngay', r'\1 lần/ngày', text)
        text = re.sub(r'(\d+)\s*lan/tuan', r'\1 lần/tuần', text)
        
        return text

    def standardize_name(self, name):
        if not name:
            return name
        
        name = self.standardize_vietnamese(name)
        words = name.split()
        return ' '.join(word.capitalize() for word in words)

    def standardize_address(self, address):
        if not address:
            return address
        
        address = self.standardize_vietnamese(address)
        
        # Capitalize after comma and period
        address = re.sub(r'(?<=[\.,])\s*(\w)', lambda m: ' ' + m.group(1).upper(), address)
        
        # Capitalize first letter of each part
        parts = address.split(',')
        parts = [part.strip().capitalize() for part in parts]
        
        return ', '.join(parts)
