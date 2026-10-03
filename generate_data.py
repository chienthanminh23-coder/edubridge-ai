import google.generativeai as genai
import os
import time

# 1. CẤU HÌNH API KEY
# BẠN HÃY DÁN LẠI KEY THẬT (AQ.Ab8RN6...) VÀO ĐÂY THAY CHO CHỮ "hehe"
API_KEY = "11"
genai.configure(api_key=API_KEY)

# 2. HÀM TỰ ĐỘNG DÒ TÌM MODEL (Đã khóa chặt mục tiêu vào bản 1.5 ổn định)
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

    # Bắt buộc chọn gemini-1.5-flash, né bản 2.5
    chosen_model = None
    for m in models:
        if 'gemini-1.5-flash' in m:
            chosen_model = m
            break
            
    if not chosen_model:
        for m in models:
            if '2.5' not in m: 
                chosen_model = m
                break
                
    if not chosen_model:
        chosen_model = models[0]

    chosen_model = chosen_model.replace('models/', '')
    print(f"✅ Đã tìm thấy và khóa mục tiêu vào model ổn định: {chosen_model}")
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
    mon_tieu_hoc = ["toan", "tiengviet", "anh", "tunhienxahoi", "daoduc", "tin", "nghethuat"]
    mon_trung_hoc = ["toan", "van", "anh", "ly", "hoa", "sinh", "su", "dia", "gdcd", "tin", "congnghe"]

    khung_gdpt_tho = []

    # 2. Thuật toán tự động sinh tổ hợp 12 khối lớp
    for lop in range(8, 13):
        # Lớp 1 đến 5 dùng mảng tiểu học, lớp 6 đến 12 dùng mảng trung học
        danh_sach_mon = mon_tieu_hoc if lop <= 5 else mon_trung_hoc
        
        for mon in danh_sach_mon:
            # Tạm thời chỉ quét Tuần 1 (Khoảng 120 bài học) để test hệ thống
            # Nếu muốn sinh cả 35 tuần, bạn có thể thêm: 
            for tuan in range(1, 2):
                khung_gdpt_tho.append({
                    "lop": lop,
                    "mon": mon,
                    "tuan": tuan,
                    # Yêu cầu tổng quát để AI tự động suy luận bám sát chương trình
                    "yeu_cau_can_dat": f"Tổng hợp lý thuyết và bài tập trọng tâm tuần {tuan} môn {mon} lớp {lop} theo chuẩn sách giáo khoa GDPT 2018."
                })

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