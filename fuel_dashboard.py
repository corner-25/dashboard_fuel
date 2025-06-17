import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Cấu hình trang
st.set_page_config(
    page_title="Dashboard Quản Lý Xăng Dầu",
    page_icon="⛽",
    layout="wide"
)

@st.cache_data
def load_data():
    """Đọc dữ liệu Excel"""
    try:
        # Đọc file Excel
        df = pd.read_excel('Du lieu xang dau theo xe.xlsx')
        
        # Đổi tên cột để dễ xử lý
        df.columns = ['Ngay', 'BSX', 'Lit', 'Do_ngoai_he_thong']
        
        # Chuyển đổi cột ngày (dữ liệu đã được xử lý thành dd/mm/yyyy)
        df['Ngay'] = pd.to_datetime(df['Ngay'], dayfirst=True, errors='coerce')
        
        # Làm sạch dữ liệu
        df = df.dropna(subset=['Ngay', 'BSX'])
        df['BSX'] = df['BSX'].astype(str)
        df['Lit'] = pd.to_numeric(df['Lit'], errors='coerce').fillna(0)
        df['Do_ngoai_he_thong'] = pd.to_numeric(df['Do_ngoai_he_thong'], errors='coerce').fillna(0)
        
        # Tính toán các cột bổ sung
        df['Lit_he_thong'] = df['Lit'] - df['Do_ngoai_he_thong']
        df['Thang'] = df['Ngay'].dt.to_period('M').astype(str)
        df['Tuan'] = df['Ngay'].dt.to_period('W').astype(str)
        
        # Phân loại loại nhiên liệu
        df['Loai_nhien_lieu'] = df['BSX'].apply(lambda x: 'Dầu' if '50A01990' in str(x) else 'Xăng')
        
        return df
    except Exception as e:
        st.error(f"Lỗi đọc dữ liệu: {str(e)}")
        return pd.DataFrame()

def create_vehicle_summary_table(df_filtered):
    """Tạo bảng thống kê nhiên liệu theo xe"""
    if df_filtered.empty:
        return pd.DataFrame()
    
    # Thống kê theo xe
    vehicle_stats = df_filtered.groupby(['BSX', 'Loai_nhien_lieu']).agg({
        'Lit': ['sum', 'mean', 'count'],
        'Do_ngoai_he_thong': 'sum',
        'Lit_he_thong': 'sum',
        'Ngay': ['min', 'max']
    }).round(2)
    
    # Làm phẳng MultiIndex columns
    vehicle_stats.columns = [
        'Tổng lít', 'TB lít/lần', 'Số lần đổ', 
        'Lít đổ ngoài', 'Lít đổ trong HT', 
        'Ngày đầu', 'Ngày cuối'
    ]
    
    # Reset index để có BSX và Loại nhiên liệu thành cột
    vehicle_stats = vehicle_stats.reset_index()
    
    # Sắp xếp theo tổng lít giảm dần
    vehicle_stats = vehicle_stats.sort_values('Tổng lít', ascending=False)
    
    # Format ngày
    vehicle_stats['Ngày đầu'] = vehicle_stats['Ngày đầu'].dt.strftime('%d/%m/%Y')
    vehicle_stats['Ngày cuối'] = vehicle_stats['Ngày cuối'].dt.strftime('%d/%m/%Y')
    
    return vehicle_stats

def main():
    # Header với logo bên trái, text căn giữa
    col1, col2, col3 = st.columns([2, 6, 2])
    with col1:
        try:
            st.image("logo.png", width=120)
        except:
            st.write("")  # Để trống nếu không có logo
    with col2:
        st.markdown("""
        <div style="display: flex; align-items: center; height: 120px; justify-content: center;">
            <div style="text-align: center;">
                <h1 style="margin: 0; color: #2E86AB; font-size: 3rem; line-height: 1.2;">
                    Dashboard Quản lý xăng dầu<br>
                    Bệnh viện Đại học Y Dược TP. HCM
                </h1>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.write("")  # Để trống để cân đối
    
    st.markdown("---")
    
    # Load dữ liệu
    df = load_data()
    
    if df.empty:
        st.error("Không thể đọc dữ liệu. Vui lòng kiểm tra file Excel.")
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Bộ Lọc")
    
    # Filter theo ngày
    min_date = df['Ngay'].min().date()
    max_date = df['Ngay'].max().date()
    
    st.sidebar.subheader("Khoảng thời gian")
    date_range = st.sidebar.date_input(
        "Chọn khoảng thời gian:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Filter theo loại nhiên liệu
    st.sidebar.subheader("Loại nhiên liệu")
    fuel_types = st.sidebar.multiselect(
        "Chọn loại nhiên liệu:",
        options=['Xăng', 'Dầu'],
        default=['Xăng', 'Dầu']
    )
    
    # Filter theo xe
    st.sidebar.subheader("Xe")
    all_vehicles = sorted(df['BSX'].unique())
    selected_vehicles = st.sidebar.multiselect(
        "Chọn xe (để trống = chọn tất cả):",
        options=all_vehicles,
        default=[]
    )
    
    # Áp dụng filters
    df_filtered = df.copy()
    
    # Filter theo thời gian
    if len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df_filtered[
            (df_filtered['Ngay'].dt.date >= start_date) & 
            (df_filtered['Ngay'].dt.date <= end_date)
        ]
    
    # Filter theo loại nhiên liệu
    if fuel_types:
        df_filtered = df_filtered[df_filtered['Loai_nhien_lieu'].isin(fuel_types)]
    
    # Filter theo xe
    if selected_vehicles:
        df_filtered = df_filtered[df_filtered['BSX'].isin(selected_vehicles)]
    
    # Thống kê tổng quan
    st.header("📊 Thống Kê Tổng Quan")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_fuel = df_filtered['Lit'].sum()
        st.metric("Tổng lít nhiên liệu", f"{total_fuel:,.0f}", "lít")
    
    with col2:
        total_gasoline = df_filtered[df_filtered['Loai_nhien_lieu'] == 'Xăng']['Lit'].sum()
        st.metric("🚗 Tổng lít xăng", f"{total_gasoline:,.0f}", "lít")
    
    with col3:
        total_diesel = df_filtered[df_filtered['Loai_nhien_lieu'] == 'Dầu']['Lit'].sum()
        st.metric("🚛 Tổng lít dầu", f"{total_diesel:,.0f}", "lít")
    
    with col4:
        total_outside = df_filtered['Do_ngoai_he_thong'].sum()
        st.metric("Đổ ngoài hệ thống", f"{total_outside:,.0f}", "lít")
    
    with col5:
        total_vehicles = df_filtered['BSX'].nunique()
        st.metric("Số xe", f"{total_vehicles}", "xe")
    
    st.markdown("---")
    
    # Tabs cho các phân tích
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Thống kê theo xe", "📊 Tổng quan", "⛽ Xăng vs Dầu", "📅 Theo thời gian", "📋 Dữ liệu chi tiết"])
    
    with tab1:
        st.header("📋 Thống Kê Nhiên Liệu Theo Xe")
        
        if not df_filtered.empty:
            vehicle_summary = create_vehicle_summary_table(df_filtered)
            
            if not vehicle_summary.empty:
                # Hiển thị bảng
                st.dataframe(
                    vehicle_summary,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Nút download Excel
                from io import BytesIO
                output = BytesIO()
                
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    vehicle_summary.to_excel(writer, sheet_name='Thống kê theo xe', index=False)
                    
                    # Thêm sheet dữ liệu chi tiết
                    detail_data = df_filtered[['Ngay', 'BSX', 'Loai_nhien_lieu', 'Lit', 'Do_ngoai_he_thong', 'Lit_he_thong']].copy()
                    detail_data['Ngay'] = detail_data['Ngay'].dt.strftime('%d/%m/%Y')
                    detail_data.columns = ['Ngày', 'Biển số xe', 'Loại NL', 'Tổng lít', 'Đổ ngoài HT', 'Đổ trong HT']
                    detail_data.to_excel(writer, sheet_name='Dữ liệu chi tiết', index=False)
                
                excel_data = output.getvalue()
                
                st.download_button(
                    label="📥 Tải xuống Excel",
                    data=excel_data,
                    file_name=f"thong_ke_xang_dau_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("Không có dữ liệu để hiển thị với bộ lọc hiện tại.")
        else:
            st.warning("Không có dữ liệu để hiển thị với bộ lọc hiện tại.")
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Biểu đồ tổng lượng xăng theo tháng
            monthly_data = df_filtered.groupby('Thang').agg({
                'Lit': 'sum',
                'Do_ngoai_he_thong': 'sum',
                'Lit_he_thong': 'sum'
            }).reset_index()
            
            fig_monthly = px.bar(
                monthly_data, 
                x='Thang', 
                y=['Lit_he_thong', 'Do_ngoai_he_thong'],
                title="Lượng nhiên liệu theo tháng",
                labels={'value': 'Lít nhiên liệu', 'variable': 'Loại'},
                color_discrete_map={
                    'Lit_he_thong': '#2E86AB',
                    'Do_ngoai_he_thong': '#F24236'
                }
            )
            fig_monthly.update_layout(height=400)
            st.plotly_chart(fig_monthly, use_container_width=True)
        
        with col2:
            # Top 10 xe tiêu thụ nhiều nhất
            vehicle_consumption = df_filtered.groupby(['BSX', 'Loai_nhien_lieu'])['Lit'].sum().sort_values(ascending=False).head(10).reset_index()
            
            fig_top_vehicles = px.bar(
                vehicle_consumption,
                x='Lit',
                y='BSX',
                color='Loai_nhien_lieu',
                orientation='h',
                title="Top 10 xe tiêu thụ nhiều nhất",
                labels={'Lit': 'Tổng lít nhiên liệu', 'BSX': 'Biển số xe'},
                color_discrete_map={'Xăng': '#2E86AB', 'Dầu': '#A23B72'}
            )
            fig_top_vehicles.update_layout(height=400)
            st.plotly_chart(fig_top_vehicles, use_container_width=True)
    
    with tab3:
        st.subheader("So sánh Xăng vs Dầu")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Biểu đồ pie chart phân bố xăng vs dầu
            fuel_summary = df_filtered.groupby('Loai_nhien_lieu')['Lit'].sum().reset_index()
            
            if len(fuel_summary) > 0:
                fig_pie = px.pie(
                    fuel_summary,
                    values='Lit',
                    names='Loai_nhien_lieu',
                    title="Phân bố tiêu thụ Xăng vs Dầu",
                    color_discrete_map={'Xăng': '#2E86AB', 'Dầu': '#A23B72'}
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Biểu đồ so sánh theo tháng
            monthly_fuel_data = df_filtered.groupby(['Thang', 'Loai_nhien_lieu'])['Lit'].sum().reset_index()
            
            if len(monthly_fuel_data) > 0:
                fig_monthly_fuel = px.bar(
                    monthly_fuel_data,
                    x='Thang',
                    y='Lit',
                    color='Loai_nhien_lieu',
                    title="Tiêu thụ Xăng vs Dầu theo tháng",
                    labels={'Lit': 'Lít nhiên liệu', 'Thang': 'Tháng'},
                    color_discrete_map={'Xăng': '#2E86AB', 'Dầu': '#A23B72'},
                    barmode='group'
                )
                st.plotly_chart(fig_monthly_fuel, use_container_width=True)
        
        # Bảng thống kê chi tiết
        st.subheader("Thống kê chi tiết theo loại nhiên liệu")
        fuel_stats = df_filtered.groupby('Loai_nhien_lieu').agg({
            'Lit': ['sum', 'mean', 'count'],
            'Do_ngoai_he_thong': 'sum',
            'BSX': 'nunique'
        }).round(2)
        
        fuel_stats.columns = ['Tổng lít', 'TB lít/lần', 'Số lần đổ', 'Lít ngoài HT', 'Số xe']
        st.dataframe(fuel_stats, use_container_width=True)
    
    with tab4:
        st.subheader("Phân tích theo thời gian")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Xu hướng theo ngày
            daily_consumption = df_filtered.groupby('Ngay')['Lit'].sum().reset_index()
            
            fig_trend = px.line(
                daily_consumption,
                x='Ngay',
                y='Lit',
                title="Xu hướng tiêu thụ nhiên liệu theo ngày",
                labels={'Ngay': 'Ngày', 'Lit': 'Tổng lít nhiên liệu'}
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            # Phân bố theo ngày trong tuần
            df_filtered['Thu'] = df_filtered['Ngay'].dt.day_name()
            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday_consumption = df_filtered.groupby('Thu')['Lit'].sum().reindex(weekday_order)
            
            fig_weekday = px.bar(
                x=['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'],
                y=weekday_consumption.values,
                title="Tiêu thụ nhiên liệu theo ngày trong tuần",
                labels={'x': 'Ngày trong tuần', 'y': 'Tổng lít nhiên liệu'}
            )
            st.plotly_chart(fig_weekday, use_container_width=True)
    
    with tab5:
        st.subheader("Dữ liệu chi tiết")
        
        # Hiển thị dữ liệu đã được xử lý
        display_df = df_filtered[['Ngay', 'BSX', 'Loai_nhien_lieu', 'Lit', 'Do_ngoai_he_thong', 'Lit_he_thong']].copy()
        display_df['Ngay'] = display_df['Ngay'].dt.strftime('%d/%m/%Y')
        display_df.columns = ['Ngày', 'Biển số xe', 'Loại NL', 'Tổng lít', 'Đổ ngoài HT', 'Đổ trong HT']
        
        st.dataframe(display_df, use_container_width=True)
        
        # Nút download CSV
        csv = display_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Tải xuống CSV",
            data=csv,
            file_name="du_lieu_xang_dau_processed.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()