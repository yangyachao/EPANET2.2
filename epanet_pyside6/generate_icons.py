import os

ICONS_DIR = "resources/icons"

ICONS = {
    "new.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#2ecc71" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" fill="#e8f8f5" stroke="#27ae60"></path><polyline points="14 2 14 8 20 8" stroke="#27ae60"></polyline><line x1="12" y1="18" x2="12" y2="12" stroke="#2ecc71"></line><line x1="9" y1="15" x2="15" y2="15" stroke="#2ecc71"></line></svg>""",
    
    "open.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#f1c40f" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" fill="#fcf3cf" stroke="#f39c12"></path></svg>""",
    
    "save.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#3498db" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" fill="#ebf5fb" stroke="#2980b9"></path><polyline points="17 21 17 13 7 13 7 21" fill="#d6eaf8" stroke="#2980b9"></polyline><polyline points="7 3 7 8 15 8" stroke="#2980b9"></polyline></svg>""",
    
    "select.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#34495e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3l7.07 16.97 2.51-7.39 7.39-2.51L3 3z" fill="#ecf0f1" stroke="#2c3e50"></path><path d="M13 13l6 6" stroke="#2c3e50"></path></svg>""",
    
    "pan.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#34495e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 11V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v0" stroke="#2c3e50"></path><path d="M14 10V4a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v2" stroke="#2c3e50"></path><path d="M10 10.5V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v8" stroke="#2c3e50"></path><path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15" fill="#ecf0f1" stroke="#2c3e50"></path></svg>""",
    
    "junction.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#2980b9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="8" fill="#d6eaf8" stroke="#2980b9"></circle><circle cx="12" cy="12" r="3" fill="#2980b9" stroke="none"></circle></svg>""",
    
    "reservoir.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#16a085" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2" fill="#d1f2eb" stroke="#16a085"></rect><path d="M3 9h18" stroke="#16a085"></path></svg>""",
    
    "tank.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#27ae60" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 5h18v14H3z" fill="#e9f7ef" stroke="#27ae60"></path><path d="M3 5v14" stroke="#27ae60"></path><path d="M21 5v14" stroke="#27ae60"></path><path d="M3 19h18" stroke="#27ae60"></path><path d="M5 5v-2h14v2" stroke="#27ae60"></path></svg>""",
    
    "pipe.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#7f8c8d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="2" y1="12" x2="22" y2="12" stroke-width="4" stroke="#95a5a6"></line><circle cx="2" cy="12" r="2" fill="#7f8c8d" stroke="none"></circle><circle cx="22" cy="12" r="2" fill="#7f8c8d" stroke="none"></circle></svg>""",
    
    "pump.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#c0392b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="8" fill="#fadbd8" stroke="#c0392b"></circle><path d="M12 5l-5 10h10z" fill="#e74c3c" stroke="none"></path><line x1="2" y1="12" x2="4" y2="12" stroke="#c0392b"></line><line x1="20" y1="12" x2="22" y2="12" stroke="#c0392b"></line></svg>""",
    
    "valve.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#d35400" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12h20" stroke="#d35400"></path><path d="M12 12l-7-7v14z" fill="#e67e22" stroke="#d35400"></path><path d="M12 12l7-7v14z" fill="#e67e22" stroke="#d35400"></path></svg>""",
    
    "label.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#7f8c8d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" fill="#f4f6f7" stroke="#7f8c8d"></path><line x1="7" y1="7" x2="7.01" y2="7" stroke="#7f8c8d"></line></svg>""",
    
    "run.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#27ae60" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3" fill="#2ecc71" stroke="#27ae60"></polygon></svg>""",
    
    "graph.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#8e44ad" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2" fill="#f4ecf7" stroke="#8e44ad"></rect><line x1="8" y1="17" x2="8" y2="11" stroke="#9b59b6"></line><line x1="12" y1="17" x2="12" y2="8" stroke="#9b59b6"></line><line x1="16" y1="17" x2="16" y2="13" stroke="#9b59b6"></line><line x1="3" y1="17" x2="21" y2="17" stroke="#8e44ad"></line></svg>""",
    
    "table.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#8e44ad" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2" fill="#f4ecf7" stroke="#8e44ad"></rect><line x1="3" y1="9" x2="21" y2="9" stroke="#8e44ad"></line><line x1="3" y1="15" x2="21" y2="15" stroke="#8e44ad"></line><line x1="9" y1="3" x2="9" y2="21" stroke="#8e44ad"></line><line x1="15" y1="3" x2="15" y2="21" stroke="#8e44ad"></line></svg>""",
    
    "contour.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#d35400" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8z" fill="#fbeee6" stroke="#d35400"></path><path d="M12 6a6 6 0 1 0 6 6 6 6 0 0 0-6-6zm0 10a4 4 0 1 1 4-4 4 4 0 0 1-4 4z" fill="#e67e22" stroke="#d35400"></path></svg>""",
    
    "status.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#2980b9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10" fill="#d6eaf8" stroke="#2980b9"></circle><line x1="12" y1="16" x2="12" y2="12" stroke="#2980b9"></line><line x1="12" y1="8" x2="12.01" y2="8" stroke="#2980b9"></line></svg>""",
    
    "calibration.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#c0392b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10" fill="#fadbd8" stroke="#c0392b"></circle><circle cx="12" cy="12" r="6" stroke="#c0392b"></circle><circle cx="12" cy="12" r="2" fill="#c0392b" stroke="none"></circle></svg>""",
    
    "energy.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#f39c12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" fill="#fcf3cf" stroke="#f39c12"></polygon></svg>""",
    
    "map_options.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#7f8c8d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3" fill="#95a5a6" stroke="none"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" fill="#f4f6f7" stroke="#7f8c8d"></path></svg>""",
    
    "find.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#2c3e50" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8" fill="#ecf0f1" stroke="#2c3e50"></circle><line x1="21" y1="21" x2="16.65" y2="16.65" stroke="#2c3e50"></line></svg>""",
    
    "backdrop_load.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#8e44ad" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2" fill="#f4ecf7" stroke="#8e44ad"></rect><circle cx="8.5" cy="8.5" r="1.5" fill="#8e44ad" stroke="none"></circle><polyline points="21 15 16 10 5 21" stroke="#8e44ad"></polyline></svg>""",
    
    "backdrop_align.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#8e44ad" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="5 9 2 12 5 15" stroke="#8e44ad"></polyline><polyline points="9 5 12 2 15 5" stroke="#8e44ad"></polyline><polyline points="19 9 22 12 19 15" stroke="#8e44ad"></polyline><polyline points="9 19 12 22 15 19" stroke="#8e44ad"></polyline><line x1="2" y1="12" x2="22" y2="12" stroke="#8e44ad"></line><line x1="12" y1="2" x2="12" y2="22" stroke="#8e44ad"></line></svg>""",
    
    "backdrop_show.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#8e44ad" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" fill="#f4ecf7" stroke="#8e44ad"></path><circle cx="12" cy="12" r="3" fill="#8e44ad" stroke="none"></circle></svg>""",
    
    "backdrop_unload.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#c0392b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2" fill="#fadbd8" stroke="#c0392b"></rect><line x1="9" y1="9" x2="15" y2="15" stroke="#c0392b"></line><line x1="15" y1="9" x2="9" y2="15" stroke="#c0392b"></line></svg>""",
    
    "zoom_in.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#2980b9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8" fill="#d6eaf8" stroke="#2980b9"></circle><line x1="21" y1="21" x2="16.65" y2="16.65" stroke="#2980b9"></line><line x1="11" y1="8" x2="11" y2="14" stroke="#2980b9"></line><line x1="8" y1="11" x2="14" y2="11" stroke="#2980b9"></line></svg>""",
    
    "zoom_out.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#2980b9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8" fill="#d6eaf8" stroke="#2980b9"></circle><line x1="21" y1="21" x2="16.65" y2="16.65" stroke="#2980b9"></line><line x1="8" y1="11" x2="14" y2="11" stroke="#2980b9"></line></svg>""",
    
    "fit_window.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#2980b9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 3 21 3 21 9" stroke="#2980b9"></polyline><polyline points="9 21 3 21 3 15" stroke="#2980b9"></polyline><line x1="21" y1="3" x2="14" y2="10" stroke="#2980b9"></line><line x1="3" y1="21" x2="10" y2="14" stroke="#2980b9"></line></svg>"""
}

def main():
    if not os.path.exists(ICONS_DIR):
        os.makedirs(ICONS_DIR)
        
    for filename, content in ICONS.items():
        filepath = os.path.join(ICONS_DIR, filename)
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Generated {filepath}")

if __name__ == "__main__":
    main()
