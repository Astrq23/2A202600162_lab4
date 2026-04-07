from langchain_core.tools import tool

# MOCK DATA
FLIGHTS_DB = {
    ("Hà Nội", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "07:20", "price": 1450000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "14:00", "arrival": "15:20", "price": 2800000, "class": "business"},
        {"airline": "VietJet Air", "departure": "08:30", "arrival": "09:50", "price": 890000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "11:00", "arrival": "12:20", "price": 1200000, "class": "economy"},
    ],
    ("Hà Nội", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "07:00", "arrival": "09:15", "price": 2100000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "10:00", "arrival": "12:15", "price": 1350000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "16:00", "arrival": "18:15", "price": 1100000, "class": "economy"},
    ],
    ("Hồ Chí Minh", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "09:00", "arrival": "10:20", "price": 1300000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "13:00", "arrival": "14:20", "price": 780000, "class": "economy"},
    ],
    ("Hồ Chí Minh", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "08:00", "arrival": "09:00", "price": 1100000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "15:00", "arrival": "16:00", "price": 650000, "class": "economy"},
    ]
}

HOTELS_DB = {
    "Đà Nẵng": [
        {"name": "Mường Thanh Luxury", "stars": 5, "price_per_night": 1800000, "area": "Mỹ Khê", "rating": 4.5},
        {"name": "Sala Danang Beach", "stars": 4, "price_per_night": 1200000, "area": "Mỹ Khê", "rating": 4.3},
        {"name": "Fivitel Danang", "stars": 3, "price_per_night": 650000, "area": "Sơn Trà", "rating": 4.1},
        {"name": "Memory Hostel", "stars": 2, "price_per_night": 250000, "area": "Hải Châu", "rating": 4.6},
        {"name": "Christina's Homestay", "stars": 2, "price_per_night": 350000, "area": "An Thượng", "rating": 4.7},
    ],
    "Phú Quốc": [
        {"name": "Vinpearl Resort", "stars": 5, "price_per_night": 3500000, "area": "Bãi Dài", "rating": 4.4},
        {"name": "Sol by Meliá", "stars": 4, "price_per_night": 1500000, "area": "Bãi Trường", "rating": 4.2},
        {"name": "Lahana Resort", "stars": 3, "price_per_night": 800000, "area": "Dương Đông", "rating": 4.0},
        {"name": "9Station Hostel", "stars": 2, "price_per_night": 200000, "area": "Dương Đông", "rating": 4.5},
    ]
}

@tool
def search_flights(origin: str, destination: str) -> str:
    """Tra cứu chuyến bay giữa hai thành phố trong dữ liệu nội bộ.

    Dùng khi cần gợi ý phương án di chuyển bằng máy bay cho lịch trình.

    Args:
        origin: Thành phố khởi hành (ví dụ: "Hà Nội", "Hồ Chí Minh").
        destination: Thành phố điểm đến (ví dụ: "Đà Nẵng", "Phú Quốc").

    Returns:
        Chuỗi văn bản gồm danh sách chuyến bay theo định dạng:
        - Hãng bay
        - Hạng vé
        - Giờ đi/giờ đến
        - Giá vé
        Nếu không có dữ liệu phù hợp, trả về thông báo không tìm thấy.
    """
    # Xử lý tra cứu và tra ngược
    flights = FLIGHTS_DB.get((origin, destination)) or FLIGHTS_DB.get((destination, origin))
    
    if not flights:
        return f"Không tìm thấy chuyến bay từ {origin} đến {destination}."
    
    res = [f"Chuyến bay từ {origin} đến {destination}:"]
    for f in flights:
        # Format giá tiền có dấu chấm phân cách
        price_fmt = f"{f['price']:,}₫".replace(",", ".")
        res.append(f"- {f['airline']} ({f['class']}): {f['departure']}-{f['arrival']}, Giá: {price_fmt}")
    return "\n".join(res)

@tool
def search_hotels(city: str, max_price_per_night: int = 99999999) -> str:
    """Tìm khách sạn theo thành phố, lọc theo ngân sách mỗi đêm và ưu tiên rating cao.

    Dùng khi người dùng đã có điểm đến và mức chi tối đa cho chỗ ở.

    Args:
        city: Thành phố cần tìm khách sạn.
        max_price_per_night: Mức giá tối đa mỗi đêm (VND).

    Returns:
        Chuỗi văn bản chứa danh sách khách sạn thỏa điều kiện, đã sắp xếp
        theo rating giảm dần, kèm:
        - Tên khách sạn
        - Số sao
        - Giá mỗi đêm
        - Khu vực
        - Điểm đánh giá
        Nếu không có kết quả, trả về thông báo phù hợp.
    """
    hotels = HOTELS_DB.get(city, [])
    # Lọc theo giá tối đa
    filtered = [h for h in hotels if h["price_per_night"] <= max_price_per_night]
    # Sắp xếp theo rating giảm dần
    filtered.sort(key=lambda x: x["rating"], reverse=True)
    
    if not filtered:
        return f"Không tìm thấy khách sạn tại {city} với giá dưới {max_price_per_night:,}₫/đêm."
    
    res = [f"Khách sạn tại {city} (Ưu tiên đánh giá cao):"]
    for h in filtered:
        price_fmt = f"{h['price_per_night']:,}₫".replace(",", ".")
        res.append(f"- {h['name']} ({h['stars']}*): {price_fmt}/đêm, Khu vực: {h['area']}, Rating: {h['rating']}")
    return "\n".join(res)

@tool
def calculate_budget(total_budget: int, expenses: str) -> str:
    """Tính ngân sách còn lại dựa trên tổng ngân sách và danh sách chi phí.

    Dùng để kiểm tra kế hoạch chi tiêu có vượt ngân sách hay không.

    Args:
        total_budget: Tổng ngân sách chuyến đi (VND).
        expenses: Chuỗi chi phí theo mẫu "hạng_mục: số_tiền, hạng_mục: số_tiền".
            Ví dụ: "vé máy bay: 890000, khách sạn: 650000".

    Returns:
        Chuỗi văn bản gồm bảng chi phí, tổng chi, ngân sách ban đầu và phần còn lại.
        Nếu tổng chi vượt mức cho phép, trả về cảnh báo vượt ngân sách.
        Nếu nhập sai định dạng expenses, trả về hướng dẫn nhập đúng.
    """
    try:
        # Parse chuỗi expenses 'tên: số tiền, tên: số tiền'
        items = [ex.split(":") for ex in expenses.split(",")]
        total_spent = 0
        details = []
        for name, amount in items:
            amt = int(amount.strip())
            total_spent += amt
            details.append(f"{name.strip().capitalize()}: {amt:,}₫".replace(",", "."))
        
        remaining = total_budget - total_spent
        res = ["Bảng chi phí:"] + details
        res.append(f"Tổng chi: {total_spent:,}₫".replace(",", "."))
        res.append(f"Ngân sách: {total_budget:,}₫".replace(",", "."))
        
        if remaining < 0:
            res.append(f"⚠️ Vượt ngân sách {abs(remaining):,}₫! Cần điều chỉnh.")
        else:
            res.append(f"Còn lại: {remaining:,}₫".replace(",", "."))
        return "\n".join(res)
    except Exception:
        return "Lỗi định dạng chi phí. Vui lòng nhập theo mẫu 'vé máy bay: 890000, khách sạn: 650000'."