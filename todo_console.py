import json
import os
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional

# ================== CẤU HÌNH ==================
FILE_NAME = "todo_data.json"
PRIORITY_OPTIONS = {
    "1": {"label": "🔴 Ưu tiên Cao", "weight": 3},
    "2": {"label": "🟡 Trung bình", "weight": 2},
    "3": {"label": "🟢 Ưu tiên Thấp", "weight": 1}
}

# ================== HÀM HỖ TRỢ ==================
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_data() -> List[Dict]:
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_data(tasks: List[Dict]):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def get_days_left(deadline_str: str, completed: bool) -> str:
    if completed:
        return "✅ Hoàn thành"
    try:
        dl_date = datetime.strptime(deadline_str, "%Y-%m-%d").date()
        diff = (dl_date - date.today()).days
        
        if diff < 0:
            return f"⚠️ Quá hạn {abs(diff)} ngày"
        elif diff == 0:
            return "🔥 Hạn hôm nay"
        elif diff <= 2:
            return f"⏳ Còn {diff} ngày"
        else:
            return f"📅 Còn {diff} ngày"
    except:
        return "❓ Không rõ hạn"

def get_priority_display(weight: int) -> str:
    for key, val in PRIORITY_OPTIONS.items():
        if val["weight"] == weight:
            return val["label"]
    return "🟡 Trung bình"

def sort_tasks(tasks: List[Dict]) -> List[Dict]:
    """Sắp xếp: Chưa xong trước → Ưu tiên cao → Deadline gần"""
    return sorted(
        tasks,
        key=lambda x: (x["completed"], -x["priority_weight"], x["deadline"])
    )

def display_tasks(tasks: List[Dict], title: str = "DANH SÁCH CÔNG VIỆC"):
    clear_screen()
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")
    
    if not tasks:
        print("🎉 Không có công việc nào!")
        return
    
    for i, task in enumerate(tasks, 1):
        days_text = get_days_left(task["deadline"], task["completed"])
        priority_text = get_priority_display(task["priority_weight"])
        
        status = "✅" if task["completed"] else "❌"
        text_display = task["text"]
        
        print(f"\n{i}. {status} {text_display}")
        print(f"   📌 {priority_text}")
        print(f"   📅 Hạn: {task['deadline']}  →  {days_text}")
        print(f"   🆔 ID: {task['id'][:8]}...")

def find_task_by_id(tasks: List[Dict], task_id: str) -> Optional[Dict]:
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None

def find_task_by_index(tasks: List[Dict], index: int) -> Optional[Dict]:
    if 1 <= index <= len(tasks):
        return tasks[index - 1]
    return None

# ================== CHỨC NĂNG CHÍNH ==================
def add_task(tasks: List[Dict]):
    clear_screen()
    print("\n➕ THÊM CÔNG VIỆC MỚI")
    print("-" * 40)
    
    text = input("📝 Nội dung công việc: ").strip()
    if not text:
        print("❌ Nội dung không được để trống!")
        input("\nNhấn Enter để tiếp tục...")
        return
    
    # Ngày hết hạn
    while True:
        try:
            deadline_str = input("📅 Ngày hết hạn (YYYY-MM-DD) [Enter = hôm nay + 3 ngày]: ").strip()
            if not deadline_str:
                deadline = date.today() + timedelta(days=3)
            else:
                deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()
            break
        except ValueError:
            print("❌ Định dạng ngày không hợp lệ! Ví dụ: 2026-05-10")
    
    # Mức ưu tiên
    print("\nMức ưu tiên:")
    print("1. 🔴 Cao")
    print("2. 🟡 Trung bình")
    print("3. 🟢 Thấp")
    
    while True:
        choice = input("Chọn mức ưu tiên (1-3): ").strip()
        if choice in PRIORITY_OPTIONS:
            priority_data = PRIORITY_OPTIONS[choice]
            break
        print("❌ Vui lòng chọn 1, 2 hoặc 3!")
    
    new_task = {
        "id": str(datetime.now().timestamp()),
        "text": text,
        "completed": False,
        "deadline": str(deadline),
        "priority_label": priority_data["label"],
        "priority_weight": priority_data["weight"]
    }
    
    tasks.append(new_task)
    save_data(tasks)
    print("\n✅ Đã thêm công việc mới thành công!")
    input("\nNhấn Enter để tiếp tục...")

def edit_task(tasks: List[Dict]):
    clear_screen()
    print("\n✏️ CHỈNH SỬA CÔNG VIỆC")
    print("-" * 40)
    
    sorted_tasks = sort_tasks(tasks)
    display_tasks(sorted_tasks, "CHỌN CÔNG VIỆC ĐỂ SỬA")
    
    if not sorted_tasks:
        return
    
    try:
        choice = int(input("\nNhập số thứ tự công việc cần sửa (0 để hủy): "))
        if choice == 0:
            return
        
        task = find_task_by_index(sorted_tasks, choice)
        if not task:
            print("❌ Số thứ tự không hợp lệ!")
            input("\nNhấn Enter để tiếp tục...")
            return
        
        print(f"\nĐang sửa: {task['text']}")
        
        # Sửa nội dung
        new_text = input(f"Nội dung mới [{task['text']}]: ").strip()
        if new_text:
            task["text"] = new_text
        
        # Sửa deadline
        while True:
            new_deadline = input(f"Ngày hết hạn mới [{task['deadline']}]: ").strip()
            if not new_deadline:
                break
            try:
                datetime.strptime(new_deadline, "%Y-%m-%d")
                task["deadline"] = new_deadline
                break
            except ValueError:
                print("❌ Định dạng ngày không hợp lệ!")
        
        # Sửa ưu tiên
        print("\nMức ưu tiên mới:")
        print("1. 🔴 Cao  |  2. 🟡 Trung bình  |  3. 🟢 Thấp")
        new_priority = input(f"Chọn (1-3) [{task['priority_weight']}]: ").strip()
        
        if new_priority in PRIORITY_OPTIONS:
            task["priority_label"] = PRIORITY_OPTIONS[new_priority]["label"]
            task["priority_weight"] = PRIORITY_OPTIONS[new_priority]["weight"]
        
        save_data(tasks)
        print("\n✅ Đã cập nhật công việc!")
        
    except ValueError:
        print("❌ Vui lòng nhập số hợp lệ!")
    
    input("\nNhấn Enter để tiếp tục...")

def toggle_complete(tasks: List[Dict]):
    clear_screen()
    print("\n🔄 ĐÁNH DẤU HOÀN THÀNH / CHƯA XONG")
    print("-" * 40)
    
    sorted_tasks = sort_tasks(tasks)
    display_tasks(sorted_tasks, "CHỌN CÔNG VIỆC")
    
    if not sorted_tasks:
        return
    
    try:
        choice = int(input("\nNhập số thứ tự công việc (0 để hủy): "))
        if choice == 0:
            return
        
        task = find_task_by_index(sorted_tasks, choice)
        if not task:
            print("❌ Số thứ tự không hợp lệ!")
            input("\nNhấn Enter để tiếp tục...")
            return
        
        task["completed"] = not task["completed"]
        status = "hoàn thành" if task["completed"] else "chưa hoàn thành"
        save_data(tasks)
        print(f"\n✅ Đã đánh dấu công việc là {status}!")
        
    except ValueError:
        print("❌ Vui lòng nhập số hợp lệ!")
    
    input("\nNhấn Enter để tiếp tục...")

def delete_task(tasks: List[Dict]):
    clear_screen()
    print("\n🗑️ XÓA CÔNG VIỆC")
    print("-" * 40)
    
    sorted_tasks = sort_tasks(tasks)
    display_tasks(sorted_tasks, "CHỌN CÔNG VIỆC ĐỂ XÓA")
    
    if not sorted_tasks:
        return
    
    try:
        choice = int(input("\nNhập số thứ tự công việc cần xóa (0 để hủy): "))
        if choice == 0:
            return
        
        task = find_task_by_index(sorted_tasks, choice)
        if not task:
            print("❌ Số thứ tự không hợp lệ!")
            input("\nNhấn Enter để tiếp tục...")
            return
        
        confirm = input(f"\nBạn có chắc muốn xóa '{task['text']}'? (y/n): ").lower()
        if confirm == 'y':
            tasks.remove(task)
            save_data(tasks)
            print("\n✅ Đã xóa công việc!")
        else:
            print("\n❌ Đã hủy xóa.")
        
    except ValueError:
        print("❌ Vui lòng nhập số hợp lệ!")
    
    input("\nNhấn Enter để tiếp tục...")

def search_tasks(tasks: List[Dict]):
    clear_screen()
    print("\n🔍 TÌM KIẾM CÔNG VIỆC")
    print("-" * 40)
    
    keyword = input("Nhập từ khóa tìm kiếm: ").strip().lower()
    if not keyword:
        return
    
    results = [t for t in tasks if keyword in t["text"].lower()]
    
    if not results:
        print(f"\n❌ Không tìm thấy công việc nào chứa '{keyword}'")
    else:
        sorted_results = sort_tasks(results)
        display_tasks(sorted_results, f"KẾT QUẢ TÌM KIẾM: '{keyword}'")
    
    input("\nNhấn Enter để tiếp tục...")

def clear_completed(tasks: List[Dict]):
    clear_screen()
    print("\n🗑️ XÓA TẤT CẢ CÔNG VIỆC ĐÃ HOÀN THÀNH")
    print("-" * 40)
    
    completed_count = sum(1 for t in tasks if t["completed"])
    
    if completed_count == 0:
        print("🎉 Không có công việc nào đã hoàn thành!")
        input("\nNhấn Enter để tiếp tục...")
        return
    
    confirm = input(f"Bạn có chắc muốn xóa {completed_count} công việc đã hoàn thành? (y/n): ").lower()
    
    if confirm == 'y':
        tasks[:] = [t for t in tasks if not t["completed"]]
        save_data(tasks)
        print(f"\n✅ Đã xóa {completed_count} công việc!")
    else:
        print("\n❌ Đã hủy thao tác.")
    
    input("\nNhấn Enter để tiếp tục...")

def show_statistics(tasks: List[Dict]):
    clear_screen()
    print("\n📊 THỐNG KÊ CÔNG VIỆC")
    print("-" * 40)
    
    total = len(tasks)
    completed = sum(1 for t in tasks if t["completed"])
    pending = total - completed
    
    high = sum(1 for t in tasks if t["priority_weight"] == 3 and not t["completed"])
    medium = sum(1 for t in tasks if t["priority_weight"] == 2 and not t["completed"])
    low = sum(1 for t in tasks if t["priority_weight"] == 1 and not t["completed"])
    
    print(f"Tổng số công việc     : {total}")
    print(f"Đã hoàn thành         : {completed} ({completed/total*100:.1f}%)" if total > 0 else "Đã hoàn thành         : 0")
    print(f"Còn lại               : {pending}")
    print()
    print("📌 Theo mức ưu tiên (chưa xong):")
    print(f"   🔴 Cao     : {high}")
    print(f"   🟡 Trung bình: {medium}")
    print(f"   🟢 Thấp    : {low}")
    
    input("\nNhấn Enter để tiếp tục...")

# ================== MENU CHÍNH ==================
def main_menu():
    tasks = load_data()
    
    while True:
        clear_screen()
        print("\n" + "="*60)
        print("✨ CÔNG VIỆC CỦA TÔI - To-Do List (Console)")
        print("="*60)
        print("1. 📋 Xem tất cả công việc")
        print("2. ⏳ Xem công việc chưa xong")
        print("3. ✅ Xem công việc đã xong")
        print("4. ➕ Thêm công việc mới")
        print("5. ✏️  Sửa công việc")
        print("6. 🔄 Đánh dấu hoàn thành / Chưa xong")
        print("7. 🗑️  Xóa công việc")
        print("8. 🔍 Tìm kiếm công việc")
        print("9. 🗑️  Xóa tất cả đã hoàn thành")
        print("10. 📊 Thống kê")
        print("0. 🚪 Thoát")
        print("-" * 60)
        
        choice = input("Chọn chức năng (0-10): ").strip()
        
        if choice == "1":
            sorted_tasks = sort_tasks(tasks)
            display_tasks(sorted_tasks, "TẤT CẢ CÔNG VIỆC")
            input("\nNhấn Enter để quay lại menu...")
        elif choice == "2":
            pending = [t for t in tasks if not t["completed"]]
            sorted_pending = sort_tasks(pending)
            display_tasks(sorted_pending, "CÔNG VIỆC CHƯA XONG")
            input("\nNhấn Enter để quay lại menu...")
        elif choice == "3":
            done = [t for t in tasks if t["completed"]]
            sorted_done = sort_tasks(done)
            display_tasks(sorted_done, "CÔNG VIỆC ĐÃ XONG")
            input("\nNhấn Enter để quay lại menu...")
        elif choice == "4":
            add_task(tasks)
        elif choice == "5":
            edit_task(tasks)
        elif choice == "6":
            toggle_complete(tasks)
        elif choice == "7":
            delete_task(tasks)
        elif choice == "8":
            search_tasks(tasks)
        elif choice == "9":
            clear_completed(tasks)
        elif choice == "10":
            show_statistics(tasks)
        elif choice == "0":
            print("\n👋 Cảm ơn bạn đã sử dụng! Hẹn gặp lại.")
            break
        else:
            print("❌ Lựa chọn không hợp lệ!")
            input("\nNhấn Enter để tiếp tục...")

# ================== CHẠY CHƯƠNG TRÌNH ==================
if __name__ == "__main__":
    main_menu()