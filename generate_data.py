import google.generativeai as genai
import os
import time

# 1. CẤU HÌNH API KEY
API_KEY = "trong_đây_bạn_nhập_api_key_của_bạn"
genai.configure(api_key=API_KEY)

# 2. HÀM TỰ ĐỘNG DÒ TÌM MODEL (Khắc phục triệt để lỗi 404)
def get_available_model():
    print("🔍 Đang quét danh sách model tương thích với API Key của bạn...")
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except Exception as e:
        print("❌ Lỗi kết nối API Key:", e)
        return None

    if not models:
        print("❌ API Key không có quyền truy cập model nào.")
        return None

    # Tự động ưu tiên chọn bản flash hoặc pro nếu có, nếu không lấy model đầu tiên khả dụng
    chosen_model = models[0] 
    for m in models:
        if 'flash' in m:
            chosen_model = m
            break
        elif 'pro' in m:
            chosen_model = m

    chosen_model = chosen_model.replace('models/', '')
    print(f"✅ Đã tìm thấy! Tự động kết nối với model: {chosen_model}")
    return genai.GenerativeModel(chosen_model)

# 3. HÀM GỌI AI
def generate_lesson_json(model, lop, mon, tuan, yeu_cau_can_dat):
    prompt = f"""
    Bạn là chuyên gia giáo dục. Soạn bài học chuyển tiếp cho môn {mon.upper()}, Lớp {lop}, Tuần {tuan}.
    Yêu cầu cần đạt: "{yeu_cau_can_dat}". Tuyệt đối không chép sách giáo khoa.
    
    CHỈ TRẢ VỀ ĐÚNG ĐỊNH DẠNG JSON SAU, KHÔNG GIẢI THÍCH THÊM:
    {{
        "title": "Tiêu đề bài học ngắn gọn",
        "objective": "Mục tiêu cốt lõi của bài",
        "theory": "Tóm tắt lý thuyết dưới 150 chữ",
        "exercises": ["Bài tập 1: ...", "Bài tập 2: ..."]
    }}
    """
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            return response.text.replace("```json", "").replace("```", "").strip()
        except Exception as e:
            print(f"   ⚠️ Lỗi (lần {attempt + 1}/3): {e}")
            time.sleep(3)
    return None

# 4. LUỒNG DỮ LIỆU TỰ ĐỘNG
def run_pipeline():
    model = get_available_model()
    if not model:
        return

    os.makedirs("data", exist_ok=True)
    khung_gdpt_tho = [
        {"lop": 10, "mon": "toan", "tuan": 2, "yeu_cau_can_dat": "Hiểu khái niệm tập hợp, các phép toán trên tập hợp (giao, hợp, hiệu)."},
        {"lop": 10, "mon": "van", "tuan": 1, "yeu_cau_can_dat": "Nhận biết và phân tích được một số yếu tố của thần thoại: không gian, thời gian, cốt truyện, nhân vật."},
        {"lop": 10, "mon": "van", "tuan": 2, "yeu_cau_can_dat": "Phân tích được chủ đề, thông điệp của văn bản thần thoại; phân tích được các chi tiết tiêu biểu."}
    ]

    print("🚀 Bắt đầu hệ thống sinh dữ liệu...")
    for item in khung_gdpt_tho:
        file_name = f"data/lop{item['lop']}_{item['mon']}_tuan{item['tuan']}.json"
        print(f"⏳ Đang xử lý: {file_name}...")
        
        json_data = generate_lesson_json(model, item['lop'], item['mon'], item['tuan'], item['yeu_cau_can_dat'])
        
        if json_data:
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(json_data)
            print(f"✅ Hoàn tất: {file_name}")
        else:
            print(f"❌ THẤT BẠI tại {file_name}")
        time.sleep(2)

if __name__ == "__main__":
    run_pipeline()