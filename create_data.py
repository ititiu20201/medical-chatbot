import json
import random
from faker import Faker

# Initialize Faker
fake = Faker()

# Vietnamese-style data samples for manual customization
first_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ"]
middle_names = ["Văn", "Thị", "Hữu", "Minh", "Xuân", "Quang", "Phúc", "Công", "Ngọc", "Anh"]
last_names = ["An", "Bình", "Cường", "Dương", "Hà", "Hùng", "Linh", "Nam", "Phong", "Tú"]
streets = [
    "Nguyễn Huệ", "Lê Lợi", "Trần Phú", "Phạm Ngũ Lão", "Cách Mạng Tháng Tám",
    "Hai Bà Trưng", "Điện Biên Phủ", "Lý Thường Kiệt", "Ngô Quyền", "Hoàng Văn Thụ",
    "Phan Văn Trị", "Nguyễn Trãi", "Tôn Đức Thắng", "Trường Chinh", "Lý Tự Trọng",
    "Nguyễn Văn Cừ", "Hoàng Diệu", "Bạch Đằng", "Hùng Vương", "Trần Hưng Đạo"
]
districts = [
    "Quận 1", "Quận 3", "Quận 7", "Quận Bình Thạnh", "Quận Tân Bình",
    "Quận Gò Vấp", "Quận 5", "Quận 10", "Quận 2", "Quận Phú Nhuận",
    "Quận 4", "Quận Thủ Đức", "Huyện Bình Chánh", "Huyện Hóc Môn", "Huyện Cần Giờ"
]
cities = [
    "Hồ Chí Minh", "Hà Nội", "Đà Nẵng", "Hải Phòng", "Cần Thơ",
    "Huế", "Vinh", "Nha Trang", "Quy Nhơn", "Buôn Ma Thuột"
]

# Helper function to generate a Vietnamese-style phone number
def generate_vietnamese_phone():
    return f"0{random.randint(90, 99)}{random.randint(1000000, 9999999)}"

# Generate unique patient data
def generate_patient_data(patient_id):
    genders = ["Nam", "Nữ"]
    blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    chronic_conditions = [
        "Tiểu đường type 1", "Cao huyết áp", "Hen suyễn", "Suy thận mạn", "Loãng xương", "không"
    ]
    allergies = [
        "Penicillin", "Đậu phộng", "Hải sản", "Sữa", "Lông động vật", "Phấn hoa", "không"
    ]
    procedures = ["Phẫu thuật ruột thừa", "Phẫu thuật túi mật", "không"]
    medications = ["Metformin", "Losartan", "Paracetamol", "không"]
    exercises = ["1 lần/tuần", "3 lần/tuần", "Không tập"]
    diets = ["Bình thường", "Ăn chay", "Thấp đường", "Thấp muối"]

    # Generate basic information
    name = f"{random.choice(first_names)} {random.choice(middle_names)} {random.choice(last_names)}"
    address = f"Số {random.randint(1, 999)}, đường {random.choice(streets)}, {random.choice(districts)}, {random.choice(cities)}"
    phone = generate_vietnamese_phone()
    gender = random.choice(genders)

    return {
        "patient_id": patient_id,
        "basic_info": {
            "name": name,
            "date_of_birth": fake.date_of_birth(minimum_age=1, maximum_age=85).strftime("%Y-%m-%d"),
            "gender": gender,
            "blood_type": random.choice(blood_types),
            "contact": {
                "phone": phone,
                "address": address
            },
            "emergency_contact": {
                "name": f"{random.choice(first_names)} {random.choice(middle_names)} {random.choice(last_names)}",
                "relationship": random.choice(["Vợ", "Chồng", "Con", "Cha", "Mẹ", "Anh", "Chị","Em"]),
                "phone": generate_vietnamese_phone()
            }
        },
        "medical_history": {
            "chronic_conditions": random.sample(chronic_conditions, k=random.randint(1, 3)),
            "allergies": random.sample(allergies, k=random.randint(1, 3)),
            "past_surgeries": [
                {"procedure": random.choice(procedures), "date": fake.date_between(start_date='-10y', end_date='today').strftime("%Y-%m-%d")}
            ] if random.choice([True, False]) else "không",
            "current_medications": [
                {"name": random.choice(medications), "dosage": f"{random.randint(1, 3) * 500}mg", "frequency": f"{random.randint(1, 3)} lần/ngày"}
            ] if random.choice([True, False]) else "không"
        },
        "lifestyle": {
            "smoking": random.choice(["Có", "Không"]),
            "alcohol": random.choice(["Không", "Thỉnh thoảng", "Thường xuyên"]),
            "exercise": random.choice(exercises),
            "diet": random.choice(diets)
        }
    }

# Generate patient data for 10 patients
patients_data = {"patients": [generate_patient_data(f"P{str(i).zfill(3)}") for i in range(1, 100)]}

# Save the JSON to a file
output_file = "patients_data.json"
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(patients_data, file, indent=2, ensure_ascii=False)

print(f"Patient data has been saved to {output_file}")
