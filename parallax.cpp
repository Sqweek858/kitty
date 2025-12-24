#include <iostream>
#include <vector>
#include <string>
#include <random>
#include <cmath>
#include <chrono>
#include <cstdlib>

// C++ Parallax Renderer for ZSH
// Renders the starfield ONCE to stdout without clearing screen (uses save/restore cursor)

struct Star {
    int x, y;
    int color_type;
    int brightness;
    char symbol;
};

// Simple pseudo-random for determinism if needed, but we want random here
std::mt19937 rng(std::random_device{}());

std::string get_color_sequence(int type, int brightness) {
    int r, g, b;
    switch (type) {
        case 0: r=40+brightness; g=180+brightness/2; b=220+brightness/3; break; // Cyan
        case 1: r=180+brightness/2; g=50+brightness/2; b=180+brightness/2; break; // Magenta
        case 2: r=200+brightness/3; g=180+brightness/3; b=40+brightness/3; break; // Yellow
        case 3: r=40+brightness/2; g=180+brightness/2; b=80+brightness/2; break; // Green
        case 4: r=220+brightness/4; g=120+brightness/3; b=30+brightness/4; break; // Orange
        case 5: r=60+brightness/2; g=100+brightness/2; b=200+brightness/3; break; // Blue
        case 6: r=160+brightness/2; g=170+brightness/2; b=190+brightness/2; break; // White
        case 7: r=200+brightness/3; g=50+brightness/3; b=60+brightness/3; break; // Red
        default: r=200; g=200; b=200; break;
    }
    if(r>255) r=255; if(g>255) g=255; if(b>255) b=255;
    return "\x1b[38;2;" + std::to_string(r) + ";" + std::to_string(g) + ";" + std::to_string(b) + "m";
}

int main(int argc, char* argv[]) {
    // Get terminal size
    // Default
    int cols = 80;
    int rows = 24;
    
    // We expect COLUMNS and LINES env vars or args
    if (const char* env_cols = std::getenv("COLUMNS")) cols = std::atoi(env_cols);
    if (const char* env_rows = std::getenv("LINES")) rows = std::atoi(env_rows);

    if (argc > 1) cols = std::atoi(argv[1]);
    if (argc > 2) rows = std::atoi(argv[2]);

    int num_stars = (cols * rows) / 35;
    
    std::vector<Star> stars;
    
    for(int i=0; i<num_stars; ++i) {
        Star s;
        s.x = std::uniform_int_distribution<int>(3, cols-2)(rng);
        s.y = std::uniform_int_distribution<int>(4, rows-2)(rng); // Avoid top/bottom overlap
        s.color_type = std::uniform_int_distribution<int>(0, 7)(rng);
        s.brightness = std::uniform_int_distribution<int>(0, 100)(rng);
        
        if (s.brightness > 85) s.symbol = '*'; // Simplified symbols for safety
        else if (s.brightness > 65) s.symbol = '+';
        else if (s.brightness > 45) s.symbol = '.';
        else s.symbol = '.';

        stars.push_back(s);
    }

    // Save cursor position
    std::cout << "\x1b[s";

    for(const auto& s : stars) {
        std::cout << "\x1b[" << s.y << ";" << s.x << "H";
        std::cout << get_color_sequence(s.color_type, s.brightness);
        std::cout << s.symbol;
    }

    // Restore cursor position and reset color
    std::cout << "\x1b[0m\x1b[u";
    std::cout.flush();

    return 0;
}
