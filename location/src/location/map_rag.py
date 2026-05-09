import json
from pathlib import Path
from typing import Dict, List, Optional


class HospitalMapRAG:
    def __init__(self, map_json_path: Path):
        self.map_json_path = map_json_path
        self.map_data = self._load_map()

    def _load_map(self) -> Dict:
        if not self.map_json_path.exists():
            return {
                "map_name": "",
                "building": "",
                "floor": "",
                "zones": [],
            }

        return json.loads(self.map_json_path.read_text(encoding="utf-8"))

    def get_metadata(self) -> Dict[str, str]:
        return {
            "map_name": str(self.map_data.get("map_name", "")).strip(),
            "building": str(self.map_data.get("building", "")).strip(),
            "floor": str(self.map_data.get("floor", "")).strip(),
        }

    def get_zones(self) -> List[Dict]:
        zones = self.map_data.get("zones", [])
        if isinstance(zones, list):
            return zones
        return []

    def find_zone_by_name(self, query_text: str) -> Optional[Dict]:
        query_text = (query_text or "").strip()
        if not query_text:
            return None

        zones = self.get_zones()

        for zone in zones:
            zone_name = str(zone.get("name", "")).strip()
            if zone_name and zone_name in query_text:
                return zone

        for zone in zones:
            zone_name = str(zone.get("name", "")).strip()
            if zone_name and query_text in zone_name:
                return zone

        return None
        
    def get_matched_place_name(self, query_text: str) -> str:
        zone = self.find_zone_by_name(query_text)
        if zone is None:
            return ""
        return str(zone.get("name", "")).strip()

    def has_match(self, query_text: str) -> bool:
        return self.find_zone_by_name(query_text) is not None
        
    def build_map_context(self, query_text: str) -> str:
        metadata = self.get_metadata()
        zone = self.find_zone_by_name(query_text)

        if zone is None:
            zone_names = [
                str(z.get("name", "")).strip()
                for z in self.get_zones()
                if str(z.get("name", "")).strip()
            ]
            return (
                f"맵 이름: {metadata['map_name']}\n"
                f"건물: {metadata['building']}\n"
                f"층: {metadata['floor']}\n"
                f"검색 결과: 일치하는 장소를 찾지 못함\n"
                f"등록된 장소: {', '.join(zone_names)}"
            )

        description = str(zone.get("description", "")).strip()

        if description:
            return (
                f"맵 이름: {metadata['map_name']}\n"
                f"건물: {metadata['building']}\n"
                f"층: {metadata['floor']}\n"
                f"검색된 장소: {zone.get('name', '')}\n"
                f"자연어 위치 설명: {description}\n"
                f"frame_id: {zone.get('frame_id', '')}\n"
                f"type: {zone.get('type', '')}\n"
                f"x_min: {zone.get('x_min', '')}\n"
                f"x_max: {zone.get('x_max', '')}\n"
                f"y_min: {zone.get('y_min', '')}\n"
                f"y_max: {zone.get('y_max', '')}\n"
                f"rotation_deg: {zone.get('rotation_deg', '')}"
            )

        return (
            f"맵 이름: {metadata['map_name']}\n"
            f"건물: {metadata['building']}\n"
            f"층: {metadata['floor']}\n"
            f"검색된 장소: {zone.get('name', '')}\n"
            f"frame_id: {zone.get('frame_id', '')}\n"
            f"type: {zone.get('type', '')}\n"
            f"x_min: {zone.get('x_min', '')}\n"
            f"x_max: {zone.get('x_max', '')}\n"
            f"y_min: {zone.get('y_min', '')}\n"
            f"y_max: {zone.get('y_max', '')}\n"
            f"rotation_deg: {zone.get('rotation_deg', '')}"
        )
