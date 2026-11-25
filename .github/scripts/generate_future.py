#!/usr/bin/env python3
"""Generates the 'Future Tech Stack' grid (dist/future-skills.svg).

Reuses the exact same grid, logo loader and animation as generate_skills.py,
so this grid looks identical to the current skills grid. Only the list differs.
Logos come from the Simple Icons CDN; anything missing falls back to
assets/icons/<slug>.svg, then to a coloured monogram (same as the skills grid).
Standard library only. Set NO_CDN=1 to test offline.
"""
import os
import generate_skills as skills

OUT = os.environ.get("FUTURE_OUT_FILE", "dist/future-skills.svg")

# (simple-icons slug, label, brand colour, optional fallback text)
FUTURE = [
    ("openjdk", "Java", "ED8B00", "Java"),
    ("springboot", "Spring Boot", "6DB33F", "SB"),
    ("apachekafka", "Kafka", "231F20", "Kafka"),
    ("rabbitmq", "RabbitMQ", "FF6600", "MQ"),
    ("tailwindcss", "Tailwind CSS", "06B6D4", "TW"),
    ("linux", "Linux", "FCC624", "Lnx"),
    ("django", "Django", "44B78B", "Dj"),
    ("hibernate", "Hibernate", "59666C", "Hib"),
    ("jsonwebtokens", "JWT", "D63AFF", "JWT"),
    ("redis", "Redis", "FF4438", "Rd"),
    ("elasticsearch", "Elasticsearch", "005571", "ES"),
    ("amazonapigateway", "API Gateway", "FF4F8B", "API"),
    ("spring", "Config Server", "6DB33F", "CS"),
    ("nginx", "Nginx", "009639", "Nx"),
    ("jenkins", "Jenkins", "D24939", "Jnk"),
    ("micrometer", "Micrometer", "1C6EA4", "Mic"),
    ("grafana", "Grafana", "F46800", "Gf"),
    ("logstash", "Logstash", "005571", "LS"),
    ("kibana", "Kibana", "005571", "Kb"),
    ("prometheus", "Prometheus", "E6522C", "Pr"),
]

if __name__ == "__main__":
    skills.SKILLS = FUTURE  # build() reads the module-level list
    svg, found = skills.build()
    svg = svg.replace('aria-label="Skills"', 'aria-label="Future tech stack"', 1)
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {OUT}: {len(FUTURE)} future items, {found} logos loaded, {len(FUTURE)-found} monogram fallbacks")
