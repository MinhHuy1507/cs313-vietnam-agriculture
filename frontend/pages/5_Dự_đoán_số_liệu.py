"""
File: pages/5_Dự_đoán.py
Description:
    This is the "Prediction" page of the application.
    This page is responsible for:
    1. Retrieving master data that has been pre-loaded from st.session_state
       (especially df_soil_master and df_climate_master to get fixed values
       and historical averages).
    2. Displaying a form (st.form) for user input.
    3. Clear separation:
        - Basic factors (Province, Commodity) - OUTSIDE form for
          automatic updating of fixed information.
        - Soil information (Fixed, read-only) - OUTSIDE form.
        - Climate factors (Forecast, user input) - INSIDE form.
    4. When "Predict" is clicked:
        - Display results (Production, Area, Yield) returned from API.
"""
import os
import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from utils.load_data import load_master_data

# --- 1. RETRIEVE DATA ---
df_agri_master, df_provinces_master, df_regions_master, df_climate_master, df_soil_master = load_master_data()
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api/v1")

# --- 2. PAGE 5 CONTENT: PREDICTION ---
st.title("Trang Dự đoán Sản lượng và năng suất")

# --- 3. BASIC FILTERS ---
st.header("Yếu tố Cơ bản (Bắt buộc)")
col1, col2 = st.columns(2)
with col1:
    province_list = sorted(df_provinces_master['province_name'].unique())
    selected_province = st.selectbox(
        "Chọn Tỉnh:", options=province_list, index=0, key="pred_province"
    )
    
    commodity_list = sorted(df_agri_master['commodity'].unique())
    selected_commodity = st.selectbox(
        "Chọn Nông sản:", options=commodity_list, index=0, key="pred_commodity"
    )
with col2:
    selected_year = st.number_input(
        "Năm dự đoán:", min_value=2025, max_value=2050, 
        value=2025, step=1, key="pred_year"
    )
    
    # Logic: Only Rice has multiple seasons. Others default to 'annual'.
    # Ensure case-insensitive check for 'rice'
    if selected_commodity.lower() == 'rice':
        # Filter seasons for rice from the master data
        rice_seasons = df_agri_master[df_agri_master['commodity'] == selected_commodity]['season'].dropna().unique()
        season_options = sorted(rice_seasons)
    else:
        season_options = ['annual']
        
    selected_season = st.selectbox(
        "Chọn Mùa vụ:", options=season_options, index=0, key="pred_season"
    )

# --- 4. DISPLAY SOIL INFORMATION ---
st.markdown("---")
st.subheader("Thông tin Thổ nhưỡng (Cố định)")
st.info(f"Các đặc tính đất dưới đây là cố định cho tỉnh **{selected_province}** và sẽ được tự động sử dụng trong dự đoán.", icon="ℹ️")

# Retrieve soil data for selected province
soil_data = df_soil_master[df_soil_master['province_name'] == selected_province]

if not soil_data.empty:
    soil_data_row = soil_data.iloc[0]
    
    scol1, scol2, scol3 = st.columns(3)
    with scol1:
        st.metric(label="Độ cao (m)", value=f"{soil_data_row.get('surface_elevation', 0.0):,.0f}")
        st.metric(label="Độ pH", value=f"{soil_data_row.get('soil_ph_level', 0.0):,.2f}")
        st.metric(label="Chỉ số NDVI", value=f"{soil_data_row.get('avg_ndvi', 0.0):,.3f}")
    with scol2:
        st.metric(label="Hàm lượng Carbon Hữu cơ (%)", value=f"{soil_data_row.get('soil_organic_carbon', 0.0):,.2f} %")
        st.metric(label="Hàm lượng Nitơ (%)", value=f"{soil_data_row.get('soil_nitrogen_content', 0.0):,.4f} %")
    with scol3:
        st.metric(label="Hàm lượng Cát (%)", value=f"{soil_data_row.get('soil_sand_ratio', 0.0):,.1f} %")
        st.metric(label="Hàm lượng Sét (%)", value=f"{soil_data_row.get('soil_clay_ratio', 0.0):,.1f} %")
else:
    st.warning(f"Không tìm thấy dữ liệu thổ nhưỡng cho tỉnh {selected_province}.")

# --- 5. INPUT FORM ---
with st.form(key="prediction_form"):
    
    st.markdown("---")
    st.header("Yếu tố Khí hậu (Dự báo)")
    st.markdown("Nhập các giá trị dự báo. Nếu để `0`, hệ thống sẽ dùng giá trị trung bình lịch sử của tỉnh đó.")
    
    c_col1, c_col2, c_col3 = st.columns(3)
    with c_col1:
        pred_avg_temp = st.number_input("Nhiệt độ TB (°C)", key="pred_avg_temp", value=0.0, format="%.2f")
        pred_min_temp = st.number_input("Nhiệt độ Min (°C)", key="pred_min_temp", value=0.0, format="%.2f")
        pred_max_temp = st.number_input("Nhiệt độ Max (°C)", key="pred_max_temp", value=0.0, format="%.2f")
        pred_wet_bulb = st.number_input("Nhiệt độ Bầu ướt (°C)", key="pred_wet_bulb", value=0.0, format="%.2f")
    with c_col2:
        pred_precip = st.number_input("Lượng mưa (mm)", key="pred_precip", value=0.0, format="%.2f")
        pred_solar = st.number_input("Bức xạ (kW-hr/m^2/day)", key="pred_solar", value=0.0, format="%.2f")
        pred_humid = st.number_input("Độ ẩm (%)", key="pred_humid", value=0.0, format="%.2f")
    with c_col3:
        pred_wind = st.number_input("Sức gió (m/s)", key="pred_wind", value=0.0, format="%.2f")
        pred_pressure = st.number_input("Áp suất (kPa)", key="pred_pressure", value=0.0, format="%.2f")
        pred_surf_temp = st.number_input("Nhiệt độ Bề mặt (°C)", key="pred_surf_temp", value=0.0, format="%.2f")
        
    st.markdown("---")
    st.header("Thông tin Diện tích (Mặc định lấy của năm 2024)")
    
    # Fetch area for 2024
    default_area = 10.0
    try:
        # Filter by Province, Commodity, Year AND Season
        row_2024 = df_agri_master[
            (df_agri_master['region_name'] == selected_province) & 
            (df_agri_master['commodity'] == selected_commodity) & 
            (df_agri_master['year'] == 2024) &
            (df_agri_master['season'] == selected_season)
        ]
        if not row_2024.empty:
            default_area = float(row_2024.iloc[0]['area_thousand_ha'])
    except Exception:
        pass
        
    # Use dynamic key to force reset when province/commodity/season changes
    pred_area = st.number_input(
        f"Diện tích canh tác (nghìn ha) - Mặc định lấy từ năm 2024 của {selected_province}", 
        key=f"pred_area_{selected_province}_{selected_commodity}_{selected_season}", 
        value=default_area, 
        format="%.2f", 
        min_value=0.1
    )

    # Submit button
    submitted = st.form_submit_button("Dự đoán")

# --- 6. PROCESSING LOGIC WHEN BUTTON IS CLICKED ---
if submitted:
    with st.spinner("Đang xử lý dự đoán..."):
        
        if soil_data.empty:
            st.error(f"Không thể dự đoán vì thiếu dữ liệu thổ nhưỡng cho {selected_province}.")
            st.stop()
        
        # Retrieve historical averages for the province
        hist_climate = df_climate_master[df_climate_master['province_name'] == selected_province].mean(numeric_only=True)
        
        def get_value(pred_val, hist_val_key):
            # Check if hist_val_key doesn't exist
            if hist_val_key not in hist_climate or pd.isna(hist_climate[hist_val_key]):
                return pred_val if pred_val != 0.0 else 0.0
            return pred_val if pred_val != 0.0 else hist_climate[hist_val_key]

        # Package 21 features (Payload)
        input_data = {
            "province_name": selected_province,
            "year": selected_year,
            "commodity": selected_commodity,
            "season": selected_season,

            # Get from form widget
            "avg_temperature": get_value(pred_avg_temp, 'avg_temperature'),
            "min_temperature": get_value(pred_min_temp, 'min_temperature'),
            "max_temperature": get_value(pred_max_temp, 'max_temperature'),
            "surface_temperature": get_value(pred_surf_temp, 'surface_temperature'),
            "wet_bulb_temperature": get_value(pred_wet_bulb, 'wet_bulb_temperature'),
            "precipitation": get_value(pred_precip, 'precipitation'),
            "solar_radiation": get_value(pred_solar, 'solar_radiation'),
            "relative_humidity": get_value(pred_humid, 'relative_humidity'),
            "wind_speed": get_value(pred_wind, 'wind_speed'),
            "surface_pressure": get_value(pred_pressure, 'surface_pressure'),
            
            # Get from soil_data_row
            "surface_elevation": soil_data_row.get('surface_elevation', 0.0),
            "avg_ndvi": soil_data_row.get('avg_ndvi', 0.0),
            "soil_ph_level": soil_data_row.get('soil_ph_level', 0.0),
            "soil_organic_carbon": soil_data_row.get('soil_organic_carbon', 0.0),
            "soil_nitrogen_content": soil_data_row.get('soil_nitrogen_content', 0.0),
            "soil_sand_ratio": soil_data_row.get('soil_sand_ratio', 0.0),
            "soil_clay_ratio": soil_data_row.get('soil_clay_ratio', 0.0),
            
            # Additional fields for ML pipeline
            "yield_ta_per_ha": 0.0, # Placeholder
            "area_thousand_ha": pred_area
        }
        
        # Call API
        try:
            response = requests.post(f"{API_BASE_URL}/predict", json=input_data)
            
            if response.status_code == 200:
                results = response.json()
                st.success("Dự đoán thành công!")
                st.header("Kết quả Dự đoán")
                
                res_col1, res_col2 = st.columns(2)
                res_col1.metric(
                    "Sản lượng Dự đoán", 
                    f"{results['predicted_production']:,.0f} Tấn"
                )
                res_col2.metric(
                    "Năng suất Dự đoán", 
                    f"{results['predicted_yield']:,.2f} Tấn/Ha"
                )
                
                # --- COMPARISON CHARTS ---
                # Filter historical data for comparison
                hist_data = df_agri_master[
                    (df_agri_master['region_name'] == selected_province) & 
                    (df_agri_master['commodity'] == selected_commodity) & 
                    (df_agri_master['season'] == selected_season)
                ]
                
                last_year_prod = 0.0
                last_year_yield = 0.0
                last_year_val = 0
                
                if not hist_data.empty:
                    # Try to find the most recent year before the selected year
                    past_data = hist_data[hist_data['year'] < selected_year]
                    if not past_data.empty:
                        latest_row = past_data.sort_values('year', ascending=False).iloc[0]
                        last_year_val = int(latest_row['year'])
                    else:
                        # If no past data, take the latest available year
                        latest_row = hist_data.sort_values('year', ascending=False).iloc[0]
                        last_year_val = int(latest_row['year'])
                    
                    # Get values (handle NaNs)
                    prod_val = latest_row.get('production_thousand_tonnes', 0.0)
                    yield_val = latest_row.get('yield_ta_per_ha', 0.0)
                    
                    last_year_prod = (prod_val * 1000) if pd.notna(prod_val) else 0.0
                    last_year_yield = (yield_val / 10) if pd.notna(yield_val) else 0.0

                if last_year_val > 0:
                    st.markdown("---")
                    st.subheader(f"So sánh với dữ liệu năm gần nhất ({last_year_val})")
                    
                    chart_col1, chart_col2 = st.columns(2)
                    
                    # Chart 1: Production Comparison
                    fig_prod = go.Figure(data=[
                        go.Bar(name=f'Năm {last_year_val}', x=['Sản lượng'], y=[last_year_prod], marker_color='gray'),
                        go.Bar(name=f'Dự đoán ({selected_year})', x=['Sản lượng'], y=[results['predicted_production']], marker_color='green')
                    ])
                    fig_prod.update_layout(title_text='So sánh Sản lượng (Tấn)', barmode='group')
                    chart_col1.plotly_chart(fig_prod, use_container_width=True)
                    
                    # Chart 2: Yield Comparison
                    fig_yield = go.Figure(data=[
                        go.Bar(name=f'Năm {last_year_val}', x=['Năng suất'], y=[last_year_yield], marker_color='gray'),
                        go.Bar(name=f'Dự đoán ({selected_year})', x=['Năng suất'], y=[results['predicted_yield']], marker_color='blue')
                    ])
                    fig_yield.update_layout(title_text='So sánh Năng suất (Tấn/Ha)', barmode='group')
                    chart_col2.plotly_chart(fig_yield, use_container_width=True)
                else:
                    st.info("Chưa có dữ liệu lịch sử để so sánh.")

                with st.expander("Xem chi tiết Dữ liệu đầu vào (đã xử lý)"):
                    st.json(input_data)

            else:
                st.error(f"Lỗi từ API: {response.status_code} - {response.text}")
                
        except Exception as e:
            st.error(f"Lỗi kết nối đến API: {e}")