# AI Assistant - Example Conversations

This file shows what the AI can now answer with real water level data.

---

## Example 1: Current Water Level Question

**User:** "Mực nước hiện tại là bao nhiêu mm?"

**AI Response (with real data):**
```
Mực nước hiện tại là 34.77 mm. Đây là mức nước bình thường, không có nguy hiểm lũ lụt.
Dự báo trong 10 phút tới, mực nước sẽ tăng lên khoảng 35.42 mm.
```

**How it works:**
1. AI receives: `current = 34.77 mm` from sensor
2. AI receives: `pred_10min = 35.42 mm` from ML model
3. AI uses this data to answer specifically

---

## Example 2: Prediction Question

**User:** "Mực nước sẽ bao nhiêu trong 10 phút tới? Có nguy hiểm không?"

**AI Response:**
```
Theo dự báo machine learning, mực nước sẽ là 35.42 mm trong 10 phút tới.
Điều này vẫn nằm trong mức bình thường (dưới 150 mm).
Không có nguy hiểm lũ lụt trong khung thời gian này.
```

**How it works:**
1. AI gets ML forecast: `35.42 mm`
2. AI checks: `35.42 < 150` (safe threshold)
3. AI provides safe assessment

---

## Example 3: Comparison with Average

**User:** "Mực nước hiện tại so với bình thường thế nào?"

**AI Response:**
```
Mực nước hiện tại là 34.77 mm.
Mực nước trung bình từ lịch sử là 32.45 mm.
Vậy mực nước hiện tại cao hơn trung bình 2.32 mm (tăng 7%), nhưng vẫn nằm trong phạm vi an toàn.
```

**How it works:**
1. AI gets: `current = 34.77 mm`, `average = 32.45 mm`
2. AI calculates: `34.77 - 32.45 = 2.32 mm`
3. AI calculates: `(2.32 / 32.45) × 100 = 7.1%`
4. AI contextualizes with comparison

---

## Example 4: Trend Analysis

**User:** "Mực nước đang tăng hay giảm? Chiều hướng như thế nào?"

**AI Response:**
```
Dựa trên dữ liệu lịch sử:
- Mực nước min ghi nhận: 20.15 mm
- Mực nước max ghi nhận: 45.30 mm
- Mực nước trung bình: 32.45 mm
- Mực nước hiện tại: 34.77 mm (cao hơn trung bình)

Dự báo cho thấy xu hướng tăng nhẹ (34.77 → 35.42 mm trong 10 phút).
Tuy nhiên, vẫn nằm trong phạm vi lịch sử an toàn.
```

**How it works:**
1. AI gets: `min = 20.15`, `max = 45.30`, `avg = 32.45`, `current = 34.77`, `pred = 35.42`
2. AI analyzes trend: current > avg, and forecast > current
3. AI provides comprehensive trend assessment

---

## Example 5: Warning/Alert Scenario

**User:** "Có nguy hiểm lũ lụt không? Tôi nên lo lắng không?"

**Hypothetical Response (if water high):**
```
⚠️ CẢNH BÁO!
Mực nước hiện tại là 185 mm, cao hơn ngưỡng cảnh báo (150 mm).
Dự báo 10 phút tới: 198 mm (tiếp tục tăng).

Khuyến cáo:
- Theo dõi tình hình liên tục
- Chuẩn bị kế hoạch sơ tán nếu cần
- Liên hệ chính quyền địa phương
- Không ra khỏi nhà nếu có mưa lớn

🚨 Nếu vượt 200 mm: CÓ NGUY HIỂM LŨ LỤT - DI TÁN NGAY!
```

**How it works:**
1. AI checks: `185 > 150` (warning threshold)
2. AI checks: forecast `198` (increasing)
3. AI provides urgent warnings with action items

---

## Example 6: Historical Record

**User:** "Mực nước cao nhất ghi nhận được là bao nhiêu?"

**AI Response:**
```
Mực nước cao nhất ghi nhận được trong lịch sử là 45.30 mm.
Mực nước hiện tại là 34.77 mm, so với mức cao nhất còn thấp hơn 10.53 mm.
Nếu mực nước tiếp tục tăng với tốc độ hiện tại, sẽ không đạt mức cao nhất trong 10 phút tới.
```

**How it works:**
1. AI gets: `max = 45.30 mm`, `current = 34.77 mm`
2. AI calculates difference: `45.30 - 34.77 = 10.53 mm`
3. AI contextualizes with forecast

---

## Example 7: Statistical Analysis

**User:** "Cho tôi xem thống kê mực nước"

**AI Response:**
```
📊 THỐNG KÊ MỰC NƯỚC

Dữ liệu hiện tại:
- Mức nước hiện tại: 34.77 mm
- Mức nước min: 20.15 mm
- Mức nước max: 45.30 mm
- Mức nước trung bình: 32.45 mm
- Tổng cộng: 120 bản ghi

Dự báo:
- 10 phút tới: 35.42 mm
- 30 phút tới: 36.15 mm

Tình trạng: ✓ AN TOÀN
```

**How it works:**
1. AI retrieves all statistics from history
2. AI formats as readable report
3. AI adds forecast and status

---

## Example 8: Rapid Changes

**User:** "Mực nước có thay đổi nhanh không? Tôi có cần lo lắng?"

**AI Response:**
```
Dựa trên dự báo ML:
- Mực nước hiện tại: 34.77 mm
- Mực nước sau 10 phút: 35.42 mm
- Mức tăng: 0.65 mm / 10 phút

Tốc độ thay đổi là bình thường và gradual. Không có sự gia tăng đột ngột.
Khuyến cáo: Tiếp tục theo dõi nhưng không cần lo lắng ngay.
```

**How it works:**
1. AI calculates rate of change: `(35.42 - 34.77) / 10 = 0.065 mm/min`
2. AI contextualizes as "bình thường"
3. AI provides reassurance

---

## Example 9: Multiple Sensors (Future)

**User:** "So sánh mực nước sensor1 và sensor2"

**AI Response (when multi-sensor available):**
```
📍 Sensor 1 (Khu A): 34.77 mm (bình thường)
📍 Sensor 2 (Khu B): 42.50 mm (cảnh báo)

Sensor 2 ở mức cao hơn, gần ngưỡng cảnh báo (150 mm).
Khuyến cáo kiểm tra Khu B trong vòng 15 phút tới.
```

---

## Example 10: Natural Language Variations

**Different ways users might ask the same thing:**

- "Bây giờ nước mấy mm?"
  - Response: Uses current sensor value
  
- "Nước sẽ bao nhiêu?"
  - Response: Uses ML prediction
  
- "Có lũ không?"
  - Response: Compares with thresholds
  
- "Mực nước bình thường không?"
  - Response: Compares with average
  
- "Nước đang lên hay xuống?"
  - Response: Analyzes trend from forecast

---

## System Prompt Structure

The AI uses this context for ALL responses:

```
**Dữ liệu Cảm Biến Nước Thực Tế:**
- Mực nước hiện tại: [SENSOR_VALUE] mm
- Khoảng cách: [DISTANCE] cm
- Cập nhật lúc: [TIMESTAMP]

**Dự Báo ML (10 phút tới):**
- Dự báo mực nước: [FORECAST_10MIN] mm

**Thống Kê Lịch Sử:**
- Mực nước min: [MIN] mm
- Mực nước max: [MAX] mm
- Mực nước trung bình: [AVG] mm
- Số lần đo: [COUNT]

---

Hướng dẫn:
1. Khi hỏi "mực nước hiện tại?": dùng [SENSOR_VALUE]
2. Khi hỏi "trong tương lai?"": dùng [FORECAST_10MIN]
3. Khi hỏi "xu hướng?": dùng MIN/MAX/AVG so sánh
4. Khi mực nước > 200mm: cảnh báo nguy hiểm
5. Khi mực nước 150-200mm: cảnh báo cần chú ý
```

---

## Tips for Best Results

1. **Be Specific:** "Mực nước bây giờ?" vs "Thông tin chi tiết về mực nước"
2. **Ask Trends:** "So với hôm qua thế nào?" → AI compares with min/max/avg
3. **Request Advice:** "Tôi nên làm gì?" → AI provides action items
4. **Check Safety:** "Có an toàn không?" → AI analyzes vs thresholds
5. **Monitor Trends:** "Mực nước đang tăng?" → AI predicts future levels

---

## Edge Cases Handled

- **No Data Yet:** "Đang chờ dữ liệu từ cảm biến..."
- **Firebase Error:** "❌ Không kết nối được Firebase"
- **Insufficient History:** "⏳ Chưa đủ dữ liệu để dự báo"
- **No Forecast Yet:** "Dự báo đang cập nhật..."

---

**Last Updated:** November 19, 2025
