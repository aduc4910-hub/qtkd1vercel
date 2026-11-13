"""
Main Execution Script for B2B Sales Opportunity Processing Agent
Đồ án AI301 | Đề 01 - Công ty Minh An
Hỗ trợ nạp bộ dữ liệu bất kỳ qua tham số dòng lệnh phục vụ chấm thi trực tiếp
"""

import sys
import json
import os
from src.rules import BusinessRulesEngine
from src.tools import InquiryProcessingTools
from src.logger import AuditLogger
from src.agent import B2BSalesAgent


def run_pipeline(data_file_path: str = "data/test_inquiries.json"):
    print("=" * 80)
    print("  HỆ THỐNG AI AGENT XỬ LÝ CƠ HỘI BÁN HÀNG B2B - CÔNG TY MINH AN")
    print("  Học phần: AI301 | Đề 01 | Phiên bản Kiểm thử Tự động")
    print("=" * 80)

    # 1. Nạp Master Data & Policies
    with open("data/products_inventory.json", "r", encoding="utf-8") as f:
        products = json.load(f)

    with open("data/business_policies.json", "r", encoding="utf-8") as f:
        policies = json.load(f)

    if not os.path.exists(data_file_path):
        print(f"[LỖI] Không tìm thấy tệp dữ liệu: {data_file_path}")
        return

    with open(data_file_path, "r", encoding="utf-8") as f:
        inquiries = json.load(f)

    print(f"-> Đã nạp {len(products)} sản phẩm từ danh mục niêm yết.")
    print(f"-> Đã nạp quy tắc nghiệp vụ từ chính sách chiết khấu & thẩm quyền.")
    print(f"-> Đang xử lý {len(inquiries)} yêu cầu từ tệp: {data_file_path}\n")

    # 2. Khởi tạo Agent & Engine
    rules_engine = BusinessRulesEngine(policies, products)
    tools = InquiryProcessingTools(rules_engine)
    logger = AuditLogger(log_dir="outputs/logs")
    agent = B2BSalesAgent(tools, policies, logger)

    results = []
    status_counts = {
        "Có thể tiếp tục": 0,
        "Cần bổ sung thông tin": 0,
        "Chưa đáp ứng": 0,
        "Chờ duyệt": 0,
    }
    total_eligible_value = 0.0

    # 3. Chạy xử lý tuần tự từng yêu cầu
    for idx, inq in enumerate(inquiries, 1):
        inq_id = inq.get("inquiry_id", f"REQ-{idx}")
        cust_name = inq.get("customer_name", "Không rõ")
        category = inq.get("case_category", "N/A")

        print(f"[{idx}/{len(inquiries)}] Đang xử lý {inq_id} ({cust_name})")
        print(f"    Phân loại thử nghiệm: {category}")

        res = agent.process_inquiry(inq)
        results.append(res)

        status = res["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

        if res["eligible_for_pipeline"]:
            total_eligible_value += res["final_total"]
            print(f"    => Trạng thái: [{status}] | Giá trị: {res['final_total']:,.0f} VND | Phụ trách: {res['assigned_rep']['name']}")
        else:
            print(f"    => Trạng thái: [{status}] | Phụ trách: {res['assigned_rep']['name']}")

        # Xuất file nhật ký truy vết dạng đọc được
        logger.export_readable_log(inq_id)
        print()

    # 4. Tạo Bảng Tổng Hợp Số Liệu (Dashboard Summary)
    summary_data = {
        "total_inquiries": len(inquiries),
        "status_breakdown": status_counts,
        "total_eligible_pipeline_value_vnd": total_eligible_value,
        "currency": "VND",
        "detailed_results": results,
    }

    with open("outputs/summary_dashboard.json", "w", encoding="utf-8") as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)

    # In Bảng Tổng Hợp ra màn hình console
    print("=" * 80)
    print("                      BẢNG TỔNG HỢP CƠ HỘI BÁN HÀNG B2B")
    print("=" * 80)
    print(f"1. Tổng số cơ hội tiếp nhận:       {len(inquiries)} cơ hội")
    print(f"2. Có thể tiếp tục (Qualified):    {status_counts.get('Có thể tiếp tục', 0)} cơ hội")
    print(f"3. Cần bổ sung thông tin:          {status_counts.get('Cần bổ sung thông tin', 0)} cơ hội")
    print(f"4. Chưa đáp ứng (Unfulfillable):   {status_counts.get('Chưa đáp ứng', 0)} cơ hội")
    print(f"5. Chờ duyệt (Pending Approval):   {status_counts.get('Chờ duyệt', 0)} cơ hội")
    print("-" * 80)
    print(f">> TỔNG GIÁ TRỊ CÁC CƠ HỘI ĐỦ ĐIỀU KIỆN TIẾP TỤC HOẶC CHỜ DUYỆT: {total_eligible_value:,.0f} VND")
    print("=" * 80)
    print("Tất cả Hồ sơ Cơ hội (.md), Bản nháp Email (.txt) và Nhật ký truy vết (.jsonl, .txt)")
    print("đã được ghi đầy đủ tại thư mục: outputs/\n")

    # Lưu bản Markdown của Dashboard
    md_summary = f"""# BẢNG TỔNG HỢP KẾT QUẢ XỬ LÝ CƠ HỘI BÁN HÀNG B2B - CÔNG TY MINH AN
- Thời gian trích xuất: {summary_data.get('total_inquiries')} hồ sơ
- Tệp dữ liệu đầu vào: `{data_file_path}`

| Chỉ số / Trạng thái | Số lượng cơ hội | Tỷ lệ (%) | Ghi chú hành động tiếp theo |
|---|---|---|---|
| **Có thể tiếp tục (Qualified / Ready)** | **{status_counts.get('Có thể tiếp tục', 0)}** | {status_counts.get('Có thể tiếp tục', 0)/len(inquiries)*100:.1f}% | NVKD kiểm tra bản nháp & gửi báo giá chính thức |
| **Cần bổ sung thông tin (Need Info)** | **{status_counts.get('Cần bổ sung thông tin', 0)}** | {status_counts.get('Cần bổ sung thông tin', 0)/len(inquiries)*100:.1f}% | Tự động gửi email nháp đề nghị KH làm rõ dữ liệu |
| **Chưa đáp ứng (Unfulfillable)** | **{status_counts.get('Chưa đáp ứng', 0)}** | {status_counts.get('Chưa đáp ứng', 0)/len(inquiries)*100:.1f}% | Gửi email từ chối lịch sự & đề xuất giải pháp thay thế |
| **Chờ duyệt (Pending Approval)** | **{status_counts.get('Chờ duyệt', 0)}** | {status_counts.get('Chờ duyệt', 0)/len(inquiries)*100:.1f}% | Chuyển phiếu duyệt Escalation Ticket cho Trưởng phòng |
| **TỔNG CỘNG** | **{len(inquiries)}** | 100% | 6 NVKD được chia đều hồ sơ theo vòng tròn |

### DOANH THU CƠ HỘI TIỀM NĂNG:
> **TỔNG GIÁ TRỊ CÁC CƠ HỘI ĐỦ ĐIỀU KIỆN TIẾP TỤC HOẶC CHỜ DUYỆT:** **{total_eligible_value:,.0f} VND**
*(Chỉ bao gồm các cơ hội đã kiểm tra tính khả thi tồn kho, thời hạn và thỏa mãn ngân sách)*

### DANH SÁCH CHI TIẾT CÁC CƠ HỘI:
| Mã YC | Khách hàng | Trạng thái | Giá trị đề xuất (VND) | NVKD phụ trách | Tóm tắt căn cứ |
|---|---|---|---|---|---|
"""
    for r in results:
        val_str = f"{r['final_total']:,.0f}" if r['final_total'] > 0 else "-"
        md_summary += f"| {r['inquiry_id']} | {r['customer_name']} | **{r['status']}** | {val_str} | {r['assigned_rep']['name']} | {r['summary'][:60]}... |\n"

    with open("outputs/summary_dashboard.md", "w", encoding="utf-8") as f:
        f.write(md_summary)


if __name__ == "__main__":
    data_path = sys.argv[1] if len(sys.argv) > 1 else "data/test_inquiries.json"
    run_pipeline(data_path)

