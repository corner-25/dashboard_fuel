# 🚗⛽ Dashboard Quản Lý Xăng Dầu

Dashboard Streamlit để quản lý và phân tích dữ liệu tiêu thụ xăng dầu theo xe.

## ✨ Tính năng

### 📊 **Thống kê tổng quan**
- Tổng lượng nhiên liệu tiêu thụ
- Phân biệt xăng và dầu diesel
- Thống kê đổ ngoài hệ thống
- Số lượng xe

### 📋 **Thống kê theo xe**
- Bảng chi tiết từng xe
- Export Excel với nhiều sheet
- Thông tin ngày đầu/cuối đổ xăng
- Tính trung bình lít/lần đổ

### 📈 **Phân tích trực quan**
- Biểu đồ theo thời gian
- So sánh xăng vs dầu
- Top xe tiêu thụ nhiều nhất
- Phân tích theo ngày trong tuần

### 🔍 **Bộ lọc thông minh**
- Lọc theo khoảng thời gian
- Lọc theo loại nhiên liệu
- Lọc theo xe cụ thể

## 🚀 Cách sử dụng

1. Upload file Excel với định dạng:
   - Cột 1: Ngày (dd/mm/yyyy)
   - Cột 2: Biển số xe
   - Cột 3: Số lít
   - Cột 4: Đổ ngoài hệ thống

2. Sử dụng bộ lọc để xem dữ liệu theo nhu cầu

3. Export báo cáo Excel hoặc CSV

## 📝 Ghi chú
- 🚛 Xe 50A01990: Dầu diesel
- 🚗 Các xe khác: Xăng
- Dữ liệu trong hệ thống = Tổng lít - Đổ ngoài hệ thống

## 🛠️ Công nghệ sử dụng
- **Streamlit**: Framework web app
- **Pandas**: Xử lý dữ liệu
- **Plotly**: Biểu đồ tương tác
- **OpenPyXL**: Đọc/ghi Excel