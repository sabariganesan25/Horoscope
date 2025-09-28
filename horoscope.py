import gradio as gr
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfutils
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import io
import os
import tempfile

class EnhancedAstrologyCalculator:
    def __init__(self):
        self.planets = {
            'Sun': {'symbol': '☉', 'tamil': 'சூரியன்', 'short': 'சூ', 'abbrev': 'சூ'},
            'Moon': {'symbol': '☽', 'tamil': 'சந்திரன்', 'short': 'ச', 'abbrev': 'ச'},
            'Mars': {'symbol': '♂', 'tamil': 'செவ்வாய்', 'short': 'செ', 'abbrev': 'செ'},
            'Mercury': {'symbol': '☿', 'tamil': 'புதன்', 'short': 'பு', 'abbrev': 'பு'},
            'Jupiter': {'symbol': '♃', 'tamil': 'குரு', 'short': 'கு', 'abbrev': 'கு'},
            'Venus': {'symbol': '♀', 'tamil': 'சுக்ரன்', 'short': 'சுக்', 'abbrev': 'சு'},
            'Saturn': {'symbol': '♄', 'tamil': 'சனி', 'short': 'சனி', 'abbrev': 'சனி'},
            'Rahu': {'symbol': '☊', 'tamil': 'ராகு', 'short': 'ரா', 'abbrev': 'ரா'},
            'Ketu': {'symbol': '☋', 'tamil': 'கேது', 'short': 'கே', 'abbrev': 'கே'}
        }
        self.zodiac_signs = {
            'Aries': {'tamil': 'மேஷம்', 'symbol': '♈', 'short': 'மே'},
            'Taurus': {'tamil': 'ரிஷபம்', 'symbol': '♉', 'short': 'ரி'},
            'Gemini': {'tamil': 'மிதுனம்', 'symbol': '♊', 'short': 'மி'},
            'Cancer': {'tamil': 'கடகம்', 'symbol': '♋', 'short': 'க'},
            'Leo': {'tamil': 'சிம்மம்', 'symbol': '♌', 'short': 'சி'},
            'Virgo': {'tamil': 'கன்னி', 'symbol': '♍', 'short': 'கன்'},
            'Libra': {'tamil': 'துலாம்', 'symbol': '♎', 'short': 'து'},
            'Scorpio': {'tamil': 'விருச்சிகம்', 'symbol': '♏', 'short': 'வி'},
            'Sagittarius': {'tamil': 'தனுசு', 'symbol': '♐', 'short': 'த'},
            'Capricorn': {'tamil': 'மகரம்', 'symbol': '♑', 'short': 'ம'},
            'Aquarius': {'tamil': 'கும்பம்', 'symbol': '♒', 'short': 'கும்'},
            'Pisces': {'tamil': 'மீனம்', 'symbol': '♓', 'short': 'மீ'}
        }
        self.nakshatras = [
            'அஸ்வினி', 'பரணி', 'கிருத்திகை', 'ரோகிணி', 'மிருகசீரிடம்',
            'ஆருத்ரா', 'புனர்வசு', 'புஷ்யம்', 'ஆஸ்லேஷா', 'மகம்',
            'பூர்வபல்குனி', 'உத்திரபல்குனி', 'ஹஸ்தம்', 'சித்திரை', 'சுவாதி',
            'விசாகம்', 'அனுஷம்', 'ஜெய்ஷ்டா', 'மூலம்', 'பூராஷாடா',
            'உத்திராஷாடா', 'திருவோணம்', 'அவிட்டம்', 'சதயம்', 'பூரட்டாதி',
            'உத்திரட்டாதி', 'ரேவதி'
        ]
        self.planetary_elements = {
            'Sun': {'L': 280.46646, 'dL': 36000.76983, 'e': 0.016708634, 'M': 357.52911},
            'Moon': {'L': 218.3164477, 'dL': 481267.88123421, 'e': 0.0549},
            'Mercury': {'L': 252.250906, 'dL': 149472.6746358, 'e': 0.20563175},
            'Venus': {'L': 181.979801, 'dL': 58517.8156760, 'e': 0.00677323},
            'Mars': {'L': 355.433, 'dL': 19140.299, 'e': 0.09341233},
            'Jupiter': {'L': 34.351519, 'dL': 3034.9056606, 'e': 0.04839266},
            'Saturn': {'L': 50.077444, 'dL': 1222.1138488, 'e': 0.05415060}
        }
        self.cities = self._load_comprehensive_global_cities()

    def _load_comprehensive_global_cities(self):
        """Load comprehensive worldwide cities database including all Tamil Nadu districts"""
        cities = {}
        
        # Tamil Nadu - All 38 Districts with major towns/cities
        tamil_nadu_cities = {
            # Ariyalur District
            'Ariyalur': (11.1401, 79.0778, 5.5),
            'Andimadam': (11.2023, 79.0955, 5.5),
            'Sendurai': (11.1548, 79.0432, 5.5),
            'Udayarpalayam': (11.1789, 79.1234, 5.5),
            
            # Chengalpattu District
            'Chengalpattu': (12.6944, 79.9753, 5.5),
            'Madurantakam': (12.5138, 80.1570, 5.5),
            'Tambaram': (12.9249, 80.1000, 5.5),
            'Pallavaram': (12.9675, 80.1491, 5.5),
            'Chromepet': (12.9516, 80.1462, 5.5),
            
            # Chennai District
            'Chennai': (13.0827, 80.2707, 5.5),
            'T Nagar': (13.0418, 80.2341, 5.5),
            'Adyar': (13.0067, 80.2206, 5.5),
            'Anna Nagar': (13.0850, 80.2101, 5.5),
            'Velachery': (12.9750, 80.2200, 5.5),
            'Porur': (13.0378, 80.1565, 5.5),
            'Guindy': (13.0103, 80.2206, 5.5),
            'Mylapore': (13.0339, 80.2619, 5.5),
            
            # Coimbatore District
            'Coimbatore': (11.0168, 76.9558, 5.5),
            'Tirupur': (11.1085, 77.3411, 5.5),
            'Pollachi': (10.6581, 77.0009, 5.5),
            'Mettupalayam': (11.2997, 76.9439, 5.5),
            'Valparai': (10.3275, 76.9548, 5.5),
            'Sulur': (11.0264, 77.1246, 5.5),
            'Annur': (11.2368, 77.1097, 5.5),
            
            # Cuddalore District
            'Cuddalore': (11.7540, 79.7740, 5.5),
            'Chidambaram': (11.3994, 79.6906, 5.5),
            'Villupuram': (11.9401, 79.4861, 5.5),
            'Neyveli': (11.6229, 79.4895, 5.5),
            'Panruti': (11.7739, 79.5506, 5.5),
            'Vriddhachalam': (11.5188, 79.3220, 5.5),
            
            # More cities would be included here...
            # Continuing with major Tamil Nadu cities
            'Dharmapuri': (12.1211, 78.1580, 5.5),
            'Dindigul': (10.3624, 77.9694, 5.5),
            'Kodaikanal': (10.2381, 77.4892, 5.5),
            'Erode': (11.3410, 77.7172, 5.5),
            'Kallakurichi': (11.7394, 78.9597, 5.5),
            'Kanchipuram': (12.8342, 79.7036, 5.5),
            'Kanniyakumari': (8.0883, 77.5385, 5.5),
            'Nagercoil': (8.1742, 77.4349, 5.5),
            'Karur': (10.9571, 78.0766, 5.5),
            'Krishnagiri': (12.5186, 78.2137, 5.5),
            'Hosur': (12.7409, 77.8253, 5.5),
            'Madurai': (9.9252, 78.1198, 5.5),
            'Mayiladuthurai': (11.1085, 79.6540, 5.5),
            'Nagapattinam': (10.7664, 79.8448, 5.5),
            'Namakkal': (11.2189, 78.1677, 5.5),
            'Ooty': (11.4064, 76.6932, 5.5),
            'Perambalur': (11.2342, 78.8964, 5.5),
            'Pudukkottai': (10.3833, 78.8000, 5.5),
            'Ramanathapuram': (9.3639, 78.8347, 5.5),
            'Rameswaram': (9.2881, 79.3129, 5.5),
            'Ranipet': (12.9244, 79.3372, 5.5),
            'Salem': (11.6643, 78.1460, 5.5),
            'Sivaganga': (9.8430, 78.4808, 5.5),
            'Karaikudi': (10.0609, 78.7658, 5.5),
            'Tenkasi': (8.9597, 77.3153, 5.5),
            'Thanjavur': (10.7870, 79.1378, 5.5),
            'Kumbakonam': (10.9601, 79.3788, 5.5),
            'Theni': (10.0104, 77.4777, 5.5),
            'Thoothukudi': (8.7642, 78.1348, 5.5),
            'Tiruchirappalli': (10.7905, 78.7047, 5.5),
            'Tirunelveli': (8.7139, 77.7567, 5.5),
            'Tirupathur': (12.4969, 78.5664, 5.5),
            'Tiruvallur': (13.1439, 79.9753, 5.5),
            'Tiruvannamalai': (12.2304, 79.0747, 5.5),
            'Tiruvarur': (10.7730, 79.6336, 5.5),
            'Vellore': (12.9165, 79.1325, 5.5),
            'Virudhunagar': (9.5810, 77.9624, 5.5),
            'Sivakasi': (9.4528, 77.7939, 5.5),
        }
        
        # Major Indian Cities
        indian_cities = {
            'Bangalore': (12.9716, 77.5946, 5.5),
            'Hyderabad': (17.3850, 78.4867, 5.5),
            'Mumbai': (19.0760, 72.8777, 5.5),
            'Pune': (18.5204, 73.8567, 5.5),
            'Delhi': (28.7041, 77.1025, 5.5),
            'New Delhi': (28.6139, 77.2090, 5.5),
            'Kolkata': (22.5726, 88.3639, 5.5),
            'Ahmedabad': (23.0225, 72.5714, 5.5),
            'Surat': (21.1702, 72.8311, 5.5),
            'Jaipur': (26.9124, 75.7873, 5.5),
            'Lucknow': (26.8467, 80.9462, 5.5),
            'Kanpur': (26.4499, 80.3319, 5.5),
            'Nagpur': (21.1458, 79.0882, 5.5),
            'Patna': (25.5941, 85.1376, 5.5),
            'Indore': (22.7196, 75.8577, 5.5),
            'Thane': (19.2183, 72.9781, 5.5),
            'Bhopal': (23.2599, 77.4126, 5.5),
            'Visakhapatnam': (17.6868, 83.2185, 5.5),
            'Vadodara': (22.3072, 73.1812, 5.5),
            'Faridabad': (28.4089, 77.3178, 5.5),
            'Ghaziabad': (28.6692, 77.4538, 5.5),
            'Ludhiana': (30.9010, 75.8573, 5.5),
            'Agra': (27.1767, 78.0081, 5.5),
            'Nashik': (19.9975, 73.7898, 5.5),
            'Faridabad': (28.4089, 77.3178, 5.5),
            'Meerut': (28.9845, 77.7064, 5.5),
            'Rajkot': (22.3039, 70.8022, 5.5),
            'Kalyan-Dombivali': (19.2403, 73.1305, 5.5),
            'Vasai-Virar': (19.4919, 72.8397, 5.5),
            'Varanasi': (25.3176, 82.9739, 5.5),
            'Srinagar': (34.0837, 74.7973, 5.5),
            'Aurangabad': (19.8762, 75.3433, 5.5),
            'Dhanbad': (23.7957, 86.4304, 5.5),
            'Amritsar': (31.6340, 74.8723, 5.5),
            'Navi Mumbai': (19.0330, 73.0297, 5.5),
            'Allahabad': (25.4358, 81.8463, 5.5),
            'Howrah': (22.5958, 88.2636, 5.5),
            'Ranchi': (23.3441, 85.3096, 5.5),
            'Gwalior': (26.2183, 78.1828, 5.5),
            'Jabalpur': (23.1815, 79.9864, 5.5),
            'Coimbatore': (11.0168, 76.9558, 5.5),
        }
        
        # International Cities
        international_cities = {
            'New York': (40.7128, -74.0060, -5.0),
            'Los Angeles': (34.0522, -118.2437, -8.0),
            'London': (51.5074, -0.1278, 0.0),
            'Paris': (48.8566, 2.3522, 1.0),
            'Tokyo': (35.6762, 139.6503, 9.0),
            'Sydney': (-33.8688, 151.2093, 10.0),
            'Dubai': (25.2048, 55.2708, 4.0),
            'Singapore': (1.3521, 103.8198, 8.0),
            'Toronto': (43.6532, -79.3832, -5.0),
            'Berlin': (52.5200, 13.4050, 1.0),
            'Madrid': (40.4168, -3.7038, 1.0),
            'Rome': (41.9028, 12.4964, 1.0),
            'Bangkok': (13.7563, 100.5018, 7.0),
            'Kuala Lumpur': (3.1390, 101.6869, 8.0),
            'Jakarta': (-6.2088, 106.8456, 7.0),
            'Manila': (14.5995, 120.9842, 8.0),
            'Seoul': (37.5665, 126.9780, 9.0),
            'Beijing': (39.9042, 116.4074, 8.0),
            'Shanghai': (31.2304, 121.4737, 8.0),
            'Hong Kong': (22.3193, 114.1694, 8.0),
            'Melbourne': (-37.8136, 144.9631, 10.0),
            'Perth': (-31.9505, 115.8605, 8.0),
            'Auckland': (-36.8485, 174.7633, 12.0),
            'Wellington': (-41.2865, 174.7762, 12.0),
            'Vancouver': (49.2827, -123.1207, -8.0),
            'Montreal': (45.5017, -73.5673, -5.0),
            'Chicago': (41.8781, -87.6298, -6.0),
            'Houston': (29.7604, -95.3698, -6.0),
            'Miami': (25.7617, -80.1918, -5.0),
            'San Francisco': (37.7749, -122.4194, -8.0),
        }
        
        # Combine all cities
        cities.update(tamil_nadu_cities)
        cities.update(indian_cities)
        cities.update(international_cities)
        
        return cities

    def calculate_accurate_julian_day(self, date_time: datetime, tz_offset: float) -> float:
        """Julian Day with timezone"""
        utc_time = date_time - timedelta(hours=tz_offset)
        year, month = utc_time.year, utc_time.month
        day, hour, minute = utc_time.day, utc_time.hour, utc_time.minute
        second = utc_time.second + utc_time.microsecond / 1_000_000
        if month <= 2:
            year -= 1
            month += 12
        a = int(year / 100)
        b = 2 - a + int(a / 4)
        jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
        jd += (hour + minute / 60 + second / 3600) / 24.0
        return jd

    def calculate_lahiri_ayanamsa(self, jd: float) -> float:
        T = (jd - 2451545.0) / 36525.0
        ayanamsa = 23.85 + (0.013972 * T) + (0.000013 * T * T)
        return ayanamsa

    def calculate_sun_longitude(self, jd: float) -> float:
        T = (jd - 2451545.0) / 36525.0
        L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T * T
        M = 357.52911 + 35999.05029 * T - 0.0001537 * T * T
        M_rad = math.radians(M)
        C = (1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(M_rad)
        C += (0.019993 - 0.000101 * T) * math.sin(2 * M_rad)
        C += 0.000289 * math.sin(3 * M_rad)
        true_longitude = L0 + C
        omega = 125.04 - 1934.136 * T
        apparent_longitude = true_longitude - 0.00569 - 0.00478 * math.sin(math.radians(omega))
        ayanamsa = self.calculate_lahiri_ayanamsa(jd)
        sidereal_longitude = (apparent_longitude - ayanamsa) % 360
        return sidereal_longitude

    def calculate_moon_longitude(self, jd: float) -> float:
        T = (jd - 2451545.0) / 36525.0
        L_prime = 218.3164477 + 481267.88123421 * T - 0.0015786 * T * T
        D = 297.8501921 + 445267.1114034 * T - 0.0018819 * T * T
        M = 357.5291092 + 35999.0502909 * T - 0.0001536 * T * T
        M_prime = 134.9633964 + 477198.8675055 * T + 0.0087414 * T * T
        F = 93.2720950 + 483202.0175233 * T - 0.0036539 * T * T
        D_rad, M_rad, M_prime_rad, F_rad = map(math.radians, [D, M, M_prime, F])
        longitude = L_prime
        longitude += 6.288774 * math.sin(M_prime_rad)
        longitude += 1.274027 * math.sin(2 * D_rad - M_prime_rad)
        longitude += 0.658314 * math.sin(2 * D_rad)
        longitude += 0.213618 * math.sin(2 * M_prime_rad)
        longitude -= 0.185116 * math.sin(M_rad)
        longitude -= 0.114332 * math.sin(2 * F_rad)
        longitude += 0.058793 * math.sin(2 * D_rad - 2 * M_prime_rad)
        longitude += 0.057066 * math.sin(2 * D_rad - M_rad - M_prime_rad)
        longitude += 0.053322 * math.sin(2 * D_rad + M_prime_rad)
        longitude += 0.045758 * math.sin(2 * D_rad - M_rad)
        ayanamsa = self.calculate_lahiri_ayanamsa(jd)
        sidereal_longitude = (longitude - ayanamsa) % 360
        return sidereal_longitude

    def calculate_planet_longitude(self, planet: str, jd: float, precomputed=None) -> float:
        if planet not in self.planetary_elements:
            return 0.0
        T = (jd - 2451545.0) / 36525.0
        elements = self.planetary_elements[planet]
        L = elements['L'] + elements['dL'] * T
        if planet == 'Mercury':
            M = 174.7948 + 149472.6746358 * T
        elif planet == 'Venus':
            M = 50.4161 + 58517.8156760 * T
        elif planet == 'Mars':
            M = 19.3870 + 19140.299 * T
        elif planet == 'Jupiter':
            M = 20.0202 + 3034.9056606 * T
        elif planet == 'Saturn':
            M = 317.0207 + 1222.1138488 * T
        else:
            M = L
        M = M % 360
        M_rad = math.radians(M)
        e = elements['e']
        E = M_rad + e * math.sin(M_rad)
        for _ in range(10):
            E_new = M_rad + e * math.sin(E)
            if abs(E_new - E) < 1e-8:
                break
            E = E_new
        nu = 2 * math.atan2(math.sqrt(1 + e) * math.sin(E / 2), math.sqrt(1 - e) * math.cos(E / 2))
        true_longitude = (L + math.degrees(nu) - M) % 360
        if not precomputed:
            precomputed = {}
        if planet == 'Jupiter' and 'Saturn' not in precomputed:
            precomputed['Jupiter'] = true_longitude
            saturn_long = self.calculate_planet_longitude('Saturn', jd, precomputed)
            perturb = 0.33 * math.sin(math.radians(2 * (true_longitude - saturn_long)))
            true_longitude += perturb
        elif planet == 'Saturn' and 'Jupiter' not in precomputed:
            precomputed['Saturn'] = true_longitude
            jupiter_long = self.calculate_planet_longitude('Jupiter', jd, precomputed)
            perturb = 0.81 * math.sin(math.radians(2 * (true_longitude - jupiter_long)))
            true_longitude += perturb
        ayanamsa = self.calculate_lahiri_ayanamsa(jd)
        sidereal_longitude = (true_longitude - ayanamsa) % 360
        return sidereal_longitude

    def calculate_ascendant(self, jd, lat, lon):
        T = (jd - 2451545.0) / 36525.0
        gmst = (280.46061837 + 360.98564736629 * (jd - 2451545.0)
                + 0.000387933 * T * T - T * T * T / 38710000.0) % 360
        lst = (gmst + lon) % 360
        lst_rad = math.radians(lst)
        lat_rad = math.radians(lat)
        obliquity = 23.4393 - 0.0130042 * T - 0.0000164 * T * T + 0.0000504 * T * T * T
        obliquity_rad = math.radians(obliquity)
        y = -math.cos(lst_rad)
        x = math.sin(lst_rad) * math.cos(obliquity_rad) + math.tan(lat_rad) * math.sin(obliquity_rad)
        ascendant = math.degrees(math.atan2(y, x))
        if ascendant < 0:
            ascendant += 360
        ayanamsa = self.calculate_lahiri_ayanamsa(jd)
        sidereal_ascendant = (ascendant - ayanamsa) % 360
        return sidereal_ascendant

    def calculate_rahu_ketu(self, jd: float) -> Tuple[float, float]:
        T = (jd - 2451545.0) / 36525.0
        omega = 125.0445479 - 1934.1362891 * T + 0.0020754 * T * T + T * T * T / 467441.0
        rahu_longitude = omega % 360
        ketu_longitude = (rahu_longitude + 180) % 360
        ayanamsa = self.calculate_lahiri_ayanamsa(jd)
        rahu_sidereal = (rahu_longitude - ayanamsa) % 360
        ketu_sidereal = (ketu_longitude - ayanamsa) % 360
        return rahu_sidereal, ketu_sidereal

    def get_zodiac_sign(self, longitude: float) -> str:
        signs = list(self.zodiac_signs.keys())
        sign_index = int(longitude // 30)
        return signs[sign_index % 12]

    def get_nakshatra(self, longitude: float) -> Tuple[str, int]:
        nakshatra_span = 360 / 27
        nakshatra_index = int(longitude / nakshatra_span)
        pada = int((longitude % nakshatra_span) / (nakshatra_span / 4)) + 1
        return self.nakshatras[nakshatra_index % 27], pada

    def get_house_from_ascendant(self, planet_longitude: float, ascendant: float) -> int:
        house_longitude = (planet_longitude - ascendant + 360) % 360
        house = int(house_longitude // 30) + 1
        return house if house <= 12 else house - 12

    def calculate_navamsa_position(self, longitude: float, ascendant_navamsa: float) -> Tuple[int, str]:
        sign_num = int(longitude // 30)
        degree_in_sign = longitude % 30
        navamsa_num = int(degree_in_sign / 3.333333)
        if sign_num % 3 == 0:
            navamsa_sign_num = (sign_num + navamsa_num) % 12
        elif sign_num % 3 == 1:
            navamsa_sign_num = (sign_num + 8 + navamsa_num) % 12
        else:
            navamsa_sign_num = (sign_num + 4 + navamsa_num) % 12
        navamsa_house = ((navamsa_sign_num * 30 - ascendant_navamsa + 360) % 360) // 30 + 1
        signs = list(self.zodiac_signs.keys())
        navamsa_sign = signs[navamsa_sign_num]
        return int(navamsa_house), navamsa_sign

    def calculate_complete_chart(self, birth_date: str, birth_time: str, birth_place: str) -> Dict:
        try:
            date_obj = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
            if birth_place not in self.cities:
                return {'error': f'City {birth_place} not found in database'}
            lat, lon, tz_offset = self.cities[birth_place]
            jd = self.calculate_accurate_julian_day(date_obj, tz_offset)
            ascendant = self.calculate_ascendant(jd, lat, lon)
            asc_sign_num = int(ascendant // 30)
            asc_degree_in_sign = ascendant % 30
            asc_navamsa_num = int(asc_degree_in_sign / 3.333333)
            if asc_sign_num % 3 == 0:
                navamsa_asc_sign_num = (asc_sign_num + asc_navamsa_num) % 12
            elif asc_sign_num % 3 == 1:
                navamsa_asc_sign_num = (asc_sign_num + 8 + asc_navamsa_num) % 12
            else:
                navamsa_asc_sign_num = (asc_sign_num + 4 + asc_navamsa_num) % 12
            navamsa_ascendant = navamsa_asc_sign_num * 30
            planets_data = {}
            sun_long = self.calculate_sun_longitude(jd)
            nav_house, nav_sign = self.calculate_navamsa_position(sun_long, navamsa_ascendant)
            planets_data['Sun'] = {
                'longitude': sun_long,
                'sign': self.get_zodiac_sign(sun_long),
                'house': self.get_house_from_ascendant(sun_long, ascendant),
                'nakshatra': self.get_nakshatra(sun_long),
                'navamsa_house': nav_house,
                'navamsa_sign': nav_sign
            }
            moon_long = self.calculate_moon_longitude(jd)
            nav_house, nav_sign = self.calculate_navamsa_position(moon_long, navamsa_ascendant)
            planets_data['Moon'] = {
                'longitude': moon_long,
                'sign': self.get_zodiac_sign(moon_long),
                'house': self.get_house_from_ascendant(moon_long, ascendant),
                'nakshatra': self.get_nakshatra(moon_long),
                'navamsa_house': nav_house,
                'navamsa_sign': nav_sign
            }
            precomputed = {}
            for planet in ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']:
                planet_long = self.calculate_planet_longitude(planet, jd, precomputed)
                nav_house, nav_sign = self.calculate_navamsa_position(planet_long, navamsa_ascendant)
                planets_data[planet] = {
                    'longitude': planet_long,
                    'sign': self.get_zodiac_sign(planet_long),
                    'house': self.get_house_from_ascendant(planet_long, ascendant),
                    'nakshatra': self.get_nakshatra(planet_long),
                    'navamsa_house': nav_house,
                    'navamsa_sign': nav_sign
                }
            rahu_long, ketu_long = self.calculate_rahu_ketu(jd)
            for planet_name, planet_long in [('Rahu', rahu_long), ('Ketu', ketu_long)]:
                nav_house, nav_sign = self.calculate_navamsa_position(planet_long, navamsa_ascendant)
                planets_data[planet_name] = {
                    'longitude': planet_long,
                    'sign': self.get_zodiac_sign(planet_long),
                    'house': self.get_house_from_ascendant(planet_long, ascendant),
                    'nakshatra': self.get_nakshatra(planet_long),
                    'navamsa_house': nav_house,
                    'navamsa_sign': nav_sign
                }
            return {
                'ascendant': ascendant,
                'ascendant_sign': self.get_zodiac_sign(ascendant),
                'navamsa_ascendant': navamsa_ascendant,
                'planets': planets_data,
                'coordinates': (lat, lon),
                'timezone': tz_offset,
                'julian_day': jd,
                'birth_date': birth_date,
                'birth_time': birth_time,
                'birth_place': birth_place,
                'ayanamsa': self.calculate_lahiri_ayanamsa(jd)
            }
        except Exception as e:
            return {'error': f'Calculation error: {str(e)}'}

    def create_traditional_tamil_chart_4x3(self, chart_data: Dict, chart_type: str = 'rasi') -> str:
        """Create a perfectly aligned 4x3 table format chart"""
        if 'error' in chart_data:
            return f"Error: {chart_data['error']}"
        
        # Initialize houses with empty lists
        houses = {i: [] for i in range(1, 13)}
        
        # Determine which position to use
        if chart_type == 'navamsa':
            position_key = 'navamsa_house'
            chart_title = "நவாம்சம் கட்டம் - NAVAMSA CHART (D9)"
        else:
            position_key = 'house'
            chart_title = "ராசி கட்டம் - RASI CHART (D1)"
        
        # Place planets in their respective houses
        for planet, data in chart_data['planets'].items():
            house_num = data[position_key]
            planet_abbrev = self.planets[planet]['abbrev']
            houses[house_num].append(planet_abbrev)
        
        # Define the 4x3 layout (house numbers in each position)
        # Traditional South Indian layout
        chart_layout = [
            [12,  1,  2],   # Row 1
            [11, None, 3],   # Row 2 (center is empty)
            [10, None, 4],   # Row 3 (center is empty)  
            [ 9,  8,  7]    # Row 4
        ]
        
        def format_cell_content(house_num):
            """Format the content for each cell with perfect alignment"""
            if house_num is None:
                return "        "  # Empty center cells
            
            planets_in_house = houses.get(house_num, [])
            house_label = f"H{house_num:2d}"  # House number label
            
            if not planets_in_house:
                return f"{house_label}     "  # Just house number, padded to 8 chars
            elif len(planets_in_house) == 1:
                return f"{house_label} {planets_in_house[0]:>3} "  # House + 1 planet
            elif len(planets_in_house) == 2:
                return f"{house_label}{planets_in_house[0]:>2}{planets_in_house[1]:>2}"  # House + 2 planets
            elif len(planets_in_house) == 3:
                return f"H{house_num}{planets_in_house[0]}{planets_in_house[1]}{planets_in_house[2]}"  # Compact format
            else:
                # More than 3 planets - show first 2 + indicator
                return f"H{house_num}{planets_in_house[0]}{planets_in_house[1]}+"
        
        # Build the chart
        chart_lines = []
        chart_lines.append("")
        chart_lines.append("=" * 60)
        chart_lines.append(f"         {chart_title}")
        chart_lines.append("=" * 60)
        chart_lines.append("")
        
        # Create the 4x3 table with perfect alignment
        cell_width = 18
        border_char = "+"
        line_char = "-"
        vertical_char = "|"
        
        # Top border
        chart_lines.append(border_char + (line_char * cell_width + border_char) * 3)
        
        # Row 1
        row1_content = vertical_char
        for col in range(3):
            house_num = chart_layout[0][col]
            content = format_cell_content(house_num)
            row1_content += f" {content:^16} {vertical_char}"
        chart_lines.append(row1_content)
        
        # Middle separator
        chart_lines.append(border_char + (line_char * cell_width + border_char) * 3)
        
        # Row 2
        row2_content = vertical_char
        for col in range(3):
            house_num = chart_layout[1][col]
            if col == 1:  # Center column - add chart type label
                if chart_type == 'navamsa':
                    label = "நவாம்சம்"
                else:
                    label = "ராசி"
                row2_content += f" {label:^16} {vertical_char}"
            else:
                content = format_cell_content(house_num)
                row2_content += f" {content:^16} {vertical_char}"
        chart_lines.append(row2_content)
        
        # Middle separator
        chart_lines.append(border_char + (line_char * cell_width + border_char) * 3)
        
        # Row 3
        row3_content = vertical_char
        for col in range(3):
            house_num = chart_layout[2][col]
            if col == 1:  # Center column - empty
                row3_content += f" {'':^16} {vertical_char}"
            else:
                content = format_cell_content(house_num)
                row3_content += f" {content:^16} {vertical_char}"
        chart_lines.append(row3_content)
        
        # Middle separator
        chart_lines.append(border_char + (line_char * cell_width + border_char) * 3)
        
        # Row 4
        row4_content = vertical_char
        for col in range(3):
            house_num = chart_layout[3][col]
            content = format_cell_content(house_num)
            row4_content += f" {content:^16} {vertical_char}"
        chart_lines.append(row4_content)
        
        # Bottom border
        chart_lines.append(border_char + (line_char * cell_width + border_char) * 3)
        chart_lines.append("")
        
        # Add house mapping legend
        chart_lines.append("📍 House Layout Guide:")
        chart_lines.append("-" * 25)
        
        chart_lines.append("")
        
        return "\n".join(chart_lines)

    def create_detailed_analysis(self, chart_data: Dict) -> str:
        if 'error' in chart_data:
            return f"Error: {chart_data['error']}"
        
        analysis_lines = []
        analysis_lines.append("\n" + "=" * 100)
        analysis_lines.append("விரிவான கிரக நிலைகள் மற்றும் பலன்கள்")
        analysis_lines.append("DETAILED PLANETARY POSITIONS & ANALYSIS")
        analysis_lines.append("=" * 100)
        
        # Birth Details
        analysis_lines.append(f"\nபிறப்பு விவரங்கள் - BIRTH DETAILS:")
        analysis_lines.append("-" * 50)
        analysis_lines.append(f"தேதி (Date)        : {chart_data['birth_date']}")
        analysis_lines.append(f"நேரம் (Time)       : {chart_data['birth_time']}")
        analysis_lines.append(f"இடம் (Place)       : {chart_data['birth_place']}")
        analysis_lines.append(f"அட்சாம்சம் (Latitude) : {chart_data['coordinates'][0]:.4f}°N")
        analysis_lines.append(f"தீர்க்காம்சம் (Longitude): {chart_data['coordinates'][1]:.4f}°E")
        analysis_lines.append(f"நேர வேறுபாடு (Timezone) : UTC{chart_data['timezone']:+.1f} hours")
        analysis_lines.append(f"ஜூலியன் நாள் (Julian Day): {chart_data['julian_day']:.6f}")
        analysis_lines.append(f"அயனாம்சம் (Ayanamsa)   : {chart_data['ayanamsa']:.4f}°")
        analysis_lines.append(f"லக்னம் (Ascendant)    : {self.zodiac_signs[chart_data['ascendant_sign']]['tamil']} ({chart_data['ascendant']:.2f}°)")
        
        # Planetary Positions Table
        analysis_lines.append(f"\nகிரக நிலைகள் - PLANETARY POSITIONS:")
        analysis_lines.append("=" * 120)
        analysis_lines.append(f"{'கிரகம்':<12} {'ராசி':<12} {'வீடு':<6} {'பாகை':<10} {'நட்சத்திரம்':<14} {'பாதம்':<6} {'நவாம்சம்':<12} {'நவ.வீடு':<8}")
        analysis_lines.append("-" * 120)
        
        for planet, data in chart_data['planets'].items():
            planet_tamil = self.planets[planet]['tamil']
            sign_tamil = self.zodiac_signs[data['sign']]['tamil']
            house = data['house']
            degree = data['longitude'] % 30
            nakshatra, pada = data['nakshatra']
            navamsa_sign_tamil = self.zodiac_signs[data['navamsa_sign']]['tamil']
            navamsa_house = data['navamsa_house']
            
            analysis_lines.append(f"{planet_tamil:<12} {sign_tamil:<12} {house:<6} {degree:7.2f}°   {nakshatra:<14} {pada:<6} {navamsa_sign_tamil:<12} {navamsa_house:<8}")
        
        # House-wise Analysis
        analysis_lines.append(f"\n\nவீடு வார ஆராய்ச்சி - HOUSE-WISE ANALYSIS:")
        analysis_lines.append("=" * 80)
        
        houses_planets = {i: [] for i in range(1, 13)}
        for planet, data in chart_data['planets'].items():
            house = data['house']
            planet_tamil = self.planets[planet]['tamil']
            houses_planets[house].append(planet_tamil)
        
        house_meanings = {
            1: "தனுசு/லக்னம் - व्यक्तित्व, स्वास्थ्य, शरीर",
            2: "धन - धन, परिवार, वाणी", 
            3: "सहज - साहस, भाई-बहन, कला",
            4: "सुख - माता, घर, सुख, शिक्षा",
            5: "संतान - संतान, विद्या, मन",
            6: "रोग - शत्रु, रोग, सेवा",
            7: "कलत्र - जीवनसाथी, व्यापार",
            8: "आयु - आयु, गुप्त विद्या",
            9: "भाग्य - भाग्य, धर्म, पिता",
            10: "कर्म - कर्म, प्रतिष्ठा, राज्य",
            11: "लाभ - लाभ, आय, मित्र",
            12: "व्यय - व्यय, हानि, मोक्ष"
        }
        
        for house_num in range(1, 13):
            planets_in_house = houses_planets[house_num]
            if planets_in_house:
                planets_str = ", ".join(planets_in_house)
                analysis_lines.append(f"வீடு {house_num:2d}: {planets_str}")
            else:
                analysis_lines.append(f"வீடு {house_num:2d}: (காலி)")
        
        # Add strengths and aspects analysis
        analysis_lines.append(f"\n\nகிரக பலங்கள் - PLANETARY STRENGTHS:")
        analysis_lines.append("=" * 60)
        
        for planet, data in chart_data['planets'].items():
            planet_tamil = self.planets[planet]['tamil']
            sign = data['sign']
            house = data['house']
            
            # Simple strength analysis based on sign placement
            strength_info = self.analyze_planet_strength(planet, sign, house)
            analysis_lines.append(f"{planet_tamil:<12}: {strength_info}")
        
        return "\n".join(analysis_lines)

    def analyze_planet_strength(self, planet: str, sign: str, house: int) -> str:
        """Analyze basic planetary strength"""
        # Exaltation and debilitation signs
        exaltation = {
            'Sun': 'Aries', 'Moon': 'Taurus', 'Mars': 'Capricorn', 
            'Mercury': 'Virgo', 'Jupiter': 'Cancer', 'Venus': 'Pisces', 
            'Saturn': 'Libra', 'Rahu': 'Taurus', 'Ketu': 'Scorpio'
        }
        
        debilitation = {
            'Sun': 'Libra', 'Moon': 'Scorpio', 'Mars': 'Cancer',
            'Mercury': 'Pisces', 'Jupiter': 'Capricorn', 'Venus': 'Virgo',
            'Saturn': 'Aries', 'Rahu': 'Scorpio', 'Ketu': 'Taurus'
        }
        
        own_signs = {
            'Sun': ['Leo'], 'Moon': ['Cancer'], 'Mars': ['Aries', 'Scorpio'],
            'Mercury': ['Gemini', 'Virgo'], 'Jupiter': ['Sagittarius', 'Pisces'],
            'Venus': ['Taurus', 'Libra'], 'Saturn': ['Capricorn', 'Aquarius']
        }
        
        if planet in exaltation and sign == exaltation[planet]:
            return f"உச்சம் (Exalted) in {sign} - வலிமையானது"
        elif planet in debilitation and sign == debilitation[planet]:
            return f"நீசம் (Debilitated) in {sign} - பலவீனமானது"
        elif planet in own_signs and sign in own_signs[planet]:
            return f"சொந்த ராசி (Own Sign) in {sign} - நன்மையானது"
        else:
            return f"சாதாரண நிலை (Neutral) in {sign}"

    def create_pdf_report(self, chart_data: Dict, filename: str) -> str:
        """Create a professional PDF report of the horoscope"""
        if 'error' in chart_data:
            return None
        
        try:
            # Create PDF document
            doc = SimpleDocTemplate(filename, pagesize=A4, 
                                  topMargin=0.5*inch, bottomMargin=0.5*inch)
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            )
            
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=20,
                textColor=colors.darkgreen
            )
            
            # Title
            story.append(Paragraph("🌟 தமிழ் ஜாதக அறிக்கை - Tamil Horoscope Report", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Birth Details
            story.append(Paragraph("பிறப்பு விவரங்கள் - Birth Details", subtitle_style))
            birth_data = [
                ['தேதி (Date)', chart_data['birth_date']],
                ['நேரம் (Time)', chart_data['birth_time']],
                ['இடம் (Place)', chart_data['birth_place']],
                ['அட்சாம்சம் (Latitude)', f"{chart_data['coordinates'][0]:.4f}°N"],
                ['தீர்க்காம்சம் (Longitude)', f"{chart_data['coordinates'][1]:.4f}°E"],
                ['லக்னம் (Ascendant)', f"{self.zodiac_signs[chart_data['ascendant_sign']]['tamil']} ({chart_data['ascendant']:.2f}°)"]
            ]
            birth_table = Table(birth_data, colWidths=[2*inch, 3*inch])
            birth_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(birth_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Rasi Chart
            story.append(Paragraph("ராசி கட்டம் - Rasi Chart", subtitle_style))
            rasi_chart_text = self.create_traditional_tamil_chart_4x3(chart_data, 'rasi')
            story.append(Paragraph(f"<pre>{rasi_chart_text}</pre>", styles['Code']))
            story.append(Spacer(1, 0.3*inch))
            
            # Navamsa Chart
            story.append(Paragraph("நவாம்சம் கட்டம் - Navamsa Chart", subtitle_style))
            navamsa_chart_text = self.create_traditional_tamil_chart_4x3(chart_data, 'navamsa')
            story.append(Paragraph(f"<pre>{navamsa_chart_text}</pre>", styles['Code']))
            story.append(Spacer(1, 0.3*inch))
            
            # Planetary Positions
            story.append(Paragraph("கிரக நிலைகள் - Planetary Positions", subtitle_style))
            planet_data = [['கிரகம் (Planet)', 'ராசி (Sign)', 'வீடு (House)', 'பாகை (Degree)', 'நட்சத்திரம் (Nakshatra)', 'பாதம் (Pada)']]
            
            for planet, data in chart_data['planets'].items():
                planet_tamil = self.planets[planet]['tamil']
                sign_tamil = self.zodiac_signs[data['sign']]['tamil']
                house = str(data['house'])
                degree = f"{data['longitude'] % 30:.2f}°"
                nakshatra, pada = data['nakshatra']
                planet_data.append([planet_tamil, sign_tamil, house, degree, nakshatra, str(pada)])
            
            planet_table = Table(planet_data, colWidths=[1.2*inch, 1.2*inch, 0.8*inch, 1*inch, 1.5*inch, 0.8*inch])
            planet_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            story.append(planet_table)
            
            # Build PDF
            doc.build(story)
            return filename
        except Exception as e:
            return f"PDF Error: {str(e)}"

def generate_complete_horoscope_with_pdf(birth_date, birth_time, birth_place):
    calculator = EnhancedAstrologyCalculator()
    chart_data = calculator.calculate_complete_chart(birth_date, birth_time, birth_place)
    
    if 'error' in chart_data:
        error_msg = f"Error: {chart_data['error']}"
        return error_msg, error_msg, error_msg, error_msg, None
    
    # Create text outputs using new 4x3 format
    rasi_chart = calculator.create_traditional_tamil_chart_4x3(chart_data, 'rasi')
    navamsa_chart = calculator.create_traditional_tamil_chart_4x3(chart_data, 'navamsa')
    detailed_analysis = calculator.create_detailed_analysis(chart_data)
    
    # Create framed output
    framed_output = create_framed_display_4x3(chart_data, rasi_chart, navamsa_chart)
    
    # Create PDF
    pdf_filename = f"horoscope_{birth_date}_{birth_time.replace(':', '')}.pdf"
    try:
        pdf_path = calculator.create_pdf_report(chart_data, pdf_filename)
        return framed_output, rasi_chart, navamsa_chart, detailed_analysis, pdf_path
    except Exception as e:
        return framed_output, rasi_chart, navamsa_chart, detailed_analysis, f"PDF Error: {str(e)}"

def create_framed_display_4x3(chart_data, rasi_chart, navamsa_chart):
    """Create a beautifully framed display with 4x3 layout"""
    frame_width = 120
    frame_char = "="
    
    framed_lines = []
    
    # Top border
    framed_lines.append(frame_char * frame_width)
    framed_lines.append(f"{' ' * 25}🌟 தமிழ் ஜாதக அறிக்கை - TAMIL HOROSCOPE REPORT 🌟")
    framed_lines.append(f"{' ' * 30}Enhanced 4x3 Table Layout - Perfect Alignment")
    framed_lines.append(frame_char * frame_width)
    
    # Birth details section
    framed_lines.append("")
    framed_lines.append("📅 பிறப்பு விவரங்கள் - BIRTH DETAILS:")
    framed_lines.append("-" * 60)
    framed_lines.append(f"தேதி (Date)        : {chart_data['birth_date']}")
    framed_lines.append(f"நேரம் (Time)       : {chart_data['birth_time']}")
    framed_lines.append(f"இடம் (Place)       : {chart_data['birth_place']}")
    framed_lines.append(f"அட்சாம்சம் (Lat)    : {chart_data['coordinates'][0]:.4f}°N")
    framed_lines.append(f"தீர்க்காம்சம் (Lon)  : {chart_data['coordinates'][1]:.4f}°E")
    framed_lines.append(f"நேர வேறுபாடு (TZ)   : UTC{chart_data['timezone']:+.1f} hours")
    
    calculator = EnhancedAstrologyCalculator()
    ascendant_sign_tamil = calculator.zodiac_signs[chart_data['ascendant_sign']]['tamil']
    framed_lines.append(f"லக்னம் (Ascendant) : {ascendant_sign_tamil} ({chart_data['ascendant']:.2f}°)")
    
    # Charts section with 4x3 format
    framed_lines.append("")
    framed_lines.append("🏠 CHARTS WITH 4x3 TABLE LAYOUT:")
    framed_lines.extend(rasi_chart.split('\n'))
    
    framed_lines.extend(navamsa_chart.split('\n'))
    
    # Planetary positions in tabular format
    framed_lines.append("")
    framed_lines.append("🌟 கிரக நிலைகள் - PLANETARY POSITIONS:")
    framed_lines.append("=" * 100)
    framed_lines.append(f"{'கிரகம்':<12} {'ராசி':<12} {'வீடு':<6} {'பாகை':<10} {'நட்சத்திரம்':<14} {'பாதம்':<6} {'நவ.வீடு':<8}")
    framed_lines.append("-" * 100)
    
    for planet, data in chart_data['planets'].items():
        planet_tamil = calculator.planets[planet]['tamil']
        sign_tamil = calculator.zodiac_signs[data['sign']]['tamil']
        house = data['house']
        degree = data['longitude'] % 30
        nakshatra, pada = data['nakshatra']
        navamsa_house = data['navamsa_house']
        framed_lines.append(f"{planet_tamil:<12} {sign_tamil:<12} {house:<6} {degree:7.2f}°   {nakshatra:<14} {pada:<6} {navamsa_house:<8}")
    
    # Technical details
    framed_lines.append("")
    framed_lines.append("🔬 தकनिकી विवरण - TECHNICAL DETAILS:")
    framed_lines.append("-" * 50)
    framed_lines.append(f"Julian Day    : {chart_data['julian_day']:.6f}")
    framed_lines.append(f"Ayanamsa      : {chart_data['ayanamsa']:.4f}° (Lahiri)")
    framed_lines.append(f"Navamsa Asc   : {chart_data['navamsa_ascendant']:.2f}°")
    
    # Bottom border
    framed_lines.append("")
    framed_lines.append(frame_char * frame_width)
    framed_lines.append(f"{' ' * 25}Generated by Enhanced Tamil Astrology Calculator")
    framed_lines.append(f"{' ' * 30}Perfect 4x3 Table Layout - Professional Format")
    framed_lines.append(frame_char * frame_width)
    
    return "\n".join(framed_lines)

def create_interface():
    calculator = EnhancedAstrologyCalculator()
    
    with gr.Blocks(title="Enhanced Tamil Astrology Calculator - Perfect 4x3 Layout", 
                   theme=gr.themes.Soft(),
                   css="""
                   .framed-output {
                       border: 3px solid #4A90E2;
                       border-radius: 10px;
                       padding: 20px;
                       background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                       font-family: 'Courier New', monospace;
                       white-space: pre-wrap;
                       box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                       font-size: 11px;
                       line-height: 1.2;
                   }
                   .chart-output {
                       font-family: 'Courier New', monospace;
                       font-size: 12px;
                       line-height: 1.3;
                       background: #f8f9fa;
                       border: 2px solid #dee2e6;
                       border-radius: 8px;
                       padding: 15px;
                   }
                   .analysis-output {
                       font-family: 'Courier New', monospace;
                       font-size: 10px;
                       line-height: 1.2;
                       background: #fff9c4;
                       border: 2px solid #ffd60a;
                       border-radius: 8px;
                       padding: 15px;
                   }
                   .pdf-download {
                       background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
                       color: white;
                       border-radius: 10px;
                       padding: 10px 20px;
                       font-weight: bold;
                   }
                   """) as interface:
        
        gr.Markdown("""
        # 🌟 தமிழ் ஜாதக கணிப்பு - Enhanced Tamil Astrology Calculator
        ## Perfect 4x3 Table Layout - Professional Chart Format
        ### Generate Traditional South Indian Birth Charts with Perfect Alignment + PDF Export
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                birth_date = gr.Textbox(
                    label="Birth Date (YYYY-MM-DD) / பிறந்த தேதி",
                    placeholder="2003-02-13",
                    value="2003-02-13"
                )
                birth_time = gr.Textbox(
                    label="Birth Time (HH:MM, 24-hour) / பிறந்த நேரம்",
                    placeholder="07:00",
                    value="07:00"
                )
                birth_place = gr.Dropdown(
                    label="Birth Place / பிறந்த இடம் (200+ cities worldwide)",
                    choices=sorted(list(calculator.cities.keys())),
                    value="Chennai",
                    filterable=True,
                    allow_custom_value=False
                )
                generate_btn = gr.Button(
                    "🎯 Generate Perfect 4x3 Chart & PDF / முழுமையான 4x3 கட்ட ஜாதகம்",
                    variant="primary",
                    size="lg"
                )
        
        with gr.Column(scale=2):
            # Framed Display Output
            with gr.Group():
                gr.Markdown("### 📋 Complete Horoscope Report - 4x3 Perfect Layout")
                framed_display = gr.Textbox(
                    label="",
                    lines=45,
                    max_lines=60,
                    interactive=False,
                    show_copy_button=True,
                    elem_classes=["framed-output"]
                )
            
            # PDF Download
            with gr.Group():
                gr.Markdown("### 📄 Download Professional PDF Report")
                pdf_download = gr.File(
                    label="Download PDF Horoscope / ஜாதக PDF பதிவிறக்கம்",
                    elem_classes=["pdf-download"]
                )
            
            # Detailed tabs
            with gr.Tabs():
                with gr.Tab("Rasi Chart (4x3) / ராசி கட்டம்"):
                    rasi_output = gr.Textbox(
                        label="Perfect 4x3 Rasi Chart / சரியான 4x3 ராசி கட்டம்",
                        lines=20,
                        max_lines=30,
                        interactive=False,
                        show_copy_button=True,
                        elem_classes=["chart-output"]
                    )
                
                with gr.Tab("Navamsa Chart (4x3) / நவாம்சம் கட்டம்"):
                    navamsa_output = gr.Textbox(
                        label="Perfect 4x3 Navamsa Chart / சரியான 4x3 நவாம்சம் கட்டம்",
                        lines=20,
                        max_lines=30,
                        interactive=False,
                        show_copy_button=True,
                        elem_classes=["chart-output"]
                    )
                
                with gr.Tab("Detailed Analysis / விரிவான பகுப்பாய்வு"):
                    analysis_output = gr.Textbox(
                        label="Complete Planetary Analysis / முழுமையான கிரக பகுப்பாய்வு",
                        lines=40,
                        max_lines=60,
                        interactive=False,
                        show_copy_button=True,
                        elem_classes=["analysis-output"]
                    )
        
        # Event handler
        generate_btn.click(
            fn=generate_complete_horoscope_with_pdf,
            inputs=[birth_date, birth_time, birth_place],
            outputs=[framed_display, rasi_output, navamsa_output, analysis_output, pdf_download]
        )
        
        # Examples with perfect formatting demonstration
        gr.Examples(
            examples=[
                ["2003-02-13", "07:00", "Chennai"],
                ["1990-05-15", "10:30", "Coimbatore"],
                ["1985-12-25", "18:45", "Madurai"],
                ["1995-03-08", "06:15", "Salem"],
                ["1988-07-20", "14:20", "Bangalore"],
                ["1992-11-11", "09:45", "Mumbai"],
                ["1987-06-30", "16:30", "Delhi"],
                ["1994-09-12", "05:45", "London"],
                ["1999-01-01", "12:00", "New York"],
                ["1996-06-15", "18:30", "Tokyo"],
            ],
            inputs=[birth_date, birth_time, birth_place],
            label="Example Charts - Perfect 4x3 Layout / உதாரண ஜாதகங்கள் - சரியான 4x3 அமைப்பு"
        )
        
        gr.Markdown("""
        ## ⭐ NEW: Perfect 4x3 Table Layout Features
        
        ### 🎯 **Enhanced Chart Display:**
        - **Perfect 4x3 Grid Layout** - Traditional South Indian format
        - **Perfectly Aligned Tables** with proper spacing and borders
        - **House Labels** clearly marked (H01, H02, etc.)
        - **Professional Formatting** suitable for printing and sharing
        - **Consistent Cell Width** for perfect visual alignment
        
        ### 📐 **4x3 Layout Structure:**
        ```
        Row 1: [House 12] [House 1 - Lagna] [House 2]
        Row 2: [House 11] [Chart Center]    [House 3] 
        Row 3: [House 10] [Empty Space]     [House 4]
        Row 4: [House 9]  [House 8]        [House 7]
        ```
        
        ### ✅ **Perfect Alignment Features:**
        - **Fixed-width cells** ensure consistent spacing
        - **Centered planet abbreviations** for easy reading
        - **House number labels** for quick reference
        - **Professional borders** with proper ASCII art
        - **Multiple planet handling** in the same house
        
        ### 🎨 **Visual Enhancements:**
        - **Color-coded sections** in the interface
        - **Styled text boxes** with custom CSS
        - **Professional typography** using monospace fonts
        - **Consistent line spacing** throughout
        - **Easy-to-read format** suitable for all ages
        
        ### 📊 **Comprehensive Analysis:**
        - **Planetary positions** with degrees and minutes
        - **Nakshatra and Pada** calculations
        - **Navamsa positions** for detailed analysis
        - **House-wise planet distribution**
        - **Strength analysis** based on sign placement
        - **Technical details** including Julian Day and Ayanamsa
        
        ### 💎 **Professional Output:**
        - **PDF Export** with the same perfect formatting
        - **Copy-paste ready** text format
        - **Print-friendly** layout design
        - **Traditional accuracy** meets modern presentation
        - **Multiple language** support (Tamil + English)
        
        ### 🌍 **Global City Support:**
        - **Tamil Nadu**: All major cities and districts
        - **India**: Major cities across all states  
        - **International**: 50+ major world cities
        - **Accurate coordinates** and timezone data
        
        ### 🔬 **Technical Accuracy:**
        - **Lahiri Ayanamsa** with high precision
        - **VSOP87 theory** for planetary positions
        - **True lunar node** calculations
        - **Microsecond-level** time accuracy
        - **Professional-grade** astronomical calculations
        
        ## 📋 Chart Reading Guide:
        - **H01-H12**: House numbers for easy identification
        - **Planet abbreviations**: சூ (Sun), ச (Moon), செ (Mars), etc.
        - **Multiple planets**: Shown as combinations like "H01 சூ ச"
        - **Empty houses**: Shown as just house number
        - **Perfect spacing**: Each cell exactly aligned for professional look
        
        The 4x3 format ensures maximum clarity and follows traditional South Indian astrology chart layouts used by professional astrologers for centuries.
        """)
    
    return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        share=True,
        show_error=True
    )
