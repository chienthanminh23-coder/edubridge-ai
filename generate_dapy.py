import google.generativeai as genai
import os
import time

# 1. Cấu hình API Key
API_KEY = "ĐIỀN_API_KEY_CỦA_BẠN_VÀO_ĐÂY"
genai.configure(api_key=API_KEY)

# 2. Khởi tạo Model NÂNG CẤP (Pro + System Instruction + Schema)
model = genai.GenerativeModel(
    model_name='gemini-1.5-pro', # Đổi sang bản Pro thông minh hơn
    system_instruction="Bạn là một chuyên gia thiết kế chương trình giáo dục phổ thông xuất sắc tại Việt Nam. Nhiệm vụ của bạn là biên soạn tài liệu học tập ngắn gọn, dễ hiểu, bám sát Yêu cầu cần đạt của Bộ GD&ĐT mà không sao chép sách giáo khoa.",
    generation_config={
        "temperature": 0.3, # Giảm bay bổng, tăng tính chuẩn xác sư phạm
        "response_mime_type": "application/json",
        "response_schema": { # Ép cấu trúc dữ liệu nghiêm ngặt
            "type": "OBJECT",
            "properties": {
                "title": {"type": "STRING", "description": "Tiêu đề bài học ngắn gọn"},
                "objective": {"type": "STRING", "description": "Mục tiêu cốt lõi của bài"},
                "theory": {"type": "STRING", "description": "Tóm tắt lý thuyết trọng tâm dưới 150 chữ"},
                "exercises": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                    "description": "Danh sách 2 bài tập vận dụng"
                }
            },
            "required": ["title", "objective", "theory", "exercises"]
        }
    }
)

# 3. Hàm gọi AI (Prompt giờ đây cực kỳ ngắn gọn và sạch sẽ)
def generate_lesson_json(lop, mon, tuan, yeu_cau_can_dat):
    prompt = f'Soạn tài liệu chuyển tiếp cho môn {mon.upper()}, Lớp {lop}, Tuần {tuan}. Yêu cầu cần đạt: "{yeu_cau_can_dat}".'
    
    # Thử gọi API tối đa 3 lần nếu gặp lỗi (Retry logic - Kỹ năng của Senior)
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"   ⚠️ Lỗi mạng/API (lần {attempt + 1}/3): {e}. Đang thử lại...")
            time.sleep(3)
    
    raise Exception("Không thể kết nối với AI sau 3 lần thử.")

# 4. Luồng Dữ liệu (Data Pipeline)
def run_pipeline():
    os.makedirs("data", exist_ok=True)

    khung_gdpt_tho = [
        {
            "lop": 10, "mon": "toan", "tuan": 2, 
            "yeu_cau_can_dat": "Hiểu khái niệm tập hợp, các phép toán trên tập hợp (giao, hợp, hiệu)."
        },
        {
            "lop": 10, "mon": "van", "tuan": 1, 
            "yeu_cau_can_dat": "Nhận biết và phân tích được một số yếu tố của thần thoại: không gian, thời gian, cốt truyện, nhân vật."
        },
        {
            "lop": 10, "mon": "van", "tuan": 2, 
            "yeu_cau_can_dat": "Phân tích được chủ đề, thông điệp của văn bản thần thoại; phân tích được các chi tiết tiêu biểu."
        }
    ]

    print("🚀 Bắt đầu quá trình sinh dữ liệu hàng loạt bằng Gemini 1.5 Pro...")
    
    for item in khung_gdpt_tho:
        file_name = f"data/lop{item['lop']}_{item['mon']}_tuan{item['tuan']}.json"
        print(f"⏳ Đang xử lý: {file_name}...")
        
        try:
            json_data = generate_lesson_json(item['lop'], item['mon'], item['tuan'], item['yeu_cau_can_dat'])
            
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(json_data)
                
            print(f"✅ Hoàn tất: {file_name}")
            time.sleep(3) # Tăng thời gian nghỉ vì bản Pro cần nhiều thời gian xử lý hơn
            
        except Exception as e:
            print(f"❌ THẤT BẠI tại {file_name}: {e}")

if __name__ == "__main__":
    run_pipeline()