"""
Port service for looking up port coordinates and shipping information
"""

import logging
import math
from typing import Dict, Optional, List, Any
import asyncio


logger = logging.getLogger(__name__)


class PortService:
    """Service for port lookup and shipping calculations"""
    
    def __init__(self):
        # Major world ports database (expanded for better coverage)
        self.ports_db = {
            # North America - US West Coast
            "port of los angeles": {"lat": 33.7361, "lon": -118.2922, "country": "United States", "code": "USLAX"},
            "port of long beach": {"lat": 33.7543, "lon": -118.2139, "country": "United States", "code": "USLGB"},
            "port of oakland": {"lat": 37.7955, "lon": -122.3120, "country": "United States", "code": "USOAK"},
            "port of seattle": {"lat": 47.6062, "lon": -122.3321, "country": "United States", "code": "USSEA"},
            "port of tacoma": {"lat": 47.2529, "lon": -122.4443, "country": "United States", "code": "USTAC"},
            "port of san francisco": {"lat": 37.7749, "lon": -122.4194, "country": "United States", "code": "USSFO"},
            
            # North America - US East Coast & Gulf
            "port of new york": {"lat": 40.6892, "lon": -74.0445, "country": "United States", "code": "USNYC"},
            "port of savannah": {"lat": 32.0835, "lon": -81.0998, "country": "United States", "code": "USSAV"},
            "port of charleston": {"lat": 32.7767, "lon": -79.9311, "country": "United States", "code": "USCHS"},
            "port of miami": {"lat": 25.7617, "lon": -80.1918, "country": "United States", "code": "USMIA"},
            "port of houston": {"lat": 29.7604, "lon": -95.3698, "country": "United States", "code": "USHOU"},
            "port of new orleans": {"lat": 29.9511, "lon": -90.0715, "country": "United States", "code": "USMSY"},
            "port of baltimore": {"lat": 39.2904, "lon": -76.6122, "country": "United States", "code": "USBAL"},
            "port of norfolk": {"lat": 36.8468, "lon": -76.2951, "country": "United States", "code": "USNFK"},
            "port of san francisco": {"lat": 37.7749, "lon": -122.4194, "country": "United States", "code": "USSFO"},
            
            # North America - Canada
            "port of vancouver": {"lat": 49.2827, "lon": -123.1207, "country": "Canada", "code": "CAVAN"},
            "port of montreal": {"lat": 45.5017, "lon": -73.5673, "country": "Canada", "code": "CAMTR"},
            "port of halifax": {"lat": 44.6488, "lon": -63.5752, "country": "Canada", "code": "CAHAL"},
            "port of prince rupert": {"lat": 54.3150, "lon": -130.3208, "country": "Canada", "code": "CAPRP"},
            
            # Asia - China
            "port of shanghai": {"lat": 31.2304, "lon": 121.4737, "country": "China", "code": "CNSHA"},
            "port of shenzhen": {"lat": 22.5431, "lon": 114.0579, "country": "China", "code": "CNSZX"},
            "port of ningbo": {"lat": 29.8683, "lon": 121.5440, "country": "China", "code": "CNNGB"},
            "port of qingdao": {"lat": 36.0986, "lon": 120.3719, "country": "China", "code": "CNTAO"},
            "port of tianjin": {"lat": 39.1042, "lon": 117.2009, "country": "China", "code": "CNTSN"},
            "port of guangzhou": {"lat": 23.1291, "lon": 113.2644, "country": "China", "code": "CNGZH"},
            "port of dalian": {"lat": 38.9140, "lon": 121.6147, "country": "China", "code": "CNDLC"},
            "port of xiamen": {"lat": 24.4798, "lon": 118.0819, "country": "China", "code": "CNXMN"},
            "port of suzhou": {"lat": 31.2983, "lon": 120.5831, "country": "China", "code": "CNSUZ"},
            
            # Asia - India
            "port of mumbai": {"lat": 19.0760, "lon": 72.8777, "country": "India", "code": "INMAA"},
            "port of chennai": {"lat": 13.0827, "lon": 80.2707, "country": "India", "code": "INMAA"},
            "port of kolkata": {"lat": 22.5726, "lon": 88.3639, "country": "India", "code": "INCCU"},
            "port of kochi": {"lat": 9.9312, "lon": 76.2673, "country": "India", "code": "INCOK"},
            "port of visakhapatnam": {"lat": 17.6868, "lon": 83.2185, "country": "India", "code": "INVTZ"},
            "port of jawaharlal nehru": {"lat": 18.9480, "lon": 72.9881, "country": "India", "code": "INNSA"},
            
            # Asia - Southeast Asia
            "port of singapore": {"lat": 1.2966, "lon": 103.8517, "country": "Singapore", "code": "SGSIN"},
            "port of bangkok": {"lat": 13.7563, "lon": 100.5018, "country": "Thailand", "code": "THBKK"},
            "port of ho chi minh city": {"lat": 10.8231, "lon": 106.6297, "country": "Vietnam", "code": "VNSGN"},
            "port of jakarta": {"lat": -6.1087, "lon": 106.3694, "country": "Indonesia", "code": "IDJKT"},
            "port of manila": {"lat": 14.5995, "lon": 120.9842, "country": "Philippines", "code": "PHMNL"},
            "port of haiphong": {"lat": 20.8449, "lon": 106.6881, "country": "Vietnam", "code": "VNHPH"},
            "port of kuala lumpur": {"lat": 3.1390, "lon": 101.6869, "country": "Malaysia", "code": "MYKUL"},
            
            # Asia - Other East Asia
            "port of busan": {"lat": 35.1796, "lon": 129.0756, "country": "South Korea", "code": "KRPUS"},
            "port of hong kong": {"lat": 22.3193, "lon": 114.1694, "country": "Hong Kong", "code": "HKHKG"},
            "port of kobe": {"lat": 34.6901, "lon": 135.1956, "country": "Japan", "code": "JPUKB"},
            "port of yokohama": {"lat": 35.4437, "lon": 139.6380, "country": "Japan", "code": "JPYOK"},
            "port of tokyo": {"lat": 35.6762, "lon": 139.6503, "country": "Japan", "code": "JPTYO"},
            "port of kaohsiung": {"lat": 22.6273, "lon": 120.3014, "country": "Taiwan", "code": "TWKHH"},
            "port of nagoya": {"lat": 35.1815, "lon": 136.9066, "country": "Japan", "code": "JPNGO"},
            "port of incheon": {"lat": 37.4563, "lon": 126.7052, "country": "South Korea", "code": "KRICN"},
            
            # Europe - Northern Europe
            "port of rotterdam": {"lat": 51.9225, "lon": 4.4792, "country": "Netherlands", "code": "NLRTM"},
            "port of antwerp": {"lat": 51.2993, "lon": 4.4014, "country": "Belgium", "code": "BEANR"},
            "port of hamburg": {"lat": 53.5511, "lon": 9.9937, "country": "Germany", "code": "DEHAM"},
            "port of felixstowe": {"lat": 51.9640, "lon": 1.3518, "country": "United Kingdom", "code": "GBFXT"},
            "port of le havre": {"lat": 49.4944, "lon": 0.1079, "country": "France", "code": "FRLEH"},
            "port of bremen": {"lat": 53.0793, "lon": 8.8017, "country": "Germany", "code": "DEBRE"},
            "port of london": {"lat": 51.5074, "lon": -0.1278, "country": "United Kingdom", "code": "GBLON"},
            "port of gothenburg": {"lat": 57.7089, "lon": 11.9746, "country": "Sweden", "code": "SEGOT"},
            "port of oslo": {"lat": 59.9139, "lon": 10.7522, "country": "Norway", "code": "NOOSL"},
            
            # Europe - Southern Europe
            "port of genoa": {"lat": 44.4056, "lon": 8.9463, "country": "Italy", "code": "ITGOA"},
            "port of barcelona": {"lat": 41.3851, "lon": 2.1734, "country": "Spain", "code": "ESBCN"},
            "port of valencia": {"lat": 39.4699, "lon": -0.3763, "country": "Spain", "code": "ESVLC"},
            "port of piraeus": {"lat": 37.9755, "lon": 23.7348, "country": "Greece", "code": "GRPIR"},
            "port of marseille": {"lat": 43.2965, "lon": 5.3698, "country": "France", "code": "FRMRS"},
            "port of naples": {"lat": 40.8518, "lon": 14.2681, "country": "Italy", "code": "ITNAP"},
            "port of algeciras": {"lat": 36.1408, "lon": -5.4526, "country": "Spain", "code": "ESALG"},
            "port of gioia tauro": {"lat": 38.4244, "lon": 15.8897, "country": "Italy", "code": "ITGIT"},
            
            # Middle East
            "port of dubai": {"lat": 25.2048, "lon": 55.2708, "country": "UAE", "code": "AEDXB"},
            "port of jebel ali": {"lat": 25.0118, "lon": 55.0618, "country": "UAE", "code": "AEJEA"},
            "port of abu dhabi": {"lat": 24.4539, "lon": 54.3773, "country": "UAE", "code": "AEAUH"},
            "port of jeddah": {"lat": 21.4858, "lon": 39.1925, "country": "Saudi Arabia", "code": "SAJED"},
            "port of dammam": {"lat": 26.4207, "lon": 50.0888, "country": "Saudi Arabia", "code": "SADMM"},
            "port of bandar abbas": {"lat": 27.1865, "lon": 56.2808, "country": "Iran", "code": "IRBND"},
            "port of sohar": {"lat": 24.3415, "lon": 56.7539, "country": "Oman", "code": "OMSOH"},
            "port of kuwait": {"lat": 29.3759, "lon": 47.9774, "country": "Kuwait", "code": "KWKWI"},
            
            # Africa - North Africa
            "port of alexandria": {"lat": 31.2001, "lon": 29.9187, "country": "Egypt", "code": "EGALX"},
            "port of suez": {"lat": 29.9668, "lon": 32.5498, "country": "Egypt", "code": "EGSUZ"},
            "port of casablanca": {"lat": 33.5731, "lon": -7.5898, "country": "Morocco", "code": "MACAS"},
            "port of tunis": {"lat": 36.8065, "lon": 10.1815, "country": "Tunisia", "code": "TNTUN"},
            
            # Africa - West Africa
            "port of lagos": {"lat": 6.5244, "lon": 3.3792, "country": "Nigeria", "code": "NGLOS"},
            "port of tema": {"lat": 5.6037, "lon": -0.0163, "country": "Ghana", "code": "GHTEM"},
            "port of abidjan": {"lat": 5.3600, "lon": -4.0083, "country": "Ivory Coast", "code": "CIABJ"},
            "port of dakar": {"lat": 14.6937, "lon": -17.4441, "country": "Senegal", "code": "SNDKR"},
            
            # Africa - East & South Africa
            "port of durban": {"lat": -29.8587, "lon": 31.0218, "country": "South Africa", "code": "ZADUR"},
            "port of cape town": {"lat": -33.9249, "lon": 18.4241, "country": "South Africa", "code": "ZACPT"},
            "port of dar es salaam": {"lat": -6.7924, "lon": 39.2083, "country": "Tanzania", "code": "TZDAR"},
            "port of mombasa": {"lat": -4.0435, "lon": 39.6682, "country": "Kenya", "code": "KEMBA"},
            "port of port elizabeth": {"lat": -33.9580, "lon": 25.6022, "country": "South Africa", "code": "ZAPLZ"},
            
            # South America
            "port of santos": {"lat": -23.9618, "lon": -46.3322, "country": "Brazil", "code": "BRSSZ"},
            "port of buenos aires": {"lat": -34.6118, "lon": -58.3960, "country": "Argentina", "code": "ARBUE"},
            "port of callao": {"lat": -12.0464, "lon": -77.1428, "country": "Peru", "code": "PECLL"},
            "port of cartagena": {"lat": 10.3910, "lon": -75.4794, "country": "Colombia", "code": "COCTG"},
            "port of rio de janeiro": {"lat": -22.9068, "lon": -43.1729, "country": "Brazil", "code": "BRRIO"},
            "port of valparaiso": {"lat": -33.0472, "lon": -71.6127, "country": "Chile", "code": "CLVAP"},
            "port of montevideo": {"lat": -34.9011, "lon": -56.1645, "country": "Uruguay", "code": "UYMVD"},
            "port of fortaleza": {"lat": -3.7172, "lon": -38.5433, "country": "Brazil", "code": "BRFOR"},
            
            # Australia & Oceania
            "port of sydney": {"lat": -33.8688, "lon": 151.2093, "country": "Australia", "code": "AUSYD"},
            "port of melbourne": {"lat": -37.8136, "lon": 144.9631, "country": "Australia", "code": "AUMEL"},
            "port of brisbane": {"lat": -27.4698, "lon": 153.0251, "country": "Australia", "code": "AUBNE"},
            "port of fremantle": {"lat": -32.0569, "lon": 115.7445, "country": "Australia", "code": "AUFRE"},
            "port of adelaide": {"lat": -34.9285, "lon": 138.6007, "country": "Australia", "code": "AUADL"},
            "port of auckland": {"lat": -36.8485, "lon": 174.7633, "country": "New Zealand", "code": "NZAKL"},
            "port of tauranga": {"lat": -37.6870, "lon": 176.1651, "country": "New Zealand", "code": "NZTAU"},
            
            # Caribbean & Central America
            "port of kingston": {"lat": 17.9712, "lon": -76.7928, "country": "Jamaica", "code": "JMKIN"},
            "port of colon": {"lat": 9.3547, "lon": -79.9009, "country": "Panama", "code": "PACLN"},
            "port of san juan": {"lat": 18.4655, "lon": -66.1057, "country": "Puerto Rico", "code": "PRSJU"},
            "port of freeport": {"lat": 26.5285, "lon": -78.6957, "country": "Bahamas", "code": "BSFPO"},
            
            # Russia & Eastern Europe
            "port of st petersburg": {"lat": 59.9311, "lon": 30.3609, "country": "Russia", "code": "RULED"},
            "port of novorossiysk": {"lat": 44.7230, "lon": 37.7687, "country": "Russia", "code": "RUNVS"},
            "port of vladivostok": {"lat": 43.1056, "lon": 131.8735, "country": "Russia", "code": "RUVVO"},
            "port of gdansk": {"lat": 54.3520, "lon": 18.6466, "country": "Poland", "code": "PLGDN"},
            "port of constanta": {"lat": 44.1598, "lon": 28.6348, "country": "Romania", "code": "ROCND"},
        }
        
        # Create reverse lookup by variations
        self._create_port_variations()
    
    def _create_port_variations(self):
        """Create variations of port names for better matching"""
        variations = {}
        
        for port_name, port_data in self.ports_db.items():
            # Add the original name
            variations[port_name] = port_data
            
            # Add variations without "port of"
            clean_name = port_name.replace("port of ", "")
            variations[clean_name] = port_data
            
            # Add code-based lookup
            if "code" in port_data:
                variations[port_data["code"].lower()] = port_data
            
            # Add country-based variations for major cities
            city_name = clean_name.split()[0]  # First word (city name)
            if len(city_name) > 3:
                variations[city_name] = port_data
        
        self.ports_db.update(variations)
    
    async def get_port_coordinates(self, port_name: str) -> Optional[Dict[str, Any]]:
        """
        Get coordinates for a port by name
        
        Args:
            port_name: Name of the port to look up
            
        Returns:
            Dict with lat, lon, country, and code if found, None otherwise
        """
        # Normalize the port name
        normalized_name = port_name.lower().strip()
        
        # Direct lookup
        if normalized_name in self.ports_db:
            return self.ports_db[normalized_name]
        
        # Fuzzy matching for common variations
        fuzzy_matches = self._fuzzy_port_search(normalized_name)
        if fuzzy_matches:
            return fuzzy_matches[0]  # Return best match
            
        logger.warning(f"Port not found: {port_name}")
        return None
    
    def _fuzzy_port_search(self, query: str) -> List[Dict[str, Any]]:
        """Perform fuzzy search for port names"""
        matches = []
        query_words = set(query.split())
        
        for port_name, port_data in self.ports_db.items():
            port_words = set(port_name.split())
            
            # Calculate word overlap
            overlap = len(query_words & port_words)
            total_words = len(query_words | port_words)
            
            if overlap > 0:
                similarity = overlap / total_words
                if similarity > 0.3:  # Threshold for fuzzy matching
                    matches.append({
                        **port_data,
                        "match_score": similarity,
                        "matched_name": port_name
                    })
        
        # Sort by similarity score
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches
    
    async def search_ports(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for ports matching a query
        
        Args:
            query: Search term
            limit: Maximum number of results
            
        Returns:
            List of matching ports with metadata
        """
        matches = self._fuzzy_port_search(query.lower())
        
        # Remove duplicates and limit results
        seen_codes = set()
        unique_matches = []
        
        for match in matches:
            port_code = match.get("code", match.get("matched_name", ""))
            if port_code not in seen_codes:
                seen_codes.add(port_code)
                unique_matches.append({
                    "name": match.get("matched_name", "Unknown"),
                    "country": match.get("country", "Unknown"),
                    "latitude": match.get("lat"),
                    "longitude": match.get("lon"),
                    "code": match.get("code"),
                    "match_score": match.get("match_score", 0)
                })
                
                if len(unique_matches) >= limit:
                    break
        
        return unique_matches
    
    def calculate_distance_km(self, coord1: Dict[str, float], coord2: Dict[str, float]) -> float:
        """
        Calculate the great circle distance between two points in kilometers
        
        Args:
            coord1: Dictionary with 'lat' and 'lon' keys
            coord2: Dictionary with 'lat' and 'lon' keys
            
        Returns:
            Distance in kilometers
        """
        # Convert latitude and longitude from degrees to radians
        lat1, lon1 = math.radians(coord1["lat"]), math.radians(coord1["lon"])
        lat2, lon2 = math.radians(coord2["lat"]), math.radians(coord2["lon"])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        
        return c * r
    
    def estimate_travel_time(
        self, 
        departure_coords: Dict[str, float], 
        destination_coords: Dict[str, float], 
        goods_type: str
    ) -> int:
        """
        Estimate travel time between two ports
        
        Args:
            departure_coords: Departure port coordinates
            destination_coords: Destination port coordinates
            goods_type: Type of goods (affects vessel speed)
            
        Returns:
            Estimated travel time in days
        """
        # Calculate distance
        distance_km = self.calculate_distance_km(departure_coords, destination_coords)
        
        # Estimate average vessel speed based on goods type and route
        if "container" in goods_type.lower() or "electronics" in goods_type.lower():
            # Fast container ships
            avg_speed_kph = 45  # ~24 knots
        elif "bulk" in goods_type.lower() or "grain" in goods_type.lower():
            # Bulk carriers
            avg_speed_kph = 35  # ~19 knots
        elif "oil" in goods_type.lower() or "fuel" in goods_type.lower():
            # Tankers
            avg_speed_kph = 30  # ~16 knots
        else:
            # General cargo
            avg_speed_kph = 40  # ~22 knots
        
        # Add weather and port delays (20-30% additional time)
        delay_factor = 1.25
        
        # Calculate travel time in hours, then convert to days
        travel_hours = (distance_km / avg_speed_kph) * delay_factor
        travel_days = max(1, round(travel_hours / 24))
        
        logger.info(f"Estimated travel time: {distance_km:.0f} km, {travel_days} days")
        return travel_days
    
    def get_route_characteristics(
        self, 
        departure_coords: Dict[str, float], 
        destination_coords: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Get characteristics of the shipping route
        
        Args:
            departure_coords: Departure port coordinates
            destination_coords: Destination port coordinates
            
        Returns:
            Dictionary with route characteristics
        """
        distance_km = self.calculate_distance_km(departure_coords, destination_coords)
        
        # Determine ocean/sea regions
        route_type = self._classify_route(departure_coords, destination_coords)
        
        # Assess route complexity
        complexity = "low"
        if distance_km > 15000:  # Very long routes
            complexity = "high"
        elif distance_km > 8000:  # Medium routes
            complexity = "medium"
        
        return {
            "distance_km": round(distance_km, 1),
            "route_type": route_type,
            "complexity": complexity,
            "crosses_equator": (departure_coords["lat"] * destination_coords["lat"]) < 0,
            "longitude_span": abs(departure_coords["lon"] - destination_coords["lon"]),
            "latitude_span": abs(departure_coords["lat"] - destination_coords["lat"])
        }
    
    def _classify_route(
        self, 
        departure_coords: Dict[str, float], 
        destination_coords: Dict[str, float]
    ) -> str:
        """Classify the type of shipping route based on coordinates"""
        dep_lat, dep_lon = departure_coords["lat"], departure_coords["lon"]
        dest_lat, dest_lon = destination_coords["lat"], destination_coords["lon"]
        
        # Simple classification based on geographical regions
        if abs(dep_lon - dest_lon) > 60:
            return "transoceanic"
        elif abs(dep_lat - dest_lat) < 10 and abs(dep_lon - dest_lon) < 30:
            return "regional"
        elif max(abs(dep_lat), abs(dest_lat)) > 50:
            return "northern_route"
        elif min(dep_lat, dest_lat) < -30:
            return "southern_route"
        else:
            return "standard"